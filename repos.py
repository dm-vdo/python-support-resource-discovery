#! /usr/bin/env python

from __future__ import print_function

import command
import repos

#############################################################################
#############################################################################
if __name__ == "__main__":
  command.CommandShell(repos.ReposCommand).run()
