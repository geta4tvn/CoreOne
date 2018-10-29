def InputKeys():

# This is the input module.
# It should accept and error check inputs from KEYBOARD, RS232, TEXT FILES and ETHERNET
# The KEYBOARD input on the ECR will come as an RS232 stream of BYTES generated by the onboard keyboard controller

# Key codes will be bytes returned by the keyboard controller  and a dictionary will map whatever function we want on the key numbers
# Keypad is 5X6, so key codes will be 0 to 29.
# the keypad code layout on hardware level is:

# WHEN KEYBOARD LEVEL IS 0 (NORMAL FIRST LEVEL FUNCTIONS):

#   00h ON    01h INVOI  02h PLU   03h PRC    04h MENU
#   05h CLR   06h VOID   07h X     08h TM5    09h SHIFT
#   0ah 7     0bh 8      0ch 9     0dh TM4    0eh DISCNT
#   0fh 4     10h 5      11h 6     12h TM3    13h PMNT
#   14h 1     15h 2      16h 3     17h TM2    18h SUB
#   19h 0     1ah 00     1bh .     1ch TM1    1dh CASH

# WHEN KEYBOARD LEVEL IS 1 (AUTO-TURN TO ALPHANUMERIC):

#   00h ON    01h A      02h B     03h C      04h MENU
#   05h D     06h E      07h F     08h G      09h SHIFT
#   0ah H     0bh I      0ch J     0dh K      0eh L
#   0fh J     10h K      11h L     12h M      13h N
#   14h O     15h P      16h Q     17h R      18h S
#   19h T     1ah W      1bh .     1ch TM1    1dh CASH

#   THE actual transformations should be part of the static.sqlite and be read into lists on startup. In this way we can have multiple keyboard layouts
#   Table keyblayouts in static.sqlite contains all COMMANDS and DATA mapped to key codes 0-29

# I have opened account geta4tvn at github with passw Q2 and then installed git in Dell
# Then used VCS > Import into version control > Share Project on GitHub where I successfuly created repository EngineOneCore
# When using a test input file, we are using the commands and NOT THE KEYBOARD HARDWARE CODES to generate the input
#  The COMMANDS understood by the system are described in CASH REGISTER ENGINE ANALYSIS.XLSX but are also given below:



    import CheckIn
    import time
    from datetime import datetime
    import sqlite3
    from sqlite3 import Error


    now=time.time()
    #global stampnow
    stampnow=int(now)
    #print(stampnow)
    #print(datetime.utcfromtimestamp(stampnow).strftime('%Y-%m-%d %H:%M:%S'))    # gives the UTC time
    #print(datetime.fromtimestamp(stampnow).strftime('%Y-%m-%d %H:%M:%S'))       # gives the local time from the TIMESTAMP which is a float if you need uicroseconds
    DayMonthYearDate=datetime.fromtimestamp(stampnow).strftime('%d-%m-%Y')
    DayMonthDate=datetime.fromtimestamp(stampnow).strftime('%d/%m')
    DayNameMonthyear=datetime.fromtimestamp(stampnow).strftime('%d %b %y')
    DayOfYear=datetime.fromtimestamp(stampnow).strftime('%j')
    WeekOfYear=datetime.fromtimestamp(stampnow).strftime('%W')
    NameOfDay=datetime.fromtimestamp(stampnow).strftime('%a')
    HourMinAMPM=datetime.fromtimestamp(stampnow).strftime('%I:%M %p')
    HourMin=datetime.fromtimestamp(stampnow).strftime('%H:%M')
    #print('finally a date from timestamp float=', DayMonthYearDate)
    #print('Just day and month: ',DayMonthDate)
    #print('The abbrev month name:',DayNameMonthyear)
    #print('This is the number of the day in the year: ',DayOfYear, '  and week of year is ',WeekOfYear)
    #print('The abbrev name of day - use %A for full name: ',NameOfDay)
    print('Hour in 24h form =', HourMin, 'Hour in 12h am pm form=', HourMinAMPM)


    folder='C:\\Tevin\\CoreOne\\'
    arxeio=folder+'TestKeysIn.txt'

    global logfile
    logfile=folder+"logfile.txt"

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

    #===================================  RUN ONCE ON STARTUP TO PREPARE SYSTEM WITH VAT RATES, STATE FLAGS, CLERK LOGIN, HARDWARE CHECKS=======
    #-------------------------------------------------------------------------------------------------------------------------------------------
    dbStatic = 'C:\\Tevin\\CoreOne\\static.sqlite'
    # ======================  PATH TO USE IF IN  LINUX  =====================================================================
    # dbStatic='/usr/ecr/static.sqlite'
    # dbJournal='/usr/ecr/journal.sqlite'

    def create_connection(db_file):
        try:
            conn = sqlite3.connect(db_file)
            return conn
        except Error as e:
            ErrorLog('InputKeys-create con Error'+e,1)
        return None

    STAT = create_connection(dbStatic)      # ++++++++++++++   static.sqlite
    S = STAT.cursor()

    # HOW TO SELECT THE ROW HOLDING THE MAXIMUM OF A CERTAIN COLUMN
    S.execute("SELECT * FROM VATRates WHERE TimeStampEntered=(SELECT MAX(TimeStampEntered) FROM VATRates)")
    VatData = S.fetchone()
    global VAT
    VAT=[0,0,0,0,0,0,0,0,0]                 # You MUST initialize a list like this....
    VAT[0]=VatData[6]   # Read ONCE ON STARTUP to get the current VAT Rates from static.VATRates table
    VAT[1]=VatData[2]   # This is VATA
    VAT[2]=VatData[3]   # This is VATB
    VAT[3]=VatData[4]   # This is VATC
    VAT[4]=VatData[5]   # This is VATD
    VAT[5]=VatData[6]   # This is VATE
    # The idea is to have all VAT rates at hand WITHOUT READING THE SQLITE EVERY TIME....
    # As long as there is power... you have the VAT in a list in memory..................
    print('On startup, readings of VAT rates give: VATA=',VAT[1], '  VATB=', VAT[2], 'VATC=', VAT[3], 'VATD=',VAT[4], 'VATE=',VAT[5])

    STAT.close()        # Close this connection, we are done with getting the vat rates on startup

#===================================  MAIN BODY HERE - READS FROM AN INPUT FILE (OR OTHER INPUT) ========================================
    #----------------------------------------------------------------------------------------------------------------------------------------
    counter=1
    while counter<2:
        ReadFile=open(arxeio,"r")
        for line in ReadFile.readlines():
            for x in line:
                if x>chr(32):               # do NOT send LF, CR and other controls
                   # print('>>',x)
                    CheckIn.CheckIn(x,VAT)  # PASSES THE VAT LIST AS SECOND PARAMETER HERE, tried to make it global but it will not work....

        stopped=time.time()
        counter=counter+1
        duration=int(1000*(stopped-now))
        print('THE WHOLE THING TOOK ',duration,'msec'+'   ----- COUNTER =',counter)
        ErrorLog('----------------- WHOLE THING DURATION: '+str(duration)+'msec'+'  ---------- COUNTER='+str(counter), 0)
if __name__ == "__main__":
    InputKeys()


    #================================ EXAMPLES OF re MODULE (REGULAR EXPRESSION STRING MANIPULATION ================================================
    # line=re.sub('[\s+]','',line)    #(from re) this one from re library substitutes all spaces with nul
    # line=re.sub(',',', ',line)      #use again the substitute function to insert a space after a coma
    # words=line.split()              #(from re) the text.split() function will turn a string into a list provided you have words separated by ", "
    # for M in range(0, 10):
    #     words[M]=re.sub(',','',words[M])  #this is to remove the comma from interfering with numbers
    #     words[M]=re.sub('None','0',words[M])