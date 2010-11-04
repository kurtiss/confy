#!/usr/bin/env python
# encoding: utf-8
"""
setup.py
"""

from setuptools import setup, find_packages
import os

os.chdir('src')
execfile(os.path.join('confy', 'version.py'))

setup(
    name = 'confy',
    version = VERSION,
    description = 'confy configures things.',
    author = 'Kurtiss Hare',
    author_email = 'kurtiss@gmail.com.com',
    url = 'http://www.github.com/kurtiss/confy',
    packages = find_packages(),
    scripts = [],
    classifiers = [
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    zip_safe = False
)
