#!/usr/bin/env python

import platform
import setuptools
import sys

def prefixed(src):
  if ("bdist_wheel" not in sys.argv) or ("--universal" not in sys.argv):
    src = python_prefixed(src)
  return src

def python_prefixed(src):
  return "{0}-{1}".format(versioned("python"), src)

def versioned(src):
  python_version = platform.python_version_tuple()[0]
  if ("bdist_wheel" in sys.argv) and ("--universal" in sys.argv):
    python_version = ""
  return "{0}{1}".format(src, python_version)

setuptools.setup(
  name = prefixed("repos"),
  version = "1.1.0",
  description = prefixed("repos"),
  author = "Joe Shimkus",
  author_email = "jshimkus@redhat.com",
  packages = setuptools.find_packages(exclude = []),
  entry_points = {
    "console_scripts" :
      "{0} = repos:repos".format(versioned("repos"))
  },
  install_requires = [prefixed("architectures"), prefixed("command")]
)
