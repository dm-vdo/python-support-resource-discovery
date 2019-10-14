import re

from RepoRoots import RepoRoots

######################################################################
######################################################################
class RhelRoots(RepoRoots):
  __RHEL_MINIMUM_MAJOR = 7

  ####################################################################
  # Overridden methods
  ####################################################################
  @classmethod
  def _availableLatest(cls, architecture):
    path = cls._startingPath()
    data = cls._path_contents("{0}/".format(path))

    # Find all the latest greater than or equal to the RHEL minimum major
    # (limited to no less than 7, RHEL 7 being the major version first
    # incorporating VDO).
    regex = r"(?i)<a\s+href=\"(latest-RHEL-(\d+)\.(\d+)(|\.\d+))/\">\1/</a>"
    matches = filter(lambda x: int(x[1]) >= max(7, cls.__RHEL_MINIMUM_MAJOR),
                     re.findall(regex, data))
    # RHEL 7.5 is the first RHEL release that incorporated VDO; exclude any
    # 7.x versions where x is less than 5.
    matches = filter(lambda x: not ((int(x[1]) == 7) and (int(x[2]) < 5)), 
                     matches)
    matches = list(matches)
    
    available = {}
    for major in range(int(min(matches)[1]), int(max(matches)[1]) + 1):
      majorMatches = list(filter(lambda x: int(x[1]) == major, matches))
      for minor in range(int(min(majorMatches)[2]), 
                         int(max(majorMatches)[2]) + 1):
        minorMatches = list(filter(lambda x: int(x[2]) == minor, majorMatches))
        maxMatch = max(minorMatches)
        available["{0}.{1}".format(maxMatch[1], maxMatch[2])] = (
          "http://{0}{1}/{2}/compose".format(cls._host(), path, maxMatch[0]))
    return available
  
  ####################################################################
  @classmethod
  def _availableReleased(cls, architecture):
    path = cls._startingPath()
    data = cls._path_contents("{0}/".format(path))

    # Find all the released versions greater than or equal to the RHEL minimum 
    # major (limited to no less than 7, RHEL 7 being the major version first
    # incorporating VDO) and then find their minors.
    available = {}
    regex = r"(?i)<a\s+href=\"(released-RHEL-(\d+))/\">\1/</a>"
    for release in filter(
                      lambda x: int(x[1]) >= max(7, cls.__RHEL_MINIMUM_MAJOR),
                      re.findall(regex, data)):
      available.update(cls._availableReleasedMinors(
                          "{0}/{1}".format(path, release[0]), int(release[1])))
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
    if major == 7:
      matches = filter(lambda x: int(x[1]) >= 5, matches)
    matches = list(matches)
    
    available = {}
    for minor in range(int(min(matches)[1]), 
                       int(max(matches)[1]) + 1):
      minorMatches = list(filter(lambda x: int(x[1]) == minor, matches))
      maxMatch = max(minorMatches)
      available["{0}.{1}".format(major, maxMatch[1])] = (
        "http://{0}{1}/{2}".format(cls._host(), path, maxMatch[0]))
    return available

  ####################################################################
  @classmethod
  def _startingPath(cls):
    return "/composes"
   
