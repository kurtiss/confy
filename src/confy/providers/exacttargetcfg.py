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
    def __init__(self, username, password, from_address, from_name):
        self.username = username
        self.password = password
        self.from_address = from_address
        self.from_name = from_name
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
                d._(unicode(method))

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
                            d._(self.from_address)
                        with d.FromName():
                            d._(self.from_name)
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

    def subscribe_list(self, email_address, list_id, status='active'):
        """
        Adds an email to a list. Status should either be active or unsub.
        """
        d = PrettyMarkup()
        with d.system_name():
            d._('subscriber')
        with d.action():
            d._('add')
        with d.search_type():
            d._('listid')
        with d.search_value():
            d._(str(list_id))
        with d.values():
            with d.Email__Address():
                d._(email_address)
            with d.status():
                d._(status)

        return self.send(d)


class ExactTargetProvider(InstanceProvider, Provider):
    __abstract__ = True

    def construct(self, config):
        return ExactTargetXML(
            config['username'],
            config['password'],
            config['from_address'],
            config['from_name']
        )

    def __defaults__(self):
        return dict(
            username = 'WRONGUSERNAME',
            password = 'WRONGPASSWORD',
            from_address = 'exacttarget@confy',
            from_name = 'ConfyExactTarget'
        )