#!/usr/bin/env python
# encoding: utf-8
"""
__init__.py
"""

from confy.version import VERSION
from confy.providers import *

__version__ = VERSION

instance = Provider.instance