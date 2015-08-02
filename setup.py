#!/usr/bin/env python
import os, sys
from setuptools import setup

extra = {}
if sys.version_info >= (3,):
    extra['use_2to3'] = True

setup(
    name="hooklib",
    version="0.2.1",
    author="Laurent Charignon",
    author_email="l.charignon@gmail.com",
    description="Hook helper library in python",
    keywords="hooks",
    py_modules=['hooklib', 'hooklib_git', 'hooklib_input', 'hooklib_hg'],
    **extra
)
