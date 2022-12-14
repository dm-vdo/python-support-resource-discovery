#
# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright Red Hat
#
from discovery import repos
from .Distribution import Distribution

########################################################################
class Fedora(Distribution):
  """Class for Fedora distributions.
  """
  # Available for use.
  _available = True

  ####################################################################
  # Public methods
  ####################################################################

  ####################################################################
  # Overridden methods
  ####################################################################
  @property
  def variant(self):
    return "Everything"

  ####################################################################
  @classmethod
  def _repoClass(cls):
    return repos.Fedora

  ####################################################################
  @property
  def _familyPrefix(self):
    return "Fedora"

  ####################################################################
  @property
  def _repoRootReleasedIndicator(self):
    return "releases"

  ####################################################################
  # Protected methods
  ####################################################################

  ####################################################################
  # Private methods
  ####################################################################
