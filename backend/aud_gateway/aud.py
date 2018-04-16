from driver import *


class Driver(BaseDriver):
    
    def make_payment_info(self, sender, memo):
        mode = None
        MEMO_PATTERN1="bsb +([0-9 -])+ (?:account|acct|acct no|number|a/c) +([0-9] -]+) +(?:ref|reference) +(.+)"
        MEMO_PATTERN2="bsb +([0-9 -])+ (?:account|acct|acct no|number|a/c) +([0-9] -]+) +name +(.*) +(?:ref|reference) +(.+)"
        MEMO_PATTERN3="bpay +([0-9]+)[ /]+([0-9] ]+)"
        m = re.match(MEMO_PATTERN1, memo)
        if m:
            bsb = m[1]
            acct_no = m[2]
            ref = m[3]
            name = sender.name
            mode = 'S' # Standard
        else:
            m = re.match(MEMO_PATTERN2, memo)
            if m:
                bsb = m[1]
                acct_no = m[2]
                name = m[3]
                ref = m[4]
                mode = 'S'
            else:
                m = re.match(MEMO_PATTERN3, memo)
                if m:
                    bsb = m[1]
                    acct_no = m[2]
                    name = "BPAY"
                    ref = "BPAY"
                    mode = 'B'
        if not mode:
            mode = 'S'
            bsb = sender.default_bsb
            acct_no = sender.default_account_no
            name = sender.name
            ref = memo
        return (mode, bsb, acct_no, name, ref)

    def field(self, n, thing="", align=None, pad=None):
        if type(thing) is int:
            pad = pad or "0"
            align = align or ">"
            fmt = "{:"+pad+align+str(n)+"}"
        else:
            pad = pad or " "
            align = align or "<"
            fmt = "{:"+pad+align+str(n)+"."+str(n)+"}"
        sys.stdout.write(fmt.format(thing))

    def nl(self):
        sys.stdout.write("\r\n") # ? should be \r\n in production 

    def first_line(self):
        self.field(1, "0")
        self.field(17)
        self.field(2, "01") # reel sequence number. Yes, reels, I kid you not
        self.field(3, self.config['aba']['bankcode']) # bank's 3-letter code
        #ANZ 	Australia and New Zealand Banking Group
        #WBC 	Westpac Banking Corporation
        #CBA 	Commonwealth Bank of Australia
        #NAB 	National Australia Bank
        #BSA 	BankSA
        #STG 	St George Bank
        #BQL 	Bank of Queensland
        #MBL 	Macquarie Bank
        #CTI 	Citibank
        #BWA 	Bankwest
        #HBA 	HSBC Bank Australia
        #MET 	Suncorp-Metway
        #BBL 	Bendigo Bank
        #ING 	ING Bank
        self.field(7)
        self.field(26, self.config['aba']['user_preferred_specification']) # User Preferred Specification - allocated by bank
        self.field(6, self.format_account(self.config['aba']['user_id_number']), ">", "0") # User identification Number - allocated by bank
        self.field(12, self.format_text(self.config['aba'].get('file_description','PAYMENTS')))
        self.field(6, time.strftime("%d%m%y"))
        self.field(40)
        self.nl()
        self.total_payment = 0
        self.total_lines = 0

    def format_bsb(self, bsb):
        bsb = re.sub("[^0-9]", "", bsb)
        while len(bsb) < 6: bsb = "0"+bsb
        assert len(bsb) == 6
        return bsb[0:3]+'-'+bsb[3:6]

    def format_account(self, acct):
        return re.sub("[^0-9]", "", str(acct))

    def format_text(self, txt):
        txt = str(txt).upper()
        txt = re.sub("[^A-Z0-9 ]", "", txt) # banks are really, really tight about their references
        return txt

    def printout(self, tx):
        if tx.mode == 'B':
            # currently BPays get spewed to stderr for user to manually enter
            sys.stderr.write("{} BPAY: {} {} pay {}\n".format(tx.when, tx.bsb, tx.account_no, tx.amount))
        elif tx.mode == 'E':
            sys.stderr.write("{} ERROR: {}\n".format(tx.when, tx.comment))
        else:
            # line in ABA format, to stdout
            self.total_lines += 1
            self.total_payment += tx.amount
            self.field(1, "1")
            self.field(7, self.format_bsb(tx.bsb))
            self.field(9, self.format_account(tx.account_no), pad="0", align=">")
            self.field(1, " ") # "indicator"
            self.field(2, "50") # transaction type
            assert tx.amount > 0
            assert tx.amount < 99999999
            self.field(10, int(tx.amount*100)) # in cents
            self.field(32, self.format_text(tx.account_name))
            self.field(18, self.format_text(tx.comment))
            self.field(7, self.format_bsb(self.config['aba']['originating_bsb']))
            self.field(9, self.format_account(self.config['aba']['originating_account_number']), ">", "0")
            
            self.field(16, tx.bts_account)
            self.field(8, 0) # withholding tax
            self.nl()
            
    def last_line(self):
        self.field(1, "7")
        self.field(7, "999-999")
        self.field(12)
        self.field(10, int(self.total_payment*100)) # credit-debit
        self.field(10, int(self.total_payment*100)) # total credit
        self.field(10, 0) # total debits
        self.field(24)
        self.field(6, self.total_lines)
        self.field(40)
        self.nl()
        if self.total_lines == 0:
            sys.stderr.write("WARNING: no actual ABA lines\n")

    def input_data(self, cur=None):
        for row in csv.reader(sys.stdin):
            date = row[0]
            amount = Decimal(row[1])
            acct = "1.2."+row[2]
            yield InputTx(acct, amount, date)
