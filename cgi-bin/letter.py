
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
import mimetypes
from email import encoders
import cgi
import pgp_mime.pgp
import cgitb
import collections
cgitb.enable()

form = cgi.FieldStorage()

def get(key):
    s = form.getfirst(key).value
    assert len(s) < 2048
    for i in range(0,32): s = s.replace(chr(i),repr(chr(i)))
    return s
        
mt = MIMEText("""Account: {account}
Transaction Time: {time}
{body}
""".format(body=form.getfirst('body').value,account=get('bts_account'),time=get('time'))

pgp_mime.pgp.send_mail([mt],"forms@haywood.id.au","ian@haywood.id.au",'Question: '+get('subject'),"haywood.id.au",reply_to=get('email')


        
