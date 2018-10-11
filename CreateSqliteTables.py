import sqlite3
from sqlite3 import Error

#https://www.youtube.com/watch?v=q5uM4VKywbA
#lesson about using csv
import csv
with open('myfile.csv','r') as csv_file:
    csv_reader=csv.reader(csv_file)
    next(csv_reader)

    for line in csv_reader:
        print(line[2])



        
#lesson about creating dbs and tables
c.execute("CREATE TABLE IF NOT EXISTS InvoiceId(Num, AccumNum, column3)")
# using c.execute(""" (triple") I can have multiple lines without \   """
conn.commit()
c.execute("INSERT INTO InvoiceId VALUES()")
conn.commit()
conn.close() #  must do this to FREE RAM!!!
