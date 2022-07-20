import pip
import distutils
import os
from os import walk
#import numpy
import setuptools
#from PIL import Image
#import pyglet

#os.system(r"pip install tensorflow")
#os.system(r"C:\Users\GercakD\AppData\Local\Programs\Python\Python310\Scripts -m pip install pyncclient")
#print(dir(pip))
pip.main(['install', 'pyncclient'])
#print(dir(pip))
#os.system(r"/data/user/0/org.qpython.qpy/files/bin/pip install gmpy2-2.1.0a1-cp27-cp27mu-manylinux1_x86_64.whl")
#cfg_vars = distutils.sysconfig.get_config_vars()
#include_dir = cfg_vars['CONFINCLUDEDIR']
#include_dirs = [numpy.get_include(), include_dir]
#include_files = os.listdir(include_dir)
#print cfg_vars
#dirs = os.get_exec_path()
#print __name__
''' def printEnvs():
    envir = os.environ
    for key, value in envir.items():
        print (key)
        for x in value.split(":"):
            print (x)
        print ("\n") '''
#print os.getenv('PATH').split(":")
#printEnvs()
#help (str)
#loadPath = r"/data/user/0/org.qpython.qpy/files/lib/python2.7/site-packages/kivy_u4_qpython-1.10.0-py2.7.egg/kivy/uix/"
#loadPath = r"/data/user/0/org.qpython.qpy/files/bin/"
#loadPath = r"/data/user/0/"
#baseLoadPath = loadPath.split("org.qpython.qpy/")
#print baseLoadPath
#fileName = "pkg_resources.py"
#fileName = "scatter.py"
#baseSavePath = r"/storage/emulated/0/CA/_moje pokusy/CELULAR_AUTOMAT-2D/zaloha/data_qpython/"
#saveFName = "pyRead.txt"

def readDir(inLoadPath):
    print ("\ndir content: ")
    print (inLoadPath + "\n")
    d = []
    f = []
    for (path, dirnames, filenames) in walk(inLoadPath): 
        d.extend(dirnames) 
        f.extend(filenames) 
        break
    f.sort()
    d.sort()
    for key, value in enumerate(d):
        print ("D" + str(key) + " + " + value)
    for key, value in enumerate(f):
        print ("f" + str(key) + " + " + value)
#myDirs = os.listdir(r"/data/user/0/org.qpython.qpy/files/lib/python2.7/site-packages/pip/")

def readFile(inLoadPath, inFName, inBSPath, inSFName, inBLPath):
    myF = open(inLoadPath + inFName)
    print ("\n opened file: ")
    print (str(myF) + "\n")
#    help(myF)
#    myString = ""
#    content = myF.readlines()
#    for line in content:
#        print line
#    while True:
#        reader = myF.read()
#        if reader == "":
#            break
#        else:
#            myString += reader
#    myF.close()
#    print myString
#    ensure_dir(inBSPath + inBLPath[1])
#    mySF = open(inBSPath + inBLPath[1] + inFName, 'w')
#    mySF.write(myString)
#    print "file was saved: "
#    print str(mySF)
#    mySF.close()

def ensure_dir(file_path):
    directory = os.path.dirname(file_path) 
    if not os.path.exists(directory):
        os.makedirs(directory)
        
#readDir(loadPath)
#readFile(loadPath, fileName, baseSavePath, saveFName, baseLoadPath)

