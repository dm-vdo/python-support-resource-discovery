#!/usr/bin/env python

import functools
import os
import platform
import setuptools
import sys
import yaml

package_name = "repos"
config_file_name = "config.yml"

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


with open(os.path.join(".", package_name, config_file_name)) as f:
  defaults = yaml.safe_load(f)["config"]["defaults"]
  defaultsFileName = defaults["name"]
  defaultsInstallDir = defaults["install-dir"]

  setup = functools.partial(
            setuptools.setup,
            name = python_prefixed(package_name),
            version = "3.0.0",
            description = python_prefixed(package_name),
            author = "Joe Shimkus",
            author_email = "jshimkus@redhat.com",
            packages = setuptools.find_packages(exclude = []),
            entry_points = {
              "console_scripts" :
                "{0} = repos:repos".format(versioned("repos"))
            },
            install_requires = ["{0} >= 2"
                                  .format(python_prefixed("architectures")),
                                "{0} >= 2"
                                  .format(python_prefixed("command")),
                                "{0} >= 2"
                                  .format(python_prefixed("defaults"))],
            zip_safe = False
          )

  # If there is a defaults file we need to install it in the correct location.
  package_data_files = [config_file_name]
  if defaultsFileName is not None:
    # If the install directory is None the defaults file is installed as part
    # of the package.  If not, that's where the defaults is to be installed.
    if defaultsInstallDir is None:
      package_data_files.append(defaultsFileName)
    else:
      setup = functools.partial(
                setup,
                data_files = [(defaultsInstallDir,
                              [os.path.join(package_name, defaultsFileName)])])

  # Execute setup.
  setup(package_data = { package_name : package_data_files })
