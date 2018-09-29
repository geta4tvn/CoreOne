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

#=======================================================================================================================
#=======================    ACCESS THE TWO DATABASES: STATIC AND JOURNAL     ===========================================
dbStatic='D:\\000 WORK 2017\\2 general\\00 2018 Tevin\\OUR ETR\\CharmSources\\static.sqlite'
dbJournal='D:\\000 WORK 2017\\2 general\\00 2018 Tevin\\OUR ETR\\CharmSources\\journal.sqlite'
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
        self.OpMode         = OpMode        # 0 = in menu, standby, 1=in SALES, 2= in REPORTS, 3= in PROGRAMMING
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
        self.RTClow         = RTCLow        # 0 = RTC battery OK, 1 = RTC battery low
        self.FMerr          = FMerr         # 0 = No FM error, 1 = FM not detected, 2 = FM s/n invalid, 3 = FM read/write errors
        self.ClerkPerms     = ClerkPerms    # 0 = SALES no discnts/refunds, 1=all SALES, 2=Sales, X,  no Z - 3 = up to Z, 4 = GOD LEVEL, change time, erase...
        self.ClerkCode      = ClerkCode     # N where N = 1, 2, 3 etc active clerk code, enter 99 for clerk code capable of GOD LEVEL
        self.PrnStat        = PrnStat       # 0 = no error, 1 = PaperEnd, 2 = head up, 3 = overheat, 4 = disconnected
        self.WiFiStat       = WiFiStat      # 0 = connected OK, 1 = no network, 2 = cannot login, 3 = no internet access
        self.NetStat        = NetStat       # 0 = connected to internet, access to maintenance server, 1 = internet OK, no maint server, 2...
        self.DemoMode       = DemoMode      # 0 = normal fiscal operation, 1 = demo mode, do not write to FM, ignore all FM related errors
        self.Zpending       = Zpending      # 0 = no pending Z, last Z completed OK,  1 = Z not completed due to errors, needs to be re-printed

    def ReadCurStat(self):
        global J
        J.execute("SELECT * FROM state WHERE ROWID=(SELECT MAX(ROWID) FROM state)")
        LastState=J.fetchone()
        return LastState

    def SaveCurStat(self):
        global J
        J.execute("INSERT INTO state VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);",(self.OpMode, self.OpenRcpt, self.OpenRcptNum, self.OpenRcptTStamp, \
        self.OpenDay, self.TStamp, self.LastZTStamp, self.LastZ, self.ShutDn, self.Poff, self.BatLow, self.RTCLow, self.FMerr, \
        self.ClerkPerms, self.ClerkCode, self.PrnStat, self.WiFiStat, self.NetStat, self.DemoMode, self.Zpending))
        J.commit()


        

global SystemState
SystemState=SyState(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)
NowStat=SystemState.ReadCurStat()
print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@   Status from db',NowStat)




# ============================================================================================================================
# class ReceiptId contains top and end receipt parameters and totals
class ReceiptId(object):
    def __init__(self, Num, AccuNum, DocType, Z, Clerk, Station, TStamp, Date, Time, HashA, HashE, Approv, CustTIN, CustName, CustType,
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


#=======================================================================================================================

# =================================================================================================================================
# class phrase contains a SINGLE TRANSACTION ENTRY with all necessary variables needed for this line to be COMPLETE (to make sense)
class phrase(object):
    def __init__(self, Cmd, CmdId, Qty1, Qty2, PluCode, PluDesc, Dpt, Cat, Price, DiscountPrc, DiscountAm, UpPrc, 
                 UpAm, Amnt, Comment):
        self.Cmd            = Cmd  # this is T, P, E, V, X, D, R, c, p all commands that are described in analysis
        self.CmdId          = CmdId  # this is the nn after command Tnn, Vnn etc so that for example if T, fetch from DPT# table nn dpt
        self.Qty1           = Qty1  # we support qty X qty X price - this is Qty1, the first number before first X command
        self.Qty2           = Qty2  # this is second qty to support qty X qty
        self.PluCode        = PluCode  # this is the barcode or PLU code entered by scanner or manually
        self.PluDesc        = PluDesc  # to be compatible with fiscal printer we can accept PLU description directly in the command line
        self.Dpt            = Dpt  # this is the nn in Tnn (the department code)
        self.Cat            = Cat  # this is the code for category in case we want to support sales by category
        self.Price          = Price  # price of the PLU or DPT
        self.DiscountPrc    = DiscountPrc  # In case of % discount, this holds the Prcentage - !! the TYPE of discount is given in command Dnn, 01: immediate, 02: on subtotal, 03: ticket
        self.DiscountAm     = DiscountAm  # In case of amount discount, this holds the amount
        self.UpPrc          = UpPrc  # in case of % markup, this holds the Prcentage
        self.UpAm           = UpAm  # in case of amount markup, this holds the Prcentage
        self.Amnt           = Amnt  # amount given from host PC in certain cases
        self.Comment        = Comment  # comment text entered by command c

    # !! THIS SHOULD BE CALLED FOR ERROR CHECKS AFTER THE NEWLINE IS COMPLETE AND JUST BEFORE PASSED TO EXECUTE
    def ErrorCheck(self):
        global S
        S.execute("SELECT from dpt VATclas WHERE dptCode='01'")
        return

global newline
newline=phrase(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)
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
        return dptData

#..........................................................................................
def fP(a,b):  # PLU command function
    global S
    S.execute("SELECT description, department, category, price1, active  FROM plu WHERE barcode=?", (b,))
    pluData = S.fetchone()
    if pluData is not None:  # comparison with None is done using is / is not ERROR IF USE ==
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
    global newline
    if newline.Qty1==0:
        newline.Qty1=b
    else:
        newline.Qty2=b
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
            PassOn(TokeNumPre, CmdIn, CmdInCode, dataInDb)


#------------------------------------------------- if x is NOT Command but a number  // HANDLES Tnn or commands that have POST codes
    elif x not in Commands and '-'< x <':': # the input will EITHER contain COMMAND or DATA
        if ActiveCmd==0:
            TokeNumPre=TokeNumPre+x
        elif ActiveCmd==1 and postCmd!=0: # this is after T, V, E commands that take nn or nnnn arguments
            CmdInCode=CmdInCode+x
            postCmd=postCmd-1
            if postCmd==0 and endCmd==0:    # this is X case
                dataInDb=Commands[CmdIn][3](CmdInCode,TokeNumPre) # ERROR CHECK HERE: based on the command function returned by Commands[CmdIn][3](params)
                PassOn(TokeNumPre, CmdIn, CmdInCode, dataInDb)
                ActiveCmd=0
                TokeNumPre=''
                CmdIn=''
                CmdInCode=''
        elif ActiveCmd==1 and preCmd==7:
            QtyA=TokeNumPre
            TokeNumPre=''
            TokeNumPre=TokeNumPre+x
            ActiveCmd=0
            PassOn('empty', CmdIn, 'empty', QtyA)

#--------------------------------------------------  if x is NOT Command but NOT a number also
    elif x not in Commands and not '-'< x <':':
        print('ERROR INPUT or COMMENT/FREE TEXT')


    return

#========================   M A I N    C O N T R O L    E N D S    H E R E   ===================================================
#===============================================================================================================================
#===============================================================================================================================



# TODO do not leave checkin unless the command entered is an "ending" command, for example X does not leave here, T01 will leave

def PassOn(a,b,c,d):

    print('>>>>>>>>>>>>>>>  Pass to Execution')
    print('Pre command number:',a)
    print('Command is',b)
    if b=='X':
        SystemState.OpenRcptTStamp='12355555555'
        SystemState.SaveCurStat()
    print('Command Code is:',c)
    print('================================================  THIS IS FROM THE DB:',d)

    return



def PhrasePass(a,b,c,d):
    global QtyA
    QtyA=1
    if b=='X':
        QtyA=a

    return


#-------------------------------------  END OF MODULE CheckIn.py ---------------------------------------------------------
if __name__ == "__main__":
    CheckIn('1')
