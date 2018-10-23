import sqlite3
from sqlite3 import Error
import AllJournalClasses as AJC


def ektelese(x):
    print('**Execution.py** LINE NUMBER ---------------- ',x.LineNum)
    # print('Command  =', x.Command)
    # print('CmndID   =', x.CommandID)
    # print('DptDescr =', x.DptDescr)
    print('**Execution.py*  Price    =', x.UnitPrice)
    print('**Execution.py*  Qty1     =', x.QTY1)
    # print('Qty2     =', x.QTY2)
    # print('Qt1 X Qt2=', x.QTY)

    AJC.InvoiceLines.InvLinesWrite(x)
    x.LineNum=x.LineNum+1
    x.QTY1=0
    x.QTY2=0
    return