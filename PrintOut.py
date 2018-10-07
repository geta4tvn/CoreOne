# This is the final module where a receipt or invoice gets printed out, emailed, written to a file etc
# PrintOut module receives commands from Execution.py module
# PrintOut reads from static.sqlite, templates table the form it is supposed to print depending on which type of document is printed
# Templates table contain the structure of different possible documents, for example a RECEIPT has a different form than an INVOICE
# and there are special templates for the printout of coupons or advertisements or notifications like loyalty points


import sqlite3
from sqlite3 import Error

