import flexepin_python
import time, math

class Flexepin(flexepin_python.Flexepin):

    def __init__(self, key, secret, terminalId, testing=True):
        flexepin_python.Flexepin.__init__(self, key, secret)
        self.terminalId = terminalId
        if not testing:
            self.rootPath = "" # production URL
        self.trans_sequence = 0

    def trans_id(self):
        s = time.strftime("%Y%m%d%H%M%s")
        frac, _ = math.modf(time.time())
        s += "{:.6f}".format(frac)[1:]
        s += ".{:0>4}".format(self.trans_sequence)
        self.trans_sequence = (self.trans_sequence + 1) % 1000
        return s
    
    def status(self):
        return self.do_private_query('GET', 'status', None).json()

    def validate(self, pin):
        return self.do_private_query('GET', 'voucher/validate/{0}/{1}/{2}'.format(pin, self.terminalId, self.trans_id()), None).json()

    def redeem(self, pin, customer_ip):
        self.do_private_query('PUT', 'voucher/redeem/{0}/{1}/{2}'.format(pin, self.terminalId, self.trans_id()), {"customer_ip": customer_ip}).json()

if __name__ == '__main__':
    f = Flexepin('RIVERSTONEE6BP2X', '7CBJB6MY34NOGIR1', '0001')
    print(f.validate('3236296144942131'))
    
