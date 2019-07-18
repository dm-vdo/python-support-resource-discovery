from ..Architecture import Architecture

########################################################################
class PPC(Architecture):
  """Class for PPC architectures.
  """

  ####################################################################
  # Public methods
  ####################################################################

  ####################################################################
  # Overridden methods
  ####################################################################

  ####################################################################
  # Protected methods
  ####################################################################

  ####################################################################
  # Private methods
  ####################################################################

########################################################################
class PPC64(PPC):
  """Class for PPC 64 architectures.
  """
########################################################################
class PPC64LE(PPC64):
  """Class for PPC 64 little-endian architectures.
  """
  _available = True