
# 3rd party
import ccxt.bittrex

# local
import lib.exchange.concrete
import lib.logconfig

LOG = lib.logconfig.app_log


class Bittrex(ccxt.bittrex, lib.exchange.concrete.Concrete):

    def filled(self, order):
        return order['info']['success']

    def cancelall(self):
        orders = self.fetchOpenOrders()
        LOG.debug("ORDERS={}".format(orders))

        for order in orders:
            LOG.debug("ORDER={}".format(order))
            self.cancelOrder(order['id'])

    def datetime_closed(self, order):
        return order['info']['Closed']

    def datetime_opened(self, order):
        return order['info']['Opened']

    def sellall(self):

        self.cancelall()
        balances = self.fetchBalance()
        LOG.debug("-- balances ------------------ {}".format(balances))

        """
        {'info': {'makerCommission': 10, 'takerCommission': 10, 'buyerCommission': 0, 'sellerCommission': 0, 'canTrade': True, 'canWithdraw': True, 'canDeposit': True, 'updateTime': 1525348371503, 'balances': [{'asset': 'BTC', 'free': '0.02430571', 'locked': '0.00000000'}, {'asset': 'LTC', 'free': '0.00872000', 'locked': '1.00000000'}, {'asset': 'ETH', 'free': '0.14788804', 'locked': '0.00000000'}, {'asset': 'BNC', 'free': '0.00000000', 'locked': '0.00000000'}, {'asset': 'ICO', 'free': '0.00000000', 'locked': '0.00000000'}, {'asset': 'NEO', 'free': '0.54940000', 'locked': '2.00000000'}, {'asset': 'BNB', 'free': '50.59812785', 'locked': '0.00000000'}, {'asset
        """

        for balance in balances['info']:
            LOG.debug("-- balance ------------------ {}".format(balance))


            balance['free'] = float(balance['Available'])
            balance['asset'] = balance['Currency']

            if ((balance['free'] < 4e-8) or (balance['asset'] == 'BTC')):
                LOG.debug("\tno balance or this is BTC")
                continue

            skipcoin = "RDD BCC BTCP GCR MYST INFX PDC RISE CTR SBTC"
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
                r = self.createLimitSellOrder(market, balance['free'], my_ask)
                LOG.debug(r)
            except:
                pass
