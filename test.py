#! /usr/bin/env python

from __future__ import print_function

import yaml

import repos

#############################################################################
#############################################################################
if __name__ == "__main__":
  for architecture in repos.Architecture.choices():
    print("CentOS {0} released roots:".format(architecture.name()))
    print(yaml.safe_dump(repos.CentOS.availableRoots(architecture.name()),
                         default_flow_style = False))
    print("CentOS {0} latest roots:".format(architecture.name()))
    print(yaml.safe_dump(repos.CentOS.availableLatestRoots(
                                                          architecture.name()),
                         default_flow_style = False))
    print("CentOS {0} nightly roots:".format(architecture.name()))
    print(yaml.safe_dump(repos.CentOS.availableNightlyRoots(
                                                        architecture.name()),
                         default_flow_style = False))

  for architecture in repos.Architecture.choices():
    print("Fedora {0} released roots:".format(architecture.name()))
    print(yaml.safe_dump(repos.Fedora.availableRoots(architecture.name()),
                         default_flow_style = False))
    print("Fedora {0} latest roots:".format(architecture.name()))
    print(yaml.safe_dump(repos.Fedora.availableLatestRoots(
                                                        architecture.name()),
                         default_flow_style = False))
    print("Fedora {0} nightly roots:".format(architecture.name()))
    print(yaml.safe_dump(repos.Fedora.availableNightlyRoots(
                                                        architecture.name()),
                         default_flow_style = False))

  for architecture in repos.Architecture.choices():
    print("RHEL {0} released roots:".format(architecture.name()))
    print(yaml.safe_dump(repos.RHEL.availableRoots(architecture.name()),
                         default_flow_style = False))
    print("RHEL {0} latest roots:".format(architecture.name()))
    print(yaml.safe_dump(repos.RHEL.availableLatestRoots(architecture.name()),
                         default_flow_style = False))
    print("RHEL {0} nightly roots:".format(architecture.name()))
    print(yaml.safe_dump(repos.RHEL.availableNightlyRoots(architecture.name()),
                         default_flow_style = False))
