# -*- coding: utf-8 -*-
from configparser import RawConfigParser

class CaseConfigParser(RawConfigParser):
    def optionxform(self, optionstr):
        return optionstr

