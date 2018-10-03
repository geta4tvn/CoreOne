import sqlite3
from sqlite3 import Error

def ektelese(x,y,z):
    global SystemState
    SystemState=x
    global NewLine
    NewLine=y

    print('-------  we are in execution.ektelese()')


    SystemState.SaveCurStat()
    print('I just executed a function belonging to a class from another module!!!!!!')
    print('Time Stamp is',SystemState.OpenRcptTStamp)
