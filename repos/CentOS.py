import re

from .Repository import (Repository, RepositoryBeakerNoDistroTree,
                         RepositoryBeakerNotFound)

######################################################################
######################################################################
class CentOS(Repository):
  # Exclude any release prior to the combined minimum major and minor.
  __CENTOS_MINIMUM_MAJOR = 8
  __CENTOS_MINIMUM_MINOR = 3

  # All found roots with no distinction as to architecture.
  # Keyed by category.
  __agnosticRoots = {}

  ####################################################################
  # Overridden methods
  ####################################################################
  @classmethod
  def _availableLatest(cls, architecture):
    return cls._availableReleased(architecture)

  ####################################################################
  @classmethod
  def _availableNightly(cls, architecture):
    return cls._availableReleased(architecture)

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
        path = cls._releasedStartingPath()
        data = cls._path_contents("{0}/".format(path))

        # Find all the released versions greater than or equal to the CentOS
        # minimum major and then find their minors.
        regex = r"(?i)<a\s+href=\"(centos-(\d+))/\">\1/</a>"
        for release in filter(
                        lambda x: int(x[1]) >= cls.__CENTOS_MINIMUM_MAJOR,
                        re.findall(regex, data)):
          roots.update(cls._availableReleasedMinors(
                          "{0}/centos-{1}".format(path, release[1]),
                          int(release[1])))

      cls.__agnosticRoots["released"] = roots

    return cls. _filterNonExistentArchitecture(cls.__agnosticRoots["released"],
                                               architecture)

  ####################################################################
  @classmethod
  def _beakerRoots(cls):
    roots = {}
    major = cls.__CENTOS_MINIMUM_MAJOR - 1
    while True:
      major += 1
      minor = (-1 if major > cls.__CENTOS_MINIMUM_MAJOR
                  else cls.__CENTOS_MINIMUM_MINOR - 1)
      try:
        while True:
          minor += 1
          family = "CentOSLinux{0}".format(major)
          name = "CentOS-{0}.{1}".format(major, minor,)
          variant = "BaseOS"
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
  def _releasedStartingPath(cls, architecture = None):
    return "/released/CentOS"

  ####################################################################
  # Protected methods
  ####################################################################
  @classmethod
  def _availableReleasedMinors(cls, path, major):
    data = cls._path_contents("{0}/".format(path))

    regex = r"(?i)<a\s+href=\"({0}\.(\d+)(|\.\d+))/\">\1/</a>".format(major)
    matches = re.findall(regex, data)
    if major == cls.__CENTOS_MINIMUM_MAJOR:
      matches = filter(lambda x: int(x[1]) >= cls.__CENTOS_MINIMUM_MINOR,
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
                      "{0}/{1}".format(value, "BaseOS"))) is not None ])

