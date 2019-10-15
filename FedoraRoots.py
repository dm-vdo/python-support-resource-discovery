import re

from .RepoRoots import RepoRoots

######################################################################
######################################################################
class FedoraRoots(RepoRoots):
  # Exclude any release prior to 28.
  __FEDORA_MINIMUM_MAJOR = 28
  
  ####################################################################
  # Overridden methods
  ####################################################################
  @classmethod
  def _availableLatest(cls, architecture):
    return cls._availableCommon("{0}/development".format(
                                  cls._startingPath(architecture)))
    
  ####################################################################
  @classmethod
  def _availableReleased(cls, architecture):
    return cls._availableCommon("{0}/releases".format(
                                  cls._startingPath(architecture)))
  
  ####################################################################
  @classmethod
  def _host(cls):
    return "dl.fedoraproject.org"

  ####################################################################
  # Protected methods
  ####################################################################
  @classmethod
  def _availableCommon(cls, path):
    data = cls._path_contents("{0}/".format(path))

    # Find all the released versions greater than or equal to the Fedora
    # minimum major (limited to no less than 28, Fedora 28 being the version
    # first incorporating VDO).
    regex = r"(?i)<a\s+href=\"(\d+)/\">\1/</a>"
    available = { x : cls._availableUri(path, x)
                  for x in filter(
                              lambda x: int(x) >= cls.__FEDORA_MINIMUM_MAJOR,
                              re.findall(regex, data)) }
    return available

  ####################################################################
  @classmethod
  def _availableUri(cls, path, version):
    # If the version has a README file that indicates it has been moved to
    # the archive server.
    data = cls._path_contents("{0}/{1}/".format(path, version))
    regex = r"(?i)<a\s+href=\"(README)\">\1</a>"
    host = cls._host()
    match = re.search(regex, data)
    if match is not None:
      host = "archives.fedoraproject.org"
      path = path.replace("/pub/", "/pub/archive/", 1)
    return "http://{0}{1}/{2}".format(host, path, version) 

  ####################################################################
  @classmethod
  def _startingPath(cls, architecture):
    path = "/pub/fedora"
    if architecture not in ["ppc64le", "s390x"]:
      path = "{0}/linux".format(path)
    else:
      path = "{0}-secondary".format(path)
    return path
