from ..Architecture import Architecture

########################################################################
class S390(Architecture):
  """Class for S390 architectures.
  """

  ####################################################################
  # Public methods
  ####################################################################

  ####################################################################
  # Overridden methods
  ####################################################################
  @property
  def isFedoraSecondary(self):
    return True

  ####################################################################
  @property
  def requiresExternalStorage(self):
    return True

  ####################################################################
  # Protected methods
  ####################################################################

  ####################################################################
  # Private methods
  ####################################################################

########################################################################
class S390X(S390):
  """Class for S390X architectures.
  """
  _available = True
