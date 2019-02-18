# -*- coding: utf-8 -*-
"""Provide object-oriented access to the ini files.

SurgeTrader uses a system.ini file and a user ini file. This module provides
OO access to both.
"""

# core
import pprint
import random

# 3rd party
from configobj import ConfigObj

# local
import exchange.abstract


class System:

    def __init__(self):
        config = ConfigObj("system.ini")
        self.configo = config

    def __str__(self):
        return """{}:
            configo  = {}
            """.format(self.__class__, pprint.pformat(self.configo))

    @property
    def users_inis(self):
        _ = self.configo['users']['inis'].split()
        return _

    @property
    def any_users_ini(self):
        return random.choice(self.users_inis)

    @property
    def ignore_markets_by_in(self):
        _ = self.configo['ignore']['coin'].split()
        return _

    @property
    def ignore_markets_by_find(self):
        _ = self.configo['ignore']['market'].split()
        return _

    @property
    def max_open_trades_per_market(self):
        _ = self.configo['trade']['per_market']
        return int(_)

    @property
    def min_price(self):
        _ = self.configo['trade']['min_price']
        return float(_)

    @property
    def min_volume(self):
        _ = self.configo['trade']['min_volume']
        return float(_)

    @property
    def min_gain(self):
        _ = self.configo['trade']['min_gain']
        return float(_)

    @property
    def email_bcc(self):
        _ = self.configo['email']['bcc']
        return _

    @property
    def email_sender(self):
        _ = self.configo['email']['sender']
        return _

from icecream import ic
class User(System):

    def __init__(self, ini):
        self.system = System()

        self.filename = "accounts/{}.ini".format(ini)
        self.configo  = ConfigObj(self.filename)
        self.config_name = ini
        ic(self.configo)

    def __str__(self):
        return """{}:
            filename = {}
            exchange  = TODO
            """.format(self.__class__, self.filename)

    @classmethod
    def from_string(cls, ini_string):
        user_ini, exchange_section, exchange_subsection = ini_string.split("/")
        instance = User(user_ini, exchange_section, exchange_subsection)
        return instance

    def make_exchangeo(self):
        _ = exchange.abstract.Abstract.factory(self)
        return _

    @property
    def exchangeo(self):
        return self.make_exchangeo()

    def exchange(self, param):
        _ = self.configo['exchange'][param]
        return _

    @property
    def exchange_label(self):
        _ = self.exchange('label')
        return _

    @property
    def apikey(self):
        _ = self.exchange('apikey')
        return _

    @property
    def secret(self):
        _ = self.exchange('secret')
        return _

    def corepositions(self, symbol=None):
        ""
        if symbol is None:
            return self.configo['markets'].items()
        else:
            return self.configo['markets'][symbol]

    @property
    def takeprofit(self):
        "Percentage of seed capital to trade."
        _ = self.account('takeprofit')
        return float(_)
