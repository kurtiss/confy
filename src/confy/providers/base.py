#!/usr/bin/env python
# encoding: utf-8
"""
base.py

Created by Kurtiss Hare on 2010-11-04.
Copyright (c) 2010 Medium Entertainment, Inc. All rights reserved.
"""

__all__ = ['Provider', 'SingletonProvider', 'InstanceProvider', 'ProviderMetaclass']


class ProviderMetaclass(type):
    _subclasses = {}

    def __new__(cls, name, bases, attrs):
        new_cls = type.__new__(cls, name, bases, attrs)

        if not attrs.pop('__abstract__', False):
            namespace = attrs.get('__namespace__', False)

            if not namespace:
                import re
                match = re.match(r'^(.*)ConfigurationProvider$', name)

                if match:
                    namespace = match.group(1).lower()
                else:
                    namespace = name

            cls._subclasses[namespace] = new_cls

        return new_cls

    @classmethod
    def find(cls, cls_name):
        try:
            return cls._subclasses[cls_name]
        except KeyError:
            raise LookupError, "Couldn't find provider class for {0}".format(cls_name)


class Provider(object):
    @classmethod
    def instance(cls, name, *args, **kwargs):
        provider, method_name = cls._get_provider_spec(name, *args, **kwargs)
        return provider.__provide__(method_name)

    @classmethod
    def config(cls, name, *args, **kwargs):
        provider, method_name = cls._get_provider_spec(name, *args, **kwargs)
        return provider.get_config(method_name)

    @classmethod
    def _get_provider_spec(cls, name, *args, **kwargs):
        try:
            cls_name, method_name = name.split('.')
        except ValueError:
            cls_name, method_name = name, "__default__"

        ProviderClass = type(cls).find(cls_name)
        if ProviderClass._instance == None:
            ProviderClass._instance = ProviderClass()
        return ProviderClass._instance, method_name

    __metaclass__ = ProviderMetaclass
    __abstract__ = True
    _instance = None

    def __defaults__(self):
        return dict()

    def construct(self, configuration):
        return configuration

    def get_config(self, method_name):
        config_method = getattr(self, method_name)
        config = {}
        config.update(self.__defaults__())
        config.update(config_method())
        return config

    def __init__(self):
        self._instances = {}
        super(Provider, self).__init__()

    def __default__(self):
        return dict()

    def __provide__(self, method_name):
        raise RuntimeError("A __provide__ method has not been set for this provider.")


class SingletonProvider(object):
    def __init__(self, *args, **kwargs):
        self._instances = dict()
        super(SingletonProvider, self).__init__(*args, **kwargs)

    def __provide__(self, method_name):
        import threading

        try:
            result = self._instances[method_name]
        except KeyError:
            with threading.Lock():
                try:
                    result = self._instances[method_name]
                except KeyError:
                    config = self.get_config(method_name)
                    result = self._instances[method_name] = self.construct(config)

        return result


class InstanceProvider(object):
    def __provide__(self, method_name):
        config = self.get_config(method_name)
        return self.construct(config)