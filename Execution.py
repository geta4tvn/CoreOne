import sqlite3
from sqlite3 import Error
import AllJournalClasses


def ektelese(x):
    print('!!!! EKTELESE AYTO: !!!!')
    print(x.DptDescr)
    AllJournalClasses.InvoiceLines.InvLinesWrite(x)
    return