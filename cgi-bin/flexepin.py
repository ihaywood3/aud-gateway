
import socket, re
import cgi, cgitb
cgitb.enable()


form = cgi.FieldStorage()

pin = ''

for i in ['pin1','pin2','pin3','pin4']:
    s = form.getfirst(i)
    s = s.strip()
    assert len(s) == 4
    assert re.match(r"[0-9]{4}$",s)
    pin += s

pin5 = form.getfirst('pin5')
pin5 = pin5.strip()
assert re.match(r"[0-9]{0,4}$",s)
pin += pin5

bts_id = form.getfirst('btsid')
assert re.match(r"\w{3,50}$", bts_id)

def talk(pin, bts_id):
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect('/tmp/flexepin.socket')
    sock.sendall(bytes(pin+'\t'+os.environ['REMOTE_ADDR']+'\t'+bts_id+'\r\n', 'ascii'))
    reply = b''
    while not b'\r\n' in reply:
        reply += sock.recv(32)
    reply = tuple(str(reply, 'utf-8', 'ignore').strip().split('\t'))
    sock.close()
    return reply

reply = talk(pin)

print("""Content-Type: text/html

<!--#set var="title" value="Flexepin Voucher" -->
<!--#include virtual="header.shtml" -->
""")

if reply[0] == "OK":
    print("<p>The voucher of value {} has been redeemed, {} credited to account {}</p>".format(reply[1], reply[2], bts_id))
else:
    print("<p>The voucher has failed: {}</p>".format(reply[1]))

print("<!--#include virtual=\"footer.shtml\">")


    
    
