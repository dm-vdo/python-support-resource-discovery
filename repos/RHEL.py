import re

from .Repository import (Repository, RepositoryBeakerNoDistroTree,
                         RepositoryBeakerNotFound)

######################################################################
######################################################################
class RHEL(Repository):
  # Exclude any release prior to the combined minimum major and minor.
  __RHEL_MINIMUM_MAJOR = 7
  __RHEL_MINIMUM_MINOR = 5

  # All found roots with no distinction as to architecture.
  # Keyed by category.
  __agnosticRoots = {}

  ####################################################################
  # Overridden methods
  ####################################################################
  @classmethod
  def _availableLatest(cls, architecture):
    if "latest" not in cls.__agnosticRoots:
      # Find all the released versions greater than or equal to the RHEL
      # minimum major and then find their minors.
      roots = {}
      path = cls._latestStartingPath()

      for rhel in cls._findMajorRhels(path,
                                      r"<a\s+href=\"(rhel-(\d+))/\">\1/</a>"):
        roots.update(cls._availableLatestMinors(
                "{0}/{1}/rel-eng/{2}".format(path, rhel[0], rhel[0].upper())))
      cls.__agnosticRoots["latest"] = roots

    return cls. _filterNonExistentArchitecture(cls.__agnosticRoots["latest"],
                                               architecture)

  ####################################################################
  @classmethod
  def _availableNightly(cls, architecture):
    if "nightly" not in cls.__agnosticRoots:
      # Find all the released versions greater than or equal to the RHEL
      # minimum major and then find their minors.
      roots = {}
      path = cls._nightlyStartingPath()

      for rhel in cls._findMajorRhels(path,
                                      r"<a\s+href=\"(rhel-(\d+))/\">\1/</a>"):
        roots.update(cls._availableNightlyMinors(
                "{0}/{1}/nightly/{2}".format(path, rhel[0], rhel[0].upper())))
      cls.__agnosticRoots["nightly"] = roots

    return cls. _filterNonExistentArchitecture(cls.__agnosticRoots["nightly"],
                                               architecture)

  ####################################################################
  @classmethod
  def _availableReleased(cls, architecture):
    if "released" not in cls.__agnosticRoots:
      # Try to get the released roots from beaker.  If beaker cannot be
      # reached get them from the web.
      roots = {}
      try:
        roots = cls._beakerRoots()
      except RepositoryBeakerNotFound:
        # Find all the released versions greater than or equal to the RHEL
        # minimum major and then find their minors.
        path = cls._releasedStartingPath()
        for rhel in cls._findMajorRhels(
                                path, r"<a\s+href=\"(RHEL-(\d+))/\">\1/</a>"):
          roots.update(cls._availableReleasedMinors(
                          "{0}/{1}".format(path, rhel[0]), int(rhel[1])))

      cls.__agnosticRoots["released"] = roots

    return cls. _filterNonExistentArchitecture(cls.__agnosticRoots["released"],
                                               architecture)

  ####################################################################
  @classmethod
  def _beakerRoots(cls):
    roots = {}
    major = cls.__RHEL_MINIMUM_MAJOR - 1
    while True:
      major += 1
      minor = (-1 if major > cls.__RHEL_MINIMUM_MAJOR
                  else cls.__RHEL_MINIMUM_MINOR - 1)
      try:
        while True:
          minor += 1
          family = "RedHatEnterpriseLinux{0}".format(major)
          name = "RHEL-{0}.{1}{2}".format(major, minor,
                                          "" if major < 8 else ".0")
          variant = "Server" if major < 8 else "BaseOS"
          root = cls._beakerRoot(family, name, variant)
          if root is not None:
            roots["{0}.{1}".format(major, minor)] = root

      except RepositoryBeakerNoDistroTree:
        # If minor is zero we've exhausted the majors and are done.
        # If it's not we only know we've exhausted the current major.
        if minor == 0:
          break

    return roots

  ####################################################################
  @classmethod
  def _host(cls):
    return "download.eng.bos.redhat.com"

  ####################################################################
  @classmethod
  def _latestStartingPath(cls, architecture = None):
    return ""

  ####################################################################
  @classmethod
  def _nightlyStartingPath(cls, architecture = None):
    return ""

  ####################################################################
  @classmethod
  def _releasedStartingPath(cls, architecture = None):
    return "/released"

  ####################################################################
  # Protected methods
  ####################################################################
  @classmethod
  def _availableLatestMinors(cls, path):
    data = cls._path_contents("{0}/".format(path))

    # Find all the latest greater than or equal to the RHEL minimum major.
    regex = r"(?i)<a\s+href=\"(latest-RHEL-(\d+)\.(\d+)(|\.\d+))/\">\1/</a>"
    matches = filter(lambda x: int(x[1]) >= cls.__RHEL_MINIMUM_MAJOR,
                     re.findall(regex, data))
    # Convert the major/minor/zStream to integers.
    matches = [(x[0],
                int(x[1]),
                int(x[2]),
                int(x[3].lstrip(".")) if x[3] != "" else 0) for x in matches]
    # Exclude any minimum major versions that have a minor less than the
    # minimum minor.
    matches = filter(lambda x: not ((x[1] == cls.__RHEL_MINIMUM_MAJOR)
                                    and (x[2] < cls.__RHEL_MINIMUM_MINOR)),
                     matches)
    matches = list(matches)

    available = {}
    majors = [x[1] for x in matches]
    if len(majors) > 0:
      for major in range(min(majors), max(majors) + 1):
        majorMatches = list(filter(lambda x: x[1] == major, matches))
        minors = [x[2] for x in majorMatches]
        if len(minors) > 0:
          for minor in range(min(minors), max(minors) + 1):
            minorMatches = list(filter(lambda x: x[2] == minor, majorMatches))
            if len(minorMatches) > 0:
              maxZStream = max([x[3] for x in minorMatches])
              maxMatch = list(filter(lambda x: x[3] == maxZStream,
                                     minorMatches))
              maxMatch = maxMatch[0]
              available["{0}.{1}".format(maxMatch[1], maxMatch[2])] = (
                "http://{0}{1}/{2}/compose".format(cls._host(), path,
                                                   maxMatch[0]))

    return available

  ####################################################################
  @classmethod
  def _availableNightlyMinors(cls, path):
    return cls._availableLatestMinors(path)

  ####################################################################
  @classmethod
  def _availableReleasedMinors(cls, path, major):
    data = cls._path_contents("{0}/".format(path))

    regex = r"<a\s+href=\"({0}\.(\d+)(|\.\d+))/\">\1/</a>".format(major)
    matches = re.findall(regex, data)
    if major == cls.__RHEL_MINIMUM_MAJOR:
      matches = filter(lambda x: int(x[1]) >= cls.__RHEL_MINIMUM_MINOR,
                       matches)
    # Convert the minor/zStream to integers.
    matches = [(x[0],
                int(x[1]),
                int(x[2].lstrip(".")) if x[2] != "" else 0) for x in matches]

    available = {}
    minors = [x[1] for x in matches]
    if len(minors) > 0:
      for minor in range(min(minors), max(minors) + 1):
        minorMatches = list(filter(lambda x: x[1] == minor, matches))
        if len(minorMatches) > 0:
          maxZStream = max([x[2] for x in minorMatches])
          maxMatch = list(filter(lambda x: x[2] == maxZStream, minorMatches))
          maxMatch = maxMatch[0]
          available["{0}.{1}".format(major, maxMatch[1])] = (
            "http://{0}{1}/{2}".format(cls._host(), path, maxMatch[0]))
    return available

  ####################################################################
  @classmethod
  def _filterNonExistentArchitecture(cls, repoUris, architecture):
    """Filters out the repo uris that don't have a subdir for the
    specified archtecture returning only those that do.
    """
    regex = re.compile(r"(?i)<a\s+href=\"({0}/)\">\1</a>".format(architecture))

    return dict([ (key, value)
      for (key, value) in repoUris.items()
        if re.search(regex,
                     cls._uri_contents(
                      "{0}/{1}".format(value,
                                       "Server" if float(key) < 8
                                                else "BaseOS"))) is not None ])

  ####################################################################
  @classmethod
  def _findMajorRhels(cls, path, regex):
    data = cls._path_contents("{0}/".format(path))

    # Find all the released versions greater than or equal to the RHEL
    # minimum major.
    return filter(lambda x: int(x[1]) >= cls.__RHEL_MINIMUM_MAJOR,
                  re.findall(regex, data))
