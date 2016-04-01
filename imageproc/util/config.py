#!/usr/bin/env python

import ConfigParser
import os


class Config(object):

    def __init__(self):
        self.config = ConfigParser.ConfigParser()
        self.config.read(os.path.dirname(os.path.realpath(__file__)) + "/" + "config.ini")

    def get(self, section, option, raw=False, vars=None):
        return self.config.get(section, option, raw, vars)