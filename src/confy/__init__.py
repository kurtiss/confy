#!/usr/bin/env python
# encoding: utf-8
"""
__init__.py
"""

from confy.version import VERSION
from confy.providers import *

__version__ = VERSION


def instance(name, *args, **kwargs):
    if '.' not in name:
        name += ".__default__"
    cls_name, method_name = name.split('.')
    provider = type(Provider).find(cls_name)
    if provider._instance == None:
        provider._instance = provider()
    return provider._instance.__provide__(method_name)