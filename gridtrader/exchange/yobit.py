# 3rd party
from ccxt.base.errors import InvalidOrder

#local
import exchange.concrete
import logconfig


LOG = logconfig.app_log


import ccxt.yobit


class Yobit(ccxt.yobit, exchange.concrete.Concrete):

    def fee_adjust(self, amount_of_coin):
        _ = amount_of_coin - amount_of_coin * (0.1/100)
        LOG.debug("{} Fee adjusted = {}".format(amount_of_coin, _))
        return _

    def filled(self, order):
        LOG.debug("checking if filled using order={}".format(order))
        return order['info']['success']

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

    def sellall(self):

        self.cancelall()
        balances = self.fetchBalance()
        LOG.debug("-- balances ------------------ {}".format(balances))

        """
        {'info': {'makerCommission': 10, 'takerCommission': 10, 'buyerCommission': 0, 'sellerCommission': 0, 'canTrade': True, 'canWithdraw': True, 'canDeposit': True, 'updateTime': 1525348371503, 'balances': [{'asset': 'BTC', 'free': '0.02430571', 'locked': '0.00000000'}, {'asset': 'LTC', 'free': '0.00872000', 'locked': '1.00000000'}, {'asset': 'ETH', 'free': '0.14788804', 'locked': '0.00000000'}, {'asset': 'BNC', 'free': '0.00000000', 'locked': '0.00000000'}, {'asset': 'ICO', 'free': '0.00000000', 'locked': '0.00000000'}, {'asset': 'NEO', 'free': '0.54940000', 'locked': '2.00000000'}, {'asset': 'BNB', 'free': '50.59812785', 'locked': '0.00000000'}, {'asset
        """

        for balance in balances['info']['balances']:
            LOG.debug("-- balance ------------------ {}".format(balance))


            #balance['free'] = float(balance['Available'])
            #balance['asset'] = balance['Currency']

            if ((float(balance['free']) < 4e-8) or (balance['asset'] == 'BTC')):
                LOG.debug("\tno balance or this is BTC")
                continue

            skipcoin = "BCX SBTC CTR ETH XRP BCC EOS LTC XLM IOTA TRX"
            if balance['asset'] in skipcoin:
                LOG.debug("\tthis is a skipcoin")
                continue

            market = "{}/BTC".format(balance['asset'])

            LOG.debug(balance)

            ticker = self.fetchTicker(market)
            LOG.debug(" -- TICKER {} ".format(ticker))

            my_ask = ticker['bid'] - 1e-8

            LOG.debug(("My Ask = {}".format(my_ask)))


            try:
                r = self.createLimitSellOrder(market, float(balance['free']), my_ask)
                LOG.debug("result of limit sell={}".format(r))
            except InvalidOrder:
                print("invalid order: ")
