import sqlite3
from sqlite3 import Error


#=======================================================================================================================
#=======================    ACCESS THE TWO DATABASES: STATIC AND JOURNAL     ===========================================
# dbStatic='C:\\000 WORK 2017\\2 general\\00 2018 Tevin\\OUR ETR\\CharmSources\\static.sqlite'
# dbJournal='C:\\000 WORK 2017\\2 general\\00 2018 Tevin\\OUR ETR\\CharmSources\\journal.sqlite'
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
# this is the SUMMARY OF ONE CLOSED OR CANCELED RECEIPT OR INVOICE
# this is opened and numbered in Znum, DocNum and DocNumAccum the moment one valid keyboard entry comes in
# WE KEEP THE OBJECT IN MEMORY AND WRITE TO journal.InvoiceId table ONLY AFTER IT IS CLOSED OR PFAIL HAPPENS

class InvoiceId(object):
    def __init__(self,Znum, DocNum, DocNumAccum, DocNumMiddleware, IsOpen, IsCancelled , InvType, InvCategory, RelatedNum, \
                 ClerkCode, ClerkName, TimeStamp, Date, Time, TimeStampTransm, PinOfBuyer, CustCode, CustName, CustType, \
                 CustDetails, Location, TotalPcs, TotalQty, TaxVatA, TaxVatB, TaxVatC, TaxVatD, TaxVatE, TaxVatExempt, \
                 TaxAux, TotalAmntBefDiscnt, TotalDiscnts, TotalAmountPayable, TotalAmntPbleCurB, \
                 CurrencyBRate, CoinQRforPayment, TotalTaxableA, TotalTaxableB, TotalTaxableC, TotalTaxableD, TotalTaxableE, \
                 TotalTax , Pay1Amnt, Pay1Descr, Change, Pay2Amnt, Pay2Descr, Pay3Amnt, Pay3Desc, CouponId, \
                 CouponAmnt, LoyaltyEarned, AmountOnCredit, CheckNum, DueDateforPayment, HashA, HashE, QRCode, \
                 HeaderCode, FooterCode, FullAText):
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

    # This will return the InvoiceId object from journal.InvoiceId
    # if parameter AccNum==999 it will fetch the LAST, CURRENT doc
    # for any other AccNum it will fetch the object with the specified DocNumAccum

    def ReadInvId(self,AccNum):
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





