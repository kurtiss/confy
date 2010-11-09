#!/usr/bin/env python
# encoding: utf-8
"""
mysqldbcfg.py

Created by Stephen Altamirano on 2010-11-09.
Copyright (c) 2010 Medium Entertainment Inc.. All rights reserved.
"""

import MySQLdb
from confy.providers.base import *

class MysqlProvider(InstanceProvider, Provider):
    __abstract__ = True

    def construct(self, config):
        return MySQLdb.connect(**config)

    def __defaults__(self):
        return dict(
            host    = 'localhost',
            db      = 'database',
            user    = '',
            passwd  = ''
        )