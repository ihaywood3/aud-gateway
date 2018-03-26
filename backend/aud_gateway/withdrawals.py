#!/usr/bin/python3

from bitshares.account import Account
from bitshares.memo import Memo
import psycopg2, psycopg2.extras
from bitshares import BitShares
from bitshares.account import Account
from bitshares.asset import Asset
import os, sys, re, traceback, os.path, os
from decimal import Decimal
from configparser import ConfigParser

import engine

eng = engine.get_engine(config)

config = ConfigParser()
config.read(['/etc/gateway.conf', os.path.expanduser('~/.config/gateway.conf')])

bitshares = BitShares()
bitshares.wallet.unlock(config['gateway']['passphrase'])
memoObj = Memo()
memoObj.unlock_wallet(config['gateway']['passphrase'])


acct = Account(config['gateway']['account'])

conn = psycopg2.connect(host=config['db'].get('host',''),database=config['db']['name'], user=config['db']["user"],
                        cursor_factory=psycopg2.extras.NamedTupleCursor)
cur = conn.cursor()

class Transaction:

    def __init__(self, tx):
        self.id_ = tx['id']
        op = tx['op'][1]
        self.from_ = op['from']
        self.amount = Decimal(op['amount']['amount'])/Decimal("10000")
        self.memo = op.get('memo')
        self.asset_id = op['amount']['asset_id']

    def unmatched(self):
        cur.execute("select 1 from tx where bts_txid = %s",self.id_)
        return cur.rowcount == 0

    def get_sender(self):
        cur.execute("select * from users where account_id = %s", self.from_)
        return cur.fetchone()

    def get_memo(self):
        if self.memo:
            return memoObj.decrypt(self.memo)
        else:
            return ""
        
def fetch_tx(num=100):
    tx = list(acct.history(limit=num, only_ops=[0]))
    all_history = len(txt) < num
    # only transactions where we received AUD
    tx = [Transaction(i)
          for i in tx
          if i['op'][1]['to'] == config['gateway']['account_id']]
    unmatched = [i for i in tx if i.unmatched()] 
    if not all_history and len(unmatched) == len(tx):
        # every history item we got was unmatched: so we need to get more history
        return fetch_tx(num=num+100)
    else:
        return unmatched

def print_run(run_id):
    cur.execute("select * from tx where run_id = %s", run_id)
    eng.first_line()
    for line in cur.fetchall():
        eng.printout(line)
    eng.last_line()
        
if len(sys.argv) == 1:
    txs_pending = fetch_tx()
    if len(txs_pending) == 0:
        sys.stderr.write("No transactions\n")
        sys.exit(0)
    cur.execute("insert into run (type) values ('P') returning (id)")
    run_id = cur.fetchone().id
    for tx in txs_pending:
        try:
            sender = tx.get_sender()
            if not sender:
                raise engine.Error("Sender {} ({}) sent {] {}, but has no KYC entry\n".format(Account(tx.from_)['name'],tx.from_,tx.amount, Asset(tx.asset_id)['symbol']))
            if tx.asset_id != config['gateway']['asset_id']:
                raise engine.Error("Sender {} ({}) sent {] {}, which is not an allowed currency\n".format(Account(tx.from_)['name'],tx.from_,tx.amount, Asset(tx.asset_id)['symbol']))
            memo = tx.get_memo()
            if sender.allow_thirdparty:
                mode, bsb, acct_no, name, ref = eng.make_payment_info(sender, memo)
            else:
                # memo fed as lodgement reference without processing
                mode, bsb, acct_no, name, _ = eng.make_payment_info(sender, "")
                ref = memo
            ref = memo or "RIVER AUD"
            cur.execute("insert into tx (bts_account, amount, bts_txid, \"comment\", bsb, account_no, account_name, fk_run, mode) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)", tx.from_, tx.amount, tx.id_, ref, bsb, acct_no, name, run_id, mode)
        except BaseException as e:
            traceback.print_exc(limit=2)
            cur.execute("insert into tx (bts_account, amount, bts_txid, \"comment\", bsb, fk_run, mode) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)", tx.from_, tx.amount, tx.id_, str(e), "999999", run_id, "E")
    conn.commit()
    print_run(run_id)
elif sys.argv[1] == '--runs':
    cur.execute("select id, start, \"type\", (select count(*) from tx where tx.fk_run = run.id) order by start desc limit 20")
    for i in cur.fetchall():
        print("{:05}\t{}\t{}\t{}".format(*i))
else:
    print_run(int(sys.argv[1]))
