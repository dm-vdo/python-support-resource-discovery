#!/usr/bin/env python

import setuptools

setuptools.setup(
  name = "architectures",
  version = "1.0.0",
  description = "architectures",
  author = "Joe Shimkus",
  author_email = "jshimkus@redhat.com",
  packages = setuptools.find_packages(exclude = []),
  package_data = { "architectures" : ["defaults.yml"] },
  install_requires = ["defaults", "factory"],
  dependency_links = [
                      "http://vdo-image-store.permabit.lab.eng.bos.redhat.com/repository/jshimkus/"
                     ]
)
