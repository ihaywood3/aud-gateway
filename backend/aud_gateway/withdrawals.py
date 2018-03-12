
from bitshares.account import Account
import psycopg2
from bitshares import BitShares
import os, sys
from decimal import Decimal

bitshares = BitShares()
bitshares.wallet.unlock(os.environ['UNLOCK'])

ACCOUNT='river.aud4'
ACCOUNT_ID='1.2.650660'
ASSET='1.3.117' # bitAUD

acct = Account(ACCOUNT)

conn = psycopg2.connect(host="",database="river", user="pi")
cur = conn.cursor()

class Transaction:

    def __init__(self, tx):
        self.id_ = tx['id']
        op = tx['op'][1]
        self.from_ = op['from']
        self.amount = Decimal(op['amount']['amount'])/Decimal("10000")
        self.memo = op.get('memo')

    def unmatched(self):
        cur.execute("select 1 from tx where bts_txid = %s",self.id_)
        return cur.rowcount == 0

    def get_sender(self):
        cur.execute("select * from users where account_id = %s", self.from_)
        return cur.fetchone()
    
def fetch_tx(num=100):
    tx = list(acct.history(limit=num, only_ops=[0]))
    all_history = len(txt) < num
    # only transactions where we received AUD
    tx = [Transaction(i)
          for i in tx
          if i['op'][1]['to'] == ACCOUNT_ID and
          i['op'][1]['amount']['asset_id'] == ASSET]
    unmatched = [i for i in tx if i.unmatched()] 
    if not all_history and len(unmatched) == len(tx):
        # every history item we got was unmatched: so we need to get more history
        return fetch_tx(num=num+100)
    else:
        return unmatched

if len(sys.argv) == 1:
    txs_pending = fetch_tx()
    if len(txs_pending) == 0:
        sys.stderr.write("No transactions\n")
        sys.exit(0)
    cur.execute("insert into run (type) values ('P') returning (id)")
    run_id = cur.fetchone()[0]
    for tx in txs_pending:
        sender = tx.get_sender()
        if sender:
            
        else:
            sys.stderr.write("Sender %s (%s) sent $%s but has no KYC entry\n" % (tx.from_,Account(tx.from_)['name'],tx.amount))
    print_run(run_id)
elif sys.argv[1] == '--runs':
    cur.execute("select id, start, (select count(*) from tx where fk_run = run.id) where \"type\" = 'P' order by start desc limit 20")
    for i in cur.fetchall():
        print("{:05}\t\t{}\t\t{}".format(*i))
else:
    print_run(int(sys.argv[1]))
