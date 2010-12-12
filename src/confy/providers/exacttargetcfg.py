#!/usr/bin/env python
# encoding: utf-8
"""
exacttargetcfg.py

Created by Stephen Altamirano on 2010-12-07.
"""

from urllib import urlencode
from urllib2 import urlopen

from confy.providers.base import *

class PrettyMarkup(object):
    def __init__(self):
        self._data = []

    def _make_node(self, name, attrs = None):
        if attrs is None:
            attrs = {}

        return Node(name, attrs, self._data)

    def _(self, value):
        self._data.append(value)

    def __getattr__(self, name):
        return lambda attrs=None: self._make_node(name, attrs)

    def __str__(self):
        return ''.join(self._data)


class Node(object):
    def __init__(self, name, attrs, document):
        self.name = name
        self.attrs = attrs
        self.document = document

    def __call__(self, *args, **kwargs):
        self.attrs.update(kwargs)
        return self

    def __enter__(self):
        self.document.append('<{0}{1}>'.format(
            self.name,
            ''.join(' {0}="{1}"'.format(*pair) for pair in self.attrs.iteritems())
        ))

    def __exit__(self, *args):
        self.document.append('</{0}>'.format(self.name))

class ExactTargetXML(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.endpoint = 'https://api.dc1.exacttarget.com/integrate.aspx'

    def send(self, method):
        d = PrettyMarkup()
        with d.exacttarget():
            with d.authorization():
                with d.username():
                    d._(self.username)
                with d.password():
                    d._(self.password)
            with d.system():
                d._(str(method))

        return urlopen(
            self.endpoint,
            urlencode({
                'qf': 'xml',
                'xml': d
            }),
            60
        )

    def trigger_email(self, email_key, recipient_sets):
        d = PrettyMarkup()
        with d.system_name():
            d._('triggeredsend')
        with d.action():
            d._('add')

        attrs = {
            'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xmlns:xsd': 'http://www.w3.org/2001/XMLSchema',
            'xmlns': 'http://exacttarget.com/wsdl/partnerAPI',
        }

        with d.TriggeredSend(attrs):
            with d.TriggeredSendDefinition():
                with d.CustomerKey():
                    d._(email_key)

            for email, context in recipient_sets:
                with d.Subscribers():
                    with d.Owner():
                        with d.FromAddress():
                            d._('support@playhaven.com')
                        with d.FromName():
                            d._('PlayHaven Support')
                    with d.SubscriberKey():
                        d._(email)
                    with d.EmailAddress():
                        d._(email)

                    for key, value in context.iteritems():
                        with d.Attributes():
                            with d.Name():
                                d._(key)
                            with d.Value():
                                d._(value)

        return self.send(d)


class ExactTargetProvider(InstanceProvider, Provider):
    __abstract__ = True

    def construct(self, config):
        return ExactTargetXML(config['username'], config['password'])

    def __defaults__(self):
        return dict(
            username = 'WRONGUSERNAME',
            password = 'WRONGPASSWORD',
        )