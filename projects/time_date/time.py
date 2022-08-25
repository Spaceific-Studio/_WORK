import time
from datetime import datetime, timedelta, tzinfo
print("epoch time 0 {0}".format(time.gmtime(0)))
print("gmtime time now {0}".format(time.gmtime()))
print("gmtime time tm_mday now {0}".format(time.gmtime()[3]))
print("strftime() now %y {0}".format(time.strftime("%y")))
print("strftime() now %a {0}".format(time.strftime("%a")))
print("strftime() now %X {0}".format(time.strftime("%X")))
print("strftime() now %x {0}".format(time.strftime("%x")))
print("strftime() now %Z {0}".format(time.strftime("%Z")))
print("strftime() now %z {0}".format(time.strftime("%z")))
print("strftime() now %U {0}".format(time.strftime("%U")))
print("strftime() now %W {0}".format(time.strftime("%W")))
print("strftime() now %w {0}".format(time.strftime("%w")))

myDT = datetime.strptime("2022_04_12", "%Y_%m_%d")
nowDT = datetime.now()
print("myDT {0} now {1}".format(myDT, nowDT))
if myDT > nowDT:
    print("myDT > now")
else:
    print("myDT < now")

dTime = 10
timeDelta = timedelta(10)
addDT = nowDT + timeDelta
#print("addDT {0} day {1}".format(addDT, addDT.strftime(datetime.strftime("%A"))))
print("time zone nowDT {0}".format(nowDT.strftime("%Z")))
    



