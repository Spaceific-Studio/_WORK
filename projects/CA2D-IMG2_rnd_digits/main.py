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
    inRulesStr = ""
    for i in inRules:
        inRulesStr += str(i)
    if writeLogFile == True:
        f = open(CSV_logPath + inRulesStr + "_" + str(liWidth) + "x" + str(liHeight) + ".csv", 'w')
        writer = csv.writer(f)
    for l in range(0, inLaysCount):
        truePixs = []
        nextImg = Image.new("1",(liWidth, liHeight))
#        testImg = Image.new("1",(liWidth, liHeight))
        nextImgDraw = ImageDraw.Draw(nextImg)
#        testImgDraw = ImageDraw.Draw(testImg)
#        testData = testImg.getData()
        myPixData = []
        if writeLogFile == True:
            writer.writerow([l+1])
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
                   truePixs.append((a % liWidth, a / liWidth))
                   myStrInspArray = str(XYu) + str(XfY) + str(XY) + str(XbY) + str(XYd)
                   if writeLogFile == True:
                       writer.writerow([str(a % liWidth), str(a / liWidth), myStrInspArray, int(myStrInspArray, 2)])
        nextImgDraw.point(truePixs, 1)
        myFImgData = np.array(nextImg.getdata())
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

def run(inResX, inResY, inLayCount, inMyRule, inDirPath, inGenerateRandom, inShiftDir, inRndBaseRule):
    resXstr = str(inResX)
    resYstr = str(inResY)
    myRandomRule = generateRandomRule()
    sourceRule = getSourceRule(inMyRule, myRandomRule, inGenerateRandom, inShiftDir, inRndBaseRule)
    sourceRuleArray = [int(x) for x in sourceRule]
    print "CURRENT RULE: \n" + sourceRule
    slashChar = r"/"
    finalDirPath = inDirPath + "CA2D2_" + sourceRule + "_" + resXstr + "x" + resYstr + slashChar
    layNum = getLayNum(finalDirPath)
    print "CURRENT GENERATION: " + str(layNum)
    myInspArray = getInspArray(5)
    properLayNum = getProperLayNum(layNum)
    imageFormat = "bmp"
    
    if layNum == 0:
        firstLayer = createFirstLayerFromScratch(inResX, inResY)
        ensure_dir(finalDirPath)
        firstLayer.save(finalDirPath + properLayNum + "_" + resXstr + "x" + resYstr + "." + imageFormat)
        layNum += 1
        myLastImg = firstLayer
        myNextLayers = createNextLayer(myLastImg, sourceRuleArray, myInspArray, inLayCount-1)
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
    return sourceRule

def getInvertedDigit(inRule, inPos):
    returnString = ""
    listString = list(inRule)   
    if listString[inPos] == '0':
        listString[inPos] = '1'
    elif listString[inPos] == '1':
        listString[inPos] = '0'
    return ''.join(listString)

dirPath = r"/storage/emulated/0/CA/_moje pokusy/CELULAR_AUTOMAT-2D/IMG2/"
loadPath = r"/storage/emulated/0/CA/_moje pokusy/CELULAR_AUTOMAT-2D/interesting/"
CSV_logPath = r"/storage/emulated/0/CA/_moje pokusy/CELULAR_AUTOMAT-2D/CSV_log/IMG2/"
writeLogFile = True
generateRandom = False
invertedRule = False
shiftDir = "N"
rndBaseRule = 0
myRule = "01101000100000001000000000100000"
#myCurrentRule = myRule

resolutionX = 51
resolutionY = 51
layersCount = 100

def runRndSequence():
    rules = []
    for i in range(0, len(myRule)):
        rules.append(getInvertedDigit(myRule, i))
        run(resolutionX, resolutionY, layersCount, rules[i], dirPath, generateRandom, shiftDir, rndBaseRule)
        print "position " + str(i)
        
def runDirSequence(inLoadPath, inRange):
    rules = []
    f = []
    for (path, dirnames, filenames) in walk(inLoadPath): 
        f.extend(dirnames) 
        break
    f.sort()
    for i in f[inRange[0]:inRange[len(inRange)-1]]:
        splitedPath = i.split("_")
        rules.append(splitedPath[1])
#    for j, s in enumerate(f):
#        f[j] = inDirPath + s
    for i in rules:
        run(resolutionX, resolutionY, layersCount, i, dirPath, generateRandom, shiftDir, rndBaseRule)
    print rules
    
#runDirSequence(loadPath, range(49,60))   
runRndSequence()   
 
def runSequence():
    if generateRandom == True:
    #   NEW RANDOM RULE
        myNextRule = run(resolutionX, resolutionY, layersCount, myRule, dirPath, generateRandom, shiftDir, rndBaseRule)
    else:
        #MY RULE
        myNextRule = run(resolutionX, resolutionY, layersCount, myRule, dirPath, generateRandom, shiftDir, rndBaseRule)
    #INVERTED RULE
    generateRandom = False
    invertedRule = True
    myNextRule2 = getInvertedRule(myNextRule)
    myNextRule2 = run(resolutionX, resolutionY, layersCount, myNextRule2, dirPath, generateRandom, shiftDir, rndBaseRule)

    #SHIFTED RIGHT RULE
    invertedRule = False
    shiftDir = "R"
    myNextRule3 = run(resolutionX, resolutionY, layersCount, myNextRule, dirPath, generateRandom, shiftDir, rndBaseRule)

    #SHIFTED LEFT RANDOM RULE
    shiftDir = "L"
    myNextRule4 = run(resolutionX, resolutionY, layersCount, myNextRule, dirPath, generateRandom, shiftDir, rndBaseRule)

    #RANDOMIZED 1 RANDOM RULE
    shiftDir = "N"
    rndBaseRule = 1
    myNextRule5 = run(resolutionX, resolutionY, layersCount, myNextRule, dirPath, generateRandom, shiftDir, rndBaseRule)

    #RANDOMIZED 2 RANDOM RULE
    shiftDir = "N"
    rndBaseRule = 2
    myNextRule6 = run(resolutionX, resolutionY, layersCount, myNextRule, dirPath, generateRandom, shiftDir, rndBaseRule)

    #RANDOMIZED 3 RANDOM RULE
    shiftDir = "N"
    rndBaseRule = 3
    myNextRule7 = run(resolutionX, resolutionY, layersCount, myNextRule, dirPath, generateRandom, shiftDir, rndBaseRule)

    #RANDOMIZED 4 RANDOM RULE
    shiftDir = "N"
    rndBaseRule = 4
    myNextRule8 = run(resolutionX, resolutionY, layersCount, myNextRule, dirPath, generateRandom, shiftDir, rndBaseRule)

    print "NEW RANDOM RULE: \n" + myNextRule
    print "INVERTED RANDOM RULE: \n" + myNextRule2
    print "SHIFTED RIGHT RANDOM RULE: \n" + myNextRule3
    print "SHIFTED LEFT RANDOM RULE \n" + myNextRule4
    print "RANDOMIZED 1 RANDOM RULE: \n" + myNextRule5
    print "RANDOMIZED 2 RANDOM RULE: \n" + myNextRule6
    print "RANDOMIZED 3 RANDOM RULE: \n" + myNextRule7
    print "RANDOMIZED 4 RANDOM RULE: \n" + myNextRule8