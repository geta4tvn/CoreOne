import time
import datetime
time.strftime('{%Y-%m-%d %H:%M}')


now=time.time()
print('start=',now)
intn=int(now)
print('start integer=',intn)
humanread=datetime.datetime.fromtimestamp(intn)
print('-------------------------START= ',humanread)

time.sleep(3)

#========================================================================================
# THIS IS HOW YOU CAN STORE FUNCTIONS IN SQLITE AND EXECUTE THEM
jim=123
kom=3
phrase="print('This is the result of executing code stored in simple STRING!:',jim*kom)"
exec(phrase)
#========================================================================================
# I was thinking of using sqlite to store error functions, but this is TOO MUCH
#========================================================================================


later=time.time()
intl=int(later)
print('stop=',later)
print('later integer',intl)
millisecondsdiff=int(1000*(later-now))
print('diff=',later-now)
print('milsec=',millisecondsdiff,'msec')


humanread=datetime.datetime.fromtimestamp(intl)

print('-------------------------STOP= ',humanread)