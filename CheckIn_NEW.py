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


import sqlite3
from sqlite3 import Error


#======================================================================================================================
# Status variables contain flags to follow at what mode of operation and what error states
# yes, but do we need ASYNCHRONOUS update of these? no, no need to mess with concurrent modules, in-line makaroni updates when needed
global St_FM
global St_OpenRcpt
global St_OpenDay
global St_OpMode
global St_ClerkPerms
global St_ClerkCode
global St_ZTstamp
global St_Poff
global St_BatLow
global St_BatRTC


St_FM=0             # 0= FM is ok, 1=FM error
St_OpenRcpt=0       # 0= receipt is NOT open, open it up by 1=receipt open
St_OpenDay=0        # 0= day is NOT open, open it up by 1=day open
St_OpMode=0         # 0= SALES, 1=IN MENU, 2=REPORTS, 3=Z
St_ClerkPerms=0     # A=only sales, B= sales and discounts, C=reports and Zs, D=god
St_ClerkCode=0      # as in clerks db
St_ZTstamp=0        # should get int(time.time())
St_Poff=0           # 0= no power off has happened, 1=a power off interrupted some execution
St_BatLow=0         # 0= battery is charged / 1=battery level low
St_BatRTC=0         # 0= RTC bat is OK / 1=battery RTC low

#============================================================================================================
#=======================    ACCESS THE TWO DATABASES: STATIC AND JOURNAL     ===============================
dbStatic='D:\\000 WORK 2017\\2 general\\00 2018 Tevin\\OUR ETR\\CharmSources\\static.sqlite'
dbJournal='D:\\000 WORK 2017\\2 general\\00 2018 Tevin\\OUR ETR\\CharmSources\\journal.sqlite'
#===========================================================================================================
#======================    LINUX
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
#==========================   SO J=THE CURSOR TO JOURNAL DATABASE AND S=THE CURSOR TO STATIC DB



#=======================================================================================================================
# class ReceiptId contains top and end receipt parameters and totals
class ReceiptId(object):
    def __init__(self, Num, AccuNum, Z, Clerk, Station, Date, Time, HashA, HashE, Approv, CustTIN, CustName, CustType,
                 CustAddr, GPS, Total, TotVATa, TotVATb, TotVATc, TotVATd, TotVATe, TotVATf, Pmnt1, Pmnt2, Pmnt3):
        self.Num            = Num  # this is the daily number of receipt
        self.AccuNum        = AccuNum  # this is the accumulated number of receipt
        self.Z              = Z  # this is the current Z number
        self.Clerk          = Clerk  # this is the code of active clerk who services this receipt
        self.Station        = Station  # the name given to the station entering the receipt
        self.Date           = Date  # current date to be printed on receipt
        self.Time           = Time  # time to be printed on receipt
        self.HashA          = HashA  # the SHA-1 or SHA-256 value of the receipt's data (_a.txt data)
        self.HashE          = HashE  # the SHA-1 value of the receipt's numerical data (_e.txt data)
        self.Approv         = Approv  # any approval code
        self.CustTIN        = CustTIN  # citizens card or customer's TIN or VAT num
        self.CustName       = CustName  # customer name / company
        self.CustType       = CustType  # customer type / sector / other
        self.CustAddr       = CustAddr  # customer address
        self.GPS            = GPS  # location via GPS or other
        self.Total          = Total  # the total of the receipt
        self.TotVATa        = TotVATa  # the VATA total
        self.TotVATb        = TotVATb  # the VATB total
        self.TotVATc        = TotVATc  # the VATC total
        self.TotVATd        = TotVATd  # the VATD total
        self.TotVATe        = TotVATe  # the VATE total
        self.TotVATf        = TotVATf  # the VATF total
        self.Pmnt1          = Pmnt1
        self.Pmnt2          = Pmnt2
        self.Pmnt3          = Pmnt3


# =================================================================================================================================
# class phrase contains a SINGLE TRANSACTION ENTRY with all necessary variables
class phrase(object):
    def __init__(self, Cmd, CmdId, Qty1, Qty2, PluCode, PluDesc, PluDescIn, DptDesc, Cat, Price, VATCat, VATPer, DiscountPer, DiscountAm, UpPrc,
                 UpAm, Amnt, Comment):
        self.Cmd            = Cmd  # this is T, P, E, V, X, D, R, c, p all commands that are described in analysis
        self.CmdId          = CmdId  # this is the nn after command Tnn, Vnn etc so that for example if T, fetch from DPT# table nn dpt
        self.Qty1           = Qty1  # we support qty X qty X price - this is Qty1, the first number before first X command
        self.Qty2           = Qty2  # this is second qty to support qty X qty
        self.PluCode        = PluCode  # this is the barcode or PLU code entered by scanner or manually
        self.PluDesc        = PluDesc # (FROM STATIC.SQLITE) description fetched from the db
        self.PluDescIn      = PluDescIn  # to be compatible with fiscal printer we can accept PLU description directly in the command line
        self.DptDesc        = DptDesc  # (FROM STATIC.SQLITE) the dpt description corresponding to Cmd.CmdId
        self.Cat            = Cat  # this is the code for category in case we want to support sales by category
        self.Price          = Price  # price of the PLU or DPT
        self.VATCat         = VATCat # (FROM STATIC.SQLITE) the A, B, C, D etc
        self.VATPer         = VATPer # (FROM STATIC.SQLITE) the actual percentage
        self.DiscountPer    = DiscountPer  # In case of % discount, this holds the Prcentage - !! command Dnn, 01: immediate, 02: on subtotal, # 03: ticket
        self.DiscountAm     = DiscountAm  # In case of amount discount, this holds the amount
        self.UpPrc          = UpPrc  # in case of % markup, this holds the Prcentage
        self.UpAm           = UpAm  # in case of amount markup, this holds the Prcentage
        self.Amnt           = Amnt  # amount given from host PC in certain cases
        self.Comment        = Comment  # comment text entered by command c

    def ErrorCheck(self):
        global S
        S.execute("SELECT from dpt VATclas WHERE dptCode='01'")
        return

global newline
newline=phrase(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)
#===============================================================================================================================================================

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


#-----------------------------------------------------------------------------------------------------------------------------
#-------------  specific functions to handle error checks and complex syntax in commands, accessible via Commands dictionary--
#-----------------------------------------------------------------------------------------------------------------------------
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
            PassOn(newline)

#------------------------------------------------- if x is NOT Command but a number  // HANDLES Tnn or commands that have POST codes
    elif x not in Commands and '-'< x <':': # the input will EITHER contain COMMAND or DATA
        if ActiveCmd==0:
            TokeNumPre=TokeNumPre+x
        elif ActiveCmd==1 and postCmd!=0: # this is after T, V, E commands that take nn or nnnn arguments
            CmdInCode=CmdInCode+x
            postCmd=postCmd-1
            if postCmd==0 and endCmd==0:    # this is X case
                dataInDb=Commands[CmdIn][3](CmdInCode,TokeNumPre) # ERROR CHECK HERE: based on the command function returned by Commands[CmdIn][3](params)
                PassOn(newline)
                ActiveCmd=0
                TokeNumPre=''
                CmdIn=''
                CmdInCode=''
        elif ActiveCmd==1 and preCmd==7:
            QtyA=TokeNumPre
            TokeNumPre=''
            TokeNumPre=TokeNumPre+x
            ActiveCmd=0
            PassOn(newline)

#--------------------------------------------------  if x is NOT Command but NOT a number also
    elif x not in Commands and not '-'< x <':':
        print('ERROR INPUT or COMMENT/FREE TEXT')


    return

#========================   M A I N    C O N T R O L    E N D S    H E R E   ===================================================
#===============================================================================================================================
#===============================================================================================================================



# TODO do not leave checkin unless the command entered is an "ending" command, for example X does not leave here, T01 will leave

def PassOn(out):
    print('Command from the class Phrase is:',out.Cmd)
    print('CommandID drom the same is      :',out.CmdId)

    return



#-------------------------------------  END OF MODULE CheckIn.py ---------------------------------------------------------
if __name__ == "__main__":
    CheckIn('1')
