#!/usr/bin/env python


# Core
import logging
import sys, select, subprocess, time

# 3rd Party
from argh import dispatch_command, arg
from tqdm import tqdm

# Local
from accounts import accounts

logging.basicConfig(level=logging.DEBUG)

python = '/home/schemelab/install/miniconda3/bin/python'


def minutes(m):
    return 60 * m

DELAY = minutes(1)

def gridtrader(command, account):
    shell_cmd = '{} gridtrader/gridtrader.py --{} {}'.format(
        python, command, account)
    return shell_cmd


def _init():
    for account in accounts:
        logging.debug("*** %s", account)

        _cancel_all()

        shell_cmd = gridtrader('init', account)
        subprocess.call(shell_cmd.split())


def _monitor():
    for account in accounts:
        shell_cmd = gridtrader('monitor', account)
        subprocess.call(shell_cmd.split())


def _balances():
    for account in accounts:
        shell_cmd = gridtrader('balances', account)
        subprocess.call(shell_cmd.split())


def _cancel_all():
    for account in accounts:
        shell_cmd = gridtrader('cancel-all', account)
        subprocess.call(shell_cmd.split())

def headless_sleep(t):
    time.sleep(t)

def graphical_sleep(t):
    with tqdm(total=t) as pbar:
        for i in range(t):
            time.sleep(1)
            pbar.update(1)


def _monitor_forever(delay, headless):
    i = 1
    while True:
        _monitor()
        i += 1
        print("Loop number {} begins in {} minutes".format(i, delay))
        total=minutes(delay)

        if headless:
            headless_sleep(total)
        else:
            graphical_sleep(total)

def main(
        init=False,
        monitor=False,
        loop_monitor=False,
        balances=False,
        delay=3,
        headless=False,
        cancel_all=False
):

    if init:
        _init()

    if monitor:
        _monitor()

    if loop_monitor:
        _monitor_forever(delay, headless)

    if balances:
        _balances()

    if cancel_all:
        _cancel_all()


if __name__ == '__main__':
    dispatch_command(main)
