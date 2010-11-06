#!/usr/bin/env python
# encoding: utf-8
"""
__init__.py

Created by Kurtiss Hare on 2010-11-04.
Copyright (c) 2010 Medium Entertainment, Inc. All rights reserved.
"""

from confy.providers.base import *
from confy.providers.tornadodbcfg.connection import *

import threading


class DatabaseProvider(InstanceProvider, Provider):
    __abstract__ = True
    pools = dict()

    def construct(self, config):
        pool_key = hash("{0[user]}:{0[password]}@{0[host]}/{0[database]}".format(config))

        try:
            pool = self.pools[pool_key]
        except KeyError:
            with threading.Lock():
                try:
                    pool = self.pools[pool_key]
                except KeyError:
                    pool = self.pools[pool_key] = ConnectionPool.instance(
                        config['host'],
                        config['database'],
                        config['user'],
                        config['password']
                    )

        return Connection(pool)

    def __defaults__(self):
        return dict(
            host            = 'localhost:3306', # '/path/to/mysql.sock'
            database        = 'database',
            user            = None,
            password        = None
        )