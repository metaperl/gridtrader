# ADSactly Grid Trader

Grid trading algorithm: setup a grid of LIMIT BUY and LIMIT SELL
orders around the current market price of a coin.

For precise details on the algorithm, consult [SPEC.md](SPEC.md)

The original purpose of this code was to trade within a range and have
futures positions setup above and below this range.

## Installation

1. `git clone git@gitlab.com:metaperl/surgetrader.git`
1. `pip3 install -r requirements.txt`


### API Key

Login to Bittrex, Binance or wherever and [create an API key](https://poloniex.com/apiKeys)
with trading privileges enabled for that account. Record the key and secret. You will need
to store them.

### API Key

## Configuration

### Setup a config file for each account

    shell> cd src/config ; cp sample.ini.sample myAccount.ini

Edit `src/config/myAccount.ini` per the docs in the .ini file.


### Make a logfile directory

    shell> mkdir -p src/log/myAccount

### Add an entry to system.ini for each account to trade

    [accounts]
    active = bluechip.ini


## Usage

    shell>
    shell> python gridtrader/gridtrader.py --help
    shell> python gridtrader/gridtrader.py --balances $accountName # List balances of account
    shell> python gridtrader/gridtrader.py --init $accountName    # Run once to set things up.
    shell> python gridtrader.py --monitor $accountName # Run every X minutes over and over.

## Automation

### Convenience Scripts for Everything

in the `batch` directory is a `run.py` which should allow you do
everything you want. Just set it up per the `README.md` there.

Once you configure your list of accounts in `acccounts.py` then you
can run all the commands in `gridtrader/gridtrader.py` without
specifying the account(s):

    shell> ./batch/run.py --init         # will also cancel orders
    shell> ./batch/run.py --balances     # show coin holdings
    shell> ./batch/run.py --monitor      # monitor buy/sell grids and adjust
    shell> ./batch/run.py --loop-monitor # run monitor indefinitely every `delay` minutes

### Cron

You may wish to go the cron route, but this code should run fine on
Windows. It was where it was initially developed (dons flame-retardant vest).

    # m h  dom mon dow   command

    MAILTO=""
    PY=~/install/miniconda/bin/python
    SRC=~/prg/adsactly-gridtrader/src
    GT=./gridtrader.py

    */10 * * * * cd $SRC ; $PY $GT --monitor bluechip

    # Cleanup

    @daily find $GT/src/log/ -name '*.log' -mtime +1 -delete



# Suggestions and Discussion

This code should only be run on coins that you are long-term bullish
on. I.e, should the coin drop in price versus the quote currency, you
have no problem with accumulating more.

In my case, I see the Binance token (BNB) as a sureshot long-term
gainer coin, because of the obvious use case and incentive to
buy.

It is very possible for this bot to drain **ALL** of your quote
currency in a very short period of time. At that point, you have a
"bag" of the base currency and you need to decide what to do with
it. In my case, the options are:

1. Move it to my portfolio account, where it is held with other
long-term coins.
1. Move it to another trading account, setting a limit order for profit.

## Initial Coin Proportions



I recommend that you only make use of 25% of your base and quote
currencies for the initial grids. That way, when new buy/sell grids
are created when the old ones are exhausted



# WARNING

If you change the program code you *MUST* run --init again. You cannot
run `--monitor` right after a change to the source code. You must --init
after that in ALL cases, because of how the serialization of program objects
to disk between runs works.

# Batch execution on Windows

`src/batch/run.py`
