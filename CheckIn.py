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


#===============================================================================================================================++++++====
#  I N P U T:       one by one the characters read and prepared by InputKeys.txt (for testing these are in TestKeys.txt)
#  O U T P U T:     Either an error (ErrorLog()) OR data inserted into NewLine which is an instance of CLASS InvoiceLines
#  S E N D S   TO:  The NewLine is sent to Execution.py - messages are sent to DISPLAY or/and log file ErrorLog

#11111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111
#111111                                      B E G I N                       1111111111111111111111111111111111

import sqlite3
from sqlite3 import Error
import Execution as EXE
import AllJournalClasses as AJC
import time
from datetime import datetime


now=time.time()
#global stampnow
stampnow=int(now)

folder='C:\\Tevin\\CoreOne\\'
global logfile
logfile = folder + "logfile.txt"


def ErrorLog(x,T):
    global logfile
    log=open(logfile,'a')
    if T==1:
        EventTime=time.time()
        event=time.ctime(EventTime)
        log.write(event +'\n')
        del event, EventTime
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
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        ErrorLog(e)
    return None

STAT=create_connection(dbStatic)         # ++++++++++++++   static.sqlite
JOURN=create_connection(dbJournal)       # ++++++++++++++   journal.sqlite

global S
global J
S=STAT.cursor()
J=JOURN.cursor()

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

# NewLine is the INSTANCE OF CLASS InvoiceLines and is generated for every line that is logically complete, that is has enough
# data to be executable

# !!! seems it does not make a difference to set "global"
#global NewLine
NewLine=AJC.InvoiceLines(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, \
                                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)


#-------------------------------------------------------------------------------------------------------------------------------
#-------------  specific functions to handle error checks and complex syntax in commands, accessible via Commands dictionary  --
#-------------------------------------------------------------------------------------------------------------------------------
def fT(a,b):            # Department command function, where a=the DepartmentCode and b=the number BEFORE this code (that is the PRICE)
    global S            # The function by itself knows that Tnn command is EXECUTE NOW command but the same is set in endCmd=0

    #global VAT   looks like you DO NOT need to declare VAT global inside the fT -
    # PERHAPS you ONLY need the global declaration if fT will ALTER the VAT for other modules
    # in this case we only READ from VAT

    S.execute("SELECT DptDescr, VATClass, CategoryCode, DptPrice1 FROM dpt WHERE DptCode=?", (a,))
    dptData = S.fetchone()
    if dptData is None:
        ErrorLog('Error 101-CheckIn-fT(a,b)-Department not found', 1)

    else:
        NewLine.PluDpt=a
        NewLine.DptDescr=dptData[0]
        NewLine.UnitPrice=b
        NewLine.VATRate=VAT[dptData[1]]
        #----------------------------------------------------------------------------------------------------------------------------------
        EXE.ektelese(NewLine)   # IMPORTANT: SEND TO EXECUTION FROM THIS POINT - THE FUNCTION KNOWS THAT DEPART IS ENDING A TRANSACTION
        #----------------------------------------------------------------------------------------------------------------------------------
        ClearAll()              # this clears the variables used in PARSING THE INPUT so we can start all over on clean variables
    return

#..........................................................................................
def fP(a,b):                        # PLU command function
    global S
    #global VAT ??????????????? You don't need to declare global VAT here,

    c=int(b) # seems Barcode needs integer and we get b as string from the inkeys, so converting to int is needed
    S.execute("SELECT Description, dpt, cat, price1, active FROM plu WHERE Barcode=?", (c,))
    pluData = S.fetchone()
    if pluData is not None:         # comparison with None is done using is / is not. It is an ERROR IF we use ==
        active=pluData[4]
        if active==0:
            ErrorLog('CheckIn-fP-Line 157 - NOT ACTIVE!', 1)
            return
        if active!=0:
            NewLine.Command='P'
            NewLine.CommandID=b
            NewLine.PluDescr=pluData[0]
            NewLine.UnitPrice=pluData[3]
            NewLine.PluDpt=pluData[1]
            #-------- PLU gives the department code and we need to find the VAT rate of this dpt:
            S.execute("SELECT VATClass from dpt WHERE DptCode=?", (NewLine.PluDpt,))
            dptvat=S.fetchone()
            NewLine.VATRate=VAT[dptvat[0]]
            #----------------------------------------------------------------------------------------------------------------------------
            EXE.ektelese(NewLine)   # IMPORTANT: SEND TO EXECUTION FROM THIS POINT - THE FUNCTION KNOWS THAT PLU  IS ENDING A TRANSACTION
            #----------------------------------------------------------------------------------------------------------------------------
            ClearAll()              # this clears the variables used in PARSING THE INPUT so we can start all over on clean variables


    else:
        ErrorLog('CheckIn-fP-Line 164 - no plu data', 1)
        return
    return

#..........................................................................................
def fp(a,b):  # PLU DESCRIPTION command function (use as fiscal printer where description comes from outside)


    pass
#..........................................................................................
def fE(a,b):  # END/CLOSE receipt command function
    NewLine.Command = 'E'
    NewLine.CommandID = a
    NewLine.PayCode = a
    NewLine.PayAmnt = b
    #------------------------------------------------------------------------------------------------
    EXE.kleise(NewLine)     # this is END of RECEIPT with payment and calls kleise function
    #                         If payment is NOT EQUAL to TOTAL, another payment(s) is expected
    #------------------------------------------------------------------------------------------------
    ClearAll()
    return

#..........................................................................................
def fX(a,b):  # QUANTITY/MULTIPL command function
    global NewLine
    if NewLine.QTY1==0:
        NewLine.QTY1=b
    else:
        NewLine.QTY2=b
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

#..........................................................................................
def ClearAll():
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
    ActiveCmd=0

    return


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

def CheckIn(x,y):       # y is the VAT[] list coming in from InputKeys. It didn't work when I put VAT in here, parameter / variable conflict
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

    global VAT          # seems global is needed here, right before the assignement of this module's environment VAT=y where y is a parameter of CheckIn(x,y)
    VAT=y


    #InSeries.append(x)      # this is a list of the input series of characters/keystrokes/input
    
#===============================================================================================================================
#===============================================================================================================================
#===============   M A I N    C O N T R O L     H E R E ========================================================================
#-----------------------------------------------  if x is a Command
    if x in Commands:       # the input will EITHER contain COMMAND or DATA
        CmdIn=x
        ActiveCmd=1
        preCmd=Commands[x][0]               # preCmd:   0= NO numbers before the command, 7= quantity before X, 8= price or qtyXprice before T ets
        postCmd=Commands[x][1]              # postCmd:  0= NO numbers after this command, 2= 2 numbers like T01,
        endCmd=Commands[x][2]
        if postCmd==0:
            Commands[CmdIn][3](x,TokeNumPre)
            #if endCmd==0:         # if endCommand is 0 this means we can move to execution, this command is ENDING COMMAND
            #    EXE.ektelese(NewLine, VAT)


#------------------------------------------------- if x is NOT Command but a number  // HANDLES Tnn or commands that have POST codes
    elif x not in Commands and '-'< x <':': # the input will EITHER contain COMMAND or DATA, here we EXPECT NUMBERS
        if ActiveCmd==0:                    # if there is no command received, we assume that we need to gather the data as some number
            TokeNumPre=TokeNumPre+x         # and store it in TokeNumPre, which is the PRE-COMMAND NUMBER
        elif ActiveCmd==1 and postCmd!=0:   # this is after T, V, E commands that take nn or nnnn arguments
            CmdInCode=CmdInCode+x           # in this case, we are dealing with a POST-COMMAND ID, for example Tnn is postCmd=2
            postCmd=postCmd-1               # postCmd starts from elif with a value >0 and then as chars get input, postCmd is decremented and when it reaches 0 it means we are done with this
            if postCmd==0 and endCmd==0:
                Commands[CmdIn][3](CmdInCode,TokeNumPre) # this function doesn't "return" anything, it modifies object NewLine
                ActiveCmd=0
                TokeNumPre=''
                CmdIn=''
                CmdInCode=''

        elif ActiveCmd==1 and preCmd==7:    # this is special for X command (preCmd=7 for X multiplication)
            QtyA=TokeNumPre
            TokeNumPre=''
            TokeNumPre=TokeNumPre+x
            ActiveCmd=0

#--------------------------------------------------  if x is NOT Command but NOT a number also
    elif x not in Commands and not '-'< x <':':
        ErrorLog('-CheckIn.py - line approx 305 - ERROR INPUT or COMMENT/FREE TEXT', 1)


    return

#========================   M A I N    C O N T R O L    E N D S    H E R E   ===================================================
#===============================================================================================================================
#===============================================================================================================================



#-------------------------------------  END OF MODULE CheckIn.py ---------------------------------------------------------
if __name__ == "__main__":
    CheckIn('1')
