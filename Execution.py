import sqlite3
from sqlite3 import Error
import AllJournalClasses as AJC
import InputKeys
import time


NewInvoice=AJC.InvoiceId(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, \
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

def apoforologisi(gross,vatrate):

    net=gross/(1+(1/vatrate))
    vat_amnt=gross-net
    return net, vat_amnt


def ektelese(x,VAT):
    print('**Execution.py** LINE NUMBER ---------------- ',x.LineNum)
    # print('Command  =', x.Command)
    # print('CmndID   =', x.CommandID)
    # print('DptDescr =', x.DptDescr)
    print('**Execution.py*  Price    =', x.UnitPrice)
    print('**Execution.py*  Qty1     =', x.QTY1)
    price=float(x.UnitPrice)
    qty=float(x.QTY1)
    if qty==0:
        qty=1

    qtyXprice=price*qty
    print('**TOTAL is                =',qtyXprice)
    vatrate=float(x.VATRate)
    apo=apoforologisi(qtyXprice,vatrate)
    print('From apoforologisi, net =', apo[0])
    print('From apoforologisi, tax =', apo[1])

    # print('Qty2     =', x.QTY2)
    # print('Qt1 X Qt2=', x.QTY)

    AJC.InvoiceLines.InvLinesWrite(x)
    x.LineNum=x.LineNum+1
    x.QTY1=0
    x.QTY2=0
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
    # AJC.InvoiceId.InvIdWrite(NewInvoice)
    return
