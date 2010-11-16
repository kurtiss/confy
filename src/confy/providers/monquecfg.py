#!/usr/bin/env python
# encoding: utf-8
"""
monquecfg.py

Created by Kurtiss Hare on 2010-11-05.
Copyright (c) 2010 Medium Entertainment, Inc. All rights reserved.
"""

import confy
from confy.providers.base import *

import monque
import pymongo.connection

class MonqueWrapper(monque.Monque):
    def __del__(self):
        self.mongodb.connection.end_request()

class MonqueProvider(InstanceProvider, Provider):
    __abstract__ = True

    def construct(self, config):
        database = confy.instance("pymongo.{0[mongodb]}".format(config))
        return MonqueWrapper(database.get_db())

    def __defaults__(self):
        return dict(
            mongodb = '__default__',
        )