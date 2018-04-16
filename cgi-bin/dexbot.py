#!/usr/bin/python3
import io, ruamel.yaml, cgi, cgitb, collections, mimetypes, os, requests, json, time, math, os.path, threading, pudb, pdb
from bitshares.market import Market
from bitshares.price import FilledOrder
from bitshares.account import Account
from bitshares.amount import Amount
from bitshares.price import Price, Order, FilledOrder
from bitshares import BitShares
from bitshares.exceptions import AccountDoesNotExistsException
cgitb.enable()


def ok_char(c):
    if ord(c) < 32 or ord(c) > 126:
        return False
    if c in "\"\\'`/?*":
        return False
    return True

print("Content-Type: text/html")
print("")
print("<html><body>")

form = cgi.FieldStorage()

bts_id = form.getfirst("bts_account")
assert len(bts_id) < 100
bts_id = "".join(i for i in bts_id if ok_char(i))

try:
    account = Account(bts_id)
except AccountDoesNotExistsException:
    print("<p>The named account does not exist on the blockchain</p>")
else:
    print("<p>Thankyou for submitting your ID</p>")
    with open("/srv/home/pi/users.txt","a") as f:
        f.write(bts_id+"\n")


        
