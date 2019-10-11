import platform
if int(platform.python_version_tuple()[0]) < 3:
  import httplib
else:
  from http import client as httplib

import re

######################################################################
######################################################################
class RepoRoots(object):
  ####################################################################
  # Public methods
  ####################################################################
  @classmethod
  def availableRoots(cls, architecture = None):
    """Returns a dictionary with keys being the <major>.<minor> and the values
    the URI for the release repo.
    
    This method prioritizes released over latest versions.
    """
    available = cls._availableLatest(architecture)
    available.update(cls._availableReleased(architecture))
    return available
    
  ####################################################################
  @classmethod
  def availableLatestRoots(cls, architecture = None):
    """Returns a dictionary with keys being the <major>.<minor> and the values
    the URI for the release repo.
    
    This method prioritizes latest over released versions.
    """
    available = cls._availableReleased(architecture)
    available.update(cls._availableLatest(architecture))
    return available

  ####################################################################
  # Protected methods
  ####################################################################
  @classmethod
  def _availableLatest(cls, architecture):
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
    connection = httplib.HTTPConnection(cls._host())
    connection.request("GET", path)
    response = connection.getresponse()
    return response.read().decode("UTF-8")


