

# core

# 3rd party
from icecream import ic

#local
import logconfig



LOG = logconfig.app_log


class Abstract:

    @classmethod
    def bind_keys(cls, exchange, configo):
        exchange.apiKey = configo.apikey
        exchange.secret = configo.secret

    @classmethod
    def factory(cls, configo):

        exchange_label = configo.exchange_label

        if exchange_label == 'binance':
            import exchange.binance
            e = exchange.binance.Binance()
            e.options['warnOnFetchOpenOrdersWithoutSymbol'] = False

        elif exchange_label == 'bittrex':
            import exchange.bittrex
            e = exchange.bittrex.Bittrex()

        elif exchange_label == 'kucoin':
            import exchange.kucoin
            e = exchange.kucoin.Kucoin()

        elif exchange_label == 'yobit':
            import sys
            ic(sys.path)
            import exchange.yobit
            e = exchange.yobit.Yobit()
            e.enableRateLimit = True

        else:
            raise Exception("Unknown exchange label.")

        # LOG.debug("BINDKEY e={} configo={}".format(e, configo))
        cls.bind_keys(e, configo)
        return e
