import os

import defaults
import factory

########################################################################
class Architecture(factory.Factory, defaults.DefaultsFileInfo):
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
    defaultArchitecture = cls.defaults().content(["architecture"]).lower()
    return list(filter(lambda x: x.name().lower() == defaultArchitecture,
                       cls.choices()))[0]

  ####################################################################
  # Protected methods
  ####################################################################

  ####################################################################
  # Private methods
  ####################################################################

