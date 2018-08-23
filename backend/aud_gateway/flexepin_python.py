import time
import math
import json, requests
import hmac
import hashlib


class Flexepin:

    def __init__(self, key, secret):
        if key and secret:
            self.key = key
            self.rootPath = "https://testrest.flexepin.com"
            self.secret = secret
        else:
            raise RuntimeError('NO KEY/SECRET')

    def microtime(self, get_as_float=False):
        if get_as_float:
            return time.time()
        else:
            return '%f %d' % math.modf(time.time())

    def do_private_query(self, requestMethod, requestUri, body=None):

        requestUri = '/{0}'.format(requestUri)
        url = '{0}{1}'.format(self.rootPath, requestUri)
        mt = self.microtime().split(' ')
        nonce = '{0}{1}'.format(mt[1], mt[0][2:6])

        thejson = None
        if body:
            thejson = json.dumps(body,separators=(',',':'))

        payload = ''
        payload = '{0}{1}\n'.format(payload, requestMethod)
        payload = '{0}{1}\n'.format(payload, requestUri)
        payload = '{0}{1}\n'.format(payload, nonce)
        if thejson:
            payload = '{0}{1}'.format(payload, thejson)
        # print(payload)

        signature = self.get_signature(payload)
        # print(signature)

        headers = {'content-type': 'application/x-www-form-urlencoded',
                   'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
                   'Accept': '/',
                   'Connection': 'keep-alive',
                   'AUTHENTICATION': 'HMAC {0}:{1}:{2}'.format(self.key, signature, nonce)
                   }
        if requestMethod == 'PUT':
            return requests.put(url, data=thejson, headers=headers)
        elif requestMethod == 'POST':
            return requests.post(url, data=thejson, headers=headers)
        elif requestMethod == 'GET':
            return requests.get(url, headers=headers)

    def get_signature(self, payload):
        return hmac.new(self.secret, payload, hashlib.sha256).hexdigest()


key = 'DYEV7IR3NIAV7JIM'
secret = 'lmMWKaA3JzjI5eu3'

fp = Flexepin(key, secret)

pin = '3948759238498249'
terminalId = 'someterminalID'
transId = 'unique1234'

print(fp.do_private_query('GET', 'status', None).text)

print(fp.do_private_query('GET', 'voucher/validate/{0}/{1}/{2}'.format(pin, terminalId, transId), None).text)

print(fp.do_private_query('PUT', 'voucher/redeem/{0}/{1}/{2}'.format(pin, terminalId, transId), {"customer_ip":"192.168.0.1"}).text)

