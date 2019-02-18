

class MarketCrash(Exception):
    pass

class NotEnoughCoin(Exception):
    pass

class DustTrade(Exception):
    pass

class InvalidDictionaryKey(Exception):
    pass
# -*- coding: utf-8 -*-


def identify_and_raise(error_text):
    if 'Total must be at least' in error_text:
        raise DustTrade(error_text)
        
    if 'Not enough' in error_text:
        raise NotEnoughCoin(error_text)
                
    if 'INSUFFICIENT_FUNDS' in error_text:
        raise NotEnoughCoin(error_text)        