import sqlite3
from sqlite3 import Error
import AllJournalClasses as AJC
import InputKeys
import time


folder='C:\\Tevin\\CoreOne\\'
arxeio=folder+'TestKeysIn.txt'

global logfile
logfile=folder+"logfile.txt"

def ErrorLog(x, T):
    global logfile
    log = open(logfile, 'a')
    if T == 1:
        EventTime = time.time()
        event = time.ctime(EventTime)
        log.write(event + '\n')
        del event, EventTime
    log.write(x + '\n\n')
    log.close()
    return


NewInvoice=AJC.InvoiceId(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, \
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

def apoforologisi(gross,vatrate):
    net=gross/(1+(1/vatrate))
    vat_amnt=gross-net
    return net, vat_amnt


def ektelese(x):
    price=float(x.UnitPrice)
    qty=float(x.QTY1)
    if qty==0:
        qty=1
        x.QTY1=1
    print('**************************************************************')
    print('**Execution.py** LINE NUMBER ---------------- ',x.LineNum)
    print('Command  =', x.Command)
    print('CmdID    =', x.CommandID)
    print('DptDescr =', x.DptDescr)
    print('PLU Descr=', x.PluDescr)
    print('Price    =', x.UnitPrice)
    print('Qty1     =', x.QTY1)

    qtyXprice=price*qty
    print('**TOTAL is                =',qtyXprice)
    vatrate=float(x.VATRate)
    apo=apoforologisi(qtyXprice,vatrate)
    print('The VAT rate is.........=', x.VATRate)
    print('From APOFOROLOGISH, net=', "%.2f" % round(apo[0], 2))
    print('From APOFOROLOGISH, tax=', "%.2f" % round(apo[1], 2))

    #print('From apoforologisi, net =', apo[0])
    #print('From apoforologisi, tax =', apo[1])

    # print('Qty2     =', x.QTY2)
    # print('Qt1 X Qt2=', x.QTY)
    if str(x.DptDescr)=='0':
        OutputLine=str(x.QTY1) + ' X ' + str(x.UnitPrice) + '  ' + str(x.PluDescr) + '  =' + str(qtyXprice) + '    ' + str(x.VATRate) + '%'
    else:
        OutputLine = str(x.QTY1) + ' X ' + str(x.UnitPrice) + '  ' + str(x.DptDescr) + '  =' + str(qtyXprice) + '    ' + str(x.VATRate) + '%'
    ErrorLog(OutputLine,0)

    AJC.InvoiceLines.InvLinesWrite(x)
    x.LineNum=x.LineNum+1
    x.CommandID=''
    x.Command=''
    x.QTY1=0
    x.QTY2=0
    x.DptDescr=''
    x.PluDescr=''
    return

def kleise(x):
    x.LineNum=0
    AJC.InvoiceLines.InvLinesWrite(x)
    now = time.time()
    stampnow = int(now)
    NewInvoice.TimeStamp=stampnow
    # N=int(NewInvoice.DocNumAccum)
    # N=N+1
    # NewInvoice.DocNumAccum=str(N)
    # AJC.InvoiceId.InvIdWrite
    ErrorLog('------------------------------', 0)
    ErrorLog('TOTAL WILL BE HERE SOON!!!....', 0)
    ErrorLog('Payment Received is = '+ str(x.PayAmnt), 0)
    return
