#!/usr/bin/env python
# encoding: utf-8
"""
busketcfg.py

Created by Kurtiss Hare on 2010-11-05.
Copyright (c) 2010 Medium Entertainment, Inc. All rights reserved.
"""

from confy.providers.base import *

import socket
import struct
import threading

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


class BusketRecorder(object):
    @classmethod
    def record(cls, busket, events):
        return cls(busket, events)._record()

    def __init__(self, busket, events):
        self.buffer = StringIO()
        self.length = 0
        self.busket = busket
        self.events = events
        self.max_payload_size = 1024
    
    def _flush(self, final = False):
        if self.buffer:
            if self.length:
                self.busket.sock.sendto(self.buffer.getvalue(), 0, (self.busket.host, self.busket.port))
            self.buffer.close()
        if not final:
            self.buffer = StringIO()
        else:
            self.buffer = None
        self.length = 0
    
    def _encode(self, event):
        ascii_key = event[0].encode('ascii')
        return struct.pack(">cdB", event[2], event[1], len(ascii_key)) + ascii_key
    
    def _record(self):
        try:
            for event in self.events:
                encoded = self._encode(event)
                len_encoded = len(encoded)
                
                if len_encoded > self.max_payload_size:
                    raise RuntimeError("The busket message, '{0}', is larger than the max payload size: {1}".format(event[0], self.max_payload_size))
            
                if (self.length + len_encoded) > self.max_payload_size:
                    self._flush()
                
                self.buffer.write(encoded)
                self.length += len_encoded
        finally:
            self._flush(True)


class BusketTime(threading.local):
    def __init__(self, host="127.0.0.1", port=5252):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def record(self, events):
        return BusketRecorder.record(self, events)

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