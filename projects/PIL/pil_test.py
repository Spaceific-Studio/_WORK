import numpy as np
import PIL
from PIL import Image, ImageShow
import os
import subprocess

myArray = np.asarray([1,2,3,4,5,500,40,32],dtype=np.float32)
np.reshape(myArray,(int(myArray.shape[0]/2),2))
std = np.std(myArray)
mean = np.mean(myArray)
myArray -= mean
#print("myArray {0} {1} {2} {3}".format(myArray, myArray.shape, std, mean))
#print(dir(ImageShow.Viewer))
#print(ImageShow.Viewer.get_command)
myImg = Image.open("download_20200830_124806.jpg")
#ImageShow.register("Total Commander", order=1)
myImg.show()
displayImg = ImageShow.show(myImg)
#displayImg = ImageShow.show(myImg)
#print("{}".format(displayImg))
cmd = "am start -n com.google.android.contacts"
os.system(cmd)
cmd = "comp=$(adb shell cmd package resolve-activity --brief -c android.intent.category.LAUNCHER $pkg | tail -1)"
os.system(cmd)
cmd = "adb shell cmd activity start-activity $comp"
os.system(cmd)

#subprocess.call(["ls", "-l"])
#subprocess.call(["adb", "shell", "monkey", "-p", "com.microsoft.office.excel", "-c", "android.intent.category.LAUNCHER", "1"])
#subprocess.call(["adb shell monkey", "-p"])
#com.microsoft.office.excel