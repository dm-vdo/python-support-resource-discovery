#!/usr/bin/env python

import platform
import setuptools

setuptools.setup(
  name = "python{0}-architectures".format(python_version),
  version = "1.0.0",
  description = "python{0}-architectures".format(python_version),
  author = "Joe Shimkus",
  author_email = "jshimkus@redhat.com",
  package_dir = {"" : "architectures"},
  packages = setuptools.find_packages(where = "architectures",
                                      exclude = []),
  package_data = { "architectures" : ["defaults.yml"] },
  # setuptools doesn't actually put the content of "requires" in the generated
  # rpm spec file though it claims that it should.
  # We'll just make certain to always install the requirements manually, for
  # which this serves as a reminder of what to install.
  requires = ["defaults", "factory"]
)
