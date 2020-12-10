# -*- coding: utf-8 -*-
import numpy as np
np.set_printoptions(threshold='nan')
import os
from os import walk
import math
import csv
import random
random.seed()
from PIL import Image, ImageDraw

#with open(r"/storage/emulated/0/CA/_moje pokusy/CELULAR_AUTOMAT-2D/)
writeDirPath = r"C:/_WORK/PYTHON/CELULAR_AUTOMAT-2D/zaloha/q/"
#readDirPath = r"C:/_WORK/PYTHON/CELULAR_AUTOMAT-2D/RNDCA2D9-sequence/interesting/69800000800000208440000000000000800000200000208000000000000100008400000008000000480000000000000000000000000100008000000000120000/"
readDirPath = writeDirPath
generateRandom = True
      
sourceRule = "01110110110000001010011010000011"
sourceRuleArray = [int(x) for x in sourceRule]
#print sourceRuleArray
print "CURRENT RULE: \n" + sourceRule
#resolutionX = 51
#resXstr = str(resolutionX)
#resolutionY = 51
#resYstr = str(resolutionY)
slashChar = r"/"
#readDirPath = dirPath + "CA2D2_" + sourceRule + "_" + resXstr + "x" + resYstr + slashChar
#readDirPath = r"/storage/emulated/0/CA/_moje pokusy/CELULAR_AUTOMAT-2D/zaloha/CA2D2_01110110110010001010011010010011_101x101-900-999/"
sequenceRange = range(0,5)
def getText():
    returnString = "asrffhhhjgfghh"
    return returnString
    
def writeFile(inData, inFullName):
    with open(inFullName, 'wb') as myFile:
        myFile.write(inData)
        
def run(inDirNames,inReadDirPath, inWriteDirPath):
#    numOfLayers = 100
    myData = loadLayers(inReadDirPath + inDirNames)
    # print "myData[0]"
    # print myData[0]
    # print "myData[1]"
    # print myData[1]
    myString = createTextForSCAD(myData[0], myData[1], inWriteDirPath, myData[2][0], myData[2][1])
    myString2 = createSCADconvex(myData[0], myData[1], inWriteDirPath, myData[2][0], myData[2][1])

    
def runSequence(inRange,inReadDirPath, inWriteDirPath):
    myDirs = loadDirs(inReadDirPath, inRange)
    print "myDirs :"
    print myDirs
    ensure_dir(inWriteDirPath)
    for d in myDirs:
        run(d,inReadDirPath,inWriteDirPath)

    
def loadDirs(inDirPath, inRange):
    myDirs = []
    f =[]
    returnData = []
    liWidth = 0
    liHeight = 0
    if os.path.isdir(inDirPath):
        myDirs = os.listdir(inDirPath)
        myDirs.sort()
    if inRange[0] <= len(myDirs):
        startLayer = inRange[0]
        print "startLayer: " +str(startLayer) + " total dirs " + str(len(myDirs))
    else:
        return []
    if inRange[len(inRange)-1] <= len(myDirs):
        endLayer = len(inRange)-1
    elif inRange[len(inRange)-1] > len(myDirs):
        endLayer = len(myDirs) - 1
    else:
        return []
    for (path, dirnames, filenames) in walk(inDirPath): 
        f.extend(dirnames) 
        break
#    for j, s in enumerate(f):
#        f[j] = inDirPath + s
#    print myDirs[: inRange[len(inRange)-1]]
#    print f[inRange[0]:inRange[len(inRange)-1]]
    f.sort()
#    print f[inRange[0]:inRange[len(inRange)-1]]
    print "endLayer: " + str(endLayer)
    return f[inRange[0]: (inRange[len(inRange)-1])+1]
   
def getLayNum(inDirPath):
    myDir = []
    layNum = int
    if os.path.isdir(inDirPath):
        myDir = os.listdir(inDirPath)
#        myDir.sort
        myLayNum = len(myDir)
        return myLayNum
    else:
        return 0
    
def ensure_dir(file_path):
    directory = os.path.dirname(file_path) 
    if not os.path.exists(directory):
        os.makedirs(directory)
        
def getProperLayNum(inLayNum):
    returnString = ""
    inLayNumStr = str(inLayNum)
    if len(inLayNumStr) == 1:
        returnString = "00" + inLayNumStr
    elif len(inLayNumStr) == 2:
        returnString = "0" + inLayNumStr
    else:
        returnString = inLayNumStr
    return returnString

def createTextForSCAD(inData, inDirName, inWrightDirPath, inWidth, inHeight):
    splitedPath = inDirName.split("/")
#    print splitedPath[len(splitedPath)-1]
    returnString = " \n"
    returnString += "wallWidth = 4;\n"    
    returnString += "zStart = 0;\n"
    returnString += "zMax = 60;\n"
    returnString += "for(z=[zStart: (len(myBoolMx)-1) < zMax ? (len(myBoolMx)-1) : zMax]) \n"
    returnString += "{\n"
    returnString += "   for(y=[0:(len(myBoolMx[z])-1)]) \n"
    returnString += "   { \n"
    returnString += "      for(x=[0:(len(myBoolMx[z][y])-1)]) \n"
    returnString += "      { \n"
    returnString += "//substracted void from inner structure offseted by wallWidth parameter \n"
    returnString += "         if(myBoolMx[z][y][x] == 1 && (z<len(myBoolMx) && y<len(myBoolMx[z]) && x<len(myBoolMx[z][y]) && ((y<wallWidth + 1 || y>(len(myBoolMx[z]) - (wallWidth + 2)) || (x < wallWidth + 1 || x>(len(myBoolMx[z][y]) - (wallWidth + 2))))))) \n"
    returnString += "//substracted void from surface offseted by wallWidth parameter \n"
    returnString += "//         if(myBoolMx[z][y][x] == 1  && ((y>wallWidth + 1 && y<(len(myBoolMx[z]) - (wallWidth + 2)) && (x > wallWidth + 1 && x<(len(myBoolMx[z][y]) - (wallWidth + 2)))))) \n"
    returnString += "//middle cross section XZ plane\n"
    returnString += "//         if(myBoolMx[z][y][x] == 1 && (z<len(myBoolMx) && y<(len(myBoolMx[z])/2) && x<len(myBoolMx[z][y])))\n"
    returnString += "//middle cross section YZ plane\n"
    returnString += "//         if(myBoolMx[z][y][x] == 1 && (z<len(myBoolMx) && y<len(myBoolMx[z]) && x<(len(myBoolMx[z][y])/2)))\n"
    returnString += "//diagonal section 1\n"
    returnString += "//         if(myBoolMx[z][y][x] == 1 && (z<len(myBoolMx) && y>(len(myBoolMx[z][y])-x)) && x<(len(myBoolMx[z][y])))\n"
    returnString += "//diagonal section 2\n"
    returnString += "//         if(myBoolMx[z][y][x] == 1 && (z<len(myBoolMx) && y<len(myBoolMx[z]) && x>y))\n"
    returnString += "//full volume structure\n"
    returnString += "//         if(myBoolMx[z][y][x] == 1) \n"
    returnString += "         { \n"
    returnString += "            translate([x,y,z])\n"
    returnString += "            { \n"
    returnString += "               cube(1.2); \n"
    returnString += "            } \n"
    returnString += "         } \n"
    returnString += "      } \n"
    returnString += "   } \n"
    returnString += "} \n"
    returnString += " \n"
    returnString += "myBoolMx = ["
    for b, z in enumerate(inData):
        returnString += "["
        for a, y in enumerate(z):
            if a%inWidth == 0 and a == 0:
                returnString += "[" + str(returnOne(y[0])) + ", "
            elif a%inWidth == 0 and a > 0:
                returnString += "], [" + str(returnOne(y[0])) + ", "
            elif a%inWidth == inWidth - 1 and a > 0:
                returnString += str(returnOne(y[0]))
            else:
                returnString += str(returnOne(y[0])) + ", "
            if a == len(z)-1:
                returnString += "]"
#            returnString += "-" + str(a) + "-"
        if b != len(inData)-1:
            returnString += "],"
        else:
            returnString += "]"
    returnString += "]; \n"
    fileName = splitedPath[len(splitedPath)-1] + "x" + str(len(inData)) +"_cube.scad"
    fullName = inWrightDirPath + fileName
    writeFile(returnString, fullName)
    print "saved :" + fullName
    return returnString
    
def createSCADconvex(inData, inDirName, inWrightDirPath, inWidth, inHeight):
    splitedPath = inDirName.split("/")
    print splitedPath[len(splitedPath)-1]
    returnString = "\n"
    returnString += "sphereRadius = 0.1; \n"
    returnString += "wallWidth = 4; \n"
    returnString += "$fn = 2; \n"
    returnString += "zStart = 0;\n"
    returnString += "zMax = 60;\n"
    returnString += "\n"
    returnString += "//for(z=[zStart:(len(myBoolMx)-1)]) \n"
    returnString += "for(z=[zStart: (len(myBoolMx)-1) < zMax ? (len(myBoolMx)-1) : zMax])\n"
    returnString += "{ \n"
    returnString += "   for(y=[0:(len(myBoolMx[z])-1)]) \n"
    returnString += "   { \n"
    returnString += "      for(x=[0: len(myBoolMx[z][y])-1]) \n"
    returnString += "      { \n"
    returnString += "//substracted void from inner structure by wallWidth parameter      \n"
    returnString += "         if(z<len(myBoolMx) && y<len(myBoolMx[z]) && x<len(myBoolMx[z][y]) && ((y<wallWidth || y>(len(myBoolMx[z]) - (wallWidth +2)) || (x < wallWidth || x>(len(myBoolMx[z][y]) - (wallWidth + 2)))))) \n"
    returnString += "//substracted void from surface offseted by wallWidth parameter  \n"
    returnString += "//         if(z<len(myBoolMx) && y<len(myBoolMx[z]) && x<len(myBoolMx[z][y]) && ((y>wallWidth + 1 && y<(len(myBoolMx[z]) - (wallWidth + 2)) && (x > wallWidth + 1 && x<(len(myBoolMx[z][y]) - (wallWidth + 2)))))) \n"
    returnString += "//middle cross section XZ plane\n"
    returnString += "//         if(z<len(myBoolMx) && y<(len(myBoolMx[z])/2) && x<len(myBoolMx[z][y]))\n"
    returnString += "//middle cross section YZ plane\n"
    returnString += "//         if(z<len(myBoolMx) && y<(len(myBoolMx[z])) && x<(len(myBoolMx[z][y])/2))\n"
    returnString += "//diagonal section 1\n"
    returnString += "//         if(z<len(myBoolMx) && y>len(myBoolMx[z][y])-x && x<(len(myBoolMx[z][y])))\n"
    returnString += "//diagonal section 2\n"
    returnString += "//         if(z<len(myBoolMx) && y<len(myBoolMx[z]) && x>y)\n"
    returnString += "//full volume structure\n"
    returnString += "//         if(z<len(myBoolMx) && y<len(myBoolMx[z]) && x<len(myBoolMx[z][y]))\n"
    returnString += "         {\n"
    returnString += "             point1 = myBoolMx[z][y][x] == 1 ? [x,y,z] : [];\n"
    returnString += "             point2 = myBoolMx[z][y][x+1] == 1 ? [x+1,y,z] : []; \n"
    returnString += "             point3 = myBoolMx[z][y+1][x] == 1 ? [x,y+1,z] : [];\n"
    returnString += "             point4 = myBoolMx[z][y+1][x+1] == 1 ? [x+1,y+1,z] : [];\n"
    returnString += "             point5 = myBoolMx[z+1][y][x] == 1 ? [x,y,z+1] : [];\n"
    returnString += "             point6 = myBoolMx[z+1][y][x+1] == 1 ? [x+1,y,z+1] : [];\n"
    returnString += "             point7 = myBoolMx[z+1][y+1][x] == 1 ? [x,y+1,z+1] : [];\n"
    returnString += "             point8 = myBoolMx[z+1][y+1][x+1] == 1 ? [x+1,y+1,z+1] : [];\n"
    returnString += "             hull()\n"
    returnString += "             {\n"
    returnString += "                 if(len(point1) > 0) {color(\"blue\") translate(point1) sphere(sphereRadius);}\n"
    returnString += "                 if(len(point2) > 0) {color(\"blue\") translate(point2) sphere(sphereRadius);}\n"
    returnString += "                 if(len(point3) > 0) {color(\"blue\") translate(point3) sphere(sphereRadius);}\n"
    returnString += "                 if(len(point4) > 0) {color(\"blue\") translate(point4) sphere(sphereRadius);}\n"  
    returnString += "                 if(len(point5) > 0) {color(\"blue\") translate(point5) sphere(sphereRadius);}\n"    
    returnString += "                 if(len(point6) > 0) {color(\"blue\") translate(point6) sphere(sphereRadius);}\n"
    returnString += "                 if(len(point7) > 0) {color(\"blue\") translate(point7) sphere(sphereRadius);}\n"
    returnString += "                 if(len(point8) > 0) {color(\"blue\") translate(point8) sphere(sphereRadius);}\n"   
    returnString += "             }\n"
    returnString += "         }\n"
    returnString += "      }\n"
    returnString += "   }\n"
    returnString += "}\n"
    returnString += "\n"
    returnString += "myBoolMx = ["
    for b, z in enumerate(inData):
        returnString += "["
        for a, y in enumerate(z):
            if a%inWidth == 0 and a == 0:
                returnString += "[" + str(returnOne(y[0])) + ", "
            elif a%inWidth == 0 and a > 0:
                returnString += "], [" + str(returnOne(y[0])) + ", "
            elif a%inWidth == inWidth - 1 and a > 0:
                returnString += str(returnOne(y[0]))
            else:
                returnString += str(returnOne(y[0])) + ", "
            if a == len(z)-1:
                returnString += "]"
#            returnString += "-" + str(a) + "-"
        if b != len(inData)-1:
            returnString += "],"
        else:
            returnString += "]"
    returnString += "]; \n"
   
    fileName = splitedPath[len(splitedPath)-1] + "x" + str(len(inData)) +"_convexHull.scad"
    fullName = inWrightDirPath + fileName
    writeFile(returnString, fullName)
    print "saved :" + fullName
    return returnString
           
def loadLayers(inDirPath):
    myDir = []
#    truePixs = [[]]
#    returnImages = []
    returnData = []
    lastImgSize =[]
#    liWidth = 0
#    liHeight = 0
    if os.path.isdir(inDirPath):
        myDir = os.listdir(inDirPath)
        myDir.sort()
#    if inRange[0] <= len(myDir):
#        startLayer = inRange[0]
#        print "startLayer: " +str(startLayer)
#    else:
#        return []
#    if inRange[len(inRange)-1] <= len(myDir):
#        endLayer = len(inRange)-1
#    elif inRange[len(inRange)-1] > len(myDir):
#        endLayer = len(myDir) - 1
#    else:
#        return []
#    print myDir
#    print "endLayer: " + str(endLayer)
    if len(myDir) != 0:
        for i in myDir:
            lastImg = Image.open(inDirPath + "/" + i)
            lastImgSize = lastImg.size
            lastImg.convert("RGBA")
            #lastImg.tobitmap(lastImg)
            returnData.append(lastImg.getdata())
            print "LAST LOADED IMAGE: " + i
            print "colors = rs = " + str(lastImg.getcolors())
    else:
        return []
#    for x in returnData:
#        print "img " + str(x)
#        for y in x:
#            print y
    return [returnData,inDirPath,lastImgSize]
    
def returnOne(inNum):
    if inNum > 1:
        return 1
    else:
        return inNum

layNum = getLayNum(readDirPath)
print "LAST GENERATION: " + str(layNum)

properLayNum = getProperLayNum(layNum)
#imageFormat = "bmp"
layersCount = 100
runSequence(sequenceRange, readDirPath, writeDirPath) 


