#! /usr/bin/env python

from __future__ import print_function

import factory
from architectures import Architecture

#############################################################################
#############################################################################
if __name__ == "__main__":
  shell = factory.FactoryShell(Architecture)
  shell.printChoices()
  print("Default choice: {0}".format(Architecture.defaultChoice().name()))
