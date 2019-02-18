from bitex.api.REST.rest import BittrexREST

k = BittrexREST()
k.load_key('bittrex.key')  # loads key and secret from given file;

# Query a public endpoint
r = k.query('GET','public/getmarketsummary', params={'market': 'btc-bts'})
print((r.json()))

# Query a private (authenticated) endpoint
q = {'market': 'BTC-BTS', 'type': 'buy', 'ordertype': 'limit', 'price': 2200.0,
     'volume': 0.01, 'validate': True}

r = k.query('POST','market/buylimit', authenticate=True, params=q)
print((r.json()))
