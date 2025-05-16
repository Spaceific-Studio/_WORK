# -*- coding: utf-8 -*-
import numpy as np
np.set_printoptions(threshold='nan')
import os
import math
import csv
import random
random.seed()
from PIL import Image, ImageDraw
dirPath = r"/storage/emulated/0/CA/_moje pokusy/CELULAR_AUTOMAT-2D/IMG2/"
CSV_logPath = r"/storage/emulated/0/CA/_moje pokusy/CELULAR_AUTOMAT-2D/CSV_log/IMG2/"
generateRandom = False
invertedRule = False
shiftDir = "N"
rndBaseRule = 0
writeLogFile = True
#         012345678910...15...20...25...30
myRule = "01101000100100001001000001100000"

def generateRandomRule():
    myRule = ""
    for i in range(0,32):
         myRule += str(random.randint(0,1))
    return myRule

def getSourceRule(inMyRule, inRandomRule, inGenerateRandom, inShiftDir, inRndBaseRule):
   myRule = inMyRule
   print "MY RULE: \n" + myRule
   if inGenerateRandom == True:
      myRule = inRandomRule
      if inShiftDir == "R":
          myRule = shiftRule(myRule, inShiftDir)
          print "MY RANDOM RIGHT SHIFTED RULE: \n" + myRule
          return myRule
      elif inShiftDir == "L":
          myRule = shiftRule(myRule, inShiftDir)
          print "MY RANDOM LEFT SHIFTED RULE: \n" + myRule
          return myRule
      else:
          return myRule
   elif inShiftDir == "R":
      myRule = shiftRule(myRule, inShiftDir)
      print "MY RIGHT SHIFTED RULE: \n" + myRule
      return myRule
   elif inShiftDir == "L":
      myRule = shiftRule(myRule, inShiftDir)
      print "MY LEFT SHIFTED RULE: \n" + myRule
      return myRule      
   else:
       if inRndBaseRule > 0:
           myRule = randomizeRule(myRule, inRndBaseRule)
           print "MY RANDOMIZED " + str(inRndBaseRule) + " DIGITS IN RULE: \n" + myRule
           return myRule
       else:
           return myRule

def shiftRule(inRule, direction):
    shiftedRule = ""
    if direction == "R":
        shiftedRule += inRule[len(inRule)-1]
        for i, s in enumerate(inRule):
            if i< len(inRule) -1:
                shiftedRule += s
    elif direction == "L":
        shiftedRule += inRule[1]
        firstChar = inRule[0]
        for i, s in enumerate(inRule):
            if i< len(inRule) -2:
                shiftedRule += inRule[i+2]
        shiftedRule += firstChar
    elif direction == "N":
        return inRule
    return shiftedRule
        
def randomizeRule(inRule, inDigCount):
    fRule = inRule
    retRule = ""
    returnRule = []
    if inDigCount>0:
        for x in range(0,inDigCount):
            nRule = ""
            rulePos = random.randint(0,31)
            for i, y in enumerate(fRule):
                if i == rulePos:
                    if y == "0":
                         nRule += "1"
                    else:
                         nRule += "0"                
                else:
                    nRule += y
            fRule = nRule
    return fRule   

def getInvertedRule(inRule):
    returnString = ""
    for i in inRule:
        if i == "0":
            returnString += "1"
        elif i == "1":
            returnString += "0"
    return returnString
myRandomRule = generateRandomRule()
sourceRule = getSourceRule(myRule, myRandomRule, generateRandom, shiftDir, rndBaseRule)
sourceRuleArray = [int(x) for x in sourceRule]
#print sourceRuleArray
print "CURRENT RULE: \n" + sourceRule
resolutionX = 51
resXstr = str(resolutionX)
resolutionY = 51
resYstr = str(resolutionY)
layersCount = 1000
slashChar = r"/"
finalDirPath = dirPath + "CA2D2b_" + sourceRule + "_" + resXstr + "x" + resYstr + slashChar
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
    myPixDatasLog = []
    if writeLogFile == True:
        f = open(CSV_logPath + myRule +"_b" + "_" + str(liWidth) + "x" + str(liHeight) + ".csv", 'w')
        writer = csv.writer(f)
    for l in range(0, inLaysCount):
        truePixs = []
#        testImg = Image.new("RGBA",(liWidth, liHeight))
#        testData = testImg.getdata()
#        for i in testData:
#            print i
        nextImg = Image.new("1",(liWidth, liHeight))
        nextImgDraw = ImageDraw.Draw(nextImg)
        myPixData = []
        for b in myFImgData:
            myPixData.append((0,0,0,255))
        if writeLogFile == True:
            writer.writerow([l])
        for a, x in enumerate(myFImgData):   
            pX = (a % liLength) % liWidth
            pY = ((a % liLength) - (a % liWidth)) / liWidth
            XYu = returnOne(myFImgData[((a % liLength) - liWidth) % liLength])
            XfY = returnOne(myFImgData[(a - 1) + (int(math.pow(0, pX))* liWidth)])
            XY = returnOne(myFImgData[a])
            XbY = returnOne(myFImgData[(a + 1) - (int(math.pow(0, (liWidth-1) - pX))*liWidth)])
            XYd = returnOne(myFImgData[((a % liLength) + liWidth) % liLength])
            rule = getRule(inRules, inInspArray, XYu, XfY, XY, XbY, XYd)
            if rule == 1:
#              truePixs.append([a / liWidth, a % liWidth])
               truePixs.append((pX, pY))
               myStrInspArray = str(XYu) + str(XfY) + str(XY) + str(XbY) + str(XYd)
               if writeLogFile == True:
                   writer.writerow([str(pY), str(pX), myStrInspArray, int(myStrInspArray, 2)])
#               if l == 0:
               myCol = (255,37,100,255)
#              myPixData[a] = (255,255,255,255)
#              myPixData[a - liWidth] = (myCol)
#              myPixData[a-1] = (myCol)
#              myPixData[a+1] = (myCol)
#              myPixData[a + liWidth] = (myCol)
#              testImg.putdata(myPixData)      
#              testImg.save(r"/storage/emulated/0/CA/_moje pokusy/testPix_" + str(l) + ".png")
        nextImgDraw.point(truePixs, 1)
        myFImgData = np.array(nextImg.getdata())
#        testImg.save(r"/storage/emulated/0/CA/_moje pokusy/testPix.png")
        returnImgs.append(nextImg)
        myPixDatasLog.append(myPixData.append)
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


