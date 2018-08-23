#!/usr/bin/python3

import sys, time

from driver import *

from bitshares.account import Account
from bitshares.asset import Asset
                        
def deposit(i, method):
    """
    i: the InputTx
    fee: in basis points

    either succeeds returning BTS txid, or throws exception
    """
    fee = Decimal(config[method]['fee'])
    asset_symbol = config[method]['asset']
    asset = Asset(asset_symbol)
    dest_acct = Account(i.bts_account)
    i.date = i.date or time.strftime("%Y-%m-%d")
    cur = conn.cursor()
    try:
        fee = round(i.amount * fee / Decimal("10000"), 2)
        # are we KYC?
        cur.execute("select * from users where account_id = %s", (dest_acct['id'],))
        assert cur.rowcount > 0, "KYC data not found for {}".format(i.bts_account)
        # actually do BitShares send
        bts_tx_id = bitshares.transfer(dest_acct, float(i.amount - fee), asset, account=acct)
        # save to DB
        cur.execute("insert into tx (bts_account, amount, fee, bts_txid, \"comment\", mode, \"when\", asset, fiat_txid) values (%s, %s, %s, %s, %s, 'D', %s, %s, %s)", (dest_acct['id'], i.amount - fee, fee, repr(bts_tx_id), i.comment, i.date, asset_symbol, i.fiat_txid))
    except BaseException as e:
        cur.execute("insert into tx (bts_account, amount, \"when\", \"comment\", mode, bts_txid, asset) values (%s, %s, %s, %s, 'E','NONE', %s)", (dest_acct['id'], i.amount, i.date, i.comment + " " + str(e), asset_symbol))
        cur.close()
        conn.commit()
        raise
    conn.commit()
    return bts_tx_id, i.amount - fee

def print_tx(tx, i, method):
    fee = Decimal(config[method]['fee'])
    asset_symbol = config[method]['asset']
    fee = round(i.amount * fee / Decimal("10000"), 2)
    print("""Paid {} {} to {} keeping fee {}
BTS txid {}""".format(str(i.amount), asset_symbol, i.bts_account, str(fee), repr(tx)))

if __name__ == '__main__':
    if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] == '--help'):
        print("""deposit.py method [account amount [txref [date [comment]]]]

method: as defined in gateway.conf
account: BitShares account being deposited. If blank will read using method's input routine
amount: amount of ASSET (also defined in config)
date: the inherent date of deposit, default today 
txref: reference for the fiat side of the transfer
comment: a free text comment
""")
    else:
        method = sys.argv[1]
        if len(sys.argv) > 2:
            dest_acct = sys.argv[2]
            amount = Decimal(sys.argv[3])
            fiat_txid = comment = ""
            date = time.strftime("%Y-%m-%d")
            if len(sys.argv) > 4:
                fiat_txid = sys.argv[4]
                if len(sys.argv) > 5:
                    date = sys.argv[5]
                    if len(sys.argv) > 6:
                        comment = " ".join(sys.argv[6:])
            i = InputTx(dest_acct, amount, date, comment, fiat_txid)
            tx, actually_paid = deposit(i, method) 
            print_tx(tx, i, method)
        else:
            for i in get_function(config[method]['reader']) ():
                try:
                    tx, actually_paid = deposit(i, method)
                    print_tx(tx, i, method)
                except:
                    traceback.print_exc()
                    print("ON TRANSACTION:")
                    print_tx(None, i, method)
