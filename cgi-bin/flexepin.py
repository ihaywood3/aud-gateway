
import socket, re
# import cgi, chitb
# cgitb.enable()


# form = cgi.FieldStorage()

# pin = ''

# for i in ['pin1','pin2','pin3','pin4']:
#     s = form.getfirst(i)
#     s = s.strip()
#     assert len(s) == 4
#     assert re.match(r"[0-9]{4}$",s)
#     pin += s

# pin5 = form.getfirst('pin5')
# pin5 = pin5.strip()
# assert re.match(r"[0-9]{0,4}$",s)
# pin += pin5

def talk(data):
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect('/tmp/flexepin.socket')
    sock.sendall(b'PIN:'+bytes(pin, 'ascii')+b'\r\n')
    reply = ''
    while not b'\r\n' in reply:
        reply += sock.recv(32)
    reply = str(reply, 'utf-8', 'ignore').strip().split('\t')
    sock.close()
    return reply

print("""Content-Type: text/html

<!--#set var="title" value="Flexepin Voucher" -->
<!--#include virtual="header.shtml" -->
""")

if reply == b'OKK':
    
    
