#!/usr/bin/env python
# encoding: utf-8
"""
sforcecfg.py

Created by Kurtiss Hare on 2010-12-11.
Copyright (c) 2010 Medium Entertainment, Inc. All rights reserved.
"""

from confy.providers.base import *


class SforceProvider(InstanceProvider, Provider):
    __abstract__ = True

    @classmethod
    def get_client_cls(cls):
        if not hasattr(cls, '_client_cls'):
            from sforce.enterprise import SforceEnterpriseClient

            class _ClientWrapper(SforceEnterpriseClient):
                def __init__(self, name_prefix, login_params, *args, **kwargs):
                    self._name_prefix = name_prefix
                    self._login_params = login_params
                    super(_ClientWrapper, self).__init__(*args, **kwargs)

                def login(self):
                    super(_ClientWrapper, self).login(*self._login_params[0], **self._login_params[1])

                def mkname(self, name):
                    return "{0}{1}".format(self._name_prefix, name)

            cls._client_cls = _ClientWrapper
        return cls._client_cls

    def construct(self, config):
        return type(self).get_client_cls()(
            config['name_prefix'],
            ((config['username'], config['password'], config['token']), dict()),
            config['wsdl']
        )

    def __defaults__(self):
        return dict(
            wsdl        = 'enterprise.wsdl.xml',
            name_prefix = '',
            username    = '',
            password    = '',
            token       = ''
        )