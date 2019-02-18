from icecream import ic

import logconfig

LOG = logconfig.app_log


class Concrete:

    def is_closed(self, trade_id, market):
        o = self.fetchOrder(trade_id, symbol=market)
        res = o['status'] == 'closed'
        print(f"{res} is is_closed()'s result of examining {o}")
        return res

    def fee_adjust(self, amount_of_coin):
        return amount_of_coin

    def order_id(self, r):
        return r['id']

    def get_balance_str(self, filter_small=True):

        EPSILON = 1e-8

        _ = self.fetchBalance()
        v = str(_['info'])
        return v

    def open_orders_in(self, symbol, side='sell'):
        """Maximum number of unclosed SELL LIMIT orders for a coin.

    SurgeTrader detects hourly surges. On occasion the hourly surge is part
    of a longer downtrend, leading SurgeTrader to buy on surges that do not
    close. We do not want to keep buying false surges so we limit ourselves to
    3 open orders on any one coin.

    Args:
        exchange (int): The exchange object.
        market (str): The coin.

    Returns:
        int: The number of open orders for a particular coin.

    """

        LOG.debug("executing number_of_open_orders_in")
        openorders = self.fetchOpenOrders(symbol)
        LOG.debug("open orders = {}".format(openorders))

        orders = list()
        if openorders:
            for order in openorders:
                orders.append(order)

        return orders
