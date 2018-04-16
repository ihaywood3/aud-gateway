#!/usr/bin/python3

from bitshares.account import Account
from bitshares.block import Block
from bitshares.memo import Memo
import psycopg2, psycopg2.extras, psycopg2.extensions
from bitshares import BitShares
from bitshares.account import Account
from bitshares.asset import Asset
import os, sys, re, traceback, os.path, os
from decimal import Decimal
from configparser import ConfigParser

import driver

def cast_money(s, _):
    if s is None: return None
    return Decimal(s[1:].replace(",",""))
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

cur = conn.cursor()

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
        
def fetch_tx(num=100):
    tx = list(acct.history(limit=num, only_ops=0))
    all_history = len(tx) < num
    # only transactions where we are receipient
    tx = [Transaction(i)
          for i in tx
          if i['op'][0] == 0 and i['op'][1]['to'] == config['gateway']['account_id']]
    unmatched = [i for i in tx if i.unmatched()] 
    if (not all_history) and len(unmatched) == len(tx):
        # every history item we got was unmatched: so we need to get more history
        return fetch_tx(num=num+100)
    else:
        return unmatched

def print_run(run_id):
    cur.execute("select * from tx where fk_run = %s", (run_id,))
    driver_run = {}
    for line in cur.fetchall():
        if line.asset in driver_run:
            driver_run[line.asset].printout(line)
        else:
            drv = driver.get_engine(config, line.asset)
            drv.first_line()
            drv.printout(line)
            driver_run[line.asset] = drv
    for i in driver_run.values():
        i.last_line()
        
if len(sys.argv) == 1:
    txs_pending = fetch_tx()
    if len(txs_pending) == 0:
        sys.stderr.write("No transactions\n")
        sys.exit(0)
    cur.execute("insert into run (type) values ('P') returning (id)")
    run_id = cur.fetchone().id
    driver_cache = {}
    for tx in txs_pending:
        try:
            sender = tx.get_sender()
            if not sender:
                raise driver.Error("Sender {} ({}) sent {} {}, but has no KYC entry\n".format(Account(tx.from_)['name'], tx.from_, tx.amount, Asset(tx.asset_id)['symbol']))
            if not sender.active:
                raise driver.Error("Sender {} ({}) has KYC but not active".format(sender.bts_username, tx.form_))
            if tx.asset_id in driver_cache:
                drv = driver_cache[tx.asset_id]
            else:
                asset_name = Asset(tx.asset_id)['symbol']
                try:
                    drv = driver.get_driver(config, asset_name)
                except KeyError:
                    raise driver.Error("Sender {} ({}) sent {} {}, which is not an allowed currency".format(Account(tx.from_)['name'], tx.from_, tx.amount, asset_name))
                driver_cache[tx.asset_id] = drv
            memo = tx.get_memo()
            if sender.allow_thirdparty:
                mode, bsb, acct_no, name, ref = drv.make_payment_info(sender, memo)
            else:
                # memo fed as lodgement reference without processing
                mode, bsb, acct_no, name, _ = drv.make_payment_info(sender, "")
                ref = memo
            ref = memo or "RIVER AUD"
            cur.execute("insert into tx (bts_account, amount, bts_txid, \"comment\", bsb, account_no, account_name, fk_run, mode, \"when\") values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (tx.from_, tx.amount, tx.id_, ref, bsb, acct_no, name, run_id, mode, tx.timestamp))
        except BaseException as e:
            cur.execute("insert into tx (bts_account, amount, bts_txid, \"comment\", bsb, fk_run, mode, \"when\") values (%s, %s, %s, %s, %s, %s, %s, %s)", (tx.from_, tx.amount, tx.id_, str(e), "999999", run_id, "E", tx.timestamp))
    conn.commit()
    print_run(run_id)
elif sys.argv[1] == '--runs':
    cur.execute("select id, start, \"type\", (select count(*) from tx where tx.fk_run = run.id) order by start desc limit 20")
    for i in cur.fetchall():
        print("{:05}\t{}\t{}\t{}".format(*i))
else:
    print_run(int(sys.argv[1]))
