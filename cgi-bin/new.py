
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
import mimetypes
from email import encoders
import io, ruamel.yaml, cgi
import pgp_mime.pgp
import cgitb
import collections
cgitb.enable()

def clean_fname(fname):
    fname = fname.lower()
    fname = fname.replace(" ","_")
    fname = fname.replace("'","")
    fname = fname.replace("\"","")
    return fname

form = cgi.FieldStorage()

parts = []
textfields = {}
for key in form.keys():
    field = form.getfirst(key)
    if field.file:
        type_ = field.type
        ce = None
        if (not type_) or type_ == 'application/octet-stream':
            type_, ce = mimetyes.guess_type(field.filename)
        if not type_:
            type_ = 'application/octet-stream'
        m = MIMEBase(*tuple(type_.split('/')))
        if ce:
            m['Content-Encoding'] = ce
        fname = key+'_'+clean_fname(field.filename)
        m.set_param('name',fname)
        m['Content-Disposition'] = 'attachment'
        m.set_param('filename',fname,'Content-Disposition')
        m.set_payload(field.file.read())
        encoders.encode_base64(m)
        parts.append(m)
    else:
        s = field.value
        assert len(s) < 1024
        s = s.replace("'","''")
        for i in range(0,32): s = s.replace(chr(i),repr(chr(i)))
        textfields[key] = s

if not textfields.get('allow_thirdparty') == 't':
    textfields['allow_thirdparty'] = 'f'
mt = MIMEText("""
INSERT INTO users (bts_account,email,default_bsb,default_account_no,allow_thirdparty)
VALUES ('{bts_account}','{email}','{bsb}','{account_no}','{allow_thirdparty}');

UPDATE users SET
   "name" = '',
   address = '',
   telephone = '',
   dob = '',
   "comment" = ''
WHERE bts_account = '{bts_account}';
""".format(**textfields))
parts.insert(0,mt)
pgp_mime.pgp.send_mail(parts,"forms@haywood.id.au","ian@haywood.id.au",'new application',"haywood.id.au",reply_to=textfields.get('email'))


        
