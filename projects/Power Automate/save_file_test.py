import os
import time
import random
print(time.ctime())
with open(r'H:/test.txt', mode='a') as file:
	file.writelines("{0} - {1}\n".format(time.ctime(), random.randint(0,12)))
	file.close()