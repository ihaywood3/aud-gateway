"""
ere are defined different "payment engines" for each country
Currently only Australia but framework to expand
"""

import re, sys, time, collections, csv, os, importlib, traceback, os.path
from decimal import Decimal
from configparser import ConfigParser

from bitshares.account import Account
from bitshares.block import Block
from bitshares.memo import Memo
import psycopg2, psycopg2.extras, psycopg2.extensions
from bitshares import BitShares
from bitshares.account import Account
from bitshares.asset import Asset

def cast_money(s, _):
    if s is None: return None
    return Decimal(s[1:].replace(",","")) # hive off the dollar sign and filter out commas
money_type = psycopg2.extensions.new_type((790,), "MONEY", cast_money)

config = ConfigParser()
config.read(['/etc/gateway.conf', os.path.expanduser('~/.config/gateway.conf')])

bitshares = BitShares()
bitshares.wallet.unlock(config['gateway']['passphrase'])
memoObj = Memo()
memoObj.unlock_wallet(config['gateway']['passphrase'])


acct = Account(config['gateway']['account'])

conn = psycopg2.connect(host=config['db'].get('host',''),
                        database=config['db']['name'],
                        user=config['db']["user"],
                        cursor_factory=psycopg2.extras.NamedTupleCursor)
psycopg2.extensions.register_type(money_type, conn)


InputTx = collections.namedtuple("InputTx","bts_account amount date comment fiat_txid")

registry = {}

class Error(Exception): pass


class Transaction:

    def __init__(self, tx):
        self.timestamp = Block(tx['block_num'])['timestamp']
        self.id_ = tx['id']
        op = tx['op'][1]
        self.from_ = op['from']
        self.amount = Decimal(op['amount']['amount'])/Decimal("10000")
        self.memo = op.get('memo')
        self.asset_id = op['amount']['asset_id']

    def unmatched(self):
        cur.execute("select 1 from tx where bts_txid = %s", (self.id_,))
        return cur.rowcount == 0

    def get_sender(self):
        cur.execute("select * from users where account_id = %s", (self.from_,))
        return cur.fetchone()

    def get_memo(self):
        if self.memo:
            return memoObj.decrypt(self.memo)
        else:
            return ""



class BaseDriver(object):
    """abstract base class
    """

    
    def __init__(self, config):
        self.config = config
        

    def make_payment_info(self, sender, memo):
        """
        Take a sender and a memo and return tuple of (mode, bsb, account_no, name, reference)
        """
        pass


    def printout(self, tx):
        """
        Print out a transaction
        """
        pass


    def first_line(self):
        """
        First line of output
        """
        pass


    def last_line(self):
        """
        Finish output
        """
        pass

def get_driver(asset):
    klass = getattr(importlib.import_module(config[asset]['module']), 'Driver')
    return klass (config[asset])

def get_function(funcname):
    l = funcname.split('.')
    funcname = l[-1]
    module_name = ".".join(l[:-1])
    return getattr(importlib.import_module(module_name), funcname)
