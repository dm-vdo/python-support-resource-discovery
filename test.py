#! /usr/bin/env python

from __future__ import print_function

from architecture import Architecture, FactoryShell

#############################################################################
#############################################################################
if __name__ == "__main__":
  shell = FactoryShell(Architecture)
  shell.printChoices()
