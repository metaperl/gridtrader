import sys
sys.path.insert(1, '/home/schemelab/prg/ccxt/python')


# core
from datetime import datetime
import logging
logging.basicConfig(level=logging.INFO)
import os
import pprint
import sys
import time
import traceback

# 3rd party
from argh import dispatch_command, arg
import ccxt
from icecream import ic

from tabulate import tabulate

# local
import configo
import exception
import logconfig
from myconfigparser import CaseConfigParser
from mynumbers import F, CF
from persist import Persist



logger = logconfig.app_log


# os.chdir("/home/schemelab/prg/adsactly-gridtrader/src")

# If any grid position's limit order has this much or less remaining,
# consider it totally filled
EPSILON = 1e-8


def display_balances(e):
    balances = e.get_balances()

    balstr = "{}".format(balances)

    logger.info(pprint.pformat(balances))


def _set_balances(exchange, config_filename, config):
    section = 'initialcorepositions'
    config.remove_section(section)
    config.add_section(section)

    balances = get_balances(exchange)
    for coin in sorted(balances.keys()):
        logger.info("COIN %s", coin)
        config.set(section, coin, balances[coin]['TOTAL'])
    logger.info("Writing data to %s:", config_filename)
    with open(config_filename, 'w') as configfile:
        config.write(configfile)



def display_session_info(session_args, e, end=False):
    session_date = datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')
    forward_slash = "/" if end else ""

    balstr = e.get_balance_str()

    logger.info("<{}session args={} balances={} date={} >".format(
        forward_slash, session_args, balstr, session_date)
    )



def persistence_file_name(exch):
    return "persistence/{0}.storage".format(exch)

def pair2currency(pair):
    btc, currency = pair.split('-')
    return currency


def percent2ratio(i):
    return i / 100.0


def delta_by_ratio(v, r):
    return v + v * r


def delta_by_percent(v, p):
    r = percent2ratio(p)
    return delta_by_ratio(v, r)


def i_range(a):
    l = len(a)
    if not l:
        return "zero-element list"
    else:
        return "from {0} to {1}".format(0, len(a)-1)


class Grid(object):
    def __init__(
            self, market, core_position, current_market_price, gridtrader):

        logger.info("Initializing {} grid (core={}) with current market price = {}".format(
            market, core_position, current_market_price))


        self.trade_ids = list()

        self.market = market
        self.core_position = core_position
        self.current_market_price = current_market_price
        self.gridtrader = gridtrader
        self.make_grid()

    @property
    def initial_core_position(self):
        return self.core_position

    @property
    def exchange(self):
        return self.gridtrader.exchange

    @property
    def configo(self):
        return self.gridtrader.configo

    @property
    def majorLevel(self):
        return percent2ratio(
            self.configo.configo[self.config_section].as_float('majorLevel'))

    @property
    def numberOfOrders(self):
        return self.configo.configo[self.config_section].as_int('numberOfOrders')

    @property
    def increments(self):
        return percent2ratio(
            self.configo.configo[self.config_section].as_float('increments'))

    @property
    def config_section(self):
        return self.__class__.__name__.lower()

    @property
    def coreUse(self):
        return self.core_position * percent2ratio(
            self.configo.configo[self.config_section].as_float('coreUse')
            )

    @property
    def size(self):

        return self.coreUse / self.numberOfOrders

    def trade_activity(self, exchange, market):
        for i in range(len(self.trade_ids)-1, -1, -1):
            uuid = self.trade_ids[i]
            if self.exchange.is_closed(uuid, market):
                return i

        return None

    def purge_closed_trades(self, deepest_i):
        new_grid = list()
        new_trade_ids = list()
        for i in range(0, len(self.trade_ids)):
            if i > deepest_i:
                new_grid.append(self.grid[i])
                new_trade_ids.append(self.trade_ids[i])

        self.grid = new_grid
        self.trade_ids = new_trade_ids

    def __str__(self):

        config_s = str()
        for grid_section in 'sellgrid buygrid'.split():
            config_s += "<{0}>".format(grid_section)
            for option, option_value in self.configo.configo[grid_section].items():
                config_s += "{0}={1}".format(
                    option, option_value)
            config_s += "</{0}>".format(grid_section)


        table = [
            ["Core Position", self.initial_core_position],
            ["Market", self.market],
            ["Current Market Price", self.current_market_price],
            ["Grid Config", config_s],
            ["Size", self.size],
            ["Starting Price", self.starting_price],
            ["Grid", self.grid],
            ["Grid Trade Ids", self.trade_ids],
        ]

        myname = type(self).__name__
        return "  <{}>\n{}\n  </{}>\n".format(myname, tabulate(table, tablefmt="plain"), myname)

class SellGrid(Grid):

    def __init__(self, market, core_position, current_market_price, gridtrader):
        super(type(self), self).__init__(
            market, core_position, current_market_price, gridtrader)

    @property
    def starting_price(self):

        return (
            self.current_market_price +
            self.current_market_price * self.majorLevel
        )

    def make_grid(self):
        retval = list()
        last_price = self.starting_price
        for i in range(0, self.numberOfOrders):
            retval.append(last_price)
            next_price = last_price + last_price * self.increments
            # print next_price
            last_price = next_price

        self.grid = retval

    def place_orders(self, exchange):
        logger.info("<PLACE_ORDERS>")

        for rate in self.grid:
            # rate = float(rate)
            size = self.size
            logger.info(
                "createLimitSellOrder (symbol={}, size={}, price={})".format(
                    self.market, self.size, rate))
            r = exchange.createLimitSellOrder (self.market, self.size, rate)
            logger.info("RESULT OF LIMIT SELL {}".format(r))
            self.trade_ids.append(exchange.order_id(r))
            logger.info("TRADE ID APPENDED")


        logger.info("</PLACE_ORDERS>")

        return self

class BuyGrid(Grid):

    def __init__(self, market, core_position, current_market_price, gridtrader):
        super(type(self), self).__init__(
            market, core_position, current_market_price, gridtrader)

    @property
    def starting_price(self):
        return (
            self.current_market_price -
            self.current_market_price * self.majorLevel
        )

    @property
    def profitTarget(self):
        return self.configo.configo[self.config_section].as_float('profitTarget')


    def make_grid(self):
        retval = list()
        last_price = self.starting_price
        for i in range(0, self.numberOfOrders):
            retval.append(last_price)
            next_price = last_price - last_price * self.increments
            # print next_price
            last_price = next_price

        self.grid = retval

    def place_orders(self, exchange):
        print("<PLACE_ORDERS>")

        self.remaining = dict()

        for rate in self.grid:
            r = exchange.createLimitBuyOrder (self.market, self.size, rate)
            logger.info("RESULT OF LIMIT BUY {}".format(r))
            self.trade_ids.append(exchange.order_id(r))

        print("</PLACE_ORDERS>")

        return self


class GridTrader(object):

    def __init__(self, exchange, configo, account):
        self.exchange, self.configo = exchange, configo
        self.account = account
        self.market = dict()

    def __str__(self):
        s = str()
        for market in self.grids:
            s += '<{0}>\n'.format(market)
            for buysell in self.grids[market]:
                s += str(self.grids[market][buysell])
            s += '</{0}>\n'.format(market)

        return "{0}\n{1}".format(type(self).__name__, s)


    @property
    def pairs(self):

        pairs = dict()

        for market, core_position in self.config['pairs'].items():
            logger.info(f"market={market}, core_position={core_position}")
            amount_of_coin, coin = core_position.split()
            t = self.exchange.ticker(market)
            logger.info(f"ticker={t} formatted={t.formatted} ask={t.formatted.ask}")
            pairs[market] = {
                    'name' : market,
                   # 'ticker': t.formatted,
                    'core_position': (float(amount_of_coin), coin)
            }

        return pairs

    @property
    def balances(self):
        return self.exchange.returnBalances()

    def midpoint(self, market):
        ic(market)
        ticker = self.exchange.fetchTicker(market)

        return (F(ticker['ask']) + F(ticker['bid']))/ 2.0

    def config_core(self):
        pass

    def build_new_grids(self):

        grid = dict()
        logger.info("Creating buy and sell grids")
        for market, core_position in self.configo.corepositions():
            logger.info(f"market={market}, corepos={core_position}")
            grid[market] = dict()
            grid[market]['sell'] = SellGrid(
                market=market,
                core_position=float(core_position),
                current_market_price=self.midpoint(market),
                gridtrader=self
            )
            grid[market]['buy'] = BuyGrid(
                market=market,
                core_position=float(core_position),
                current_market_price=self.midpoint(market),
                gridtrader=self
            )
            for direction in 'sell buy'.split():
                logger.info(
                   "{0} grid = {1}".format(direction, grid[market][direction]))

        self.grids = grid

    def issue_trades(self):
        for market in self.grids:
            t = self.exchange.fetchTicker(market)
            ask = t['ask']
            bid = t['bid']
            print(f"ask={ask} on {market}")
            self.market[market] = {
                'lowestAsk'  : F(ask),
                'highestBid' : F(bid),
            }
            for buysell in self.grids[market]:
                g = self.grids[market][buysell]

                if buysell in 'buy sell':
                    try:
                        g.place_orders(self.exchange)
                    except (exception.NotEnoughCoin, exception.DustTrade):
                        logger.info("%s grid not fully created because there was not enough coin", buysell)
                else:
                    raise exception.InvalidDictionaryKey("Key other than buy or sell: %s", buysell)


    def poll(self):

        activity = dict(buy=0, sell=0)

        for market in self.grids:

            g = self.grids[market]

            logger.info("Checking %s buy activity", market)
            deepest_i = g['buy'].trade_activity(self.exchange, market)
            if deepest_i is None:
                logger.info(
                    "No %s buy trade activity detected %s",
                    market, i_range(g['buy'].trade_ids)
                    )
            else:
                activity['buy'] = 1 + deepest_i
                gb = g['buy']
                logger.info(
                    "%s Buy trade activity detected at index %d of %d!",
                       market, deepest_i, len(gb.trade_ids)-1)
                for i in range(deepest_i, -1, -1):

                    fill_rate = gb.grid[i]
                    logger.info("Buy rate @i={0} == {1}".format(i, fill_rate))
                    logger.info("Let's see our holdings %s", self.exchange.get_balance_str())


                    profit_target = gb.profitTarget
                    if profit_target <= 0:
                        logger.info("Accumulating purchase instead of selling for profit")
                    else:
                        sell_rate = delta_by_percent(fill_rate, profit_target)
                        logger.info(
                            "Creating sell trade size={0} rate={1}".format(
                                gb.size, sell_rate))
                        r = self.exchange.createLimitSellOrder(market, gb.size, sell_rate)

                gb.purge_closed_trades(deepest_i)

                if not gb.trade_ids:
                    logger.info(
                        """
%s Buy grid exhausted. Creating new buy grid.
Current market conditions: highestBid = %f, lowestAsk = %f
                        """,
                        market,
                        self.exchange.get_bid(market),
                        self.exchange.get_ask(market)
                    )
                    deepest_filled_rate = self.exchange.get_bid(market)
                    self.grids[market]['buy'] = BuyGrid(
                        pair=market,
                        current_market_price=deepest_filled_rate,
                        gridtrader=self
                    ).place_orders(self.exchange)

            logger.info("Checking %s sell activity", market)
            deepest_i = g['sell'].trade_activity(self.exchange, market)
            if deepest_i is None:
                logger.info(
                    "No %s sell trade activity detected %s",
                    market, i_range(g['sell'].trade_ids)
                )
            else:
                activity['sell'] = 1 + deepest_i
                logger.info(
                    "%s Sell trade activity detected at index %d of %d",
                    market, deepest_i, len(g['sell'].trade_ids)-1)

                deepest_filled_rate = g['sell'].grid[deepest_i]
                logger.info("Deepest filled rate = %f", deepest_filled_rate)

                g['sell'].purge_closed_trades(deepest_i)

                logger.info(
                    "Cancelling and elevating the %s buy grid", market)
                for trade_id in self.grids[market]['buy'].trade_ids:
                    self.exchange.cancelOrder(trade_id, market)

                self.grids[market]['buy'] = BuyGrid(
                    pair=market,
                    current_market_price=deepest_filled_rate,
                    gridtrader=self
                ).place_orders(self.exchange)

            if not g['sell'].trade_ids:
                logger.info(
                    "%s Sell grid exhausted. Creating new sell grid",
                    market)
                deepest_filled_rate = self.exchange.get_ask(market)
                g['sell'] = SellGrid(
                    pair=market,
                    current_market_price=deepest_filled_rate,
                    gridtrader=self
                ).place_orders(self.exchange)

        logger.info("Activity during this monitoring run: {}".format(activity))


    def notify_admin(self, error_msg):

        import mymailer
        mymailer.send_email(self.account, error_msg)


def delta(percent, v):
    return v + percent2ratio(percent) * v


def pdict(d, skip_false=True):
    parms = list()
    for k in sorted(d.keys()):
        if not d[k] and skip_false:
            continue
        parms.append("{0}={1}".format(k, d[k]))

    return ",".join(parms)

# http://stackoverflow.com/questions/5595425/what-is-the-best-way-to-compare-floats-for-almost-equality-in-python
def isclose(a, b, rel_tol=EPSILON, abs_tol=0.0):
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

def iszero(v):
    # logger.info("isclose(0, %f)", v)
    # return isclose(0, v)
    return v < EPSILON



def print_balances(e):
    b = get_balances(e)
    logger.info(b.pformat())


def prep_app(account, args):

    args = pdict(args)

    logPath = 'log/{}'.format(account)
    logFileName = "{0}--{1}".format(
        time.strftime("%Y%m%d-%H %M %S"),
        args
    )

    return args, logFileName

def main_init(exchange, grid_trader, persistence_file):
    # exchange.cancelAllOpen()

    logger.info("Building trade grids")
    grid_trader.build_new_grids()

    logger.info("Issuing trades on created grids")
    grid_trader.issue_trades()

    logger.info("Storing GridTrader to disk.")
    Persist(persistence_file).store(grid_trader)

@arg('--cancel-all', help="Cancel all open orders, even if this program did not open them")
@arg('--init', help="Create new trade grids, issue trades and persist grids.")
@arg('--monitor', help="See if any trades in grid have closed and adjust accordingly")
@arg('--status-of', help="(Developer use only) Get the status of a trade by trade id")
@arg('account', help="The account whose API keys we are using (e.g. terrence, joseph, peter, etc.")
@arg('--balances', help="list coin holdings")
@arg('--fetch-markets', help="fetch markets")
@arg('--set-balances', help="Alter [initialcorepositions] section of config file based on exchange holdings.")
def main(
        account,
        cancel_all=False,
        init=False,
        monitor=False,
        balances=False,
        fetch_markets=False,
        set_balances=False,
        status_of='',
):
    command_line_args = locals()

    pretty_args, log_filename = prep_app(account, command_line_args)

    user_configo = configo.User(account)


    persistence_file = persistence_file_name(account)

    exchange = user_configo.make_exchangeo()

    display_session_info(pretty_args, exchange)
    grid_trader = GridTrader(exchange, user_configo, account)

    try:

        if cancel_all:
            exchange.cancelall()

        if init:
            logger.info("Initializing...")

            main_init(exchange, grid_trader, persistence_file)

        if monitor:
            logger.info("Evaluating trade activity since last invocation")
            persistence = Persist(persistence_file)
            grid_trader = persistence.retrieve()
            grid_trader.poll()
            persistence.store(grid_trader)

        if balances:
            logger.info("Getting balances")
            display_balances(exchange)

        if fetch_markets:
            logger.info("Fetching markets")
            m = exchange.fetchMarkets()
            print(m)

        if set_balances:
            logger.info("Setting balances")
            _set_balances(exchange, config_file, config)
            main_init(exchange, grid_trader, persistence_file)

        if status_of:
            logger.info("Getting status of order")
            # get_status_of(status_of)

    except Exception as e:
        error_msg = traceback.format_exc()
        logger.info('Aborting: %s', error_msg)
        grid_trader.notify_admin(error_msg)


    display_session_info(pretty_args, exchange, end=True)

if __name__ == '__main__':
    dispatch_command(main)
