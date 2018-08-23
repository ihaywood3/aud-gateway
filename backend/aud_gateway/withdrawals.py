#!/usr/bin/python3

from bitshares.account import Account
from bitshares.asset import Asset
from decimal import Decimal

import driver

cur = driver.conn.cursor()
        
def fetch_tx(num=100):
    tx = list(driver.acct.history(limit=num, only_ops=0))
    all_history = len(tx) < num
    # only transactions where we are recipient
    tx = [driver.Transaction(i)
          for i in tx
          if i['op'][0] == 0 and i['op'][1]['to'] == driver.acct['id']
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
        if line.asset_id in driver_run:
            driver_run[line.asset_id].printout(line)
        else:
            drv = driver.get_driver(Asset(line.asset_id)['symbol'])
            drv.first_line()
            drv.printout(line)
            driver_run[line.asset_id] = drv
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
                drv, asset_name = driver_cache[tx.asset_id]
            else:
                asset_name = Asset(tx.asset_id)['symbol']
                try:
                    drv = driver.get_driver(asset_name)
                except KeyError:
                    raise driver.Error("Sender {} ({}) sent {} {}, which is not an allowed currency".format(Account(tx.from_)['name'], tx.from_, tx.amount, asset_name))
                driver_cache[tx.asset_id] = (drv, asset_name)
            memo = tx.get_memo()
            if sender.allow_thirdparty:
                mode, bsb, acct_no, name, ref = drv.make_payment_info(sender, memo)
            else:
                # memo fed as lodgement reference without processing
                mode, bsb, acct_no, name, _ = drv.make_payment_info(sender, "")
                ref = memo
            ref = memo or driver.config['gateway']['standard_memo']
            fee = round(tx.amount * Decimal(driver.config[asset_name]['fee']) / Decimal("10000"), 2)
            cur.execute("insert into tx (bts_account, amount, fee, bts_txid, \"comment\", bsb, account_no, account_name, fk_run, mode, \"when\") values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (tx.from_, tx.amount - fee, fee, tx.id_, ref, bsb, acct_no, name, run_id, mode, tx.timestamp))
        except BaseException as e:
            cur.execute("insert into tx (bts_account, amount, fee, bts_txid, \"comment\", bsb, fk_run, mode, \"when\") values (%s, %s, %s, %s, %s, %s, %s, %s)", (tx.from_, tx.amount, "$0.00", tx.id_, str(e), "999999", run_id, "E", tx.timestamp))
    conn.commit()
    print_run(run_id)
elif sys.argv[1] == '--runs':
    cur.execute("select id, start, \"type\", (select count(*) from tx where tx.fk_run = run.id) order by start desc limit 20")
    for i in cur.fetchall():
        print("{:05}\t{}\t{}\t{}".format(*i))
else:
    print_run(int(sys.argv[1]))
