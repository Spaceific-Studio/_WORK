# -*- coding: utf-8 -*-
import numpy as np
np.set_printoptions(threshold='nan')
import os
import math
import csv
import random
random.seed()
from PIL import Image, ImageDraw
print 0/9
#myImage = Image.open(r"/storage/18D4-6C41/CA/_moje pokusy/CELULAR_AUTOMAT-2D/IMG/CA2D2_00000000000000100000110011000000_51x51/014_51x51.jpg")
#myImgW = myImage.size[0]
#for x in np.nditer(myData): 
#print myData[0:myDataLen:4]
#myArray = np.array(((0,0,0,255),(0,0,0,255),(255,255,255,255),(0,0,0,255),(0,0,0,255)))
#myArrayLen = len(myArray)
#print myArrayLen
#myPixel = myImage.getpixel((20,1))
#print myPixel
#myPilImg = Image.fromarray(myData)
#myNewImage = Image.new("RGBA",(200,200))
#myNewImageBit = Image.new("L",(200,200))
#myNewImageBit2 = Image.new("1",(200,200))
#myDrawObject = ImageDraw.Draw(myNewImage)
#myDrawObjectBit = ImageDraw.Draw(myNewImageBit)
#myDrawObjectBit2 = ImageDraw.Draw(myNewImageBit2)
#myDrawObject.point([(5,5),(20,5),(20,6),(21,6),(100,20)],(255,255,255,255))
#myDrawObjectBit.point([(5,5),(20,5),(20,6),(21,6),(100,20)],255)
#myDrawObjectBit2.point([(5,5),(20,5),(20,6),(21,6),(100,20)],1)
#myNewImage.save("myImage2.jpg")
#myNewImageBit.save("myImage3.jpg")
#myNewImageBit2.save(r"/storage/emulated/0/CA/_moje pokusy/CELULAR_AUTOMAT-2D/IMG/myImageBit2.jpg")
#with open(r"/storage/emulated/0/CA/_moje pokusy/CELULAR_AUTOMAT-2D/)
dirPath = r"/storage/emulated/0/CA/_moje pokusy/CELULAR_AUTOMAT-2D/IMG/"
generateRandom = True

def getSourceRule(inGenerateRandom):
   if inGenerateRandom == True:
      myRule = ""
      for i in range(0,32):
         myRule += str(random.randint(0,1))
      return myRule
   else:
      return "10101010100010011110010110001100"
      
sourceRule = getSourceRule(generateRandom)
sourceRuleArray = [int(x) for x in sourceRule]
#print sourceRuleArray
print "CURRENT RULE: \n" + sourceRule
resolutionX = 51
resXstr = str(resolutionX)
resolutionY = 51
resYstr = str(resolutionY)
slashChar = r"/"
finalDirPath = dirPath + "CA2D2_" + sourceRule + "_" + resXstr + "x" + resYstr + slashChar
#binNum = [1,1,1,1,1]
#binStr = ""
#for i in binNum:
#    binStr += str(binNum[i])
#print binStr

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
    
    
def createFirstLayerFromScratch(inResX, inResY):
    firstLayer = Image.new("1",(inResX,inResY))
    firstLayerDraw = ImageDraw.Draw(firstLayer)
    firstLayerDraw.point((inResX/2, inResY/2), 1)
    return firstLayer

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

def getInspArray2():
    returnArray = np.array(
    	                     [[0,0,255,255,255],
    	                     	[255,0,255,255,0],
    	                     	[255,255,255,0,0],
    	                     	[0,255,255,0,255],
    	                     	[255,0,0,255,255],
    	                     	[255,255,0,0,255],
    	                     	[255,0,255,255,255],
    	                     	[255,255,255,0,255],
    	                     	[0,255,0,255,255],
    	                     	[255,255,0,255,0],
    	                     	[0,255,255,255,255],
    	                     	[255,255,255,255,0],
    	                     	[255,0,255,0,255],
    	                     	[0,255,255,255,0],
    	                     	[255,255,0,255,255],
    	                     	[255,255,255,255,255],	
    	                     	[0,0,0,0,0],
    	                     	[0,0,255,0,0],
    	                     	[255,0,0,0,255],
    	                     	[0,255,0,255,0],22
    	                     	[0,0,0,0,255],
    	                     	[255,0,0,0,0],
    	                     	[0,0,255,0,255],
    	                     	[255,0,255,0,0],
    	                     	[0,0,0,255,0],
    	                     	[0,255,0,0,0],
    	                     	[0,0,255,255,0],
    	                     	[0,255,255,0,0],
    	                     	[255,0,0,255,0],
    	                     	[0,0,0,255,255],
    	                     	[0,255,0,0,255],
    	                     	[255,255,0,0,0]],
    	                     	np.int32)
    return returnArray

def getInspArray(inArLenght):
    rulesCount = pow(2, inArLenght)
    arRange = range(0, rulesCount)
#    binSeqDiv = [pow(2, x) for x in range(0,inArLenght)]
#    binSeqDiv.reverse()
#    myArray = [[math.trunc(x / y) % 2 for x in arRange] for y in binSeqDiv]
#    myArray = map(list, zip(*myArray))
#    returnArray = [[]]
#    for i in arRange:
#        myChars = ""
#        for j in myArray[i]:
#            myChars += str(myArray[i][j])
#        returnArray[i] = myChars 
    return arRange

def getRule(inRules, inInspArray, XYu, XfY, XY, XbY, XYd):
    myPixels = str(XYu) + str(XfY) + str(XY) + str(XbY) + str(XYd)
    rulePosition = int(myPixels, 2)
    return inRules[rulePosition]

def createNextLayer(inFormerImg, inRules, inInspArray, inLaysCount):
    myFImgData = np.array(inFormerImg.getdata())
    liWidth = inFormerImg.size[0]
    liHeight = inFormerImg.size[1]
    liLength = len(myFImgData)
    returnImgs = []
    for l in range(0, inLaysCount):
        truePixs = []
        nextImg = Image.new("1",(liWidth, liHeight))
        nextImgDraw = ImageDraw.Draw(nextImg)
        for a, x in enumerate(myFImgData):
            if (a % liWidth > 0) and (a % liWidth < liWidth -1) and a > liWidth and a < liLength - liWidth:
                XYu = returnOne(myFImgData[a - liWidth])
                XfY = returnOne(myFImgData[a - 1])
                XY = returnOne(myFImgData[a])
                XbY = returnOne(myFImgData [a + 1])
                XYd = returnOne(myFImgData[a + liWidth])
                rule = getRule(inRules, inInspArray, XYu, XfY, XY, XbY, XYd)
                if rule == 1:
#                  truePixs.append([a / liWidth, a % liWidth])
                   truePixs.append((a / liWidth, a % liWidth))
        nextImgDraw.point(truePixs, 1)
        myFImgData = np.array(nextImg.getdata())
        returnImgs.append(nextImg)
#    nextImgData = np.array(nextImg.getdata())
    return returnImgs
    
def loadLastLayer(inDirPath):
    myDir = []
    truePixs = [[]]
    lastImg = Image
    liWidth = 0
    liHeight = 0
    if os.path.isdir(inDirPath):
        myDir = os.listdir(inDirPath)
        myDir.sort()
    if len(myDir) != 0:
        lastImg = Image.open(inDirPath + myDir[len(myDir)-1])
        lastImg.convert("1")
        lastImg.tobitmap(lastImg)
        print "LAST IMAGE: " +myDir[len(myDir)-1]
        print "colors = " + str(lastImg.getcolors())
    else:
        return null
 #   myImgData = np.array(lastImg.getdata())
#    liWidth = lastImg.size[0]
#    liHeight = lastImg.size[1]
#    ind = 0
#    for a, x in enumerate(myImgData):
#        if x == 1:
#            truePixs.append([a / liWidth, a % liWidth])
#            ind += 1
    return lastImg
    
def returnOne(inNum):
    if inNum > 1:
        return 1
    else:
        return inNum

layNum = getLayNum(finalDirPath)
print "CURRENT GENERATION: " + str(layNum)
myInspArray = getInspArray(5)
#print myInspArray
#print getRule(sourceRuleArray, myInspArray, 1, 1, 1, 1, 0) 
#print loadLastLayer(sourceRule, finalDirPath)
properLayNum = getProperLayNum(layNum)
imageFormat = "bmp"
layersCount = 100
if layNum == 0:
    firstLayer = createFirstLayerFromScratch(resolutionX, resolutionY)
    ensure_dir(finalDirPath)
    firstLayer.save(finalDirPath + properLayNum + "_" + resXstr + "x" + resYstr + "." + imageFormat)
    layNum += 1
    myLastImg = firstLayer
    myNextLayers = createNextLayer(myLastImg, sourceRuleArray, myInspArray, layersCount-1)
    for c in myNextLayers:
        layNum += 1
        properLayNum = getProperLayNum(layNum)
        c.save(finalDirPath + properLayNum + "_" + resXstr + "x" + resYstr + "." + imageFormat)
else:
    myLastImg = loadLastLayer(finalDirPath)
    myNextLayers = createNextLayer(myLastImg, sourceRuleArray, myInspArray, layersCount)
    for c in myNextLayers:
        layNum += 1
        
        properLayNum = getProperLayNum(layNum)
        c.save(finalDirPath + properLayNum + "_" + resXstr + "x" + resYstr + "." + imageFormat)
#   print "myImgData " + ": " + str(myNextLayers) 


