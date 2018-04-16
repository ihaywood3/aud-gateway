"""
ere are defined different "payment engines" for each country
Currently only Australia but framework to expand
"""

import re, sys, time, collections, csv, os, importlib
from decimal import Decimal

InputTx = collections.namedtuple("InputTx","bts_account amount data")

registry = {}

class Error(Exception): pass

"""abstract base class
"""
class BaseDriver(object):
            
    def __init__(self, config):
        self.config = config
        
    """
    Take a sender and a memo and return tuple of (mode, bsb, account_no, name, reference)
    """
    def make_payment_info(self, sender, memo):
        pass

    """
    Print out a transaction
    """
    def printout(self, tx):
        pass

    """
    First line of output
    """
    def first_line(self):
        pass

    """
    Finish output
    """
    def last_line(self):
        pass

    """
    Read input from stdin (in whatever format)
    Produce NamedTuple of InputTx
    Not required to do KYC check
    Given cursor to talk to DB if required (AU version doesn't)
    """
    def input_data(self, db_cursor):
        pass
    
def get_driver(config, asset):
    klass = getattr(importlib.import_module(config[asset]['module'], 'Driver'))
    return klass (config[asset])
