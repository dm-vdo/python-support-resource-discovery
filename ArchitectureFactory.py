from factory import Factory
from .Architecture import Architecture
import architectures

########################################################################
class ArchitectureFactory(Factory):
  ####################################################################
  # Public methods
  ####################################################################

  ####################################################################
  # Overridden methods
  ####################################################################
  @classmethod
  def _defaultChoice(cls):
    return architectures.X86.X86_64

  ####################################################################
  @classmethod
  def _rootClass(cls):
    return Architecture

  ####################################################################
  # Protected methods
  ####################################################################

  ####################################################################
  # Private methods
  ####################################################################
