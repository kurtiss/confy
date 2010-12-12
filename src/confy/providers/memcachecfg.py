#!/usr/bin/env python
# encoding: utf-8
"""
memcachecfg.py

Created by Kurtiss Hare on 2010-11-04.
Copyright (c) 2010 Medium Entertainment, Inc. All rights reserved.
"""

from confy.providers.base import *
import threading


class MemcacheProvider(InstanceProvider, Provider):
    __abstract__ = True
    connections = threading.local()

    def construct(self, config):
        try:
            connection = self.connections.connection
        except AttributeError:
            with threading.Lock():
                try:
                    connection = self.connections.connection
                except AttributeError:
                    import memcache
                    connection = self.connections.connection = memcache.Client(
                        ["{0[host]}:{0[port]}".format(config)], 
                        debug = config['debug']
                    )

        return connection

    def __defaults__(self):
        return dict(
            host = 'localhost',
            port = 11211,
            debug = 0
        )