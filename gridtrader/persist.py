# core
import logging
import os


# 3rd party
import dill


logging.basicConfig(level=logging.DEBUG)



class Persist(object):

    def __init__(self, dbfile):
        self.dbfile = dbfile

    def retrieve(self):
        with open(self.dbfile, 'rb') as fp:
            o = dill.load(fp)

        logging.debug("<Retrieved Object>{0}</Retrieved>".format(o))

        return o

    def store(self, o):
        with open(self.dbfile, 'wb') as fp:
            logging.debug("File pointer %s", fp)
            dill.dump(o, fp)

        logging.debug("<STORE>{0}</STORE>".format(o))
