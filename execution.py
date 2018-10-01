import sqlite3
from sqlite3 import Error

def ektelese(x):
    global SystemState
    SystemState=x
    print('-------  we are in execution.ektelese()')

    print('OpMode',SystemState.OpMode)
    SystemState.SaveCurStat()
    print('I just executed a function belonging to a class from another module!!!!!!')
    print('Time Stamp is',SystemState.OpenRcptTStamp)
