#!/usr/bin/env python
# encoding: utf-8
"""
monquecfg.py

Created by Kurtiss Hare on 2010-11-05.
Copyright (c) 2010 Medium Entertainment, Inc. All rights reserved.
"""

import confy
from confy.providers.base import *


class MonqueProvider(InstanceProvider, Provider):
    __abstract__ = True

    @classmethod
    def get_wrapper_cls(cls):
        if not hasattr(cls, '_wrapper_cls'):
            import monque

            class MonqueWrapper(monque.Monque):
                def __del__(self):
                    self.mongodb.connection.end_request()

            cls._wrapper_cls = MonqueWrapper
        return cls._wrapper_cls

    def construct(self, config):
        database = confy.instance("pymongo.{0[mongodb]}".format(config))
        return self.get_wrapper_cls()(database.get_db())

    def __defaults__(self):
        return dict(
            mongodb = '__default__',
        )