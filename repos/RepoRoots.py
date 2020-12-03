import errno
import requests
import subprocess

from .submodules.architectures import Architecture

######################################################################
######################################################################
class RepoRootsException(Exception):

  ####################################################################
  # Public methods
  ####################################################################

  ####################################################################
  # Overridden methods
  ####################################################################
  def __init__(self, msg, *args, **kwargs):
    super(RepoRootsException, self).__init__(*args, **kwargs)
    self._msg = msg

  ######################################################################
  def __str__(self):
    return self._msg

  ####################################################################
  # Protected methods
  ####################################################################

######################################################################
######################################################################
class RepoRootsBeakerNoDistroTree(RepoRootsException):

  ####################################################################
  # Overridden methods
  ####################################################################
  def __init__(self, distroFamily, *args, **kwargs):
    super(RepoRootsBeakerNoDistroTree, self).__init__(
      "beaker has no distro tree for family: {0}".format(distroFamily),
      *args, **kwargs)

######################################################################
######################################################################
class RepoRootsBeakerNotFound(RepoRootsException):

  ####################################################################
  # Overridden methods
  ####################################################################
  def __init__(self, *args, **kwargs):
    super(RepoRootsBeakerNotFound, self).__init__("beaker command not found",
                                                  *args, **kwargs)

######################################################################
######################################################################
class RepoRoots(object):
  # We cache the results of determining the various roots to avoid
  # having to constantly perform network queries.
  #
  # We start with None so that separate dictionaries are created per
  # subclass.
  __cachedLatest = None
  __cachedNightly = None
  __cachedReleased = None

  ####################################################################
  # Public methods
  ####################################################################
  @classmethod
  def availableRoots(cls, architecture = None):
    """Returns a dictionary with keys being the <major>.<minor> and the values
    the URI for the release repo.

    This method prioritizes released over latest over nightly versions.
    """
    available = cls._cachedNightly(architecture)
    available.update(cls._cachedLatest(architecture))
    available.update(cls._cachedReleased(architecture))
    return available

  ####################################################################
  @classmethod
  def availableLatestRoots(cls, architecture = None):
    """Returns a dictionary with keys being the <major>.<minor> and the values
    the URI for the release repo.

    This method prioritizes latest over released over nightly versions.
    """
    available = cls._cachedNightly(architecture)
    available.update(cls._cachedReleased(architecture))
    available.update(cls._cachedLatest(architecture))
    return available

  ####################################################################
  @classmethod
  def availableNightlyRoots(cls, architecture = None):
    """Returns a dictionary with keys being the <major>.<minor> and the values
    the URI for the release repo.

    This method prioritizes nightly over latest over released versions.
    """
    available = cls._cachedReleased(architecture)
    available.update(cls._cachedLatest(architecture))
    available.update(cls._cachedNightly(architecture))
    return available

  ####################################################################
  # Protected methods
  ####################################################################
  @classmethod
  def _availableLatest(cls, architecture):
    raise NotImplementedError

  ####################################################################
  @classmethod
  def _availableNightly(cls, architecture):
    raise NotImplementedError

  ####################################################################
  @classmethod
  def _availableReleased(cls, architecture):
    raise NotImplementedError

  ####################################################################
  @classmethod
  def _beakerRoots(cls):
    raise NotImplementedError

  ####################################################################
  @classmethod
  def _host(cls):
    raise NotImplementedError

  ####################################################################
  @classmethod
  def _path_contents(cls, path):
    return cls._uri_contents("http://{0}{1}".format(cls._host(), path))

  ####################################################################
  @classmethod
  def _uri_contents(cls, uri):
    contents = ""
    try:
      data = requests.get(uri)
      if data.status_code == requests.codes["ok"]:
        contents = data.text
    except requests.Timeout:
      pass

    return contents

  ####################################################################
  # Protected methods
  ####################################################################
  @classmethod
  def _beakerDistroTree(cls, distroFamily, name = None):
    beaker = None
    command = ["bkr", "distro-trees-list", "--family", distroFamily,
               "--format", "json"]
    if name is not None:
      command.extend(["--name", name])
    try:
      # Use universal_newlines to force python3 to return strings.
      beaker = subprocess.Popen(command, stdout = subprocess.PIPE,
                                universal_newlines = True)
    except OSError as ex:
      if ex.errno != errno.ENOENT:
        raise
      raise RepoRootsBeakerNotFound

    (stdout, _) = beaker.communicate()
    if beaker.returncode != 0:
      if beaker.returncode == 1:
        raise RepoRootsBeakerNoDistroTree(distroFamily)
      raise RepoRootsException(
              "beaker unexpected failure; return code = {0}".format(
                                                          beaker.returncode))
    return stdout

  ####################################################################
  @classmethod
  def _cachedLatest(cls, architecture):
    if cls.__cachedLatest is None:
      cls.__cachedLatest = {}
    if architecture is None:
      architecture = Architecture.defaultChoice().name()
    if architecture not in cls.__cachedLatest:
      cls.__cachedLatest[architecture] = cls._availableLatest(architecture)
    return cls.__cachedLatest[architecture].copy()

  ####################################################################
  @classmethod
  def _cachedNightly(cls, architecture):
    if cls.__cachedNightly is None:
      cls.__cachedNightly = {}
    if architecture is None:
      architecture = Architecture.defaultChoice().name()
    if architecture not in cls.__cachedNightly:
      cls.__cachedNightly[architecture] = cls._availableNightly(architecture)
    return cls.__cachedNightly[architecture].copy()

  ####################################################################
  @classmethod
  def _cachedReleased(cls, architecture):
    if cls.__cachedReleased is None:
      cls.__cachedReleased = {}
    if architecture is None:
      architecture = Architecture.defaultChoice().name()
    if architecture not in cls.__cachedReleased:
      cls.__cachedReleased[architecture] = cls._availableReleased(architecture)
    return cls.__cachedReleased[architecture].copy()
