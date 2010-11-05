#!/usr/bin/env python
# encoding: utf-8
"""
busketcfg.py

Created by Kurtiss Hare on 2010-11-05.
Copyright (c) 2010 Medium Entertainment, Inc. All rights reserved.
"""

from confy.base import *

import socket
import struct
import threading


class BusketTime(threading.local):
    def __init__(self, host="127.0.0.1", port=5252):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def record(self, events):
        data = "".join(struct.pack(">cdB", x[2], x[1], len(x[0].encode('ascii'))) + x[0].encode('ascii') for x in events)
        self.sock.sendto(data, 0, (self.host, self.port))

    def gauge(self, event, value):
        self.record([(event, value, "g")])

    def absolute(self, event, value):
        self.record([(event, value, "a")])

    def counter(self, event, value):
        self.record([(event, value, "c")])


class BusketProvider(InstanceProvider, Provider):
    __abstract__ = True

    def construct(self, config):
        return BusketTime(config['host'], config['port'])

    def __defaults__(self):
        return dict(
            host = '127.0.0.1',
            port = 5252,
        )