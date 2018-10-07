# Module CheckIn.py accepts one by one the characters being input and checks for errors
# and then creates the Phrase object which is a SYNTACTICALLY correct single transaction line
# this Phrase object is then passed on to Execution.py module to be filled in from the sqlite
# checked against transaction rules, update everything  and then printed out

# IMPORTANT: you need to declare globals OUTSIDE AND INSIDE functions and then initialize them outside the function

#------------------------------------------------------------------------------------------------------------------------------
# NOTES NOTES NOTES NOTES NOTES NOTES NOTES NOTES NOTES NOTES NOTES NOTES NOTES NOTES NOTES NOTES NOTES NOTES NOTES NOTES NOTES
#------------------------------------------------------------------------------------------------------------------------------
# It is the job of the PROGRAM module to only allow VALID entries into databases: if I program a DPT, this DPT should be
# checked ON ENTRY for having correct VAT num for example. So if something is in the db, then it should be acceptable for calculations
# WHY? Because instead of checking up EVERY DPTnn coming in by opening the db, I will just load the MAX DPTnn programmed in and
# accept ANY incoming DPTnn if it is <= than the max in the dpt

# comment to test how it works with GitHub...

#11111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111
#111111                                      B E G I N                       1111111111111111111111111111111111

import sqlite3
from sqlite3 import Error
import Execution


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
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return None

STAT=create_connection(dbStatic)         # ++++++++++++++   static.sqlite
JOURN=create_connection(dbJournal)       # ++++++++++++++   journal.sqlite

global S
global J
S=STAT.cursor()
J=JOURN.cursor()
#==========================   SO J=THE CURSOR TO JOURNAL DATABASE AND S=THE CURSOR TO STATIC DB =========
# STATIC db contains data that don't change often: DPT descriptions, VAT, PLU table, parameters, error messages, print templates etc.
# JOURNAL db changes every time a new transaction happens or machine changes status: contains e-journal, current receipt, system state class

#======================================================================================================================
# This is SYSTEM STATE CLASS: it is supposed to hold all info necessary to recover operation after a system down
# SyState will be ONLY WRITTEN TO DB IN CASE OF POWER DOWN or POWER FAIL SIGNAL, not every time
# This class is stored in journal.sqlite as table "state" with the following columns:
class SyState(object):
    def __init__(self, OpMode, OpenRcpt, OpenRcptNum, OpenRcptTStamp, OpenDay, TStamp, LastZTStamp, LastZ, ShutDn, Poff, BatLow, RTCLow, FMerr, \
                 ClerkPerms, ClerkCode, PrnStat, WiFiStat, NetStat, DemoMode, Zpending):   # 20 columns
        self.OpMode         = OpMode        # 0 = in menu, standby in sales, 1=in REPORTS, 2= in PROGRAMMING
        self.OpenRcpt       = OpenRcpt      # 0 = no open receipt, 1=receipt is open
        self.OpenRcptNum    = OpenRcptNum   # NNNN = the accumulated receipt num
        self.OpenRcptTStamp = OpenRcptTStamp # this is the RECEIPT's timestamp which is used for ejournal storage and printed ON PAPER
        self.OpenDay        = OpenDay       # 0 = no open day, 1 = open day
        self.TStamp         = TStamp        # system's time stamp in integer seconds when this record is updated
        self.LastZTStamp    = LastZTStamp   # system's time stamp of the time last Z was taken
        self.LastZ          = LastZ         # Last Z's number, this is a FINISHED CORRECTLY Z - if Z is interrupted (flag Zpending=1) LastZ is NOT updated
        self.ShutDn         = ShutDn        # 0 = no shutdown has occured, 1 = system has just booted from shutdn
        self.Poff           = Poff          # 0 = no power failure signal detected, 1 = power failure was raised and system was shutdown
        self.BatLow         = BatLow        # 0 = main battery OK, 1 = main battery please charge, 2 = main battery depleted, stop
        self.RTCLow         = RTCLow        # 0 = RTC battery OK, 1 = RTC battery low
        self.FMerr          = FMerr         # 0 = No FM error, 1 = FM not detected, 2 = FM s/n invalid, 3 = FM read/write errors
        self.ClerkPerms     = ClerkPerms    # 0 = SALES no discnts/refunds, 1=all SALES, 2=Sales, X,  no Z - 3 = up to Z, 4 = GOD LEVEL, change time, erase...
        self.ClerkCode      = ClerkCode     # N where N = 1, 2, 3 etc active clerk code, enter 99 for clerk code capable of GOD LEVEL
        self.PrnStat        = PrnStat       # 0 = no error, 1 = PaperEnd, 2 = head up, 3 = overheat, 4 = disconnected
        self.WiFiStat       = WiFiStat      # 0 = connected OK, 1 = no network, 2 = cannot login, 3 = no internet access
        self.NetStat        = NetStat       # 0 = connected to internet, access to maintenance server, 1 = internet OK, no maint server, 2...
        self.DemoMode       = DemoMode      # 0 = normal fiscal operation, 1 = demo mode, do not write to FM, ignore all FM related errors
        self.Zpending       = Zpending      # 0 = no pending Z, last Z completed OK,  1 = Z not completed due to errors, needs to be re-printed

    def ReadCurStat(self):
        #IMPORTANT: to read into the object you have to do it one attribute at a time like self.attri=readlist[n]
        global J
        J.execute("SELECT * FROM state WHERE ROWID=(SELECT MAX(ROWID) FROM state)")
        LastState=J.fetchone()
        self.OpMode         = LastState[0]
        self.OpenRcpt       = LastState[1]              # 0 = no open receipt, 1=receipt is open
        self.OpenRcptNum    = LastState[2]               # NNNN = the accumulated receipt num
        self.OpenRcptTStamp = LastState[3]                # this is the RECEIPT's timestamp which is used for ejournal storage and printed ON PAPER
        self.OpenDay        = LastState[4]            # 0 = no open day, 1 = open day
        self.TStamp         = LastState[5]                # system's time stamp in integer seconds when this record is updated
        self.LastZTStamp    = LastState[6]           # system's time stamp of the time last Z was taken
        self.LastZ          = LastState[7]                 # Last Z's number, this is a FINISHED CORRECTLY Z - if Z is interrupted (flag Zpending=1) LastZ is NOT updated
        self.ShutDn         = LastState[8]                # 0 = no shutdown has occured, 1 = system has just booted from shutdn
        self.Poff           = LastState[9]                  # 0 = no power failure signal detected, 1 = power failure was raised and system was shutdown
        self.BatLow         = LastState[10]                # 0 = main battery OK, 1 = main battery please charge, 2 = main battery depleted, stop
        self.RTCLow         = LastState[11]                # 0 = RTC battery OK, 1 = RTC battery low
        self.FMerr          = LastState[12]                 # 0 = No FM error, 1 = FM not detected, 2 = FM s/n invalid, 3 = FM read/write errors
        self.ClerkPerms     = LastState[13]            # 0 = SALES no discnts/refunds, 1=all SALES, 2=Sales, X,  no Z - 3 = up to Z, 4 = GOD LEVEL, change time, erase...
        self.ClerkCode      = LastState[14]             # N where N = 1, 2, 3 etc active clerk code, enter 99 for clerk code capable of GOD LEVEL
        self.PrnStat        = LastState[15]               # 0 = no error, 1 = PaperEnd, 2 = head up, 3 = overheat, 4 = disconnected
        self.WiFiStat       = LastState[16]              # 0 = connected OK, 1 = no network, 2 = cannot login, 3 = no internet access
        self.NetStat        = LastState[17]               # 0 = connected to internet, access to maintenance server, 1 = internet OK, no maint server, 2...
        self.DemoMode       = LastState[18]              # 0 = normal fiscal operation, 1 = demo mode, do not write to FM, ignore all FM related errors
        self.Zpending       = LastState[19]             # 0 = no pending Z, last Z completed OK,  1 = Z not completed due to errors, needs to be re-printed
        return

    def SaveCurStat(self):
        global J
        J.execute("INSERT INTO state VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);",(self.OpMode, self.OpenRcpt, self.OpenRcptNum, self.OpenRcptTStamp, \
        self.OpenDay, self.TStamp, self.LastZTStamp, self.LastZ, self.ShutDn, self.Poff, self.BatLow, self.RTCLow, self.FMerr, \
        self.ClerkPerms, self.ClerkCode, self.PrnStat, self.WiFiStat, self.NetStat, self.DemoMode, self.Zpending))
        JOURN.commit() # it is JOURN.commit() and NOT J.commit(): commit() is a connection function, and J is the CURSOR, JOURN is the connection


        

global SystemState
SystemState=SyState(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)  #first you define the object and THEN you use the class function
SystemState.ReadCurStat()  # if you do NOT define SystemState as an instance of the SyState class, then you get error SystemState not defined (dah!)
# the ReadCurStat() function is a METHOD in the SyState class and therefore when called with an object of this class takes as arguments all the attributes of the object

print('This system state OpenRcpt flag is read from db:',SystemState.OpenRcpt)
#print('all attributes of an object',vars(SystemState))
#print('Open Receipt flag is=',dir(SystemState))





# ============================================================================================================================
# class ReceiptId contains top and end receipt parameters and totals
# Ammended 7 October 2018 to reflect KENYA TIMS requirements also, like Transmission Time Stamp (TStampTx), MiddleWareInvoiceNumber etc
# KENYA TIMS use JSON structure taken from TIMS Protocol to Server.xlsx from /ELZAB HELLAS/Africa/Kenya/0 K10

class ReceiptId(object):
    def __init__(self, Num, AccuNum, DocType, Z, Clerk, Station, TStamp, Date, Time, TStampTx, HashA, HashE, Approv, CustTIN, CustName, CustType,
                 CustAddr, GPS, Total, TotVATa, TotVATb, TotVATc, TotVATd, TotVATe, TotVATf, PayAcode, PayA, PayBcode, PayB, PayCcode, PayC, PayDcode, PayD):
        self.Num            = Num       # this is the daily number of receipt
        self.AccuNum        = AccuNum   # this is the accumulated number of receipt
        self.DocType        = DocType   # 0 = retail receipt, 1 = INVOICE, 2 = other
        self.Z              = Z         # this is the current Z number
        self.Clerk          = Clerk     # this is the code of active clerk who services this receipt
        self.Station        = Station   # the name given to the station entering the receipt
        self.TStamp         = TStamp    #TimeStamp of the system is the MAIN time used, with date and time DERIVED from TStamp
        self.Date           = Date      # current date to be printed on receipt
        self.Time           = Time      # time to be printed on receipt
        self.TStampTx       = TStampTx   # KENYA Date of Transmission in form of timestamp / this can be different from TStamp, which is the date of TRANSCACTION not transmission
        self.HashA          = HashA     # the SHA-1 or SHA-256 value of the receipt's data (_a.txt data)
        self.HashE          = HashE     # the SHA-1 value of the receipt's numerical data (_e.txt data)
        self.Approv         = Approv    # any approval code
        self.CustTIN        = CustTIN   # citizens card or customer's TIN or VAT num
        self.CustName       = CustName  # customer name / company
        self.CustType       = CustType  # customer type / sector / other
        self.CustAddr       = CustAddr  # customer address
        self.GPS            = GPS       # location via GPS or other
        self.Total          = Total     # the total of the receipt
        self.TotVATa        = TotVATa   # the VATA total
        self.TotVATb        = TotVATb   # the VATB total
        self.TotVATc        = TotVATc   # the VATC total
        self.TotVATd        = TotVATd   # the VATD total
        self.TotVATe        = TotVATe   # the VATE total
        self.TotVATf        = TotVATf   # the VATF total
        self.PayAcode       = PayAcode  # payment code A
        self.PayAcode       = PayA      # the amount paid under code A
        self.PayBcode       = PayBcode  # payment code B
        self.PayB           = PayB      # the amount paid under code B
        self.PayCcode       = PayCcode  # payment code C
        self.PayC           = PayC      # the amount paid under code C
        self.PayDcode       = PayDcode  # payment code D
        self.PayD           = PayD      # the amount paid under code D

global RcptIdentity
RcptIdentity=ReceiptId(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)


#=======================================================================================================================

# =================================================================================================================================
# class phrase contains a SINGLE TRANSACTION ENTRY with all necessary variables needed for this line to be COMPLETE (to make sense)
# This class is stored into log table for every transaction line
class phrase(object):
    def __init__(self, DocNum, LineNum, LineTransType, LineCommand, LineCmdId, LineQty1, LineQty2, LinePluCode, LinePluDesc, LineHSCode, LineHSDesc, \
                 LineDptCode, LineDptDesc, LineCat, LineUnitPrice, LineSubTotal, LineDiscPerc, LineDiscAm, LineUpPerc, LineUpAm, LineComment, \
                 LineQR, LineTotAmnt, LineTaxRate, LineAuxTax, LineTaxAmnt, LineTotTaxable, LinePlainText, Pay1Amnt, Pay1Descr, Pay2Amnt, Pay2Descr, \
                 Pay3Amnt, Pay3Descr, Pay4Amnt, Pay4Descr):
        self.DocNum                 = DocNum            # the number of the receipt to which this line belongs to
        self.LineNum                = LineNum           # this is the line number
        self.LineTransType          = LineTransType     # KENYA TIMS this is supposed to be 1 for normal, 2 void, 3 refund, 4 cancel
        self.LineCommand            = LineCommand       # for example T, E, R, ...
        self.LineCmdId              = LineCmdId         # the nn after command, 01 if T01 etc...
        self.LineQty1               = LineQty1          # the 123.456 quantity before X
        self.LineQty2               = LineQty2          # in case of double X in the transaction, like 5 cases of 12 bottles
        self.LinePluCode            = LinePluCode       # the barcode entered for PLU
        self.LinePluDesc            = LinePluDesc       # description of the PLU, either from database OR from host PC
        self.LineHSCode             = LineHSCode        # KENYA TIMS compatibility, HSDescription for the PLU
        self.LineHSDesc             = LineHSDesc        # KENYA TIMS compatibility
        self.LineDptCode            = LineDptCode       # the nn from Tnn
        self.LineDptDesc            = LineDptDesc       # dpt description
        self.LineCat                = LineCat           # category entry IF needed
        self.LineUnitPrice          = LineUnitPrice     # unit price
        self.LineSubTotal           = LineSubTotal      # is S command, calculates subtotal up to this line
        self.LineDiscPerc           = LineDiscPerc      # The % Discount - command ID will further dictate how to apply
        self.LineDiscAm             = LineDiscAm        # The amount of the discount
        self.LineUpPerc             = LineUpPerc        # The % markup
        self.LineUpAm               = LineUpAm          # amount markup

        self.LineComment            = LineComment       # the nn after command, 01 if T01 etc...
        self.LineQR                 = LineQR            # the QR code
        self.LineTotAmnt            = LineTotAmnt       # total amount for this line
        self.LineTaxRate            = LineTaxRate       # the tax rate as read from db via PLU or DPT
        self.LineAuxTax             = LineAuxTax        # some other tax possible - for example service tax or sales tax
        self.LineTaxAmnt            = LineTaxAmnt       # the  tax amount for this line
        self.LineTotTaxable         = LineTotTaxable    # KENYA TIMS compatibility for json, the taxable total of the line
        self.LinePlainText          = LinePlainText     # AS IT IS PRINTED - to be able to create and sign the _a file

        self.Pay1Amnt               = Pay1Amnt          # if this is a payment line, the amount of 1st payment
        self.Pay1Descr              = Pay1Descr         # description of payment type
        self.Pay2Amnt               = Pay2Amnt          #
        self.Pay2Descr              = Pay2Descr         #
        self.Pay3Amnt               = Pay3Amnt          #
        self.Pay3Descr              = Pay3Descr         #
        self.Pay4Amnt               = Pay4Amnt          # UP TO 4 different payments to close the receipt
        self.Pay4Descr              = Pay4Descr         #

    # !! THIS SHOULD BE CALLED FOR ERROR CHECKS AFTER THE NewLine IS COMPLETE AND JUST BEFORE PASSED TO EXECUTE
    def ErrorCheck(self):
        global S
        S.execute("SELECT from dpt VATclas WHERE dptCode='01'")
        return

global NewLine
NewLine=phrase(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)

#-------------------------------------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------------------------------------
# --------------     Variables for this module, used in parsing the input and inside command functions   -----------
global CmdIn
global CmdInCode
global TokeNumPre
global TokeNumPost
global CountCmd
global CountNum
global count
global ActiveCmd
global InSeries
global preCmd
global postCmd
global endCmd
global QtyA
global QtyB


CmdIn=''
CmdInCode=''
TokeNumPre=''
TokeNumPost=''
CountCmd=0
CountNum=0
count=0
ActiveCmd=0
InSeries=[]
preCmd=0
postCmd=0
endCmd=0
QtyA=''
QtyB=''


#-------------------------------------------------------------------------------------------------------------------------------
#-------------  specific functions to handle error checks and complex syntax in commands, accessible via Commands dictionary  --
#-------------------------------------------------------------------------------------------------------------------------------
def fT(a,b):  # Department command function
    global S
    S.execute("SELECT description, VATclass, category, price1  FROM dpt WHERE dptCode=?",(a,))
    dptData = S.fetchone()
    if dptData is None:
        return 'error DPT'
    else:
        NewLine.Dpt=a
        NewLine.DptDescr=dptData[0]

        return dptData

#..........................................................................................
def fP(a,b):  # PLU command function
    global S
    S.execute("SELECT description, department, category, price1, active  FROM plu WHERE barcode=?", (b,))
    pluData = S.fetchone()
    if pluData is not None:  # comparison with None is done using is / is not. It is an ERROR IF we use ==
        active=pluData[4]

    if pluData is None:
        return 'error DPT'
    else:
        if active==0:
            pluData='Item is not active'
            return pluData
        return pluData

#..........................................................................................
def fp():  # PLU DESCRIPTION command function
    pass
#..........................................................................................
def fE():  # END/CLOSE receipt command function
    pass

#..........................................................................................
def fX(a,b):  # QUANTITY/MULTIPL command function
    global NewLine
    if NewLine.Qty1==0:
        NewLine.Qty1=b
    else:
        NewLine.Qty2=b
    return



#..........................................................................................
def fD():  # DISCOUNT% ON PREVIOUS command function
    pass
#..........................................................................................
def fd():  # DISCOUNT% ON SUBTOTAL command function
    pass

#..........................................................................................
def fr():  # PRICE ENTRY command function
    pass

#..........................................................................................
def fc():  # COMMENT command function
    pass

#..........................................................................................
def fC():   # CLEAR command function
    pass

#..........................................................................................
def fV():   # VOID command function
    pass

#..........................................................................................
def fM():   # MENU command function
    pass

#..........................................................................................
def fK():   # CLERK login function - check for password
    pass
# ------------------------  END OF COMMAND FUNCTIONS ------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------
# Functions MUST PRECEDE the Commands dictionary, otherwise they are not recognized inside the dictionary -------
# Functions are called like this: Commands[key][3]() - inside () you can put parameters...
#----------------------------------------------------------------------------------------------------------------

#-------------------------    COMMAND DICTIONARY -----------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------
# NOTE: the fT, fP MUST be defined ABOVE the command dictionary otherwise, if I setup command dictionary BEFORE DEFINITIONS I get error
#-----------------------------------------------------------------------------------------------------------------
global Commands             # SYNTAX RULES: [Pre-command chars, Post-command num, 0=execute now, 1=expect next cmd, FUNCTION NAME
Commands={'T': [8,2,0,fT],     # DEPARTMENT    * 8=pre-command price or qtyXprice, 2=2 post command nn index, 0=execute after this command
          'P': [8,0,0,fP],     # PLU           * 9= pre-command barcode, 0= no post command code, 0=execute after P
          'p': [0,9,1,fp],     # PLU DESCRIP   * 9= pre-command description, 0=no post command, 1=must have next T
          'E': [1,2,0,fE],     # END-CLOSE     * 1=possible  pre-command chars, 2=00 CASH, 01 PMNT1, 02 PMNT2 etc, 0=execute after this
          'X': [7,0,1,fX],     # QUANTITY      * 7=QTY, 0=no post command, 1=expect another "0" type command to execute
          'D': [0,4,0,fD],     # DISCOUNT% PREV* 0: no pre-command, 4= post command 4 digits %, 0=execute immediately
          'd': [0,4,0,fd],     # DISCOUNT% SUBT* 0: no pre-command, 4= post command 4 igits %, 0=execute SUBTOT automatically
          'r': [9,0,1,fr],     # PLU PRICE     * 9=pre-command price, 0=no post command, 1=expect another "0" type command
          'c': [0,8,0,fc],     # COMMENT       * 0=no pre-command chars, 8=post command must have <text>, 0=execute after this command
          'V': [0,2,0,fV],     # VOID          * 0=no pre-command chars, 2=00 TOTAL CANCEL, 01 PREV VOID, 02 VOID
          'C': [0,0,0,fC],     # CLEAR/ESC     * DELETE/CLR/ESCAPE special handling: in SALES mode it is only about DEL/CLR
          'K': [0,2,0,fK],     # CLERK         * CLERK login by giving its number nn and then it should be followed with clerk's password
          'M': [0,0,0,fM]      # MENU          * MENU special handling, starts a separate module than this one
          }
#-----------------------------------------------------------------------------------------------------------------


#------------------------------------- MAIN FUNCTION FOR THIS MODULE -----------------------------------------------
# To use some variables in the manner of TokeNumPre=TokeNumPre+x you need to declare TokeNumPre as GLOBAL
# AND INITIALIZE it like TokeNumPre='' OUTSIDE of the function, and then declare it GLOBAL AGAIN inside function

def CheckIn(x):
    global CmdIn
    global CmdInCode
    global TokeNumPre
    global TokeNumPost
    global CountCmd
    global CountNum
    global count
    global ActiveCmd
    global InSeries
    global preCmd
    global postCmd
    global endCmd
    global QtyA
    global QtyB


    InSeries.append(x)      # this is a list of the input series of characters/keystrokes/input
#===============================================================================================================================
#===============================================================================================================================
#===============   M A I N    C O N T R O L     H E R E ========================================================================
#-----------------------------------------------  if x is a Command
    if x in Commands:       # the input will EITHER contain COMMAND or DATA
        CmdIn=x
        ActiveCmd=1
        preCmd=Commands[x][0]
        postCmd=Commands[x][1]
        endCmd=Commands[x][2]
        if postCmd==0:
            dataInDb=Commands[CmdIn][3](x,TokeNumPre)
            if endCmd==0:       # if the command is NOT ending the transaction (like the X) then  you do not passon anything, wait for a command that is capable of ending
                PassOn(NewLine)


#------------------------------------------------- if x is NOT Command but a number  // HANDLES Tnn or commands that have POST codes
    elif x not in Commands and '-'< x <':': # the input will EITHER contain COMMAND or DATA
        if ActiveCmd==0:  # if there is no command received, we assume that we need to gather the data as some number
            TokeNumPre=TokeNumPre+x # and store it in TokeNumPre, which is the PRE-COMMAND NUMBER
        elif ActiveCmd==1 and postCmd!=0: # this is after T, V, E commands that take nn or nnnn arguments
            CmdInCode=CmdInCode+x         # in this case, we are dealing with a POST-COMMAND ID
            postCmd=postCmd-1 # postCmd starts from elif with a value >0 and then as chars get input, postCmd is decremented and when it reaches 0 it means we are done with this
            if postCmd==0 and endCmd==0:
                dataInDb=Commands[CmdIn][3](CmdInCode,TokeNumPre) # ERROR CHECK HERE: based on the command function returned by Commands[CmdIn][3](params)
                ActiveCmd=0
                TokeNumPre=''
                CmdIn=''
                CmdInCode=''
        elif ActiveCmd==1 and preCmd==7:
            QtyA=TokeNumPre
            TokeNumPre=''
            TokeNumPre=TokeNumPre+x
            ActiveCmd=0
            PassOn(SystemState,RcptIdentity,NewLine)

#--------------------------------------------------  if x is NOT Command but NOT a number also
    elif x not in Commands and not '-'< x <':':
        print('ERROR INPUT or COMMENT/FREE TEXT')


    return

#========================   M A I N    C O N T R O L    E N D S    H E R E   ===================================================
#===============================================================================================================================
#===============================================================================================================================



# TODO do not leave checkin unless the command entered is an "ending" command, for example X does not leave here, T01 will leave

def PassOn(x,y,z):

    print('>>>>>>>>>>>>>>>  Pass to Execution')
    Execution.ektelese(SystemState, RcptIdentity, NewLine)  # TODO here is first attempt to pass a class object to another module

    return



#-------------------------------------  END OF MODULE CheckIn.py ---------------------------------------------------------
if __name__ == "__main__":
    CheckIn('1')
