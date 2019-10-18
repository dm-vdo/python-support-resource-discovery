import re

from .RepoRoots import RepoRoots

######################################################################
######################################################################
class RhelRoots(RepoRoots):
  # Exclude any release prior to the combined minimum major and minor.
  __RHEL_MINIMUM_MAJOR = 7
  __RHEL_MINIMUM_MINOR = 5

  ####################################################################
  # Overridden methods
  ####################################################################
  @classmethod
  def _availableLatest(cls, architecture):
    path = cls._startingPath()
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
    for major in range(min(majors), max(majors) + 1):
      majorMatches = list(filter(lambda x: x[1] == major, matches))
      minors = [x[2] for x in majorMatches]
      for minor in range(min(minors), max(minors) + 1):
        minorMatches = list(filter(lambda x: x[2] == minor, majorMatches))
        maxZStream = max([x[3] for x in minorMatches])
        maxMatch = list(filter(lambda x: x[3] == maxZStream, minorMatches))
        maxMatch = maxMatch[0]
        available["{0}.{1}".format(maxMatch[1], maxMatch[2])] = (
          "http://{0}{1}/{2}/compose".format(cls._host(), path, maxMatch[0]))

    return available
  
  ####################################################################
  @classmethod
  def _availableReleased(cls, architecture):
    path = cls._startingPath()
    data = cls._path_contents("{0}/".format(path))

    # Find all the released versions greater than or equal to the RHEL
    # minimum major and then find their minors.
    available = {}
    regex = r"(?i)<a\s+href=\"(released-RHEL-(\d+))/\">\1/</a>"
    for release in filter(
                    lambda x: int(x[1]) >= cls.__RHEL_MINIMUM_MAJOR,
                    re.findall(regex, data)):
      available.update(cls._availableReleasedMinors(
                                          "{0}/{1}".format(path, release[0]),
                                          int(release[1])))
    return available

  ####################################################################
  @classmethod
  def _host(cls):
    return "download.eng.bos.redhat.com"

  ####################################################################
  # Protected methods
  ####################################################################
  @classmethod
  def _availableReleasedMinors(cls, path, major):
    path = "{0}/RHEL-{1}".format(path, major)
    data = cls._path_contents("{0}/".format(path))
  
    regex = r"(?i)<a\s+href=\"({0}\.(\d+)(|\.\d+))/\">\1/</a>".format(major)
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
    for minor in range(min(minors), max(minors) + 1):
      minorMatches = list(filter(lambda x: x[1] == minor, matches))
      maxZStream = max([x[2] for x in minorMatches])
      maxMatch = list(filter(lambda x: x[2] == maxZStream, minorMatches))
      maxMatch = maxMatch[0]
      available["{0}.{1}".format(major, maxMatch[1])] = (
        "http://{0}{1}/{2}".format(cls._host(), path, maxMatch[0]))
    return available

  ####################################################################
  @classmethod
  def _startingPath(cls):
    return "/composes"
   
