#!/usr/bin/python3
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import mimetypes
from email import encoders
import io, ruamel.yaml, cgi, mimetypes, os
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


#form = cgi.FieldStorage()

parts = []

for key in []: # ['drivers1','drivers2','selfie']:
    field = form[key]
    if type(field) is list:
        field = field[0]
    if hasattr(field,"file") and field.file:
        payload = field.file.read()
        if len(payload) == 0:
            continue
        type_ = field.type
        ce = None
        if (not type_) or type_ == 'application/octet-stream':
            type_, ce = mimetypes.guess_type(field.filename)
        if not type_:
            type_ = 'application/octet-stream'
        m = MIMEBase(*tuple(type_.split('/')))
        if ce:
            m['Content-Encoding'] = ce
        fname = key+'_'+clean_fname(field.filename or 'NONE')
        m.set_param('name',fname)
        m['Content-Disposition'] = 'attachment'
        m.set_param('filename',fname,'Content-Disposition')
        m.set_payload(payload)
        encoders.encode_base64(m)
        parts.attach(m)

class MyForm(dict):
    def __init__(self,form):
        self.form = form

    def __getitem__(self, key):
        s = self.form.getfirst(key)
        if s is None: return ""
        assert len(s) < 1024
        s = s.replace("'","''")
        for i in range(0,32): s = s.replace(chr(i),repr(chr(i)))
        return s

#mf = MyForm(form)

mf = {'bts_account': 'ihaywood3',
      'email':'ihaywood3@gmail.com',
      'bsb':'633000',
      'account_no':'123456',
      'name':'Ian Haywoood',
      'address':'1 Foo St',
      'town':'Nowhere',
      'postcode':'1111',
      'phone':'1234',
      'dob':'1973-5-14'}

mt = """
INSERT INTO users (bts_account,email,default_bsb,default_account_no,allow_thirdparty,origin_ip)
VALUES ('{bts_account}','{email}','{bsb}','{account_no}','f','ORIGINIP');

UPDATE users SET
   "name" = '{name}',
   address = '{address} {town} {postcode}',
   telephone = '{phone}',
   dob = '{dob}',
   "comment" = ''
WHERE bts_account = '{bts_account}';
""".format_map(mf)

mt = mt.replace('ORIGINIP', os.environ['REMOTE_ADDR'])

mt2 = MIMEText(mt)
    
mt2['Content-Disposition'] = 'inline'

parts.append(mt2)

pgp_mime.pgp.send_mail(parts,"daemon@river-stone.com.au","River Stone <river.stone@haywood.id.au>",'new application',"haywood.id.au",reply_to=mf['email'])


print("""Location: /success.shtml

""")

        
