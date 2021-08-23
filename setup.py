#!/usr/bin/env python

import setuptools

setuptools.setup(
  name = "repos",
  version = "1.0.0",
  description = "repos",
  author = "Joe Shimkus",
  author_email = "jshimkus@redhat.com",
  packages = setuptools.find_packages(exclude = []),
  install_requires = ["architectures", "command"],
  dependency_links = [
                      "http://vdo-image-store.permabit.lab.eng.bos.redhat.com/repository/jshimkus/"
                     ]
)
