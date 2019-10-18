#! /usr/bin/env python

from __future__ import print_function

import yaml

from repos import FedoraRoots, RhelRoots

#############################################################################
#############################################################################
if __name__ == "__main__":
  print("Fedora x86_64 released roots:")
  print(yaml.safe_dump(FedoraRoots.availableRoots("x86_64"),
                       default_flow_style = False))
  print("Fedora x86_64 latest roots:")
  print(yaml.safe_dump(FedoraRoots.availableLatestRoots("x86_64"),
                       default_flow_style = False))
  print("RHEL released roots:")
  print(yaml.safe_dump(RhelRoots.availableRoots(),
                       default_flow_style = False))
  print("RHEL latest roots:")
  print(yaml.safe_dump(RhelRoots.availableLatestRoots(),
                       default_flow_style = False))
