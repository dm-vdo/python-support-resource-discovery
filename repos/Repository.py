# Although the requests python package would simplify the processing slightly
# there is an Objective-C runtime error on macOS using it in an ansible
# context.  Thus we use httplib and urlparse.
import platform
if int(platform.python_version_tuple()[0]) < 3:
  import httplib
  import urlparse
else:
  from http import client as httplib
  from urllib import parse as urlparse

import errno
import json
import socket
import subprocess

from .submodules.architectures import Architecture

######################################################################
######################################################################
class RepositoryException(Exception):

  ####################################################################
  # Public methods
  ####################################################################

  ####################################################################
  # Overridden methods
  ####################################################################
  def __init__(self, msg, *args, **kwargs):
    super(RepositoryException, self).__init__(*args, **kwargs)
    self._msg = msg

  ######################################################################
  def __str__(self):
    return self._msg

  ####################################################################
  # Protected methods
  ####################################################################

######################################################################
######################################################################
class RepositoryBeakerNoDistroTree(RepositoryException):

  ####################################################################
  # Overridden methods
  ####################################################################
  def __init__(self, family, *args, **kwargs):
    super(RepositoryBeakerNoDistroTree, self).__init__(
      "beaker has no distro tree for family: {0}".format(family),
      *args, **kwargs)

######################################################################
######################################################################
class RepositoryBeakerNotFound(RepositoryException):

  ####################################################################
  # Overridden methods
  ####################################################################
  def __init__(self, *args, **kwargs):
    super(RepositoryBeakerNotFound, self).__init__("beaker command not found",
                                                  *args, **kwargs)

######################################################################
######################################################################
class Repository(object):
  # We cache the results of determining the various roots to avoid
  # having to constantly perform network queries.
  #
  # We start with None so that separate dictionaries are created per
  # subclass.
  __cachedLatest = None
  __cachedNightly = None
  __cachedReleased = None
  __cachedUriContents = {}

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
  def _beakerRoot(cls, family, name, variant):
    beaker = None
    command = ["bkr", "distro-trees-list", "--family", family,
               "--name", name, "--format", "json"]
    try:
      # Use universal_newlines to force python3 to return strings.
      beaker = subprocess.Popen(command, stdout = subprocess.PIPE,
                                universal_newlines = True)
    except OSError as ex:
      if ex.errno != errno.ENOENT:
        raise
      raise RepositoryBeakerNotFound

    (stdout, _) = beaker.communicate()
    if beaker.returncode != 0:
      if beaker.returncode == 1:
        raise RepositoryBeakerNoDistroTree(family)
      raise RepositoryException(
              "beaker unexpected failure; return code = {0}".format(
                                                          beaker.returncode))

    distros = list(filter(lambda x: x["variant"] == variant,
                          json.loads(stdout)))

    # Preferentially use http links from Boston beaker controller.
    available = []
    for entry in distros:
      available = list(filter(lambda x: x[0].endswith("bos.redhat.com")
                                          and x[1].startswith("http"),
                              entry["available"]))
      available = [ x[1].rsplit("/{0}/{1}/os".format(variant,
                                                     entry["arch"]), 1)[0]
                    for x in available]
      if len(available) > 0:
        break

    # If not Boston try RDU.
    if len(available) == 0:
      for entry in distros:
        available = list(filter(lambda x: x[0].endswith("rdu.redhat.com")
                                            and x[1].startswith("http"),
                                entry["available"]))
        available = [ x[1].rsplit("/{0}/{1}/os".format(variant,
                                                       entry["arch"]), 1)[0]
                      for x in available]
        if len(available) > 0:
          break

    # If not Boston nor RDU take whatever we can get.
    if len(available) == 0:
      for entry in distros:
        available = list(filter(lambda x: x[1].startswith("http"),
                                entry["available"]))
        available = [ x[1].rsplit("/{0}/{1}/os".format(variant,
                                                       entry["arch"]), 1)[0]
                      for x in available]
        if len(available) > 0:
          break

    return None if len(available) == 0 else available[0]

  ####################################################################
  @classmethod
  def _beakerRoots(cls):
    raise NotImplementedError

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

  ####################################################################
  @classmethod
  def _host(cls):
    raise NotImplementedError

  ####################################################################
  @classmethod
  def _latestStartingPath(cls, architecture = None):
    return cls._releasedStartingPath(architecture)

  ####################################################################
  @classmethod
  def _nightlyStartingPath(cls, architecture = None):
    return cls._releasedStartingPath(architecture)

  ####################################################################
  @classmethod
  def _releasedStartingPath(cls, architecture = None):
    raise NotImplementedError

  ####################################################################
  @classmethod
  def _path_contents(cls, path = None):
    if path is None:
      path = cls._releasedStartingPath()
    return cls._uri_contents("http://{0}{1}".format(cls._host(), path))

  ####################################################################
  @classmethod
  def _uri_contents(cls, uri, retries = 3):
    if not uri.endswith("/"):
      uri = "{0}/".format(uri)
    if uri not in cls.__cachedUriContents:
      parsed = urlparse.urlparse(uri)
      for iteration in range(retries):
        try:
          connection = httplib.HTTPConnection(parsed.netloc, timeout = 10)
          connection.request("GET", parsed.path)
          response = connection.getresponse()
          if response.status == 200:
            cls.__cachedUriContents[uri] = response.read().decode("UTF-8")
            break
        except (socket.gaierror, socket.timeout):
          if iteration >= (retries - 1):
            raise
      else: # for
        cls.__cachedUriContents[uri] = ""

    return cls.__cachedUriContents[uri]
