import chardet
#from fold_to_ascii import fold
from chardet.universaldetector import UniversalDetector
import os
dir = r"/storage/emulated/0/Download/"
fileName = "md5sum.txt"
filePath = os.path.join(dir, fileName)
detector = UniversalDetector()
oFile = open(filePath)
for line in oFile.readlines():
    detector.feed(line)
    if detector.done():
        break
detector.close()
oFile.close()
print(detector.result())
