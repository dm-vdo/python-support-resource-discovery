#! /usr/bin/env python

from __future__ import print_function

import yaml

from repos import ArchitectureFactory, FedoraRoots, RhelRoots

#############################################################################
#############################################################################
if __name__ == "__main__":
  for architecture in ArchitectureFactory.choices():
    print("Fedora {0} released roots:".format(architecture.name()))
    print(yaml.safe_dump(FedoraRoots.availableRoots(architecture.name()),
                         default_flow_style = False))
    print("Fedora {0} latest roots:".format(architecture.name()))
    print(yaml.safe_dump(FedoraRoots.availableLatestRoots(architecture.name()),
                         default_flow_style = False))
    print("Fedora {0} nightly roots:".format(architecture.name()))
    print(yaml.safe_dump(FedoraRoots.availableNightlyRoots(
                                                        architecture.name()),
                         default_flow_style = False))

  for architecture in ArchitectureFactory.choices():
    print("RHEL {0} released roots:".format(architecture.name()))
    print(yaml.safe_dump(RhelRoots.availableRoots(architecture.name()),
                         default_flow_style = False))
    print("RHEL {0} latest roots:".format(architecture.name()))
    print(yaml.safe_dump(RhelRoots.availableLatestRoots(architecture.name()),
                         default_flow_style = False))
    print("RHEL {0} nightly roots:".format(architecture.name()))
    print(yaml.safe_dump(RhelRoots.availableNightlyRoots(architecture.name()),
                         default_flow_style = False))
