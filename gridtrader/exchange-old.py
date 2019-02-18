# core
import inspect
import logging
import pprint

# 3rd party
from box import Box
from forwardable import forwardable

# local
import exception
from mynumbers import F, CF


logging.basicConfig(level=logging.DEBUG)


class APIData(Box):
    pass


class PoloniexAPIData(APIData):

    @property
    def lowestAsk(self):
        return F(self['lowestAsk'])

    @property
    def highestBid(self):
        return F(self['highestBid'])

    @property
    def midPoint(self):
        hb = self.highestBid
        la = self.lowestAsk
        logging.debug("tla {} thb {}".format(type(la), type(hb)))
        return (F(self.highestBid) + F(self.lowestAsk)) / 2.0

    # Created to catch failed order placements.
    # When a sell order fails instead of being able
    @property
    def orderNumber(self):
        if 'error' in self:
            exception.identify_and_raise(self['error'])

        return self['orderNumber']

def poloniex_api_data(d, **kwargs):
    if isinstance(d, dict):
        return PoloniexAPIData(d, **kwargs)
    if isinstance(d, list):
        return d



class BittrexAPIData(APIData):

    @property
    def lowestAsk(self):
        return F(self['Ask'])

    @property
    def highestBid(self):
        return F(self['Bid'])

    @property
    def orderNumber(self):
        return self['uuid']

wrapper = dict(
    polo=poloniex_api_data,
)

def exchangeFactory(exchange_label, config, **kwargs):

    if exchange_label == 'polo':
        kwargs['extend'] = True
        kwargs['retval_wrapper'] = wrapper[exchange_label]

        kwargs['Key'] = config.get('api', 'key')
        kwargs['Secret'] = config.get('api', 'secret')

        kwargs['loglevel'] = logging.DEBUG

        return PoloniexFacade(**kwargs)

    if exchange_label == 'bittrex':

        kwargs['api_key'] = config.get('api', 'key')
        kwargs['api_secret'] = config.get('api', 'secret')

        return BittrexFacade(**kwargs)

class ExchangeFacade(object):
    # verify() and swap() are abstract methods!
    pass

@forwardable()
class PoloniexFacade(ExchangeFacade):
    def_delegators(
        'api',
        'returnBalances, returnCompleteBalances, returnTicker'
    )

    def __init__(self, **kwargs):
        self.api = poloniex.Poloniex(**kwargs)

    def currency2pair(self, base, quote, uppercase=True):
        v = "{0}_{1}".format(base, quote)
        if uppercase:
            v = v.upper()
        return v

    def cancelAllOpen(self):
        orderdict = self.api.returnOpenOrders()
        # print "Open Orders {0}".format(orderdict)
        for pair, orderlist in orderdict.items():
            if orderlist:
                self.cancelOrders([o['orderNumber'] for o in orderlist])

    def cancelOrders(self, order_numbers):
        logging.debug("cancelOrders {0}".format(order_numbers))
        for order_number in order_numbers:
            logging.debug("cancelling {0}".format(order_number))
            self.cancelOrder(order_number)

    def tickerFor(self, market):
        all_markets_ticker = self.returnTicker()
        return PoloniexAPIData(all_markets_ticker[market])

    def fillAmount(self, trade_id):
        r = self.api.returnOrderTrades(trade_id)

        if isinstance(r, dict):
            if r.get('error'):
                return 0
            else:
                raise Exception("Received dict but not error in it.")

        amount_filled = F(0)

        logging.debug("R={0}".format(pprint.pformat(r)))

        for v in r:
            logging.debug("V={0}".format(v))
            amount_filled += float(v['amount'])

        logging.debug("amount filled = {0}".format(amount_filled))

        return amount_filled

    def fills(self, trade_id):
        r = self.api.returnOrderTrades(trade_id)

        if isinstance(r, dict):
            if r.get('error'):
                return []
            else:
                raise Exception("Received dict but not error in it.")

        logging.debug("returnOrderTrades={0}".format(pprint.pformat(r)))

        return r

    def buy(self, market, rate, amount):
        r = self.api.buy(market, rate, amount)
        if r.get('error'):
            exception.identify_and_raise(r.get('error'))
        return r

    def sell(self, market, rate, amount):
        logging.debug("Placing trade")
        r = self.api.sell(market, rate, amount)
        if r.get('error'):
            exception.identify_and_raise(r.get('error'))
        logging.debug("trace place result=%s", r)
        return r

class BittrexFacade(PoloniexFacade):
    def __init__(self, **kwargs):
        self.api = bittrex.Bittrex(**kwargs)

    def wrap(self, data):
        if isinstance(data, dict):
            return BittrexAPIData(data)

        if isinstance(data, list):
            return data

    def verify(self, r):
        # mute_methods = 'returnPositiveBalances returnTicker cancelAllOpen'
        mute_methods = 'returnTicker cancelAllOpen'
        if not r.get('success'):
            exception.identify_and_raise(r.get('message'))
        r = self.wrap(r['result'])

        method = inspect.stack()[1][3]
        if method not in mute_methods:
            logging.debug("<{}>{}</{}>".format(method, r, method))
        return r

    def returnCompleteBalances(self):
        r = self.api.get_balances()
        logging.debug("Balances: {}".format(pprint.pformat(r)))

    def returnPositiveBalances(self):
        b = self.verify(self.api.get_balances())
        r = dict()
        for pair in b:
            if pair['Balance'] > 0:
                pair['TOTAL'] = pair['Balance']
                r[pair['Currency']] = pair
        return r

    def returnBalance(self, currency):
        b = self.verify(self.api.get_balance(currency))
        return b

    def returnBalanceFromMarket(self, market):
        base = self.baseOf(market)
        return self.returnBalance(base)

    def baseAndQuote(self, market):
        quote, base = market.split('-')
        return (base, quote)

    def baseOf(self, market_name):
        return self.baseAndQuote(market_name)[0]

    def quoteOf(self, market_name):
        return self.baseAndQuote(market_name)[1]

    def cancelAllOpen(self):
        open_orders = self.verify(self.api.get_open_orders())
        logging.debug("Open Orders %s", open_orders)
        for open_order in open_orders:
            self.api.cancel(open_order['OrderUuid'])

    def cancelOrder(self, o):
        self.api.cancel(o)

    def returnTicker(self):
        return self.verify(self.api.get_market_summaries())

    def tickerFor(self, market):
        all_markets_ticker = self.returnTicker()
        for ticker in all_markets_ticker:
            if ticker['MarketName'] == market:
                ticker = self.wrap(ticker)
                logging.debug("Ticker for {} = {}".format(market, ticker))
                return ticker
        raise Exception("{} market not found".format(market))

    def sell(self, market, rate, amount):
        logging.debug("Placing sell %s, %s, %s", market, rate, amount)
        r = self.verify(self.api.sell_limit(market, amount, rate))
        logging.debug("sell limit result=%s", r)
        return r

    def buy(self, market, rate, amount):
        logging.debug("Placing buy %s, %s, %s", market, rate, amount)
        r = self.verify(self.api.buy_limit(market, amount, rate))
        logging.debug("buy limit result=%s", r)
        return r

    def isOpen(self, trade_id):
        r = self.verify(self.api.get_order(trade_id))
        logging.debug("result = {}".format(r))
        return r.IsOpen
