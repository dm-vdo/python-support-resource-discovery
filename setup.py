#!/usr/bin/env python

import platform
import setuptools
import sys

def prefixed(src):
  python_version = platform.python_version_tuple()[0]
  if ("bdist_wheel" in sys.argv) and ("--universal" in sys.argv):
    python_version = ""
  return "python{0}-{1}".format(python_version, src)

setuptools.setup(
  name = prefixed("architectures"),
  version = "1.0.0",
  description = prefixed("architectures"),
  author = "Joe Shimkus",
  author_email = "jshimkus@redhat.com",
  packages = setuptools.find_packages(exclude = []),
  package_data = { "architectures" : ["defaults.yml"] },
  install_requires = [prefixed("defaults"), prefixed ("factory")]
)
