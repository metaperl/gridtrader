# 3rd party
from ccxt.base.errors import InvalidOrder

#local
import exchange.concrete
import logconfig


LOG = logconfig.app_log


import ccxt.binance


class Binance(ccxt.binance, exchange.concrete.Concrete):

    def order_id(self, result):
        return result['info']['orderId']

    def filled(self, order):
        return order['info']['status'] == 'FILLED'

    def is_open(self, order_id, market):
        #LOG.info("<IS_OPEN order_id={}, market={}>".format(order_id, market))
        order = self.fetchOrder(order_id, market)
        #LOG.info("\tis_open got this order {} ... from this order _id {}".format(
        #    order, order_id))
        return self.filled(order)

    def get_bid(self, market):
        self.fetchTicker(market)['bid']

    def get_ask(self, market):
        self.fetchTicker(market)['ask']

    def cancelall(self):
        orders = self.fetchOpenOrders()
        LOG.debug("ORDERS={}".format(orders))

        for order in orders:
            LOG.debug("ORDER={}".format(order))
            self.cancelOrder(order['id'], order['symbol'])

    def datetime_closed(self, order):
        return order['datetime']

    def datetime_opened(self, order):
        return order['datetime']

    def get_balances(self, filter_small=True):

        EPSILON = 1e-8

        _ = self.fetchBalance()
        bal = list()
        for balance in _['info']['balances']:

            total_balance = float(balance['free']) + float(balance['locked'])
            balance['total'] = total_balance

            if filter_small:
                if total_balance > EPSILON:
                    bal.append(balance)
            else:
                bal.append(balance)

        # LOG.info("Balances {}".format(_))

        return bal
