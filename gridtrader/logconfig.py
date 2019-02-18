# -*- coding: utf-8 -*-
"""Configure logging.

http://www.dabeaz.com/special/Logging.pdf
"""

# logconfig.py
import logging, sys

# Set the message format
format = logging.Formatter(
 "%(asctime)s %(filename)s:%(lineno)d %(message)s")

# Create a CRITICAL message handler
crit_hand = logging.StreamHandler(sys.stderr)
crit_hand.setLevel(logging.DEBUG)
crit_hand.setFormatter(format)

# Create a handler for routing to a file
from logging.handlers import TimedRotatingFileHandler
applog_hand = TimedRotatingFileHandler(
        'log/app.log', when='d', interval=1, backupCount=365)
applog_hand.setFormatter(format)

# Create a top-level logger called 'app'
app_log = logging.getLogger("app")
app_log.setLevel(logging.DEBUG)
app_log.addHandler(applog_hand)
#app_log.addHandler(crit_hand)
