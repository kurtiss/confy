#!/usr/bin/env python
# encoding: utf-8
"""
githubcfg.py

Created by Kurtiss Hare on 2011-02-09.
Copyright (c) 2011 Medium Entertainment, Inc. All rights reserved.
"""

from confy.providers.base import *


class GithubProvider(InstanceProvider, Provider):
    def construct(self, config):
        from github2 import client
        return client.Github(
            config['login'],
            config['api_token']
        )

    def __defaults__(self):
        return dict(
            login = None,
            api_token = None,
        )