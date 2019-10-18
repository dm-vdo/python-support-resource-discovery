#! /usr/bin/env python

from __future__ import print_function

from architecture import ArchitectureFactory
from architecture.factory import FactoryShell

#############################################################################
#############################################################################
if __name__ == "__main__":
  shell = FactoryShell(ArchitectureFactory)
  shell.printChoices()
