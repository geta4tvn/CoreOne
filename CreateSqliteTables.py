import sqlite3
from sqlite3 import Error

#https://www.youtube.com/watch?v=q5uM4VKywbA
#lesson about using csv
#import csv
#with open('myfile.csv','r') as csv_file:
#    csv_reader=csv.reader(csv_file)
#    next(csv_reader)

#    for line in csv_reader:
#        print(line[2])


db_file='C:\\Tevin\\CoreOne\\dokimi.sqlite'
conn=sqlite3.connect(db_file)
c=conn.cursor()

#lesson about creating dbs and tables
c.execute("CREATE TABLE IF NOT EXISTS Dokimastiko (abcd, efgh, jklm)")
# using c.execute(""" (triple") I can have multiple lines without \   """
conn.commit()
c.execute("INSERT INTO Dokimastiko VALUES (?,?,?)",(123, 456, 'nakajue'))
conn.commit()
conn.close() #  must do this to FREE RAM!!!
