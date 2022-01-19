#!/usr/bin/env python

import functools
import os
import platform
import setuptools
import sys

import architectures

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

setup = functools.partial(
          setuptools.setup,
          name = prefixed("architectures"),
          version = "1.1.1",
          description = prefixed("architectures"),
          author = "Joe Shimkus",
          author_email = "jshimkus@redhat.com",
          packages = setuptools.find_packages(exclude = []),
          entry_points = {
            "console_scripts" :
              "{0} = architectures:arches".format(versioned("arches"))
          },
          install_requires = [prefixed("defaults"), prefixed ("factory")]
        )

# If the defaults file is in the package we have to prevent it from being
# generated as a zip file so the defaults can be found in the package
# installation.  If it's not we leave it up to setup's analysis.
if architectures.Architecture.defaultsFileInPackage():
  setup(package_data = { "architectures" :
                          [architectures.Architecture.defaultsFileName()] },
        zip_safe = False)
else:
  setup(data_files = [(architectures.Architecture.defaultsFileDirectory(),
                       [os.path.join(
                        "architectures",
                        architectures.Architecture.defaultsFileName())])])
