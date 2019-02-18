from bitex import Bittrex
k = Bittrex(key_file='bittrex.key')

r = k.ticker('BTC-BTS')

import pprint

print((r.formatted))
print((r.json()))
