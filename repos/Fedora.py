import json
import re

import architectures
from .Repository import (Repository, RepositoryBeakerNoDistroTree,
                         RepositoryBeakerNotFound)

######################################################################
######################################################################
class Fedora(Repository):
  # Exclude any release prior to 28.
  __FEDORA_MINIMUM_MAJOR = 28

  # Available via Factory.
  _available = True

  ####################################################################
  # Overridden methods
  ####################################################################
  def _beakerRoots(self):
    roots = {}
    major = self.__FEDORA_MINIMUM_MAJOR - 1
    while True:
      major += 1
      try:
        family = "Fedora{0}".format(major)
        name = "Fedora-{0}".format(major)
        variant = "Server" if major < 31 else "Everything"
        root = self._beakerRoot(family, name, variant)
        if root is not None:
          roots["{0}".format(major)] = root

      except RepositoryBeakerNoDistroTree:
        break

    return roots

  ####################################################################
  def _categoryLatest(self, architecture):
    return self._latestStartingPath(architecture).replace("/", "-")

  ####################################################################
  def _categoryNightly(self, architecture):
    # For Fedora latest is nightly.
    return self._categoryLatest(architecture)

  ####################################################################
  def _categoryReleased(self, architecture):
    return self._releasedStartingPath(architecture).replace("/", "-")

  ####################################################################
  def _filterNonExistentArchitecture(self, repos, architecture):
    repos = dict([ (key, value)
                      for (key, value) in repos.items()
                        if self._uri_contents(
                          "{0}/Everything/{1}".format(value,
                                                      architecture)) != "" ])
    return repos

  ####################################################################
  def _findAgnosticLatestRoots(self, architecture):
    return self._agnosticCommon(self._latestStartingPath(architecture))

  ####################################################################
  def _findAgnosticNightlyRoots(self, architecture):
    # For Fedora latest is nightly.
    # We could potentially make it 'rawhide', but that would require some
    # farther-reaching changes as the infrastructure is only set up to handle
    # numeric versions.
    return self._findAgnosticLatestRoots(architecture)

  ####################################################################
  def _findAgnosticReleasedRoots(self, architecture):
    return self._agnosticCommon(self._releasedStartingPath(architecture))

  ####################################################################
  def _host(self):
    return "dl.fedoraproject.org"

  ####################################################################
  def _latestStartingPath(self, architecture):
    return "{0}/development".format(self._startingPathPrefix(architecture))

  ####################################################################
  def _releasedStartingPath(self, architecture):
    return "{0}/releases".format(self._startingPathPrefix(architecture))

  ####################################################################
  # Protected methods
  ####################################################################
  def _agnosticCommon(self, path):
    # Try to get the released roots from beaker.  If beaker cannot be
    # reached get them from the web.
    roots = None
    if path.endswith("/releases"):
      try:
        roots = self._beakerRoots()
      except RepositoryBeakerNotFound:
        pass

    if roots is None:
      data = self._path_contents("{0}/".format(path))

      # Find all the released versions greater than or equal to the Fedora
      # minimum major (limited to no less than 28, Fedora 28 being the
      # version first incorporating VDO).
      regex = r"(?i)<a\s+href=\"(\d+)/\">\1/</a>"
      roots = dict([
        (x,  self._availableUri(path, x))
          for x in filter(lambda x: int(x) >= self.__FEDORA_MINIMUM_MAJOR,
                          re.findall(regex, data)) ])

    return roots

  ####################################################################
  def _availableUri(self, path, version):
    # If the version has a README file that indicates it has been moved to
    # the archive server.
    data = self._path_contents("{0}/{1}/".format(path, version))
    regex = r"(?i)<a\s+href=\"(README)\">\1</a>"
    host = self._host()
    match = re.search(regex, data)
    if match is not None:
      host = "archives.fedoraproject.org"
      path = path.replace("/pub/", "/pub/archive/", 1)
    return "http://{0}{1}/{2}".format(host, path, version)

  ####################################################################
  def _startingPathPrefix(self, architecture):
    path = "/pub/fedora"
    if not architectures.Architecture.fedoraSecondary(architecture):
      path = "{0}/linux".format(path)
    else:
      path = "{0}-secondary".format(path)
    return path
