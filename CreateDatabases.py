import sqlite3
from sqlite3 import Error
import csv

# !!!  UNCOMMENT THE PART YOU WANT TO USE  !!!

folder='C:\\000 WORK 2017\\2 general\\00 2018 Tevin\\OUR ETR\\CharmSources\\'
dbStatic=folder+'static.sqlite'
dbJournal=folder+'journal.sqlite'




def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return None

conn=create_connection(dbStatic)       # ++++++++++++++   static.sqlite
#conn=create_connection(dbJournal)       # ++++++++++++++   journal.sqlite

c=conn.cursor()


# -------------------  THIS IS ONLY USED ONCE TO CREATE THE TABLES ---------------------------------------------------------------------
# ------------------- DATA HERE ARE STATIC meaning seldom changing - for everyday totals etc use JOURNAL db
#
# c.execute('''CREATE TABLE plu (barcode, description, department, category, PluGrp, price1, price2, price3, bonus, unit, \
# maxprice, stock, active, printDpt, emphasis, openprc, zeroprc, negprc, pack, autoclose, relatedPlu, relatedQR)''')
# # !!! N O T E !!! inside column names you CANNOT use sqlite keywords LIKE GROUP: injection attacks
# # You'll see errors like sqlite3.OperationalError: near "group": syntax error
#
# c.execute('''CREATE TABLE dpt (dptCode, description, VATclass, category, price1, price2, maxprice, active, \
# emphasis, openprice, zeroprc, negprc, inpack, autoclose)''')
#
# c.execute('''CREATE TABLE cat (catCode, description, CatGrp)''')
#
# c.execute('''CREATE TABLE clerks (clerkNum, clerkName, clerkPassw, clerkPerms)''')
# # ClerkPermissions:
# # A: lowest, can only sell with no discounts etc
# # B: normal, can sell, discount, take X, take Z
# # C: owner, can do all plus override with password the max price, max discount restrictions
# # D: god, will overwrite everything and will allow change of date/time, reseting etc
# # To secure this, D's password will have to be a hash of ECR's s/n with a god passw or other...
#
# c.execute('''CREATE TABLE params (ECRnum, ECRname, OwnerAFM, Hdr1, Hdr2, Hdr3, Hdr4, Hdr5, Hdr6, LogoTop, \
# Ftr1, Ftr2, Ftr3, Ftr4, LogoBot, language, globMaxPrc, globMaxQty, globMaxDay, globMaxDscnt, DeviceKey)''')
# # language: since I'll be using db for errors and menu messages, we can have columns for greek, english, swahili
#
# c.execute('''CREATE TABLE barcodes (leadPrc, leadWeight, leadOther)''')
#
#c.execute('''CREATE TABLE errors (Type, fromModule, fromFnc, shorthand, num, descriptionGR, descriptionEN, \
#descriptionSW, remedy)''')
#
# c.execute('''CREATE TABLE menu (level, descriptionGR, descriptionEN, descriptionSW, callsFnc, needsPermsLvl)''')
#
# c.execute('''CREATE TABLE VAT (VATa, VATb, VATc, VATd, VATe, VATex, TAXontotal1, TAXontotal2)''')
#
#c.execute('''CREATE TABLE templates (Template, TopLine,	TopSector, TopSector2, TopSector3, TopSector4, TopSector5, \
#TopSector6,	TopSector7,	Transactions, Total1, Total2, Total3, Total4, Total5, PayLine1,	PayLine2, PayLine3, \
#PayLine4, Footer1, Footer2,	Footer3, Footer4, Footer5, Footer6, Footer7, Last)''')

#c.execute('''CREATE TABLE customers (CustCode, TIN, TaxOffice, Brand, Name, Surname, Occupation, Address1, \
#Address2, Address3, Address4, Address5, Tel, Mobile, email, Notes, Credit, Debit, Balance, \
#CreditLimit, Upline, DownLine, LastTransDate, Turnover)''')

c.execute('''CREATE TABLE keyblayouts (num, keyDescription, ShiftLevel, key0, key1, key2, key3, key4, \
key5, key6, key7, key8, key9,key10, key11, key12, key13, key14,key15, key16, key17, key18, key19,key20, key21, key22, key23, key24, \
key25, key26, key27, key28, key29,key30)''')

# ================================================  END CREATING STATIC.SQLITE TABLES =====================================================


#**********************************************************************************************************************************************
#===============================   CREATE TABLES IN JOURNAL DATABASE  =========================================================================
#**********************************************************************************************************************************************
#c.execute('''CREATE TABLE ej (Znum, Rnum, AccNum, Tstamp, Date, Time, Clerk, CustNum, CustAFM,	a, SHAa, Total,	VATa, VATb,	VATc, \
#VATd, VATe, VATex, Tax1, Tax2, SHAe, Refunds, Discounts, Tickets, Voids, QtyKgr, QtyPcs, QR)''')

#c.execute('''CREATE TABLE details (Znum, Rnum, Timestamp, Date,	Time, PLUcode, PLUprice, PLUqty, DPTcode, DPTprice, DPTqty,	CATcode, \
#CATprice, CATqty, DiscCode, DiscAmnt, VoidCode, VoidAmnt, RefundCode, RefundQty, RefundAmnt, Ticket, Coupon, Total, Pmnt1, Pmnt2, Pmnt3)''')








# ==============================================================================
# ============ LOAD FROM CSV to PLU TABLE static sqlite  =======================
#===============================================================================
# arxeio_csv_PLU=folder+'plu data to csv.csv'
# with open(arxeio_csv_PLU) as csvDataFile:
#     csvReader = csv.reader(csvDataFile, delimiter=';')
#     for row in csvReader:
#         #print(row[1])
#         barcode=row[0]
#         description=row[1]
#         department=row[2]
#         category=row[3]
#         PluGrp=row[4]
#         price1=row[5]
#         price2=row[6]
#         price3=row[7]
#         bonus=row[8]
#         unit=row[9]
#         maxprice=row[10]
#         stock=row[11]
#         active=row[12]
#         printDpt=row[13]
#         emphasis=row[14]
#         openprc=row[15]
#         zeroprc=row[16]
#         negprc=row[17]
#         pack=row[18]
#         autoclose=row[19]
#         relatedPlu=row[20]
#         relatedQR=row[21]
#
#
#         c.execute("INSERT INTO plu VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);",(barcode, description, \
#         department, category, PluGrp, price1, price2, price3, bonus, unit, maxprice, stock, active, \
#         printDpt, emphasis, openprc, zeroprc, negprc, pack, autoclose, relatedPlu, relatedQR))
#         conn.commit()

#================================================================================================================
#===================  LOAD FROM CSV TO DEPARTMENTS TABLE IN STATIC.SQLITE DB   ==================================
#================================================================================================================
# arxeio=folder+'dpt.csv'
# with open(arxeio) as csvDataFile:
#     csvReader = csv.reader(csvDataFile, delimiter=';')
#     for row in csvReader:
#         #print(row[1])
#         dptcode=row[0]
#         description=row[1]
#         VATclass=row[2]
#         category=row[3]
#         price1=row[4]
#         price2=row[5]
#         maxprice=row[6]
#         active=row[7]
#         emphasis=row[8]
#         openprice=row[9]
#         zeroprc=row[10]
#         negprc=row[11]
#         inpack=row[12]
#         autoclose=row[13]
#
#
#
#         c.execute("INSERT INTO dpt VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?);",(dptcode, description,VATclass,category, \
#         price1, price2, maxprice, active, emphasis, openprice, zeroprc, negprc, inpack, autoclose))
#         conn.commit()


#=======================================================================================================================
#=======================    CLERKS CSV TO STATIC DATABASE ==============================================================
#=======================================================================================================================
# arxeio=folder+'clerks.csv'
# with open(arxeio) as csvDataFile:
#     csvReader = csv.reader(csvDataFile, delimiter=';')
#     for row in csvReader:
#         #print(row[1])
#         clerkNum=row[0]
#         clerkName=row[1]
#         clerkPassw=row[2]
#         clerkPerms=row[3]
#
#         c.execute("INSERT INTO clerks VALUES (?,?,?,?);",(clerkNum, clerkName, clerkPassw, clerkPerms))
#         conn.commit()

#=========================================================================================================================
#=======================   VAT                                                                                   =========
#=========================================================================================================================
# arxeio=folder+'vat.csv'
# with open(arxeio) as csvDataFile:
#     csvReader = csv.reader(csvDataFile, delimiter=';')
#     for row in csvReader:
#         #print(row[1])
#         VATa=row[0]
#         VATb=row[1]
#         VATc=row[2]
#         VATd=row[3]
#         VATe=row[4]
#         VATex=row[5]
#         TAXontotal1=row[6]
#         TAXontotal2=row[7]
#
#         c.execute("INSERT INTO VAT VALUES (?,?,?,?,?,?,?,?);",(VATa,VATb,VATc,VATd,VATe,VATex,TAXontotal1,TAXontotal2))
#         conn.commit()


#==============================================================================================================================
#=======================  PARAMETERS TABLE TO STATIC SQLITE    ================================================================
#==============================================================================================================================
#
# arxeio=folder+'params.csv'
# with open(arxeio) as csvDataFile:
#     csvReader = csv.reader(csvDataFile, delimiter=';')
#     for row in csvReader:
#         #print(row[1])
#         ECRnum=row[0]
#         ECRname=row[1]
#         OwnerAFM=row[2]
#         Hdr1=row[3]
#         Hdr2=row[4]
#         Hdr3=row[5]
#         Hdr4=row[6]
#         Hdr5=row[7]
#         Hdr6=row[8]
#         LogoTop=row[9]
#         Ftr1=row[10]
#         Ftr2=row[11]
#         Ftr3=row[12]
#         Ftr4=row[13]
#         logoBot=row[14]
#         language=row[15]
#         globMaxPrc=row[16]
#         globMaxQty=row[17]
#         globMaxDay=row[18]
#         globMaxDscnt=row[19]
#         DeviceKey=row[20]
#
#         c.execute("INSERT INTO params VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);",(ECRnum, ECRname, OwnerAFM, Hdr1, Hdr2, \
#         Hdr3, Hdr4, Hdr5, Hdr6, LogoTop, Ftr1, Ftr2, Ftr3, Ftr4, logoBot, language, globMaxPrc, globMaxQty, \
#         globMaxDay, globMaxDscnt, DeviceKey ))
#         conn.commit()


#==============================================================================================================================
#=======================  ERRORS TABLE TO STATIC SQLITE    ================================================================
#==============================================================================================================================

# arxeio=folder+'errors.csv'
# with open(arxeio) as csvDataFile:
#     csvReader = csv.reader(csvDataFile, delimiter=';')
#     for row in csvReader:
#         #print(row[1])
#         Type=row[0]
#         fromModule=row[1]
#         fromFnc=row[2]
#         shorthand=row[3]
#         num=row[4]
#         descriptionGR=row[5]
#         descriptionEN=row[6]
#         descriptionSW=row[7]
#         remedy=row[8]
#
#         c.execute("INSERT INTO errors VALUES (?,?,?,?,?,?,?,?,?);",(Type, fromModule, fromFnc, shorthand, num, \
#         descriptionGR, descriptionEN, descriptionSW, remedy))
#         conn.commit()

#
#
#================================================================================================================
#===================  LOAD FROM CSV TO templates TABLE IN STATIC.SQLITE DB   ==================================
#================================================================================================================
# arxeio=folder+'templates.csv'
# with open(arxeio) as csvDataFile:
#     csvReader = csv.reader(csvDataFile, delimiter=';')
#     for row in csvReader:
#         #print(row[1])
#         Template=row[0]
#         TopLine=row[1]
#         TopSector=row[2]
#         TopSector2=row[3]
#         TopSector3=row[4]
#         TopSector4=row[5]
#         TopSector5=row[6]
#         TopSector6=row[7]
#         TopSector7=row[8]
#         Transactions=row[9]
#         Total1=row[10]
#         Total2=row[11]
#         Total3=row[12]
#         Total4=row[13]
#         Total5=row[14]
#         PayLine1=row[15]
#         PayLine2=row[16]
#         PayLine3=row[17]
#         PayLine4=row[18]
#         Footer1=row[19]
#         Footer2=row[20]
#         Footer3=row[21]
#         Footer4=row[22]
#         Footer5=row[23]
#         Footer6=row[24]
#         Footer7=row[25]
#         Last=row[26]
#
#
#         c.execute("INSERT INTO templates VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);",(Template, TopLine, TopSector, TopSector2,\
#         TopSector3, TopSector4, TopSector5, TopSector6,	TopSector7,	Transactions, Total1, Total2, Total3, Total4, Total5, PayLine1,	PayLine2, PayLine3, \
#         PayLine4, Footer1, Footer2,	Footer3, Footer4, Footer5, Footer6, Footer7, Last))
#         conn.commit()
