import os

from .submodules.defaults import Defaults
from .submodules.factory import Factory

########################################################################
class Architecture(Factory):
  __defaults = None

  ####################################################################
  # Public methods
  ####################################################################
  @classmethod
  def fedoraSecondary(cls, architecture):
    return cls.makeItem(architecture).isFedoraSecondary

  ####################################################################
  @property
  def is32Bit(self):
    return NotImplementedError

  ####################################################################
  @property
  def is64Bit(self):
    return NotImplementedError

  ####################################################################
  @property
  def isFedoraSecondary(self):
    return False

  ####################################################################
  @property
  def lacksHardwareData(self):
    return False

  ####################################################################
  @property
  def requiresExternalStorage(self):
    return False

  ####################################################################
  # Overridden methods
  ####################################################################
  @classmethod
  def _defaultChoice(cls):
    defaultArchitecture = cls._defaults().content(["architecture"]).lower()
    return list(filter(lambda x: x.name().lower() == defaultArchitecture,
                       cls.choices()))[0]

  ####################################################################
  # Protected methods
  ####################################################################
  @classmethod
  def _defaults(cls):
    if cls.__defaults is None:
      cls.__defaults = Defaults(os.path.join(
                                  os.path.dirname(
                                    os.path.realpath(__file__)),
                                  "..", "defaults.yml"))
    return cls.__defaults

  ####################################################################
  # Private methods
  ####################################################################
