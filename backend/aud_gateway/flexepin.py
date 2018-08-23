import flexepin_python, deposit
import time, math, sys, logging

logging.basicConfig(level=logging.INFO)

class Flexepin(flexepin_python.Flexepin):

    def __init__(self, key, secret, terminalId, testing=True):
        flexepin_python.Flexepin.__init__(self, key, secret)
        self.terminalId = terminalId
        if not testing:
            self.rootPath = "" # production URL
            
    def trans_id(self):
        s = time.strftime("%Y%m%d%H%M%s")
        frac, _ = math.modf(time.time())
        s += "{:.6f}".format(frac)[1:]
        return s
    
    def status(self):
        return self.do_private_query('GET', 'status', None).json()

    def validate(self, pin):
        return self.do_private_query('GET', 'voucher/validate/{0}/{1}/{2}'.format(pin, self.terminalId, self.trans_id()), None).json()

    def redeem(self, pin, customer_ip):
        return self.do_private_query('PUT', 'voucher/redeem/{0}/{1}/{2}'.format(pin, self.terminalId, self.trans_id()), {"customer_ip": customer_ip}).json()


if __name__ == '__main__':
    instance = sys.argv[1]

    # The connected socket is duplicated to stdin/stdout
    data = sys.stdin.readline().strip()
    logging.info('flexepin-service: at instance %s, got request: %s', instance, data)
    pin, bts_id, client_ip = tuple(data.split('\t'))
    f = Flexepin('RIVERSTONEE6BP2X', '7CBJB6MY34NOGIR1', '0001')
    res = f.redeem(pin, client_ip)
    if res['result'] == 0:
        comment = "Flexepin PIN {} from IP {}".format(pin, client_ip)
        try:
            i = InputTx(bts_id, res['value'], None, comment, res['trans_no'])
            tx, actually_paid = deposit.deposit(i, 'flexepin')
            sys.stdout.write("OK\t{}\t{}\r\n".format(res['value'], actually_paid))
        except BaseException as e:
            sys.stdout.write("FAIL\t{}\r\n".format(str(e)))
    else:
        sys.stdout.write("FAIL\t{}\r\n".format(res['result_description']))
    sys.stdout.close()

    
