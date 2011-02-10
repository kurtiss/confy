#!/usr/bin/env python
# encoding: utf-8
"""
smtplibcfg.py

Created by Kurtiss Hare on 2011-02-09.
Copyright (c) 2011 Medium Entertainment, Inc. All rights reserved.
"""

from confy.providers.base import *


class SmtplibProvider(InstanceProvider, Provider):
    def construct(self, config):
        import smtplib
        smtp = smtplib.SMTP(config['domain'], config['port'])
        login, password = config['login'], config['password']

        if login:
            smtp.login(login, password)

        return smtp

    def __defaults__(self):
        return dict(
            domain = "localhost",
            login = "",
            password = "",
            port = 25
        )