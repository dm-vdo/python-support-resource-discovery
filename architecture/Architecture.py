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
  def isFedoraSecondary(self):
    return False

  ####################################################################
  # Overridden methods
  ####################################################################
  @classmethod
  def item(cls, name):
    try:
      item = super(Architecture, cls).item(name)
    except ValueError:
      raise ValueError("unknown architecture name specified: {0}".format(name))
    return item

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
