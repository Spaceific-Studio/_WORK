import os
import time
import random
import nextcloud_client
import os
import sys
import py_compile

py_compile("save_file_test.py")

ncAdress = 'https://cloud.quorum.sk'
nc = nextcloud_client.Client(ncAdress)
nc.login('dano', 'Danger43849')
#fromDirName = "/storage/emulated/0/Download"

#source directory
fromDirName = 'C:\\Users\\GercakD\\OneDrive - pvs.cz\\H'
#source file name
fromFileName = r'test.txt'
#destination directory
toDirName = 'testdir3'
#destination file name
toFileName = fromFileName

print(time.ctime())
with open(os.path.join(fromDirName, fromFileName), mode='a') as file:
	file.writelines("{0} - {1}\n".format(time.ctime(), random.randint(0,12)))
	file.close()


try:
    nc.mkdir(toDirName)
except Exception as ex:
    print("Unable to create directory {0}, wrong path or directory allready created  - {1}".format(toDirName, sys.exc_info()))


print("cwd {0}".format(os.getcwd()))
print("from path {0}".format(os.path.join(fromDirName, fromFileName)))
print("to path {0}".format(os.path.join(toDirName, toFileName)))
try:
    nc.put_file(os.path.join(toDirName, toFileName), os.path.join(fromDirName,fromFileName))
    print("File {0} successfuly copied from {1} to {2}.../{3}".format(fromFileName, fromDirName, ncAdress, toDirName))
except Exception as ex:
    print("Unable to copy file {0} from {1} to {2} - {3}".format(fromFileName, fromDirName, toDirName, sys.exc_info()))