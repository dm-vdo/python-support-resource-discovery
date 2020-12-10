from .submodules.factory import Factory

########################################################################
class Architecture(Factory):
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
    return list(filter(lambda x: x.name() == "x86_64", cls.choices()))[0]

  ####################################################################
  # Protected methods
  ####################################################################

  ####################################################################
  # Private methods
  ####################################################################
