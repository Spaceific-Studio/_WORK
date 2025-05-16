import sys
import platform

if "Windows" in platform.uname():
	lib_path = r'C:/_WORK/PYTHON/LIB'
else:
	lib_path = r"/storage/18D4-6C41/PYTHON/LIB"

#library path for desktop station
#lib_path = r'C:\_WORK\PYTHON\LIB'

#library path for mobile android
#lib_path = r"/storage/18D4-6C41/PYTHON/LIB"
sys.path.append(lib_path)

from Ca2D import *

myCa = Ca2D_3x3()
myCa.setup(useRule="OR")
myCa.setAlphaNumRule("KCZ8C9444AIPO1RBO194DP2ASGNUCM3Z38M7K5LB20IC6E7WR1794P5V7JM0D39V1ZV436EB6CUK6CZZME9XRTXD07VQHELR8GW")
myCa.run()