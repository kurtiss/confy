#!/usr/bin/env python
# encoding: utf-8
"""
botocfg.py

Created by Kurtiss Hare on 2010-12-17.
Copyright (c) 2010 Medium Entertainment, Inc. All rights reserved.
"""

import itertools

from confy.providers.base import *


class ConnectingBotoWrapper(object):
    """
    A wrapper that proxies the boto package, design to make the connect_* family of
    calls into parameterless calls.  Everything else should be passed through directly.
    """

    __slots__ = ['boto', 'connect_params']
    def __init__(self, connect_params):
        import boto
        self.boto = boto
        self.connect_params = connect_params

    def __getattr__(self, name):
        value = getattr(self.boto, name)
        if name.startswith('connect_') and hasattr(value, '__call__'):
            def wrapper(*args, **kwargs):
                connect_args = [arg for arg in itertools.chain(
                    (a for a in self.connect_params[0]),
                    (a for a in args)
                )]

                connect_kwargs = dict((k,v) for (k,v) in itertools.chain(
                    ((k,v) for (k,v) in self.connect_params[1].items()),
                    ((k,v) for (k,v) in kwargs.items())
                ))

                return value(*connect_args, **connect_kwargs)
            return wrapper
        return value


class BotoProvider(InstanceProvider, Provider):
    def construct(self, config):
        return ConnectingBotoWrapper((
            tuple(),
            dict(
                aws_access_key_id = config['aws_access_key_id'],
                aws_secret_access_key = config['aws_secret_access_key'],
            )
        ))

    def __defaults__(self):
        return dict(
            aws_access_key_id = None,
            aws_secret_access_key = None
        )