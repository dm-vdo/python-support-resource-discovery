from __future__ import print_function

import argparse
import yaml

from .submodules import architectures
from .submodules import command
from .CentOS import CentOS
from .Fedora import Fedora
from .RHEL import RHEL

########################################################################
class ReposCommand(command.Command):
  """Command class for command line utility.
  """

  ####################################################################
  # Public factory-behavior methods
  ####################################################################

  ####################################################################
  # Public instance-behavior methods
  ####################################################################

  ####################################################################
  # Overridden factory-behavior methods
  ####################################################################
  @classmethod
  def parserParents(cls):
    parser = argparse.ArgumentParser(add_help = False)

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--latest",
                       help = "report only the available latest repos",
                       action = "store_true")
    group.add_argument("--nightly",
                       help = "report only the available nightly repos",
                       action = "store_true")
    group.add_argument("--released",
                       help = "report only the available latest repos",
                       action = "store_true")

    parents = super(ReposCommand, cls).parserParents()
    parents.append(parser)
    return parents

  ####################################################################
  # Overridden instance-behavior methods
  ####################################################################
  def run(self):
    all = not (self.args.latest or self.args.nightly or self.args.released)

    for architecture in architectures.Architecture.choices():
      if all or self.args.released:
        print("CentOS {0} released roots:".format(architecture.name()))
        print(yaml.safe_dump(CentOS.availableRoots(architecture.name()),
                             default_flow_style = False))
      if all or self.args.latest:
        print("CentOS {0} latest roots:".format(architecture.name()))
        print(yaml.safe_dump(CentOS.availableLatestRoots(architecture.name()),
                             default_flow_style = False))
      if all or self.args.nightly:
        print("CentOS {0} nightly roots:".format(architecture.name()))
        print(yaml.safe_dump(CentOS.availableNightlyRoots(architecture.name()),
                             default_flow_style = False))

    for architecture in architectures.Architecture.choices():
      if all or self.args.released:
        print("Fedora {0} released roots:".format(architecture.name()))
        print(yaml.safe_dump(Fedora.availableRoots(architecture.name()),
                             default_flow_style = False))
      if all or self.args.latest:
        print("Fedora {0} latest roots:".format(architecture.name()))
        print(yaml.safe_dump(Fedora.availableLatestRoots(architecture.name()),
                             default_flow_style = False))
      if all or self.args.nightly:
        print("Fedora {0} nightly roots:".format(architecture.name()))
        print(yaml.safe_dump(Fedora.availableNightlyRoots(architecture.name()),
                             default_flow_style = False))

    for architecture in architectures.Architecture.choices():
      if all or self.args.released:
        print("RHEL {0} released roots:".format(architecture.name()))
        print(yaml.safe_dump(RHEL.availableRoots(architecture.name()),
                             default_flow_style = False))
      if all or self.args.latest:
        print("RHEL {0} latest roots:".format(architecture.name()))
        print(yaml.safe_dump(RHEL.availableLatestRoots(architecture.name()),
                             default_flow_style = False))
      if all or self.args.nightly:
        print("RHEL {0} nightly roots:".format(architecture.name()))
        print(yaml.safe_dump(RHEL.availableNightlyRoots(architecture.name()),
                             default_flow_style = False))

  ####################################################################
  # Protected factory-behavior methods
  ####################################################################

  ####################################################################
  # Protected instance-behavior methods
  ####################################################################

  ####################################################################
  # Private factory-behavior methods
  ####################################################################

  ####################################################################
  # Private instance-behavior methods
  ####################################################################
