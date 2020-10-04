import platform
if int(platform.python_version_tuple()[0]) < 3:
  import httplib
else:
  from http import client as httplib

import re
import socket

from .architectures import Architecture

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
  def _host(cls):
    raise NotImplementedError

  ####################################################################
  @classmethod
  def _path_contents(cls, path):
    connection = httplib.HTTPConnection(cls._host(), timeout = 10)
    try:
      connection.request("GET", path)
    # Tolerate both an unresolvable host and a timeout.
    except (socket.gaierror, socket.timeout):
      content = ""
    else:
      response = connection.getresponse()
      content = response.read().decode("UTF-8")
    return content

  ####################################################################
  # Protected methods
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
