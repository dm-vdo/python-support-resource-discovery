from __future__ import print_function

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

import argparse
import errno
import functools
import json
import os
import socket
import subprocess
import sys
import time

import architectures
import factory

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
class Repository(factory.Factory):
  # We cache the results of determining the various roots to avoid
  # having to constantly perform network queries.
  #
  # We start with None so that separate dictionaries are created per
  # subclass.
  #
  # All found roots with no distinction as to architecture.
  # Keyed by category.
  __agnosticRoots = None

  # Available roots; keyed by architecture.
  __cachedLatest = None
  __cachedNightly = None
  __cachedReleased = None

  # Cached contents to avoid multiple requests for the same data.
  __cachedUriContents = {}

  ####################################################################
  # Public methods
  ####################################################################
  def availableRoots(self, architecture = None):
    """Returns a dictionary with keys being the <major>.<minor> and the values
    the URI for the release repo.

    This method prioritizes released over latest over nightly versions.
    """
    available = self._cachedNightly(architecture)
    available.update(self._cachedLatest(architecture))
    available.update(self._cachedReleased(architecture))
    return available

  ####################################################################
  def availableLatestRoots(self, architecture = None):
    """Returns a dictionary with keys being the <major>.<minor> and the values
    the URI for the release repo.

    This method prioritizes latest over released over nightly versions.
    """
    available = self._cachedNightly(architecture)
    available.update(self._cachedReleased(architecture))
    available.update(self._cachedLatest(architecture))
    return available

  ####################################################################
  def availableNightlyRoots(self, architecture = None):
    """Returns a dictionary with keys being the <major>.<minor> and the values
    the URI for the release repo.

    This method prioritizes nightly over latest over released versions.
    """
    available = self._cachedReleased(architecture)
    available.update(self._cachedLatest(architecture))
    available.update(self._cachedNightly(architecture))
    return available

  ####################################################################
  # Overridden instance-behavior methods
  ####################################################################
  def __init__(self, args = None):
    if args is None:
      args = self._defaultArguments()
    super(Repository, self).__init__(args)

  ####################################################################
  # Protected methods
  ####################################################################
  def _agnosticLatest(self, architecture):
    return self.__privateAgnosticRoots(self._categoryLatest(architecture),
                                       functools.partial(
                                        self._findAgnosticLatestRoots,
                                        architecture))

  ####################################################################
  def _agnosticNightly(self, architecture):
    return self.__privateAgnosticRoots(self._categoryNightly(architecture),
                                       functools.partial(
                                        self._findAgnosticNightlyRoots,
                                        architecture))

  ####################################################################
  def _agnosticReleased(self, architecture):
    return self.__privateAgnosticRoots(self._categoryReleased(architecture),
                                       functools.partial(
                                        self._findAgnosticReleasedRoots,
                                        architecture))

  ####################################################################
  def _availableLatest(self, architecture):
    return self.__privateAvailableRoots(self._categoryLatest(architecture),
                                        architecture,
                                        functools.partial(
                                          self. _filterNonExistentArchitecture,
                                          self._agnosticLatest(architecture),
                                          architecture))

  ####################################################################
  def _availableNightly(self, architecture):
    return self.__privateAvailableRoots(self._categoryNightly(architecture),
                                        architecture,
                                        functools.partial(
                                          self. _filterNonExistentArchitecture,
                                          self._agnosticNightly(architecture),
                                          architecture))

  ####################################################################
  def _availableReleased(self, architecture):
    return self.__privateAvailableRoots(self._categoryReleased(architecture),
                                        architecture,
                                        functools.partial(
                                          self. _filterNonExistentArchitecture,
                                          self._agnosticReleased(architecture),
                                          architecture))

  ####################################################################
  def _beakerRoot(self, family, name, variant):
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
  def _beakerRoots(self):
    raise NotImplementedError

  ####################################################################
  def _cachedLatest(self, architecture = None):
    if self.__cachedLatest is None:
      self.__cachedLatest = {}
    if architecture is None:
      architecture = architectures.Architecture.defaultChoice().name()
    if architecture not in self.__cachedLatest:
      self.__cachedLatest[architecture] = self._availableLatest(architecture)
    return self.__cachedLatest[architecture].copy()

  ####################################################################
  def _cachedNightly(self, architecture = None):
    if self.__cachedNightly is None:
      self.__cachedNightly = {}
    if architecture is None:
      architecture = architectures.Architecture.defaultChoice().name()
    if architecture not in self.__cachedNightly:
      self.__cachedNightly[architecture] = self._availableNightly(architecture)
    return self.__cachedNightly[architecture].copy()

  ####################################################################
  def _cachedReleased(self, architecture = None):
    if self.__cachedReleased is None:
      self.__cachedReleased = {}
    if architecture is None:
      architecture = architectures.Architecture.defaultChoice().name()
    if architecture not in self.__cachedReleased:
      self.__cachedReleased[architecture] = self._availableReleased(
                                                                architecture)
    return self.__cachedReleased[architecture].copy()

  ####################################################################
  def _categoryLatest(self, architecture):
    # What is returned must be suitable for use as a file name w/o special
    # handling (e.g., requiring quoting).
    return "latest"

  ####################################################################
  def _categoryNightly(self, architecture):
    # What is returned must be suitable for use as a file name w/o special
    # handling (e.g., requiring quoting).
    return "nightly"

  ####################################################################
  def _categoryReleased(self, architecture):
    # What is returned must be suitable for use as a file name w/o special
    # handling (e.g., requiring quoting).
    return "released"

  ####################################################################
  def _defaultArguments(self):
    return argparse.Namespace(forceScan = False)

  ####################################################################
  def _filterNonExistentArchitecture(self, repos, architecture):
    """Filters out the repos that don't have a subdir for the
    specified archtecture returning only those that do.
    """
    raise NotImplementedError

  ####################################################################
  def _findAgnosticLatestRoots(self, architecture):
    raise NotImplementedError

  ####################################################################
  def _findAgnosticNightlyRoots(self, architecture):
    raise NotImplementedError

  ####################################################################
  def _findAgnosticReleasedRoots(self, architecture):
    raise NotImplementedError

  ####################################################################
  def _host(self):
    raise NotImplementedError

  ####################################################################
  def _latestStartingPath(self, architecture = None):
    return self._releasedStartingPath(architecture)

  ####################################################################
  def _nightlyStartingPath(self, architecture = None):
    return self._releasedStartingPath(architecture)

  ####################################################################
  def _releasedStartingPath(self, architecture = None):
    raise NotImplementedError

  ####################################################################
  def _path_contents(self, path = None):
    if path is None:
      path = self._releasedStartingPath()
    return self._uri_contents("http://{0}{1}".format(self._host(), path))

  ####################################################################
  def _uri_contents(self, uri, retries = 3):
    if not uri.endswith("/"):
      uri = "{0}/".format(uri)
    if uri not in self.__cachedUriContents:
      parsed = urlparse.urlparse(uri)
      for iteration in range(retries):
        try:
          connection = httplib.HTTPConnection(parsed.netloc, timeout = 10)
          connection.request("GET", parsed.path)
          response = connection.getresponse()
          if response.status == 200:
            self.__cachedUriContents[uri] = response.read().decode("UTF-8")
            break
        except (socket.gaierror, socket.timeout):
          if iteration >= (retries - 1):
            raise
      else: # for
        self.__cachedUriContents[uri] = ""

    return self.__cachedUriContents[uri]

  ####################################################################
  # Private methods
  ####################################################################
  def __privateAgnosticFileName(self, category):
    return "agnostic.{0}.json".format(category)

  ####################################################################
  def __privateAgnosticRoots(self, category, finder):
    if self.__agnosticRoots is None:
      self.__agnosticRoots = {}
    if category not in self.__agnosticRoots:
      openFile = self.__privateOpenFile(
                  self.__privateAgnosticFileName(category))
      try:
        roots = self.__privateLoadFile(openFile,
                                      forceScan = self.args.forceScan)
        if roots is None:
          print("Updating saved {0} {1} repos".format(self.className(),
                                                      category),
                file = sys.stderr)
          self.__privateSaveFile(openFile, finder())
          roots = self.__privateLoadFile(openFile)
        self.__agnosticRoots[category] = roots
      finally:
        openFile.close()
    return self.__agnosticRoots[category]

  ####################################################################
  def __privateAvailableFileName(self, category, architecture):
    return "available.{0}.{1}.json".format(category, architecture)

  ####################################################################
  def __privateAvailableRoots(self, category, architecture, finder):
    openFile = self.__privateOpenFile(
                 self.__privateAvailableFileName(category, architecture))
    try:
      with self.__privateOpenFile(
            self.__privateAgnosticFileName(category)) as f:
        mtime = self.__privateFileMtime(f)
      roots = self.__privateLoadFile(openFile, mtime,
                                     forceScan = self.args.forceScan)
      if roots is None:
        print("Updating saved {0} {1} {2} repos ".format(self.className(),
                                                         category,
                                                         architecture),
              file = sys.stderr)
        self.__privateSaveFile(openFile, finder())
        roots = self.__privateLoadFile(openFile)
    finally:
      openFile.close()
    return roots

  ####################################################################
  def __privateDirPath(self):
    return os.path.sep.join([os.environ["HOME"], ".python-infrastructure",
                             "repos", self.className()])

  ####################################################################
  def __privateFileMtime(self, openFile):
    stats = os.fstat(openFile.fileno())
    return stats.st_mtime

  ####################################################################
  def __privateLoadFile(self, openFile, dependencyMtime = None,
                        forceScan = False):
    roots = None
    stats = os.fstat(openFile.fileno())
    # Truncate the file if we've been explicitly told to or its dependency is
    # more recent than the file itself or it's been more than a day since it
    # was updated.
    if (forceScan
        or ((dependencyMtime is not None)
            and (dependencyMtime > stats.st_mtime))
        or ((time.time() - stats.st_mtime) >= 86400)):
      openFile.truncate()
    elif stats.st_size > 0:
      # Seek to zero in case this is a load after a save.
      openFile.seek(0)
      roots = json.loads(openFile.read())
    return roots

  ####################################################################
  def __privateOpenFile(self, name):
    try:
      os.makedirs(self.__privateDirPath(), 0o700)
    except OSError as ex:
      if ex.errno != errno.EEXIST:
        raise
    try:
      fd = os.open(os.path.sep.join([self.__privateDirPath(), name]),
                   os.O_CREAT | os.O_RDWR | os.O_EXCL, 0o640)
    except OSError as ex:
      if ex.errno != errno.EEXIST:
        raise
      fd = os.open(os.path.sep.join([self.__privateDirPath(), name]),
                   os.O_RDWR | os.O_EXCL, 0o640)
    try:
      openFile = os.fdopen(fd, "r+")
    except:
      os.close(fd)
    return openFile

  ####################################################################
  def __privateSaveFile(self, openFile, roots):
    openFile.write(json.dumps(roots))
    openFile.flush()
    os.fsync(openFile.fileno())
