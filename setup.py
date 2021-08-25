#!/usr/bin/env python

import platform
import setuptools

python_version = platform.python_version_tuple()[0]

setuptools.setup(
  name = "python{0}-repos".format(python_version),
  version = "1.0.0",
  description = "python{0}-repos".format(python_version),
  author = "Joe Shimkus",
  author_email = "jshimkus@redhat.com",
  package_dir = {"" : "repos"},
  packages = setuptools.find_packages(where = "repos",
                                      exclude = []),
  # setuptools doesn't actually put the content of "requires" in the generated
  # rpm spec file though it claims that it should.
  # We'll just make certain to always install the requirements manually, for
  # which this serves as a reminder of what to install.
  requires = ["architectures", "command"]
)
