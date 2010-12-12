#!/usr/bin/env python
# encoding: utf-8
"""
mongodb.py

Created by Kurtiss Hare on 2010-11-04.
Copyright (c) 2010 Medium Entertainment, Inc. All rights reserved.
"""

from confy.providers.base import *
import threading

__all__ = ['PyMongoProvider']


class PyMongoHelper(object):
    connections = dict()

    def __init__(self, config):
        self.config = config

    def do(self, *args):
        results = []
        exc = None

        db = self.get_db()
        try:
            for fn in args:
                for i in xrange(0, 2):
                    try:
                        results.append(fn(db))
                    except (pymongo.errors.AutoReconnect), e:
                        exc = e
                    else:
                        exc = None
                        break

                if exc:
                    raise exc

        finally:
            db.connection.end_request()

        if len(args) == 1:
            return results[0]

        return results

    def get_db(self):
        """
        Get a new instance of the mongo db.
        """
        manipulators = self.config['son_manipulators']
        connection_key = hash("{0[host]}:{0[port]}:{0[timeout]}".format(self.config))
        
        connection = self.connections.get(connection_key)
        
        if not connection:
            with threading.Lock():
                connection = self.connections.get(connection_key)
                if not connection:
                    import pymongo.connection                    
                    connection = self.connections[connection_key] = pymongo.connection.Connection(
                        self.config['host'],
                        self.config['port'],
                        network_timeout = self.config['timeout']
                    )
        
        db = connection[self.config['database']]

        for manipulator in self.config['son_manipulators']:
            db.add_son_manipulator(manipulator)
        
        return db


class PyMongoProvider(Provider):
    __abstract__ = True
    Helper = PyMongoHelper

    def __provide__(self, method_name):
        return self.Helper(self.get_config(method_name))

    def __defaults__(self):
        return dict(
            host = 'localhost',
            port = 27017,
            timeout = None,
            database = 'testing',
            son_manipulators = []
        )