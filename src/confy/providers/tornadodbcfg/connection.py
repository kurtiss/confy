#!/usr/bin/env python
# encoding: utf-8
"""
connection.py

Created by Kurtiss Hare on 2010-11-04.
Copyright (c) 2010 Medium Entertainment, Inc. All rights reserved.
"""

import collections
import datetime
import string
import threading
import tornado.database
import tornado.ioloop
import weakref


__all__ = ['Connection', 'ConnectionPool']


class _ParameterizingFormatter(string.Formatter):
    def __init__(self, *args, **kwargs):
        super(_ParameterizingFormatter, self).__init__(*args, **kwargs)
        self.parameters = []

    def format_field(self, value, format_spec):
        if hasattr(value, '__parameterize__'):
            parameters, formatted_value = value.__parameterize__(format_spec)
            self.parameters.extend(parameters)

            return formatted_value

        self.parameters.append(value)
        return "%s"


class ConnectionPool(object):
    """
    Tornado database connection pool.  acquire() to grab a connection and reliniquish(connection) to
    move it back to the pool.  Caching of connections is keyed off thread-local-storage.
    """
    _instances = weakref.WeakValueDictionary()
    _pruner = None
    _pruner_lock = threading.Lock()
    _tls_lock = threading.Lock()

    @classmethod
    def instance(cls, *args, **kwargs):
        normalized = cls.normalize_args(*args, **kwargs)
        default_instance = cls(*args, **kwargs)
        instance = cls._instances.setdefault(normalized, default_instance)
        return instance

    @classmethod
    def normalize_args(cls, host, database, user = None, password = None):
        return (host, database, user, password)

    @classmethod
    def prune(cls):
        now = datetime.datetime.utcnow()
        max_idle_time = datetime.timedelta(minutes = 1)
        nonempty_pools = 0

        for instance in cls._instances.values():
            if instance:
                for pool in instance.pools.values():
                    while pool:
                        connection, last_used_time = pool.popleft()

                        if (now - last_used_time) <= max_idle_time:
                            nonempty_pools += 1
                            pool.appendleft((connection, last_used_time))
                            break

        if nonempty_pools == 0:
            with cls._pruner_lock:
                if cls._pruner:
                    cls._pruner.stop()
                    cls._pruner = None

    def __init__(self, *args, **kwargs):
        self.tls = threading.local()
        self.pools = weakref.WeakValueDictionary()
        self.args = args
        self.kwargs = kwargs

    @property
    def thread_local_lock(self):
        if not hasattr(self.tls, 'lock'):
            with self._tls_lock:
                if not hasattr(self.tls, 'lock'):
                    self.tls.lock = threading.Lock()
        return self.tls.lock

    @property
    def thread_local_pool(self):
        if not hasattr(self.tls, 'pool'):
            with self.thread_local_lock:
                if not hasattr(self.tls, 'pool'):
                    self.tls.pool = collections.deque()
                    self.pools[id(self.tls.pool)] = self.tls.pool
        return self.tls.pool

    def acquire(self):
        try:
            (connection, last_used_time) = self.thread_local_pool.pop()
        except IndexError:
            connection = self.create()

        return connection

    def create(self):
        return tornado.database.Connection(*self.args, **self.kwargs)

    def reliniquish(self, connection):
        self.thread_local_pool.append((connection, datetime.datetime.utcnow()))

        with self._pruner_lock:
            if not self._pruner:
                self._pruner = tornado.ioloop.PeriodicCallback(self.prune, 5000)
                self._pruner.start()


class Connection(object):
    def __init__(self, pool):
        self.pool = pool
        self._connection = None

    @property
    def connection(self):
        if not self._connection:
            self._connection = self.pool.acquire()
        return self._connection

    def __del__(self):
        self.close()

    def close(self):
        if self._connection:
            self.pool.reliniquish(self._connection)

    def reconnect(self):
        self.connection.reconnect()

    def iter(self, query, *format_args, **format_kwargs):
        return self._call_with_reconnect(self.connection.iter, query, format_args, format_kwargs)

    def query(self, query, *format_args, **format_kwargs):
        return self._call_with_reconnect(self.connection.query, query, format_args, format_kwargs)

    def get(self, query, *format_args, **format_kwargs):
        return self._call_with_reconnect(self.connection.get, query, format_args, format_kwargs)

    def execute(self, query, *format_args, **format_kwargs):
        return self._call_with_reconnect(self.connection.execute, query, format_args, format_kwargs)

    def executemany(self, query, *format_args, **format_kwargs):
        return self._call_with_reconnect(self.connection.executemany, query, format_args, format_kwargs)

    def executecursor(self, query, *format_args, **format_kwargs):
        def _executecursor(q, *params):
            cursor = self.connection._db.cursor()
            cursor.execute(q, params)
            return cursor

        return self._call_with_reconnect(_executecursor, query, format_args, format_kwargs)

    def _call_with_reconnect(self, callable, query, format_args, format_kwargs):
        formatter = _ParameterizingFormatter()
        query = formatter.vformat(query, format_args, format_kwargs)

        try:
            result = callable(query, *formatter.parameters)
        except tornado.database.OperationalError:
            self.reconnect()
            result = callable(query, *formatter.parameters)

        return result