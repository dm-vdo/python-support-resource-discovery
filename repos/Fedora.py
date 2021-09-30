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

  ####################################################################
  # Overridden methods
  ####################################################################
  @classmethod
  def _beakerRoots(cls):
    roots = {}
    major = cls.__FEDORA_MINIMUM_MAJOR - 1
    while True:
      major += 1
      try:
        family = "Fedora{0}".format(major)
        name = "Fedora-{0}".format(major)
        variant = "Server" if major < 31 else "Everything"
        root = cls._beakerRoot(family, name, variant)
        if root is not None:
          roots["{0}".format(major)] = root

      except RepositoryBeakerNoDistroTree:
        break

    return roots

  ####################################################################
  @classmethod
  def _categoryLatest(cls, architecture):
    return cls._latestStartingPath(architecture).replace("/", "-")

  ####################################################################
  @classmethod
  def _categoryNightly(cls, architecture):
    # For Fedora latest is nightly.
    return cls._categoryLatest(architecture)

  ####################################################################
  @classmethod
  def _categoryReleased(cls, architecture):
    return cls._releasedStartingPath(architecture).replace("/", "-")

  ####################################################################
  @classmethod
  def _filterNonExistentArchitecture(cls, repos, architecture):
    repos = dict([ (key, value)
                      for (key, value) in repos.items()
                        if cls._uri_contents(
                          "{0}/Everything/{1}".format(value,
                                                      architecture)) != "" ])
    return repos

  ####################################################################
  @classmethod
  def _findAgnosticLatestRoots(cls, architecture):
    return cls._agnosticCommon(cls._latestStartingPath(architecture))

  ####################################################################
  @classmethod
  def _findAgnosticNightlyRoots(cls, architecture):
    # For Fedora latest is nightly.
    # We could potentially make it 'rawhide', but that would require some
    # farther-reaching changes as the infrastructure is only set up to handle
    # numeric versions.
    return cls._findAgnosticLatestRoots(architecture)

  ####################################################################
  @classmethod
  def _findAgnosticReleasedRoots(cls, architecture):
    return cls._agnosticCommon(cls._releasedStartingPath(architecture))

  ####################################################################
  @classmethod
  def _host(cls):
    return "dl.fedoraproject.org"

  ####################################################################
  @classmethod
  def _latestStartingPath(cls, architecture):
    return "{0}/development".format(cls._startingPathPrefix(architecture))

  ####################################################################
  @classmethod
  def _releasedStartingPath(cls, architecture):
    return "{0}/releases".format(cls._startingPathPrefix(architecture))

  ####################################################################
  # Protected methods
  ####################################################################
  @classmethod
  def _agnosticCommon(cls, path):
    # Try to get the released roots from beaker.  If beaker cannot be
    # reached get them from the web.
    roots = None
    if path.endswith("/releases"):
      try:
        roots = cls._beakerRoots()
      except RepositoryBeakerNotFound:
        pass

    if roots is None:
      data = cls._path_contents("{0}/".format(path))

      # Find all the released versions greater than or equal to the Fedora
      # minimum major (limited to no less than 28, Fedora 28 being the
      # version first incorporating VDO).
      regex = r"(?i)<a\s+href=\"(\d+)/\">\1/</a>"
      roots = dict([
        (x,  cls._availableUri(path, x))
          for x in filter(lambda x: int(x) >= cls.__FEDORA_MINIMUM_MAJOR,
                          re.findall(regex, data)) ])

    return roots

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
  def _startingPathPrefix(cls, architecture):
    path = "/pub/fedora"
    if not architectures.Architecture.fedoraSecondary(architecture):
      path = "{0}/linux".format(path)
    else:
      path = "{0}-secondary".format(path)
    return path
