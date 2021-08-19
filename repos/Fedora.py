import json
import re

from .submodules.architectures import Architecture
from .Repository import (Repository, RepositoryBeakerNoDistroTree,
                         RepositoryBeakerNotFound)

######################################################################
######################################################################
class Fedora(Repository):
  # Exclude any release prior to 28.
  __FEDORA_MINIMUM_MAJOR = 28

  # All found roots with no distinction as to architecture.
  # Keyed by category path.
  __agnosticRoots = {}

  ####################################################################
  # Overridden methods
  ####################################################################
  @classmethod
  def _availableLatest(cls, architecture):
    return cls._availableCommon("{0}/development".format(
                                  cls._latestStartingPath(architecture)),
                                architecture)

  ####################################################################
  @classmethod
  def _availableNightly(cls, architecture):
    # For Fedora latest is nightly.
    # We could potentially make it 'rawhide', but that would require some
    # farther-reaching changes as the infrastructure is only set up to handle
    # numeric versions.
    return cls._availableLatest(architecture)

  ####################################################################
  @classmethod
  def _availableReleased(cls, architecture):
    return cls._availableCommon("{0}/releases".format(
                                  cls._releasedStartingPath(architecture)),
                                architecture)

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
  def _host(cls):
    return "dl.fedoraproject.org"

  ####################################################################
  @classmethod
  def _releasedStartingPath(cls, architecture):
    path = "/pub/fedora"
    if not Architecture.fedoraSecondary(architecture):
      path = "{0}/linux".format(path)
    else:
      path = "{0}-secondary".format(path)
    return path

  ####################################################################
  # Protected methods
  ####################################################################
  @classmethod
  def _agnosticRoots(cls, path):
    if path not in cls.__agnosticRoots:
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

      cls.__agnosticRoots[path] = roots

    return cls.__agnosticRoots[path]

  ####################################################################
  @classmethod
  def _availableCommon(cls, path, architecture):
    roots = cls._agnosticRoots(path)

    # Filter out all the paths that don't have an entry for the specified
    # architecture.
    roots = dict([ (key, value)
                      for (key, value) in roots.items()
                        if cls._uri_contents(
                          "{0}/Everything/{1}".format(value,
                                                      architecture)) != "" ])
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

