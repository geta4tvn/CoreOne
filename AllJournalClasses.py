import sqlite3
from sqlite3 import Error
import time


folder='C:\\Tevin\\CoreOne\\'

global logfile
logfile=folder+"logfile.txt"

def ErrorLog(x):
    global logfile
    log=open(logfile,'a')
    EventTime=time.time()
    event=time.ctime(EventTime)
    log.write(event +'\n')
    log.write(x+'\n\n')
    log.close()
    return


#=======================================================================================================================
#=======================    ACCESS THE TWO DATABASES: STATIC AND JOURNAL     ===========================================

#======================  WINDOWS PATH
dbStatic='C:\\Tevin\\CoreOne\\static.sqlite'
dbJournal='C:\\Tevin\\CoreOne\\journal.sqlite'

#======================  PATH TO USE IF IN  LINUX  =====================================================================
#dbStatic='/usr/ecr/static.sqlite'
#dbJournal='/usr/ecr/journal.sqlite'

def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)  #you can create and handle a dv IN MEMORY usint connect(:memory:)
        return conn
    except Error as e:
        print(e)
    return None

#STAT=create_connection(dbStatic)         # ++++++++++++++   static.sqlite
JOURN=create_connection(dbJournal)       # ++++++++++++++   journal.sqlite

#global S
global J
#S=STAT.cursor()
J=JOURN.cursor()   # IMPORTANT: JOURN is the CONNECTIOn and you use JOURN to commit() or close(), J is the CURSOR of the CONNECTION and you use this J for execute

#==========================   SO J=THE CURSOR TO JOURNAL DATABASE AND S=THE CURSOR TO STATIC DB =========
# STATIC db contains data that don't change often: DPT descriptions, VAT, PLU table, parameters, error messages, print templates etc.
# JOURNAL db changes every time a new transaction happens or machine changes status: contains e-journal, current receipt, system state class

#======================================================================================================================
# This is SYSTEM STATE CLASS: it is supposed to hold all info necessary to recover operation after a system down
# SyState will be ONLY WRITTEN TO DB IN CASE OF POWER DOWN or POWER FAIL SIGNAL, not every time
# This class is stored in journal.sqlite as table "state" with the following columns



#============================================================================================================================
# this is the SUMMARY OF ONE CLOSED OR CANCELED RECEIPT OR INVOICE THAT IS CURRENTLY OPEN
# this is opened and numbered in Znum, DocNum and DocNumAccum the moment one valid keyboard entry comes in
# WE KEEP THE OBJECT IN MEMORY AND WRITE TO journal.InvoiceId table ONLY AFTER IT IS CLOSED OR PFAIL HAPPENS

class InvoiceId(object):
    def __init__(self,Znum, DocNum, DocNumAccum, DocNumMiddleware, IsOpen, IsCancelled , InvType, InvCategory, RelatedNum, \
                 ClerkCode, ClerkName, TimeStamp, Date, Time, TimeStampTransm, PinOfBuyer, CustCode, CustName, CustType, \
                 CustDetails, Location, TotalPcs, TotalQty, TaxVatA, TaxVatB, TaxVatC, TaxVatD, TaxVatE, TaxVatExempt, TaxAux, \
                 TotalAmntBefDiscnt, TotalDiscnts, TotalAmountPayable, TotalAmntPbleCurB, CurrencyBRate, CoinQRforPayment, \
                 TotalTaxableA, TotalTaxableB, TotalTaxableC, TotalTaxableD, TotalTaxableE, TotalTax , Pay1Amnt, Pay1Descr, \
                 Change, Pay2Amnt, Pay2Descr, Pay3Amnt, Pay3Desc, CouponId, CouponAmnt, LoyaltyEarned, AmountOnCredit, CheckNum, \
                 DueDateforPayment, HashA, HashE, QRCode, HeaderCode, FooterCode, FullAText, RestaurantTable, Room):
        self.Znum               = Znum              # this is the Z number where this receipt/invoice belongs to (pending to be issued)
        self.DocNum             = DocNum            # the serial number of this receipt/invoice for this Z (starts at 1 every new Z)
        self.DocNumAccum        = DocNumAccum       # accumulating serial number of this rece/inv since installation - KEY to fetch all the LINES of this receipt/inv from InvoiceLines
        self.DocNumMiddleware   = DocNumMiddleware  # KENYA TIMS this is the accumulating s/n of rec/inv with added Middleware ID
        self.IsOpen             = IsOpen            # 1=means this doc is open still, payment is pending, storage is pending, 0=closed
        self.IsCancelled        = IsCancelled       # 1=means this doc is canceled so all lines were re-written with ZERO and total is ZERO but NUMBERING continues
        self.InvType            = InvType           # KENYA TIMS 0=PROTOTYPE, 1=COPY, …???
        self.InvCategory        = InvCategory       # KENYA TIMS 0=RETAIL RECEIPT, 1=INVOICE, 2=CREDIT NOTE
        self.RelatedNum         = RelatedNum        # KENYA TIMS, if this is a CREDIT NOTE, here you need to have the DocNumAccum of the invoice which is credited
        self.ClerkCode          = ClerkCode         #   The code of operator
        self.ClerkName          = ClerkName         # The name of operator, we need both here to keep record of clerks when names change on same clerk code…
        self.TimeStamp          = TimeStamp         # Time stamp of first creation of this doc
        self.Date               = Date              # Derived date in DD-MM-YYYY from TimeStamp
        self.Time               = Time              # Derived time in HH:MM:SS from TimeStamp
        self.TimeStampTransm    = TimeStampTransm   # KENYA TIMS, time stamp when this doc was transmitted to server
        self.PinOfBuyer         = PinOfBuyer        # KENYA TIMS, pin of buyer
        self.CustCode           = CustCode          # Customer / Buyer code in our database
        self.CustName           = CustName          # customer name details from our database
        self.CustType           = CustType          # type of customer, like shop, distributor, ???
        self.CustDetails        = CustDetails       # Customer address, phone number etc on an invoice
        self.Location           = Location          # GPS coordinates from GPS module??? Or simply location where the invoice was issued for truck invoicing
        self.TotalPcs           = TotalPcs          # Total pieces if goods are counted in pieces
        self.TotalQty           = TotalQty          # total quantity in Kgr
        self.TaxVatA            = TaxVatA           # tax amount for VAT A = TotalTaxableA * the VATA% currently in force - the VAT% may change later on, this is why we store both
        self.TaxVatB            = TaxVatB           # tax amount for VAT B
        self.TaxVatC            = TaxVatC           # tax amount for VAT C
        self.TaxVatD            = TaxVatD           # tax amount for VAT D
        self.TaxVatE            = TaxVatE           # tax amount for VAT E
        self.TaxVatExempt       = TaxVatExempt      # tax amount for VAT Ex
        self.TaxAux             = TaxAux            # tax amount for Tax
        self.TotalAmntBefDiscnt = TotalAmntBefDiscnt  # this is actually TotalAmountPayable + TotalDiscnts
        self.TotalDiscnts       = TotalDiscnts      # the sum total of discounts as entered in InvoiceLines
        self.TotalAmountPayable = TotalAmountPayable  # this is gross amount to be paid, including cost of goods and all taxes IN THE DEFAULT CURRENCY
        self.TotalAmntPbleCurB  = TotalAmntPbleCurB  # total payable in alternative currency
        self.CurrencyBRate      = CurrencyBRate     # the current conversion rate from base currency to alt currency
        self.CoinQRforPayment   = CoinQRforPayment  # in case alt currency is a CRYPTOCOIN, this QR code will be needed to effect the payment using mobile wallet
        self.TotalTaxableA      = TotalTaxableA     #
        self.TotalTaxableB      = TotalTaxableB     #
        self.TotalTaxableC      = TotalTaxableC     #
        self.TotalTaxableD      = TotalTaxableD     #
        self.TotalTaxableE      = TotalTaxableE     #
        self.TotalTax           = TotalTax          #
        self.Pay1Amnt           = Pay1Amnt          # payment amount
        self.Pay1Descr          = Pay1Descr         # payment code and description or just description
        self.Change             = Change            # if Pay1Amnt is > TotalAmountPayable, system will calculate Change to return to customer
        self.Pay2Amnt           = Pay2Amnt          # second payment in case payment is spread into more than a single payment
        self.Pay2Descr          = Pay2Descr         # description of second payment or code+description
        self.Pay3Amnt           = Pay3Amnt          # third payment if needed
        self.Pay3Desc           = Pay3Desc          # same
        self.CouponId           = CouponId          # the ID or code number of the coupon presented for a discount or form of payment
        self.CouponAmnt         = CouponAmnt        # the amount in that coupon
        self.LoyaltyEarned      = LoyaltyEarned     # lolyalty points credited to this customer
        self.AmountOnCredit     = AmountOnCredit    # in case credit is given, the amount on credit
        self.CheckNum           = CheckNum          # if a check is given, the check number
        self.DueDateforPayment  = DueDateforPayment  # the date due for payment
        self.HashA              = HashA             # you need to form _a.txt DYNAMICALLY by combining the text(HeaderCode)+Top+Lines+text(FooterCode)
        self.HashE              = HashE             # GREECE ONLY - the _e.txt hash value
        self.QRCode             = QRCode            # KENYA TIMS see how to form this / GR is a different thing
        self.HeaderCode         = HeaderCode        # Read the actual text used in this receipt from static.headers - you need this text for do the _a.txt and HashA
        self.FooterCode         = FooterCode        # Read the actual text used in this receipt from static.footers - you need this text to do the _a.txt and HashA
        self.FullAText          = FullAText         # GREECE ONLY - this is the PRINTED _a.txt - KENYA TIMS will use JSON, perhaps we can put the json text here
        self.RestaurantTable    = RestaurantTable   # just in case we need tables
        self.Room               = Room              # hospitality app to charge room number



    def InvIdRead(self,AccNum):
        # This will return the InvoiceId object from journal.InvoiceId
        # if parameter AccNum==999 it will fetch the LAST, CURRENT doc
        # for any other AccNum it will fetch the object with the specified DocNumAccum
        global J
        if AccNum==999:
            J.execute("SELECT * FROM InvoiceId WHERE DocNumAccum=(SELECT MAX(DocNumAccum) FROM InvoiceId)")
        elif AccNum!=999:
            J.execute("SELECT * FROM InvoiceId WHERE DocNumAccum=?",(AccNum,))
            # ALTERNATIVELY you can use DICTIONARY to fill in variables like this:
            #J.execute("SELECT * FROM InvoiceId WHERE DocNumAccum=:queryNum",{'queryNum':AccNum}) OR NO? Can you have a VARIABLE inside a DICT?

        ListFetchOne = J.fetchone()
        self.Znum               = ListFetchOne[0]  # this is the Z number where this receipt/invoice belongs to (pending to be issued)
        self.DocNum             = ListFetchOne[1]  # the serial number of this receipt/invoice for this Z (starts at 1 every new Z)
        self.DocNumAccum        = ListFetchOne[2]  # accumulating serial number of this rece/inv since installation - KEY to fetch all the LINES of this receipt/inv from InvoiceLines
        self.DocNumMiddleware   = ListFetchOne[3]  # KENYA TIMS this is the accumulating s/n of rec/inv with added Middleware ID
        self.IsOpen             = ListFetchOne[4]  # 1=means this doc is open still, payment is pending, storage is pending, 0=closed
        self.IsCancelled        = ListFetchOne[5]  # 1=means this doc is canceled so all lines were re-written with ZERO and total is ZERO but NUMBERING continues
        self.InvType            = ListFetchOne[6]  # KENYA TIMS 0=PROTOTYPE, 1=COPY, …???
        self.InvCategory        = ListFetchOne[7]  # KENYA TIMS 0=RETAIL RECEIPT, 1=INVOICE, 2=CREDIT NOTE
        self.RelatedNum         = ListFetchOne[8]  # KENYA TIMS, if this is a CREDIT NOTE, here you need to have the DocNumAccum of the invoice which is credited
        self.ClerkCode          = ListFetchOne[9]  # The code of operator
        self.ClerkName          = ListFetchOne[10]  # The name of operator, we need both here to keep record of clerks when names change on same clerk code…
        self.TimeStamp          = ListFetchOne[11]  # Time stamp of first creation of this doc
        self.Date               = ListFetchOne[12]  # Derived date in DD-MM-YYYY from TimeStamp
        self.Time               = ListFetchOne[13]  # Derived time in HH:MM:SS from TimeStamp
        self.TimeStampTransm    = ListFetchOne[14]  # KENYA TIMS, time stamp when this doc was transmitted to server
        self.PinOfBuyer         = ListFetchOne[15]  # KENYA TIMS, pin of buyer
        self.CustCode           = ListFetchOne[16]  # Customer / Buyer code in our database
        self.CustName           = ListFetchOne[17]  # customer name details from our database
        self.CustType           = ListFetchOne[18]  # type of customer, like shop, distributor, ???
        self.CustDetails        = ListFetchOne[19]  # Customer address, phone number etc on an invoice
        self.Location           = ListFetchOne[20]  # GPS coordinates from GPS module??? Or simply location where the invoice was issued for truck invoicing
        self.TotalPcs           = ListFetchOne[21]  # Total pieces if goods are counted in pieces
        self.TotalQty           = ListFetchOne[22]  # total quantity in Kgr
        self.TaxVatA            = ListFetchOne[23]  # tax amount for VAT A = TotalTaxableA * the VATA% currently in force - the VAT% may change later on, this is why we store both
        self.TaxVatB            = ListFetchOne[24]  # tax amount for VAT B
        self.TaxVatC            = ListFetchOne[25]  # tax amount for VAT C
        self.TaxVatD            = ListFetchOne[26]  # tax amount for VAT D
        self.TaxVatE            = ListFetchOne[27]  # tax amount for VAT E
        self.TaxVatExempt       = ListFetchOne[28]  # tax amount for VAT Ex
        self.TaxAux             = ListFetchOne[29]  # tax amount for Tax
        self.TotalAmntBefDiscnt = ListFetchOne[30]  # this is actually TotalAmountPayable + TotalDiscnts
        self.TotalDiscnts       = ListFetchOne[31]  # the sum total of discounts as entered in InvoiceLines
        self.TotalAmountPayable = ListFetchOne[32]  # this is gross amount to be paid, including cost of goods and all taxes IN THE DEFAULT CURRENCY
        self.TotalAmntPbleCurB  = ListFetchOne[33]  # total payable in alternative currency
        self.CurrencyBRate      = ListFetchOne[34]  # the current conversion rate from base currency to alt currency
        self.CoinQRforPayment   = ListFetchOne[35]  # in case alt currency is a CRYPTOCOIN, this QR code will be needed to effect the payment using mobile wallet
        self.TotalTaxableA      = ListFetchOne[36]  #
        self.TotalTaxableB      = ListFetchOne[37]  #
        self.TotalTaxableC      = ListFetchOne[38]  #
        self.TotalTaxableD      = ListFetchOne[39]  #
        self.TotalTaxableE      = ListFetchOne[40]  #
        self.TotalTax           = ListFetchOne[41]  #
        self.Pay1Amnt           = ListFetchOne[42]  # payment amount
        self.Pay1Descr          = ListFetchOne[43]  # payment code and description or just description
        self.Change             = ListFetchOne[44]  # if Pay1Amnt is > TotalAmountPayable, system will calculate Change to return to customer
        self.Pay2Amnt           = ListFetchOne[45]  # second payment in case payment is spread into more than a single payment
        self.Pay2Descr          = ListFetchOne[46]  # description of second payment or code+description
        self.Pay3Amnt           = ListFetchOne[47]  # third payment if needed
        self.Pay3Desc           = ListFetchOne[48]  # same
        self.CouponId           = ListFetchOne[49]  # the ID or code number of the coupon presented for a discount or form of payment
        self.CouponAmnt         = ListFetchOne[50]  # the amount in that coupon
        self.LoyaltyEarned      = ListFetchOne[51]  # lolyalty points credited to this customer
        self.AmountOnCredit     = ListFetchOne[52]  # in case credit is given, the amount on credit
        self.CheckNum           = ListFetchOne[53]  # if a check is given, the check number
        self.DueDateforPayment  = ListFetchOne[54]  # the date due for payment
        self.HashA              = ListFetchOne[55]  # you need to form _a.txt DYNAMICALLY by combining the text(HeaderCode)+Top+Lines+text(FooterCode)
        self.HashE              = ListFetchOne[56]  # GREECE ONLY - the _e.txt hash value
        self.QRCode             = ListFetchOne[57]  # KENYA TIMS see how to form this / GR is a different thing
        self.HeaderCode         = ListFetchOne[58]  # Read the actual text used in this receipt from static.headers - you need this text for do the _a.txt and HashA
        self.FooterCode         = ListFetchOne[59]  # Read the actual text used in this receipt from static.footers - you need this text to do the _a.txt and HashA
        self.FullAText          = ListFetchOne[60]  # GREECE ONLY - this is the PRINTED _a.txt - KENYA TIMS will use JSON, perhaps we can put the json text here
        self.RestaurantTable    = ListFetchOne[61]  # just in case we need tables
        self.Room               = ListFetchOne[62]  # hospitality app to charge room number


    def InvIdWrite(self):
        global J
        #ERROR HANDLING: read https://stackoverflow.com/questions/14797375/should-i-always-specify-an-exception-type-in-except-statements
        try:
            J.execute(
                "INSERT INTO InvoiceId VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, \
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);",
                (self.Znum, self.DocNum, self.DocNumAccum, self.DocNumMiddleware, self.IsOpen, self.IsCancelled, self.InvType, self.InvCategory, self.RelatedNum, self.ClerkCode,
                 self.ClerkName, self.TimeStamp, self.Date, self.Time, self.TimeStampTransm, self.PinOfBuyer, self.CustCode, self.CustName, self.CustType, self.CustDetails,
                 self.Location, self.TotalPcs, self.TotalQty, self.TaxVatA, self.TaxVatB, self.TaxVatC, self.TaxVatD, self.TaxVatE, self.TaxVatExempt, self.TaxAux,
                 self.TotalAmntBefDiscnt, self.TotalDiscnts, self.TotalAmountPayable, self.TotalAmntPbleCurB, self.CurrencyBRate, self.CoinQRforPayment, self.TotalTaxableA,
                 self.TotalTaxableB, self.TotalTaxableC, self.TotalTaxableD, self.TotalTaxableE, self.TotalTax, self.Pay1Amnt, self.Pay1Descr, self.Change, self.Pay2Amnt,
                 self.Pay2Descr, self.Pay3Amnt, self.Pay3Desc, self.CouponId, self.CouponAmnt, self.LoyaltyEarned, self.AmountOnCredit, self.CheckNum, self.DueDateforPayment,
                 self.HashA, self.HashE, self.QRCode, self.HeaderCode, self.FooterCode, self.FullAText, self.Table, self.Room,))
            JOURN.commit() # it is JOURN.commit() and NOT J.commit(): commit() is a connection function, and J is the CURSOR, JOURN is the connection
        #https://stackoverflow.com/questions/14797375/should-i-always-specify-an-exception-type-in-except-statements
        except Exception as err:
            ErrorLog(err)





    # FROM www.sqlite.org/faq:
    # read faq19 in my software notes
    # speed of INSERTs is limited, use BEGIN ..multiple INSERTS.. COMMIT otherwise by default each INSERT is a separate transaction, cant do more than 50-60 pes sec



#=================================================================================================
#========    this is the Invoice Lines Class to contain line by line all
#=================================================================================================
class InvoiceLines(object):
    def __init__(self,Znum, DocNum, DocNumAccum, LineNum, InvType, TransType, Command, CommandID, QTY1, QTY2, QTY, PluDescr, PluDescrB, \
                 HSCode, HSDescr, PluQR, UnitPrice, PluDpt, DptDescr, DptPrice, Category, DiscntPerc, DiscntPercAmnt, DiscntAmnt, \
                 MrkupPerc, MrkupPercAmnt, MrkupAmnt, VoidLineNum, VATRate, TaxableAmnt, VATTaxAmnt, OtherTaxAmnt, TaxExemptAmnt,\
                 TotalAmnt, SubTotalFromStart, PayCode, PayDescr, PayAmnt, CouponCode, CouponDescr, CouponAmnt, GiftCardCode, GiftCardDescr, GiftAmnt, \
                 Change, SpecialCommandPrint, LineComment, LinePlainTextPrintout):
        self.Znum                   = Znum                     # this is the Z number where this receipt/invoice belongs to (pending to be issued)
        self.DocNum                 = DocNum                   # the serial number of this receipt/invoice for this Z (starts at 1 every new Z)
        self.DocNumAccum            = DocNumAccum              # accumulating serial number of this rece/inv since installation - KEY to fetch all the LINES of this receipt/inv from InvoiceLines
        self.LineNum                = LineNum                  # this is the line number of each transaction belonging to DocNumAccum receipt or invoice
        self.InvType                = InvType                  # KENYA TIMS 0=PROTOTYPE, 1=COPY, … 9=TEMPORARY PARTIAL RECEIPT FOR SERVING TO A TABLE
        self.TransType              = TransType                # the type of transaction FOR THIS LINE: is it a SALE, a REFUND, a VOID, a total CANCEL (which will all prev)?
        self.Command                = Command                   # the T, R, V etc command coming in from the keyboard
        self.CommandID              = CommandID                 # this is the nn from Tnn, the ccccccc from PLUcccccccccc etc coming in from the keyboard
        self.QTY1                   = QTY1                      # quantity qqqqqX coming in from the keyboard
        self.QTY2                   = QTY2                      # second quantity if operator uses N x M x price
        self.QTY                    = QTY                       # this is either QTY=QTY1 if QTY2 null OR QTY=QTY1*QTY2
        self.PluDescr               = PluDescr                  # this is the description retrieved from static.plu - PluCode is CommandID above / if REFUND or VOID, the descr, price is NEGATIVE
        self.PluDescrB              = PluDescrB                 # auxiliary description for this plu
        self.HSCode                 = HSCode                    # KENYA TIMS - the HSCode for the plu
        self.HSDescr                = HSDescr                   # KENYA TIMS - the HSDescription for the plu
        self.PluQR                  = PluQR                     # QR code for this PLU: perhaps usefull if the PLU is a CODE by itself, for example selling BITCOINS and giving the private key here
        self.UnitPrice              = UnitPrice                 # Unit Price of the PLU as retrieved from static.plu OR given by the keyboard command
        self.PluDpt                 = PluDpt                    # The dpt this PLU belongs to as retrieved from static.plu - the VATRate retrieved from DPT is stored in VATRate
        self.DptDescr               = DptDescr                  # dpt description taken from dpt table
        self.DptPrice               = DptPrice                  # if there is a fixed dpt price in db, use this, else take input price - this will be determined in CheckIn.py module
        self.Category               = Category                  # if dpt is associated with a category, this is shown here as category CODE (description may be read from static.cat table)
        self.DiscntPerc             = DiscntPerc                # the percentage of discount - the CommandID will determine if dscnt will be on previous line item or subtotal
        self.DiscntPercAmnt         = DiscntPercAmnt            # if we have multiple discounts on subtotal then we need to keep track of all vat rates accum subtots on every line
        self.DiscntAmnt             = DiscntAmnt                # UNLESS we do it THROUGH InvoiceId which should be re-calculated if we get SUBTOTAL command….
        self.MrkupPerc              = MrkupPerc                 #
        self.MrkupPercAmnt          = MrkupPercAmnt             #
        self.MrkupAmnt              = MrkupAmnt                 #
        self.VoidLineNum            = VoidLineNum               # in case this line's command is VOID, prompt user to enter the voided line - prev void will auto fill here LineNum-1
        self.VATRate                = VATRate                   # VAT rate for this transn, taken either from the dpt assoc with PLU OR, if we decouple PLUs from DPTs, from PLU
        self.TaxableAmnt            = TaxableAmnt               # provision to handle things like PETROL STATIONS KENYA where there is a NON-taxable amnt included in PLU price
        self.VATTaxAmnt             = VATTaxAmnt                # the calculated amount of VAT
        self.OtherTaxAmnt           = OtherTaxAmnt              # any other non-VAT tax applied to this transaction
        self.TaxExemptAmnt          = TaxExemptAmnt             # the tax exempt amount
        self.TotalAmnt              = TotalAmnt                 # total amount payable
        self.SubTotalFromStart      = SubTotalFromStart         # this attribute will hold the ACCUMULATED TOTAL from all previous lines in same receipt until it is closed
        self.PayCode                = PayCode                   # one payment per line, this is the payment code / RESTAURANT support: in SPLIT function
        self.PayDescr               = PayDescr                  # description of payment
        self.PayAmnt                = PayAmnt                   # amount of payment
        self.CouponCode             = CouponCode                # we could use QR printed coupons with some encoding, code goes here
        self.CouponDescr            = CouponDescr               # description of the coupon, perhaps embedded in QR code
        self.CouponAmnt             = CouponAmnt                # the amount of coupon - if coupon is a DISCOUNT, it will be analyzed by CheckIn.py and put into discount records
        self.GiftCardCode           = GiftCardCode              # GIFTCARDS will also be QR based with encrypted detailes, issued by our system
        self.GiftCardDescr          = GiftCardDescr             # description of giftcard, embedded in QR code
        self.GiftAmnt               = GiftAmnt                  # amount embedded and encrypted in gift card
        self.Change                 = Change                    # change which is the difference between the PayAmnt - TotalAmnt
        self.SpecialCommandPrint    = SpecialCommandPrint       # For example, if this line is a REFUND, the SpecialComandPrint is *** REFUND *** etc…
        self.LineComment            = LineComment               # comment to be printed under this transaction line
        self.LinePlainTextPrintout  = LinePlainTextPrintout     # to help with the _a.txt, the exact text that is printed out when this line is executed


    def InvLinesRead(self,AccNum):
    # This will return the InvoiceLines object from journal.InvoiceId
    # if parameter AccNum==999 it will fetch the LAST, CURRENT doc
    # for any other AccNum it will fetch the object with the specified DocNumAccum
    # for EACH InvoiceLines AccNum we have as many InvoiceLines objects as there are lines in the invoice....
        global J
        if AccNum == 999:
            J.execute("SELECT * FROM InvoiceLines WHERE DocNumAccum=(SELECT MAX(DocNumAccum) FROM InvoiceLines)")
        elif AccNum != 999:
            J.execute("SELECT * FROM InvoiceLines WHERE DocNumAccum=?", (AccNum,))
        # ALTERNATIVELY you can use DICTIONARY to fill in variables like this:
        # J.execute("SELECT * FROM InvoiceId WHERE DocNumAccum=:queryNum",{'queryNum':AccNum}) OR NO? Can you have a VARIABLE inside a DICT?

            ListFetchOne = J.fetchone()
            self.Znum               = ListFetchOne[0]           # this is the Z number where this receipt/invoice belongs to (pending to be issued)
            self.DocNum             = ListFetchOne[1]           # the serial number of this receipt/invoice for this Z (starts at 1 every new Z)
            self.DocNumAccum        = ListFetchOne[2]           # accumulating serial number of this rece/inv since installation - KEY to fetch all the LINES of this receipt/inv from InvoiceLines
            self.LineNum            = ListFetchOne[3]           # this is the line number of each transaction belonging to DocNumAccum receipt or invoice
            self.InvType            = ListFetchOne[4]           # KENYA TIMS 0=PROTOTYPE, 1=COPY, … 9=TEMPORARY PARTIAL RECEIPT FOR SERVING TO A TABLE
            self.TransType          = ListFetchOne[5]           # the type of transaction FOR THIS LINE: is it a SALE, a REFUND, a VOID, a total CANCEL (which will go back to nul all prev)?
            self.Command            = ListFetchOne[6]           # the T, R, V etc command coming in from the keyboard
            self.CommandID          = ListFetchOne[7]           # this is the nn from Tnn, the ccccccc from PLUcccccccccc etc coming in from the keyboard
            self.QTY1               = ListFetchOne[8]           # quantity qqqqqX coming in from the keyboard
            self.QTY2               = ListFetchOne[9]           # second quantity if operator uses N x M x price
            self.QTY                = ListFetchOne[10]          # this is either QTY=QTY1 if QTY2 null OR QTY=QTY1*QTY2
            self.PluDescr           = ListFetchOne[11]          # this is the description retrieved from static.plu - PluCode is CommandID above / if REFUND or VOID, the descr, price is NEGATIVE
            self.PluDescrB          = ListFetchOne[12]          # auxiliary description for this plu
            self.HSCode             = ListFetchOne[13]          # KENYA TIMS - the HSCode for the plu
            self.HSDescr            = ListFetchOne[14]          # KENYA TIMS - the HSDescription for the plu
            self.PluQR              = ListFetchOne[15]          # QR code for this PLU: perhaps usefull if the PLU is a CODE by itself, for example selling BITCOINS and giving the private key here
            self.UnitPrice          = ListFetchOne[16]          # Unit Price of the PLU as retrieved from static.plu OR given by the keyboard command
            self.PluDpt             = ListFetchOne[17]          # The dpt this PLU belongs to as retrieved from static.plu - the VATRate retrieved from DPT is stored in VATRate
            self.DptDescr           = ListFetchOne[18]          # dpt description taken from dpt table
            self.DptPrice           = ListFetchOne[19]          # if there is a fixed dpt price in db, use this, else take input price - this will be determined in CheckIn.py module
            self.Category           = ListFetchOne[20]          # if dpt is associated with a category, this is shown here as category CODE (description may be read from static.cat table)
            self.DiscntPerc         = ListFetchOne[21]          # the percentage of discount - the CommandID will determine if dscnt will be on previous line item or subtotal
            self.DiscntPercAmnt     = ListFetchOne[22]          # if we have multiple discounts on subtotal then we need to keep track of all vat rates accum subtots on every line
            self.DiscntAmnt         = ListFetchOne[23]          # UNLESS we do it THROUGH InvoiceId which should be re-calculated if we get SUBTOTAL command….
            self.MrkupPerc          = ListFetchOne[24]          #
            self.MrkupPercAmnt      = ListFetchOne[25]          #
            self.MrkupAmnt          = ListFetchOne[26]          #
            self.VoidLineNum        = ListFetchOne[27]          # in case this line's command is VOID, we should prompt user to enter the voided line - prev void will auto fill here LineNum-1 (the previous line)
            self.VATRate            = ListFetchOne[28]          # The applicable VAT rate for this transaction, taken either from the dpt associated with PLU OR, if we decouple PLUs from DPTs, from PLU
            self.TaxableAmnt        = ListFetchOne[29]          # provision to handle things like PETROL STATIONS KENYA where there is a NON-taxable amnt included in PLU price
            self.VATTaxAmnt         = ListFetchOne[30]          # the calculated amount of VAT
            self.OtherTaxAmnt       = ListFetchOne[31]          # any other non-VAT tax applied to this transaction
            self.TaxExemptAmnt      = ListFetchOne[32]          # the tax exempt amount
            self.TotalAmnt          = ListFetchOne[33]          # total amount payable
            self.SubTotalFromStart  = ListFetchOne[34]          # this attribute will hold the ACCUMULATED TOTAL from all previous lines in same receipt until it is closed
            self.PayCode            = ListFetchOne[35]          # one payment per line, this is the payment code / RESTAURANT support: in SPLIT function
            self.PayDescr           = ListFetchOne[36]          # description of payment
            self.PayAmnt            = ListFetchOne[37]          # amount of payment
            self.CouponCode         = ListFetchOne[38]          # we could use QR printed coupons with some encoding, code goes here
            self.CouponDescr        = ListFetchOne[39]          # description of the coupon, perhaps embedded in QR code
            self.CouponAmnt         = ListFetchOne[40]          # the amount of coupon - if coupon is a DISCOUNT, it will be analyzed by CheckIn.py and put into discount records
            self.GiftCardCode       = ListFetchOne[41]          # GIFTCARDS will also be QR based with encrypted detailes, issued by our system
            self.GiftCardDescr      = ListFetchOne[42]          # description of giftcard, embedded in QR code
            self.GiftAmnt           = ListFetchOne[43]          # amount embedded and encrypted in gift card
            self.Change             = ListFetchOne[44]          # change which is the difference between the PayAmnt - TotalAmnt
            self.SpecialCommandPrint = ListFetchOne[45]         # For example, if this line is a REFUND, the SpecialComandPrint is *** REFUND *** etc…
            self.LineComment        = ListFetchOne[46]          # comment to be printed under this transaction line
            self.LinePlainTextPrintout = ListFetchOne[47]       # to help with the _a.txt, the exact text that is printed out when this line is executed

    def InvLinesWrite(self):

        global J
        J.execute(
            "INSERT INTO InvoiceLines VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, "
            "?, ?, ?, ?);",
            (self.Znum, self.DocNum, self.DocNumAccum, self.LineNum, self.InvType, self.TransType, self.Command, self.CommandID, self.QTY1, self.QTY2, self.QTY, self.PluDescr,
             self.PluDescrB, self.HSCode, self.HSDescr, self.PluQR, self.UnitPrice, self.PluDpt, self.DptDescr, self.DptPrice, self.Category, self.DiscntPerc, self.DiscntPercAmnt,
             self.DiscntAmnt, self.MrkupPerc, self.MrkupPercAmnt, self.MrkupAmnt, self.VoidLineNum, self.VATRate, self.TaxableAmnt, self.VATTaxAmnt, self.OtherTaxAmnt,
             self.TaxExemptAmnt, self.TotalAmnt, self.SubTotalFromStart, self.PayCode, self.PayDescr, self.PayAmnt, self.CouponCode, self.CouponDescr, self.CouponAmnt,
             self.GiftCardCode, self.GiftCardDescr, self.GiftAmnt, self.Change, self.SpecialCommandPrint, self.LineComment, self.LinePlainTextPrintout,))
        JOURN.commit()  # it is JOURN.commit() and NOT J.commit(): commit() is a connection function, and J is the CURSOR, JOURN is the connection
        # read sqlite.org/faq about speed of INSERTs
        # https://stackoverflow.com/questions/1711631/improve-insert-per-second-performance-of-sqlite

#==================================================================================================
#==========     SyState
#==================================================================================================
class SystemState(object):
    def __init__(self,OpMode, TStampNow, OpenRcpt, OpenRcptNum, OpenRcptTStamp, LastRcptTStamp, OpenDay, LastZNum, LastZTStamp, \
                 LastZUploadTStamp, InMenu, FlashDiskSpace, LastBackupTStamp, ErrorNow, ErrorPast, PowerFail, BatStat, RTCBat, \
                 ClerkCode, ClerkPerm, ClerkDesc, SerialNum, CryptoKey, WiFiOn, WiFiStat, NetStat, SrvrTaxLastTStamp, SrvrMaintLastTStamp):
        self.OpMode                 = OpMode                    # operational mode, 0=idle in sales, 1=open day, receipts are done, 2=in menu, 3=in reports, 4=in programming, 5=demo mode
        self.TStampNow              = TStampNow                 # the time stamp when this system state record was taken
        self.OpenRcpt               = OpenRcpt                  # 0=no open receipt or invoice, 1=doc is open
        self.OpenRcptNum            = OpenRcptNum               # the accumulated number of the receipt that is open / the last closed receipt number is this -1
        self.OpenRcptTStamp         = OpenRcptTStamp            # the timestamp when this open receipt was opened
        self.LastRcptTStamp         = LastRcptTStamp            # the time of the last closed receipt. If OpenDay=1 (yes) then if NowTime-LastRcptTStamp>48h then warn or is 24h take Z
        self.OpenDay                = OpenDay                   # 0=not open, meaning a Z was the last thing we did, no receipt was opened since last Z, 1=receipts issues after last Z
        self.LastZNum               = LastZNum                  # Last Z number, obviously pending Z num is LastZNum+1
        self.LastZTStamp            = LastZTStamp               # the time stamp of the last Z
        self.LastZUploadTStamp      = LastZUploadTStamp         # the time this last Z was uploaded
        self.InMenu                 = InMenu                    # if OpMode=2 we can look here InMenu to find the number of the menu, for example 231…
        self.FlashDiskSpace         = FlashDiskSpace            # sys info about flash disk space available
        self.LastBackupTStamp       = LastBackupTStamp          # time stamp of last backup to external usb stick
        self.ErrorNow               = ErrorNow                  # the error number that is now active, not resolved
        self.ErrorPast              = ErrorPast                 # the last error number that is not active now, that was resolved
        self.PowerFail              = PowerFail                 # 0=no power fail, no issues, 1=power failure happened, just re-boot from pfail, 2=reboot without power fail
        self.BatStat                = BatStat                   # 100=fully charged, 15=issue warning, 5=stop operation and force shut down
        self.RTCBat                 = RTCBat                    # 100=fully ok, 5= give warning and stop (GREECE) otherwise ignore
        self.ClerkCode              = ClerkCode                 # the code of the active clerk
        self.ClerkPerm              = ClerkPerm                 # permissions and level of the active clerk - it is put in systate to avoid reading the db all the time
        self.ClerkDesc              = ClerkDesc                 # name of the active clerk to be printed on the receipt
        self.SerialNum              = SerialNum                 # serial number of the device
        self.CryptoKey              = CryptoKey                 # AES key of the device
        self.WiFiOn                 = WiFiOn                    # 0=off, 1=on
        self.WiFiStat               = WiFiStat                  # 0=no connection, 1=connected, 2=errors,
        self.NetStat                = NetStat                   # if ethernet, 0=no con, 1=connected, 2=errors
        self.SrvrTaxLastTStamp      = SrvrTaxLastTStamp         # time of last upload to tax server
        self.SrvrMaintLastTStamp    = SrvrMaintLastTStamp       # time of last contact with our maintenance server

    def StateRead(self):
        global J
        # This will return the LAST state record in db - actually we do NOT need past records, perhaps 2-3 more to investigate
        J.execute("SELECT * FROM SyState WHERE TStampNow=(SELECT MAX(TStampNow) FROM SyState)")
        ListFetchOne = J.fetchone()

        self.OpMode                 = ListFetchOne[0]           # operational mode, 0=idle in sales, 1=open day, receipts are done, 2=in menu, 3=in reports, 4=in programming, 5=demo mode
        self.TStampNow              = ListFetchOne[1]           # the time stamp when this system state record was taken
        self.OpenRcpt               = ListFetchOne[2]           # 0=no open receipt or invoice, 1=doc is open
        self.OpenRcptNum            = ListFetchOne[3]           # the accumulated number of the receipt that is open / the last closed receipt number is this -1
        self.OpenRcptTStamp         = ListFetchOne[4]           # the timestamp when this open receipt was opened
        self.LastRcptTStamp         = ListFetchOne[5]           # the time of the last closed receipt. If OpenDay=1 (yes) then if NowTime-LastRcptTStamp>48h then warn or is 24h take Z
        self.OpenDay                = ListFetchOne[6]           # 0=not open, meaning a Z was the last thing we did, no receipt was opened since last Z, 1=receipts issues after last Z
        self.LastZNum               = ListFetchOne[7]           # Last Z number, obviously pending Z num is LastZNum+1
        self.LastZTStamp            = ListFetchOne[8]           # the time stamp of the last Z
        self.LastZUploadTStamp      = ListFetchOne[9]           # the time this last Z was uploaded
        self.InMenu                 = ListFetchOne[10]          # if OpMode=2 we can look here InMenu to find the number of the menu, for example 231…
        self.FlashDiskSpace         = ListFetchOne[11]          # sys info about flash disk space available
        self.LastBackupTStamp       = ListFetchOne[12]          # time stamp of last backup to external usb stick
        self.ErrorNow               = ListFetchOne[13]          # the error number that is now active, not resolved
        self.ErrorPast              = ListFetchOne[14]          # the last error number that is not active now, that was resolved
        self.PowerFail              = ListFetchOne[15]          # 0=no power fail, no issues, 1=power failure happened, just re-boot from pfail, 2=reboot without power fail
        self.BatStat                = ListFetchOne[16]          # 100=fully charged, 15=issue warning, 5=stop operation and force shut down
        self.RTCBat                 = ListFetchOne[17]          # 100=fully ok, 5= give warning and stop (GREECE) otherwise ignore
        self.ClerkCode              = ListFetchOne[18]          # the code of the active clerk
        self.ClerkPerm              = ListFetchOne[19]          # permissions and level of the active clerk - it is put in systate to avoid reading the db all the time
        self.ClerkDesc              = ListFetchOne[20]          # name of the active clerk to be printed on the receipt
        self.SerialNum              = ListFetchOne[21]          # serial number of the device
        self.CryptoKey              = ListFetchOne[22]          # AES key of the device
        self.WiFiOn                 = ListFetchOne[23]          # 0=off, 1=on
        self.WiFiStat               = ListFetchOne[24]          # 0=no connection, 1=connected, 2=errors,
        self.NetStat                = ListFetchOne[25]          # if ethernet, 0=no con, 1=connected, 2=errors
        self.SrvrTaxLastTStamp      = ListFetchOne[26]          # time of last upload to tax server
        self.SrvrMaintLastTStamp    = ListFetchOne[27]          # time of last contact with our maintenance server

    def StateWrite(self):
        global J
        J.execute("INSERT INTO SyState VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", (
        self.OpMode, self.TStampNow, self.OpenRcpt, self.OpenRcptNum, self.OpenRcptTStamp, self.LastRcptTStamp, self.OpenDay, self.LastZNum, self.LastZTStamp,
        self.LastZUploadTStamp, self.InMenu, self.FlashDiskSpace, self.LastBackupTStamp, self.ErrorNow, self.ErrorPast, self.PowerFail, self.BatStat, self.RTCBat, self.ClerkCode,
        self.ClerkPerm, self.ClerkDesc, self.SerialNum, self.CryptoKey, self.WiFiOn, self.WiFiStat, self.NetStat, self.SrvrTaxLastTStamp, self.SrvrMaintLastTStamp,))
        JOURN.commit()  # it is JOURN.commit() and NOT J.commit(): commit() is a connection function, and J is the CURSOR, JOURN is the connection
        # read sqlite.org/faq about speed of INSERTs
        # https://stackoverflow.com/questions/1711631/improve-insert-per-second-performance-of-sqlite


#=============================================================================================================
#=================   XZReports
#=============================================================================================================
class XZReports(object):
    def __init__(self, Znum, ZTimeStamp, Zdate, Ztime, FromInvNum, ToInvNum, FromRecNum, ToRecNum, UploadTimeStamp, UploadDate, UploadTime , \
                 UploadError, LastZUploadTStamp, ZTotalPcs, ZTotalQty, ZTotalInvCount, ZTotalInvAmnt, ZTotalCreditNotesCount, ZTotalCredNotesAmnt, \
                 ZTotalReceiptsCount, ZTotalRecAmnt, ZTotalDiscountCount, ZTotalDiscountAmnt, ZTotalMarkupUpCount, ZTotalMarkupUpAmnt, \
                 ZTotalRefundsCount, ZTotalRefundsAmnt, ZTotalTicketsCount, ZTotalTicketsAmnt, ZTotalCouponCount, ZTotalCouponAmnt, ZGrandTotal, \
                 InDrawerCash, InDrawerPayCodeA, InDrawerPayDescrA, InDrawerPayAmntA, InDrawerPayCodeB, InDrawerPayDescrB, InDrawerPayAmntB, \
                 InDrawerPayCodeC, InDrawerPayDescrC, InDrawerPayAmntC, InDrawerPayCodeD, InDrawerPayDescrD, InDrawerPayAmntD, InDrawerPayCodeE, \
                 InDrawerPayDescrE, InDrawerPayAmntE, InDrawerCheckCount, InDrawerCheckAmnt, InDrawerCoinCode, InDrawerCoinDesc, InDrawerCoinAmnt, \
                 ZCashInCount, ZCashInAmnt, ZCashOutCount, ZCashOutAmnt, VoidsCount, VoidsAmnt, PreVoidsCount, PreVoidsAmnt, CancelCount, CancelAmnt, \
                 LoyaltyCount, LoyaltyPoints, ChangeVATAfrom, ChangeVATAto, ChangeVATBfrom, ChangeVATBto, ChangeVATCfrom, ChangeVATCto, ChangeVATDfrom, \
                 ChangeVATDto, ChangeVATEfrom, ChangeVATEto, ChangeTAXfrom, ChangeTAXto, ACurrentRate, AGrossTotal, ATaxableTot, ATaxTotal, \
                 BCurrentRate, BGrossTotal, BTaxableTot, BTaxTotal, CCurrentRate, CGrossTotal, CTaxableTot, CTaxTotal, DCurrentRate, DGrossTotal, \
                 DTaxableTot, DTaxTotal, ECurrentRate, EGrossTotal, ETaxableTot, ETaxTotal, TCurrentRate, TGrossTotal, TTaxableTot, TTaxTotal, \
                 CounterHeaderChanges, CounterResets, CounterResetDateTime, CounterService, CounterServiceDateTime, CounterRTCChanges, CounterRTCDateTime, \
                 CounterDiskIssues, CounterDiskDateTime, CounterFMIssues, CounterFMDateTime, CounterPrinterIssues, CounterPrinterDateTime, \
                 CounterVATChanges, CounterVATDateTime):
        self.Znum                   = Znum                      # operational mode, 0=idle in sales, 1=open day, receipts are done, 2=in menu, 3=in reports, 4=in programming, 5=demo mode
        self.ZTimeStamp             = ZTimeStamp                # the time stamp when this system state record was taken
        self.Zdate                  = Zdate                     # date derived from the ZTimeStamp above
        self.Ztime                  = Ztime                     # time derived from the ZTimeStamp above
        self.FromInvNum             = FromInvNum                # FROM… INVOICE accumulated number in this Z
        self.ToInvNum               = ToInvNum                  # TO…. INVOICE accumulated number in this Z
        self.FromRecNum             = FromRecNum                # FROM…RECEIPT accumulated number in this Z
        self.ToRecNum               = ToRecNum                  # TO …  RECEIPT accumulated number in this Z
        self.UploadTimeStamp        = UploadTimeStamp           # When upload happens, the time of the upload is registered here as UploadTimeStamp
        self.UploadDate             = UploadDate                # date derived from the UploadTimeStamp
        self.UploadTime             = UploadTime                # the time derived…
        self.UploadError            = UploadError               # If an error was received from server, it is stored here or 0 for OK
        self.LastZUploadTStamp      = LastZUploadTStamp         # the time stamp of the latest previous upload
        self.ZTotalPcs              = ZTotalPcs                 # Total pieces if goods are counted in pieces within this Z period
        self.ZTotalQty              = ZTotalQty                 # total quantity in Kgr within this Z period
        self.ZTotalInvCount         = ZTotalInvCount            # the number of B2B or B2G INCOICES issued within this Z
        self.ZTotalInvAmnt          = ZTotalInvAmnt             # the total amount of invoices
        self.ZTotalCreditNotesCount = ZTotalCreditNotesCount    # the number of B2B or B2G CREDIT NOTES issued in this Z
        self.ZTotalCredNotesAmnt    = ZTotalCredNotesAmnt       # the total amount in CREDIT NOTES
        self.ZTotalReceiptsCount    = ZTotalReceiptsCount       # the number of total receipts in Z
        self.ZTotalRecAmnt          = ZTotalRecAmnt             # the total amount in receipts
        self.ZTotalDiscountCount    = ZTotalDiscountCount       # number of discounts given in this Z
        self.ZTotalDiscountAmnt     = ZTotalDiscountAmnt        # the amount corresponding to those discounts
        self.ZTotalMarkupUpCount    = ZTotalMarkupUpCount       # the number of markups given in this Z
        self.ZTotalMarkupUpAmnt     = ZTotalMarkupUpAmnt        # the total amount in markups
        self.ZTotalRefundsCount     = ZTotalRefundsCount        # how many refunds were made
        self.ZTotalRefundsAmnt      = ZTotalRefundsAmnt         # the  value of all refunds
        self.ZTotalTicketsCount     = ZTotalTicketsCount        # how many tickets were accepted
        self.ZTotalTicketsAmnt      = ZTotalTicketsAmnt         # value of those tickets
        self.ZTotalCouponCount      = ZTotalCouponCount         # how many coupons were accepted
        self.ZTotalCouponAmnt       = ZTotalCouponAmnt          # value of those coupons
        self.ZGrandTotal            = ZGrandTotal               # This is the grand grand total of all totals, invoices, receipts, everything, the Zs turn over
        self.InDrawerCash           = InDrawerCash              # CASH in the drawer this Z
        self.InDrawerPayCodeA       = InDrawerPayCodeA          # PAYCodeA in drawer
        self.InDrawerPayDescrA      = InDrawerPayDescrA         # PAYCodeADescription in drawer
        self.InDrawerPayAmntA       = InDrawerPayAmntA          # PAYCodeAAmount in drawer
        self.InDrawerPayCodeB       = InDrawerPayCodeB          # PAYCodeA in drawer
        self.InDrawerPayDescrB      = InDrawerPayDescrB         # PAYCodeADescription in drawer
        self.InDrawerPayAmntB       = InDrawerPayAmntB          # PAYCodeAAmount in drawer
        self.InDrawerPayCodeC       = InDrawerPayCodeC          # PAYCodeA in drawer
        self.InDrawerPayDescrC      = InDrawerPayDescrC         # PAYCodeADescription in drawer
        self.InDrawerPayAmntC       = InDrawerPayAmntC          # PAYCodeAAmount in drawer
        self.InDrawerPayCodeD       = InDrawerPayCodeD          # PAYCodeA in drawer
        self.InDrawerPayDescrD      = InDrawerPayDescrD         # PAYCodeADescription in drawer
        self.InDrawerPayAmntD       = InDrawerPayAmntD          # PAYCodeAAmount in drawer
        self.InDrawerPayCodeE       = InDrawerPayCodeE          # PAYCodeA in drawer
        self.InDrawerPayDescrE      = InDrawerPayDescrE         # PAYCodeADescription in drawer
        self.InDrawerPayAmntE       = InDrawerPayAmntE          # PAYCodeAAmount in drawer
        self.InDrawerCheckCount     = InDrawerCheckCount        # Special count for checks received in this Z
        self.InDrawerCheckAmnt      = InDrawerCheckAmnt         # total amount in checks received
        self.InDrawerCoinCode       = InDrawerCoinCode          # foreign currency code or cryptocurrency whatever
        self.InDrawerCoinDesc       = InDrawerCoinDesc          # foreign currency description or cryptocurrency name
        self.InDrawerCoinAmnt       = InDrawerCoinAmnt          # foreign currency or crypto amount
        self.ZCashInCount           = ZCashInCount              # how many Cash Ins?
        self.ZCashInAmnt            = ZCashInAmnt               # total amount of Cash Ins?
        self.ZCashOutCount          = ZCashOutCount             # how many Cash Outs?
        self.ZCashOutAmnt           = ZCashOutAmnt              # total amount of Cash Out
        self.VoidsCount             = VoidsCount                # how many immediate voids?
        self.VoidsAmnt              = VoidsAmnt                 # total amount of im. Voids?
        self.PreVoidsCount          = PreVoidsCount             # how many previous voids?
        self.PreVoidsAmnt           = PreVoidsAmnt              # total amount of prev. voids?
        self.CancelCount            = CancelCount               # how many total cancelations?
        self.CancelAmnt             = CancelAmnt                # total amount of canceled receipts?
        self.LoyaltyCount           = LoyaltyCount              # how many issues of loyalty points?
        self.LoyaltyPoints          = LoyaltyPoints             # total of loyalty points
        self.ChangeVATAfrom         = ChangeVATAfrom            # if changes to VAT or TAX rates or amounts happen, register from … to values here
        self.ChangeVATAto           = ChangeVATAto  #
        self.ChangeVATBfrom         = ChangeVATBfrom  #
        self.ChangeVATBto           = ChangeVATBto  #
        self.ChangeVATCfrom         = ChangeVATCfrom  #
        self.ChangeVATCto           = ChangeVATCto  #
        self.ChangeVATDfrom         = ChangeVATDfrom  #
        self.ChangeVATDto           = ChangeVATDto  #
        self.ChangeVATEfrom         = ChangeVATEfrom  #
        self.ChangeVATEto           = ChangeVATEto  #
        self.ChangeTAXfrom          = ChangeTAXfrom  #
        self.ChangeTAXto            = ChangeTAXto  #
        self.ACurrentRate           = ACurrentRate              # Current rate for VAT A applied to this Z period. If there is a change in rates, it is done on day open
        self.AGrossTotal            = AGrossTotal               # Gross (VAT inclusive) total turnover for this Z period
        self.ATaxableTot            = ATaxableTot               # Net (VAT exclusive) total turnover for this Z period
        self.ATaxTotal              = ATaxTotal                 # Total VAT amount for rate A for this Z period
        self.BCurrentRate           = BCurrentRate              # Current rate for VAT B applied to this Z period. If there is a change in rates, it is done on day open
        self.BGrossTotal            = BGrossTotal               # Gross (VAT inclusive) total turnover for this Z period
        self.BTaxableTot            = BTaxableTot               # Net (VAT exclusive) total turnover for this Z period
        self.BTaxTotal              = BTaxTotal                 # Total VAT amount for rate B for this Z period
        self.CCurrentRate           = CCurrentRate              # Current rate for VAT C applied to this Z period. If there is a change in rates, it is done on day open
        self.CGrossTotal            = CGrossTotal               # Gross (VAT inclusive) total turnover for this Z period
        self.CTaxableTot            = CTaxableTot               # Net (VAT exclusive) total turnover for this Z period
        self.CTaxTotal              = CTaxTotal                 # Total VAT amount for rate C for this Z period
        self.DCurrentRate           = DCurrentRate              # Current rate for VAT C applied to this Z period. If there is a change in rates, it is done on day open
        self.DGrossTotal            = DGrossTotal               # Gross (VAT inclusive) total turnover for this Z period
        self.DTaxableTot            = DTaxableTot               # Net (VAT exclusive) total turnover for this Z period
        self.DTaxTotal              = DTaxTotal                 # Total VAT amount for rate D for this Z period
        self.ECurrentRate           = ECurrentRate              # Current rate for VAT E applied to this Z period. If there is a change in rates, it is done on day open
        self.EGrossTotal            = EGrossTotal               # Gross (VAT inclusive) total turnover for this Z period
        self.ETaxableTot            = ETaxableTot               # Net (VAT exclusive) total turnover for this Z period
        self.ETaxTotal              = ETaxTotal                 # Total VAT amount for rate E for this Z period
        self.TCurrentRate           = TCurrentRate              # Current rate for other TAX applied to this Z period. If there is a change in rates, it is done on day open
        self.TGrossTotal            = TGrossTotal               # Gross (TAX inclusive) total turnover for this Z period
        self.TTaxableTot            = TTaxableTot               # Net (TAX exclusive) total turnover for this Z period
        self.TTaxTotal              = TTaxTotal                 # Total TAX amount for OTHER TAX for this Z period
        self.CounterHeaderChanges   = CounterHeaderChanges      # how many times the header has changed
        self.CounterResets          = CounterResets             # "RESET" in our system means that there is a DELETION OF JOURNAL RECORDS, because of some errors in the data?
        self.CounterResetDateTime   = CounterResetDateTime      # date and time last "RESET" was done
        self.CounterService         = CounterService            # service technician has done something and entered his password
        self.CounterServiceDateTime = CounterServiceDateTime    # the date and time this has happened within this period or the last date and time this has happened
        self.CounterRTCChanges      = CounterRTCChanges         # any RTC settings by service
        self.CounterRTCDateTime     = CounterRTCDateTime        # the last date/time of this
        self.CounterDiskIssues      = CounterDiskIssues         # we don't have internal SD, we have flash disk - this counter doesn't make much sense, let's have it
        self.CounterDiskDateTime    = CounterDiskDateTime       # the last date/time of this
        self.CounterFMIssues        = CounterFMIssues           # counts FM disconnections
        self.CounterFMDateTime      = CounterFMDateTime         # last date/time of this
        self.CounterPrinterIssues   = CounterPrinterIssues      # the idiotic printer disconnection is here
        self.CounterPrinterDateTime = CounterPrinterDateTime    # the last date/time of this
        self.CounterVATChanges      = CounterVATChanges         # counts changes in VAT rates
        self.CounterVATDateTime     = CounterVATDateTime        # the last date/time of this

    def XZReportsRead(self,Z):
        global J
        # This will return the XZ records of Z number Z: here Z is the PENDING Z number so before the Z is issued this represents the X (current) totals
        # Each Z num is UNIQUE, there is only ONE RECORD for each Z period and we therefore ADD UP / TOTALIZE every field here
        J.execute("SELECT * FROM XZReports WHERE Znum=?);",(Z,))
        ListFetchOne = J.fetchone()

        self.Znum                   = ListFetchOne[0]           # operational mode, 0=idle in sales, 1=open day, receipts are done, 2=in menu, 3=in reports, 4=in programming, 5=demo mode
        self.ZTimeStamp             = ListFetchOne[1]           # the time stamp when this system state record was taken
        self.Zdate                  = ListFetchOne[2]           # date derived from the ZTimeStamp above
        self.Ztime                  = ListFetchOne[3]           # time derived from the ZTimeStamp above
        self.FromInvNum             = ListFetchOne[4]           # FROM… INVOICE accumulated number in this Z
        self.ToInvNum               = ListFetchOne[5]           # TO…. INVOICE accumulated number in this Z
        self.FromRecNum             = ListFetchOne[6]           # FROM…RECEIPT accumulated number in this Z
        self.ToRecNum               = ListFetchOne[7]           # TO …  RECEIPT accumulated number in this Z
        self.UploadTimeStamp        = ListFetchOne[8]           # When upload happens, the time of the upload is registered here as UploadTimeStamp
        self.UploadDate             = ListFetchOne[9]           # date derived from the UploadTimeStamp
        self.UploadTime             = ListFetchOne[10]          # the time derived…
        self.UploadError            = ListFetchOne[11]          # If an error was received from server, it is stored here or 0 for OK
        self.LastZUploadTStamp      = ListFetchOne[12]          # the time stamp of the latest previous upload
        self.ZTotalPcs              = ListFetchOne[13]          # Total pieces if goods are counted in pieces within this Z period
        self.ZTotalQty              = ListFetchOne[14]          # total quantity in Kgr within this Z period
        self.ZTotalInvCount         = ListFetchOne[15]          # the number of B2B or B2G INCOICES issued within this Z
        self.ZTotalInvAmnt          = ListFetchOne[16]          # the total amount of invoices
        self.ZTotalCreditNotesCount = ListFetchOne[17]          # the number of B2B or B2G CREDIT NOTES issued in this Z
        self.ZTotalCredNotesAmnt    = ListFetchOne[18]          # the total amount in CREDIT NOTES
        self.ZTotalReceiptsCount    = ListFetchOne[19]          # the number of total receipts in Z
        self.ZTotalRecAmnt          = ListFetchOne[20]          # the total amount in receipts
        self.ZTotalDiscountCount    = ListFetchOne[21]          # number of discounts given in this Z
        self.ZTotalDiscountAmnt     = ListFetchOne[22]          # the amount corresponding to those discounts
        self.ZTotalMarkupUpCount    = ListFetchOne[23]          # the number of markups given in this Z
        self.ZTotalMarkupUpAmnt     = ListFetchOne[24]          # the total amount in markups
        self.ZTotalRefundsCount     = ListFetchOne[25]          # how many refunds were made
        self.ZTotalRefundsAmnt      = ListFetchOne[26]          # the  value of all refunds
        self.ZTotalTicketsCount     = ListFetchOne[27]          # how many tickets were accepted
        self.ZTotalTicketsAmnt      = ListFetchOne[28]          # value of those tickets
        self.ZTotalCouponCount      = ListFetchOne[29]          # how many coupons were accepted
        self.ZTotalCouponAmnt       = ListFetchOne[30]          # value of those coupons
        self.ZGrandTotal            = ListFetchOne[31]          # This is the grand grand total of all totals, invoices, receipts, everything, the Zs turn over
        self.InDrawerCash           = ListFetchOne[32]          # CASH in the drawer this Z
        self.InDrawerPayCodeA       = ListFetchOne[33]          # PAYCodeA in drawer
        self.InDrawerPayDescrA      = ListFetchOne[34]          # PAYCodeADescription in drawer
        self.InDrawerPayAmntA       = ListFetchOne[35]          # PAYCodeAAmount in drawer
        self.InDrawerPayCodeB       = ListFetchOne[36]          # PAYCodeA in drawer
        self.InDrawerPayDescrB      = ListFetchOne[37]          # PAYCodeADescription in drawer
        self.InDrawerPayAmntB       = ListFetchOne[38]          # PAYCodeAAmount in drawer
        self.InDrawerPayCodeC       = ListFetchOne[39]          # PAYCodeA in drawer
        self.InDrawerPayDescrC      = ListFetchOne[40]          # PAYCodeADescription in drawer
        self.InDrawerPayAmntC       = ListFetchOne[41]          # PAYCodeAAmount in drawer
        self.InDrawerPayCodeD       = ListFetchOne[42]          # PAYCodeA in drawer
        self.InDrawerPayDescrD      = ListFetchOne[43]          # PAYCodeADescription in drawer
        self.InDrawerPayAmntD       = ListFetchOne[44]          # PAYCodeAAmount in drawer
        self.InDrawerPayCodeE       = ListFetchOne[45]          # PAYCodeA in drawer
        self.InDrawerPayDescrE      = ListFetchOne[46]          # PAYCodeADescription in drawer
        self.InDrawerPayAmntE       = ListFetchOne[47]          #  PAYCodeAAmount in drawer
        self.InDrawerCheckCount     = ListFetchOne[48]          # Special count for checks received in this Z
        self.InDrawerCheckAmnt      = ListFetchOne[49]          # total amount in checks received
        self.InDrawerCoinCode       = ListFetchOne[50]          # foreign currency code or cryptocurrency whatever
        self.InDrawerCoinDesc       = ListFetchOne[51]          # foreign currency description or cryptocurrency name
        self.InDrawerCoinAmnt       = ListFetchOne[52]          # foreign currency or crypto amount
        self.ZCashInCount           = ListFetchOne[53]          # how many Cash Ins?
        self.ZCashInAmnt            = ListFetchOne[54]          # total amount of Cash Ins?
        self.ZCashOutCount          = ListFetchOne[55]          # how many Cash Outs?
        self.ZCashOutAmnt           = ListFetchOne[56]          # total amount of Cash Out
        self.VoidsCount             = ListFetchOne[57]          # how many immediate voids?
        self.VoidsAmnt              = ListFetchOne[58]          # total amount of im. Voids?
        self.PreVoidsCount          = ListFetchOne[59]          # how many previous voids?
        self.PreVoidsAmnt           = ListFetchOne[60]          # total amount of prev. voids?
        self.CancelCount            = ListFetchOne[61]          # how many total cancelations?
        self.CancelAmnt             = ListFetchOne[62]          # total amount of canceled receipts?
        self.LoyaltyCount           = ListFetchOne[63]          # how many issues of loyalty points?
        self.LoyaltyPoints          = ListFetchOne[64]          # total of loyalty points
        self.ChangeVATAfrom         = ListFetchOne[65]          # if changes to VAT or TAX rates or amounts happen, register from … to values here
        self.ChangeVATAto           = ListFetchOne[66]          #
        self.ChangeVATBfrom         = ListFetchOne[67]          #
        self.ChangeVATBto           = ListFetchOne[68]          #
        self.ChangeVATCfrom         = ListFetchOne[69]          #
        self.ChangeVATCto           = ListFetchOne[70]          #
        self.ChangeVATDfrom         = ListFetchOne[71]          #
        self.ChangeVATDto           = ListFetchOne[72]          #
        self.ChangeVATEfrom         = ListFetchOne[73]          #
        self.ChangeVATEto           = ListFetchOne[74]          #
        self.ChangeTAXfrom          = ListFetchOne[75]          #
        self.ChangeTAXto            = ListFetchOne[76]          #
        self.ACurrentRate           = ListFetchOne[77]          # Current rate for VAT A applied to this Z period. If there is a change in rates, it is done on day open
        self.AGrossTotal            = ListFetchOne[78]          # Gross (VAT inclusive) total turnover for this Z period
        self.ATaxableTot            = ListFetchOne[79]          # Net (VAT exclusive) total turnover for this Z period
        self.ATaxTotal              = ListFetchOne[80]          # Total VAT amount for rate A for this Z period
        self.BCurrentRate           = ListFetchOne[81]          # Current rate for VAT B applied to this Z period. If there is a change in rates, it is done on day open
        self.BGrossTotal            = ListFetchOne[82]          # Gross (VAT inclusive) total turnover for this Z period
        self.BTaxableTot            = ListFetchOne[83]          # Net (VAT exclusive) total turnover for this Z period
        self.BTaxTotal              = ListFetchOne[84]          # Total VAT amount for rate B for this Z period
        self.CCurrentRate           = ListFetchOne[85]          # Current rate for VAT C applied to this Z period. If there is a change in rates, it is done on day open
        self.CGrossTotal            = ListFetchOne[86]          # Gross (VAT inclusive) total turnover for this Z period
        self.CTaxableTot            = ListFetchOne[87]          # Net (VAT exclusive) total turnover for this Z period
        self.CTaxTotal              = ListFetchOne[88]          # Total VAT amount for rate C for this Z period
        self.DCurrentRate           = ListFetchOne[89]          # Current rate for VAT C applied to this Z period. If there is a change in rates, it is done on day open
        self.DGrossTotal            = ListFetchOne[90]          # Gross (VAT inclusive) total turnover for this Z period
        self.DTaxableTot            = ListFetchOne[91]          # Net (VAT exclusive) total turnover for this Z period
        self.DTaxTotal              = ListFetchOne[92]          # Total VAT amount for rate D for this Z period
        self.ECurrentRate           = ListFetchOne[93]          # Current rate for VAT E applied to this Z period. If there is a change in rates, it is done on day open
        self.EGrossTotal            = ListFetchOne[94]          # Gross (VAT inclusive) total turnover for this Z period
        self.ETaxableTot            = ListFetchOne[95]          # Net (VAT exclusive) total turnover for this Z period
        self.ETaxTotal              = ListFetchOne[96]          # Total VAT amount for rate E for this Z period
        self.TCurrentRate           = ListFetchOne[97]          # Current rate for other TAX applied to this Z period. If there is a change in rates, it is done on day open
        self.TGrossTotal            = ListFetchOne[98]          # Gross (TAX inclusive) total turnover for this Z period
        self.TTaxableTot            = ListFetchOne[99]          # Net (TAX exclusive) total turnover for this Z period
        self.TTaxTotal              = ListFetchOne[100]         # Total TAX amount for OTHER TAX for this Z period
        self.CounterHeaderChanges   = ListFetchOne[101]         # how many times the header has changed
        self.CounterResets          = ListFetchOne[102]         # "RESET" in our system means that there is a DELETION OF JOURNAL RECORDS, because of some errors in the data?
        self.CounterResetDateTime   = ListFetchOne[103]         # date and time last "RESET" was done
        self.CounterService         = ListFetchOne[104]         # service technician has done something and entered his password
        self.CounterServiceDateTime = ListFetchOne[105]         # the date and time this has happened within this period or the last date and time this has happened
        self.CounterRTCChanges      = ListFetchOne[106]         # any RTC settings by service
        self.CounterRTCDateTime     = ListFetchOne[107]         # the last date/time of this
        self.CounterDiskIssues      = ListFetchOne[108]         # we don't have internal SD, we have flash disk - this counter doesn't make much sense, let's have it
        self.CounterDiskDateTime    = ListFetchOne[109]         # the last date/time of this
        self.CounterFMIssues        = ListFetchOne[110]         # counts FM disconnections
        self.CounterFMDateTime      = ListFetchOne[111]         # last date/time of this
        self.CounterPrinterIssues   = ListFetchOne[112]         # the idiotic printer disconnection is here
        self.CounterPrinterDateTime = ListFetchOne[113]         # the last date/time of this
        self.CounterVATChanges      = ListFetchOne[114]         # counts changes in VAT rates
        self.CounterVATDateTime     = ListFetchOne[115]         # the last date/time of this

    def XReportsWrite(self):
        global J
        J.execute(
            """"INSERT INTO InvoiceLines VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""",
            (self.Znum, self.ZTimeStamp, self.Zdate, self.Ztime, self.FromInvNum, self.ToInvNum, self.FromRecNum, self.ToRecNum, self.UploadTimeStamp, self.UploadDate,
             self.UploadTime, self.UploadError, self.LastZUploadTStamp, self.ZTotalPcs, self.ZTotalQty, self.ZTotalInvCount, self.ZTotalInvAmnt, self.ZTotalCreditNotesCount,
             self.ZTotalCredNotesAmnt, self.ZTotalReceiptsCount, self.ZTotalRecAmnt, self.ZTotalDiscountCount, self.ZTotalDiscountAmnt, self.ZTotalMarkupUpCount,
             self.ZTotalMarkupUpAmnt, self.ZTotalRefundsCount, self.ZTotalRefundsAmnt, self.ZTotalTicketsCount, self.ZTotalTicketsAmnt, self.ZTotalCouponCount,
             self.ZTotalCouponAmnt, self.ZGrandTotal, self.InDrawerCash, self.InDrawerPayCodeA, self.InDrawerPayDescrA, self.InDrawerPayAmntA, self.InDrawerPayCodeB,
             self.InDrawerPayDescrB, self.InDrawerPayAmntB, self.InDrawerPayCodeC, self.InDrawerPayDescrC, self.InDrawerPayAmntC, self.InDrawerPayCodeD, self.InDrawerPayDescrD,
             self.InDrawerPayAmntD, self.InDrawerPayCodeE, self.InDrawerPayDescrE, self.InDrawerPayAmntE, self.InDrawerCheckCount, self.InDrawerCheckAmnt, self.InDrawerCoinCode,
             self.InDrawerCoinDesc, self.InDrawerCoinAmnt, self.ZCashInCount, self.ZCashInAmnt, self.ZCashOutCount, self.ZCashOutAmnt, self.VoidsCount, self.VoidsAmnt,
             self.PreVoidsCount, self.PreVoidsAmnt, self.CancelCount, self.CancelAmnt, self.LoyaltyCount, self.LoyaltyPoints, self.ChangeVATAfrom, self.ChangeVATAto,
             self.ChangeVATBfrom, self.ChangeVATBto, self.ChangeVATCfrom, self.ChangeVATCto, self.ChangeVATDfrom, self.ChangeVATDto, self.ChangeVATEfrom, self.ChangeVATEto,
             self.ChangeTAXfrom, self.ChangeTAXto, self.ACurrentRate, self.AGrossTotal, self.ATaxableTot, self.ATaxTotal, self.BCurrentRate, self.BGrossTotal, self.BTaxableTot,
             self.BTaxTotal, self.CCurrentRate, self.CGrossTotal, self.CTaxableTot, self.CTaxTotal, self.DCurrentRate, self.DGrossTotal, self.DTaxableTot, self.DTaxTotal,
             self.ECurrentRate, self.EGrossTotal, self.ETaxableTot, self.ETaxTotal, self.TCurrentRate, self.TGrossTotal, self.TTaxableTot, self.TTaxTotal,
             self.CounterHeaderChanges, self.CounterResets, self.CounterResetDateTime, self.CounterService, self.CounterServiceDateTime, self.CounterRTCChanges,
             self.CounterRTCDateTime, self.CounterDiskIssues, self.CounterDiskDateTime, self.CounterFMIssues, self.CounterFMDateTime, self.CounterPrinterIssues,
             self.CounterPrinterDateTime, self.CounterVATChanges, self.CounterVATDateTime,))
        JOURN.commit()  # it is JOURN.commit() and NOT J.commit(): commit() is a connection function, and J is the CURSOR, JOURN is the connection
        # read sqlite.org/faq about speed of INSERTs
        # https://stackoverflow.com/questions/1711631/improve-insert-per-second-performance-of-sqlite


#===============================================================================================================================
#================   XZDptsCategs
#===============================================================================================================================
class XZDpts(object):
    def __init__(self,Znum, ZTimeStamp, DptCode, DptDesc, VATRate, TotalAmnt, TotalQtyPcs, TotalQtyKgr, TotalRefundsQty, TotalRefundsNum, \
                 TotalPreTax, TotalTax, CatCode, CatDescr, CatTotAmnt, CatTotPcs, CatTotKgrs, CatTotRefNum, CatTotRefAmnt):
        self.Znum                   = Znum                      # the Z number, KEY to journal.Zreports table
        self.ZTimeStamp             = ZTimeStamp                # the time stamp when this system state record was taken - holds 999 if Z is PENDING (not issued yet)
        self.DptCode                = DptCode                   # department code nn
        self.DptDesc                = DptDesc                   # department description
        self.VATRate                = VATRate                   # the VAT rate assigned to this DPT in the period covered by this Z in %
        self.TotalAmnt              = TotalAmnt                 # the total amount paid in this dpt during period of this Z
        self.TotalQtyPcs            = TotalQtyPcs               # total qty in pieces
        self.TotalQtyKgr            = TotalQtyKgr               # total qty in Kgrs
        self.TotalRefundsQty        = TotalRefundsQty           # how many refunds were made in this DPT
        self.TotalRefundsNum        = TotalRefundsNum           # the total value of these refunds
        self.TotalPreTax            = TotalPreTax               # the pre-tax (taxable) total amount
        self.TotalTax               = TotalTax                  # the total tax amount = pre-tax X 1.VAT%
        self.CatCode                = CatCode                   # category code cc - categories contain mixed VAT products so we are NOT calculating tax totals and we are NOT do taxable totals
        self.CatDescr               = CatDescr                  # category description
        self.CatTotAmnt             = CatTotAmnt                # the total amount paid in for goods or dpts belonging to this category
        self.CatTotPcs              = CatTotPcs                 # total quantity in pieces sold under this category
        self.CatTotKgrs             = CatTotKgrs                # total quantity in kgrs sold under this category
        self.CatTotRefNum           = CatTotRefNum              # how many refunds were made in this category
        self.CatTotRefAmnt          = CatTotRefAmnt             # the total amount of refunds in this category


    def XZDptsReadDPT(self,Z,DPT):
        global J
        # The XZDpts table has MULTIPLE records for the SAME Z because every DPT CODE that was sold and every CAT CODE that was sold creates a NEW RECORD
        # So by fetching based on Z we get MULTIPLE records, one for DPT01, one for DPT09 (if 01 and 09 were sold) etc.
        # to fetch JUST ONE you need to specify BOTH the Znumber and DPT, which is then unique

        J.execute("SELECT * FROM XZDptsCategs WHERE Znum=? AND DptCode=?);",(Z, DPT,))
        ListFetchOne = J.fetchone()
        self.Znum                   = ListFetchOne[0]           # the Z number, KEY to journal.Zreports table
        self.ZTimeStamp             = ListFetchOne[1]           # the time stamp when this system state record was taken - holds 999 if Z is PENDING (not issued yet)
        self.DptCode                = ListFetchOne[2]           # department code nn
        self.DptDesc                = ListFetchOne[3]           # department description
        self.VATRate                = ListFetchOne[4]           # the VAT rate assigned to this DPT in the period covered by this Z in %
        self.TotalAmnt              = ListFetchOne[5]           # the total amount paid in this dpt during period of this Z
        self.TotalQtyPcs            = ListFetchOne[6]           # total qty in pieces
        self.TotalQtyKgr            = ListFetchOne[7]           # total qty in Kgrs
        self.TotalRefundsQty        = ListFetchOne[8]           # how many refunds were made in this DPT
        self.TotalRefundsNum        = ListFetchOne[9]           # the total value of these refunds
        self.TotalPreTax            = ListFetchOne[10]          # the pre-tax (taxable) total amount
        self.TotalTax               = ListFetchOne[11]          # the total tax amount = pre-tax X 1.VAT%
        self.CatCode                = ListFetchOne[12]          # category code cc - categories contain mixed VAT products so we are NOT calculating tax totals and we are NOT do taxable totals
        self.CatDescr               = ListFetchOne[13]          # category description
        self.CatTotAmnt             = ListFetchOne[14]          # the total amount paid in for goods or dpts belonging to this category
        self.CatTotPcs              = ListFetchOne[15]          # total quantity in pieces sold under this category
        self.CatTotKgrs             = ListFetchOne[16]          # total quantity in kgrs sold under this category
        self.CatTotRefNum           = ListFetchOne[17]          # how many refunds were made in this category
        self.CatTotRefAmnt          = ListFetchOne[18]          # the total amount of refunds in this category

    def XZDptsReadCAT(self, Z, CAT):
        global J
        # The XZDpts table has MULTIPLE records for the SAME Z because every DPT CODE that was sold and every CAT CODE that was sold creates a NEW RECORD
        # So by fetching based on Z we get MULTIPLE records, one for DPT01, one for DPT09 (if 01 and 09 were sold) etc.
        # to fetch JUST ONE you need to specify BOTH the Znumber and CATEGORY, which is then unique

        J.execute("SELECT * FROM XZDptsCategs WHERE Znum=? AND CatCode=?);",(Z, CAT,))
        ListFetchOne = J.fetchone()
        self.Znum                   = ListFetchOne[0]           # the Z number, KEY to journal.Zreports table
        self.ZTimeStamp             = ListFetchOne[1]           # the time stamp when this system state record was taken - holds 999 if Z is PENDING (not issued yet)
        self.DptCode                = ListFetchOne[2]           # department code nn
        self.DptDesc                = ListFetchOne[3]           # department description
        self.VATRate                = ListFetchOne[4]           # the VAT rate assigned to this DPT in the period covered by this Z in %
        self.TotalAmnt              = ListFetchOne[5]           # the total amount paid in this dpt during period of this Z
        self.TotalQtyPcs            = ListFetchOne[6]           # total qty in pieces
        self.TotalQtyKgr            = ListFetchOne[7]           # total qty in Kgrs
        self.TotalRefundsQty        = ListFetchOne[8]           # how many refunds were made in this DPT
        self.TotalRefundsNum        = ListFetchOne[9]           # the total value of these refunds
        self.TotalPreTax            = ListFetchOne[10]          # the pre-tax (taxable) total amount
        self.TotalTax               = ListFetchOne[11]          # the total tax amount = pre-tax X 1.VAT%
        self.CatCode                = ListFetchOne[12]          # category code cc - categories contain mixed VAT products so we are NOT calculating tax totals and we are NOT do taxable totals
        self.CatDescr               = ListFetchOne[13]          # category description
        self.CatTotAmnt             = ListFetchOne[14]          # the total amount paid in for goods or dpts belonging to this category
        self.CatTotPcs              = ListFetchOne[15]          # total quantity in pieces sold under this category
        self.CatTotKgrs             = ListFetchOne[16]          # total quantity in kgrs sold under this category
        self.CatTotRefNum           = ListFetchOne[17]          # how many refunds were made in this category


    def XZDptsWrite(self):
        global J
        J.execute("INSERT INTO XZDptsCategs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", (
        self.Znum, self.ZTimeStamp, self.DptCode, self.DptDesc, self.VATRate, self.TotalAmnt, self.TotalQtyPcs, self.TotalQtyKgr, self.TotalRefundsQty, self.TotalRefundsNum,
        self.TotalPreTax, self.TotalTax, self.CatCode, self.CatDescr, self.CatTotAmnt, self.CatTotPcs, self.CatTotKgrs, self.CatTotRefNum, self.CatTotRefAmnt,))
        JOURN.commit()
        # PROSOXH:  To have UNIQUE records for Z, DPT and Z, CAT we need to UPDATE the records, not just keep inserting records.
        # PROSOXH:  the same holds for most, we do not do INSERT new rows all the time but UPDATE existing ones.
        # PROSOXH:  I DO NOT HAVE UPDATE FUNCTIONS!!!!

