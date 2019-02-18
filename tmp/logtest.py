import ccxt

import logging


logging.basicConfig(level=logging.INFO)

bitmex = ccxt.binance(dict(verbose=True))
bitmex.fetch_ticker("BNB/BTC")
