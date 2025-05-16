# -*- coding: utf-8 -*-
import numpy as np
np.set_printoptions(threshold='nan')
import os
from os import walk
import os.path as osPath
import math
import csv
import random
import time
random.seed()
from PIL import Image, ImageDraw, ImageFont, ImageColor

#def generateRandomRule():
#    myRule = ""
#    for i in range(0,512):
#         myRule += str(random.randint(0,1))
#    return myRule
    
def generateRandomRule(inInspArray):
    myRule = ""
    for i in inInspArray:
         myRule += str(random.randint(0,1))
#    if inGroupName == "GROUPE_ONE":
#        myRule = adjustRuleByGroup(myRule, groupOne)
#    if inGroupName == "GROUPE_ONETWO":
#        myRule = adjustRuleByGroup(myRule, groupOneTwo)
#    if inGroupName == "GROUPE_ONETHREE":
#        myRule = adjustRuleByGroup(myRule, groupOneThree)
#    if inGroupName == "GROUPE_ONETWOTHREE":
#        myRule = adjustRuleByGroup(myRule, groupOneTwoThree)
    return myRule   
    
def adjustRuleByGroup(inRule, inPos):
    returnArray = []
    for i, v in enumerate(inRule):
        putZero = True
        if len(inPos) == 0:
            return inRule
            break
        else:
            for j, w in enumerate(inPos):
                if w == i:
                    putZero = False
        if putZero == True:
            returnArray.append("0")
        else:
            returnArray.append(v)
    return "".join(returnArray)
       
def getBinRuleFromInt(inRange):
    returnBins = []
    zeroes32 = []
    for x in range(0,32):
        zeroes = ""
        for y in range(0,x):
            zeroes += "0"
        zeroes32.append(zeroes)
    for i in inRange:
        myBin = "{0:b}".format(int(i))
        myBinFull = zeroes32[31 - (len(myBin)-1)] + myBin
        returnBins.append(myBinFull)
    return returnBins

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

def getRule(inRules, inInspArray, XYuu, XYu, XffY, XfY, XY, XbY, XbbY, XYd, XYdd):
    myPixels = str(XYuu) + str(XYu) + str(XffY) + str(XfY) + str(XY) + str(XbY) + str(XbbY) + str(XYd) + str(XYdd)
    rulePosition = int(myPixels, 2)
    return inRules[rulePosition]

def createNextLayer(inFormerImg, inRules, inInspArray, inLaysCount):
    sTime = time.time()
    myFImgData = np.array(inFormerImg.getdata())
    liWidth = inFormerImg.size[0]
    liHeight = inFormerImg.size[1]
    liLength = len(myFImgData)
    returnImgs = []
    myPixDatasLog = []
    myStrRule = ""
    for x in inRules:
        myStrRule += str(x)
    myHexCAstr = str(hex(int(myStrRule, 2)))
    if writeLogFile == True:
        f = open(CSV_logPath + "CA2D9C_" + myHexCAstr[2:len(myHexCAstr)-1] + "_" + str(liWidth) + "x" + str(liHeight) + ".csv", 'w')
        writer = csv.writer(f)
    for l in range(0, inLaysCount):
        truePixs = []
        nextImg = Image.new("1",(liWidth, liHeight))
        nextImgDraw = ImageDraw.Draw(nextImg)
        myPixData = []
        for b in myFImgData:
            myPixData.append((0,0,0,255))
        if writeLogFile == True:
            writer.writerow([l])
        for a, x in enumerate(myFImgData):   
            if (a % liWidth > 1) and (a % liWidth < liWidth -2) and a > liWidth *2 and a < liLength - liWidth * 2:
                XYuu = returnOne(myFImgData[(a - (liWidth*2))])
                XYu = returnOne(myFImgData[a - liWidth])
                XffY = returnOne(myFImgData[a - 2])
                XfY = returnOne(myFImgData[a - 1])
                XY = returnOne(myFImgData[a])
                XbY = returnOne(myFImgData [a + 1])
                XbbY = returnOne(myFImgData[a + 2])
                XYd = returnOne(myFImgData[a + liWidth])
                XYdd = returnOne(myFImgData[a + (liWidth * 2)])
                rule = getRule(inRules, inInspArray, XYuu, XYu, XffY, XfY, XY, XbY, XbbY, XYd, XYdd)
                if rule == 1:
#                  truePixs.append([a / liWidth, a % liWidth])
                   truePixs.append((a % liWidth, a / liWidth))
                   myStrInspArray = str(XYuu) + str(XYu) + str(XffY) + str(XfY) + str(XY) + str(XbY) + str(XbbY) + str(XYd)  + str(XYdd)
                   if writeLogFile == True:
                       writer.writerow([str(a % liWidth), str(a / liWidth), myStrInspArray, int(myStrInspArray, 2)])
        nextImgDraw.point(truePixs, 1)
        myFImgData = np.array(nextImg.getdata())
#        testImg.save(r"/storage/emulated/0/CA/_moje pokusy/testPix.png")
        returnImgs.append(nextImg)
        myPixDatasLog.append(myPixData.append)
        
#    nextImgData = np.array(nextImg.getdata())
    eTime = time.time()
    myTime = eTime -sTime
    print "Time of creating "+str(inLaysCount)+" CA layers is " + str(int(myTime/60))+" m " +str(int(myTime%60)) + " s"
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
    myInspArray = getInspArray(9)
    myRandomRule = generateRandomRule(myInspArray)
    sourceRule = getSourceRule(inMyRule, myRandomRule, inGenerateRandom, inShiftDir, inRndBaseRule)
    sourceRuleArray = [int(x) for x in sourceRule]
#    print "CURRENT RULE: \n" + sourceRule
    slashChar = r"/"
#    finalDirPath = inDirPath + "CA2D2_" + sourceRule + "_" + resXstr + "x" + resYstr + slashChar
    finalDirPath = inDirPath
#    layNum = 0
#    print "CURRENT GENERATION: " + str(layNum)
#    properLayNum = getProperLayNum(layNum)
    imageFormat = "bmp"
    myLayers = []
    
#    if layNum == 0:
    firstLayer = createFirstLayerFromScratch(inResX, inResY)
#    myLayers.append(firstLayer)
#    ensure_dir(finalDirPath)
#    firstLayer.save(finalDirPath + properLayNum + "_" + resXstr + "x" + resYstr + "." + imageFormat)
#    layNum += 1
    myLastImg = firstLayer
    myLayers = createNextLayer(myLastImg, sourceRuleArray, myInspArray, inLayCount-1)
    myLayers.insert(0,firstLayer)
#        for c in myNextLayers:
#            layNum += 1
#            properLayNum = getProperLayNum(layNum)
#            c.save(finalDirPath + properLayNum + "_" + resXstr + "x" + resYstr + "." + imageFormat)
#    else:
#        myLastImg = loadLastLayer(finalDirPath)
#        myNextLayers = createNextLayer(myLastImg, sourceRuleArray, myInspArray, layersCount)
#        for c in myNextLayers:
#            layNum += 1
#            properLayNum = getProperLayNum(layNum)
#            c.save(finalDirPath + properLayNum + "_" + resXstr + "x" + resYstr + "." + imageFormat)
    return myLayers

def getInvertedDigit(inRule, inPos):
    returnString = ""
    listString = list(inRule)   
    if listString[inPos] == '0':
        listString[inPos] = '1'
    elif listString[inPos] == '1':
        listString[inPos] = '0'
    return ''.join(listString)
    
def filterRule(inRule, inGroupe):
    zeroRule = getInspArrayRangeZero(9)
    print len(zeroRule)
    print len(inRule)
    for g in inGroupe:
#        print "G: " + str(g)
        zeroRule[g] = int(inRule[g])
    returnStr = ""
    for i in zeroRule:
        returnStr += str(i)
    return returnStr

def forceSymetryGroups(inRule, inGroups):
    zeroRule = getInspArrayRangeZero(9)
#    print len(zeroRule)
#    print len(inRule)
    groupe = []        
    newRule = [x for x in inRule]
    a = np.array(inGroups)
    print "Force symetry inGroups shape:"
    print a.shape
#    print len(a.shape)
    if len(a.shape) >1:
        for i in inGroups:
            groupe += i
    else:
        groupe = inGroups
    for g in groupe:
#        print "G: " + str(g)
        newRule[g] = 1
    returnStr = ""
    for i in newRule:
        returnStr += str(i)
    return returnStr
    
def getRndSymetryGroups(inGroups):
    lev1positions = range(0,len(inGroups))
    lev1RNDCount = random.randint(0,len(inGroups))
    random.shuffle(lev1positions)
    lev1positions = lev1positions[0:lev1RNDCount]
    print "lev1positions"
    print lev1positions
    lev2positions = []
    posCoords = []
    returnGroups = []
    for i,x in enumerate(lev1positions):
        myPositions = range(0,len(inGroups[x]))
        myRndCount = random.randint(0,len(inGroups[x]))
        random.shuffle(myPositions)
        myPositions = myPositions[0:myRndCount]
        for j, y in enumerate(myPositions):
            if i == 0 and j == 0:
                returnGroups = inGroups[x][y]
            else:
                returnGroups += inGroups[x][y]
            posCoords.append((x,y))
        lev2positions.append(myPositions)
    rndSymGroupeCoords = posCoords
    print "lev2positions"
    print lev2positions
    print "posCoords"
    print posCoords
    print "returnGroups"
    print returnGroups
    return [returnGroups, posCoords]
                 
groupOne = [1,2,4,8,16,32,64,128,256]
groupTwo = [3,5,6,9,10,12,17,18,20,
            24,33,34,36,40,48,65,66,
            68,72,80,96,129,130,132,
            136,144,160,192,257,258,
            260,264,272,288,320,384]
groupThree = [7,11,13,14,19,21,22,25,
              26,28,35,37,38,41,42,
              49,50,52,56,67,69,70,
              73,74,76,81,82,84,88,
              97,98,100,104,112,131,
              133,134,137,138,140,
              145,146,148,152,154,
              161,162,164,168,176,
              184,193,194,196,200,
              208,224,259,261,262,
              265,266,268,273,274,
              276,280,289,290,292,
              296,304,321,322,324,
              328,336,352,385,386,
              388,392,400,416,448]
groupFour = [15,23,27,29,30,39,43,45,
             46,53,54,57,58,60,71,75,
             77,78,83,85,86,89,90,92,
             99,101,102,105,106,108,
             113,114,116,120,135,139,
             141,142,147,149,150,153,
             154,156,163,165,166,169,
             170,172,174,177,178,180,
             184,195,197,198,201,202,
             204,209,210,212,216,225,
             226,228,232,240,263,267,
             269,270,275,277,278,281,
             282,284,291,293,294,297,
             298,300,305,306,308,312,
             323,325,326,329,330,332,
             337,338,340,344,353,354,
             356,360,368,387,389,390,
             393,394,396,401,402,404,
             408,417,418,420,424,432,
             449,450,452,456,464,480]
sym4axis = [16,170,186,325,341,495,511]
sym2axis = [40,56,68,84,108,124,130,
            146,198,214,238,254,257,
            273,297,313,365,381,387,
            427,403,443,455,471]
sym1axG = [[],
           [[1,4,64,256],[2,8,32,128]],
           [[3,12,96,384],[5,65,260,320],
            [10,34,136,160],[17,20,80,272],
            [18,24,48,144],[36,72,129,258]],
           [[19,28,112,400],[21,81,276,336],
            [26,50,152,176],[41,134,194,296],
            [42,138,162,168],[44,104,131,386],
            [52,88,145,274],[69,261,321,324],
            [70,196,265,289],[76,100,259,385]],
           [[15,99,396,480],[43,142,226,424],
            [57,150,210,312],[58,154,178,184],
            [60,120,147,402],[71,269,353,452],
            [85,277,337,340],[86,212,281,305],
            [92,116,275,401],[165,201,294,330],
            [166,169,202,298],[197,293,326,329]],
           [[31,115,412,496],[59,158,242,440],
            [87,285,369,468],[109,364,391,451],
            [110,236,395,419],[171,174,234,426],
            [181,217,310,346],[182,185,218,314],
            [199,301,361,454],[206,230,299,425],
            [213,309,342,345],[327,333,357,453]],
           [[111,399,483,492],[125,380,407,467],
            [126,252,411,435],[187,190,250,442],
            [215,317,377,470],[222,246,315,441],
            [175,235,430,490],[237,366,423,459],
            [335,359,461,485],[343,349,373,469]],
           [[127,415,499,508],[191,251,446,506],
            [239,431,491,494],[253,382,439,475],
            [351,375,477,501],[367,463,487,493]],
           [[255,447,507,510],[383,479,503,509]]]
dirPath = r"C:/_WORK/PYTHON/CELULAR_AUTOMAT-2D/RNDCA2D9c-sequence/"
loadPath = r"/storage/emulated/0/CA/_moje pokusy/CELULAR_AUTOMAT-2D/interesting3/"
CSV_logPath = r"C:/_WORK/PYTHON/CELULAR_AUTOMAT-2D/LOG/"
writeLogFile = True
generateRandom = False
invertedRule = False
shiftDir = "N"
rndBaseRule = 0
myIntRule = 2805896752
#myRule = "01101000100100011101010001100010"
myRule = getBinRuleFromInt(range(myIntRule-1, myIntRule))
print "myRule"
print type(myRule)
startRange = 0
endRange = 50
rndSymetryGroups = getRndSymetryGroups(sym1axG)
myRndSymGroups = rndSymetryGroups[0]
rndSymGroupeCoords = rndSymetryGroups[1]
groupOneTwo = groupOne + groupTwo
groupOneThree = groupOne + groupThree
groupOneTwoThree = groupOne + groupTwo + groupThree
groupeSettings = "GROUPE_ONETWOTHREE"
groupeSettings = ""

#myCurrentRule = myRule

resolutionX = 51
resolutionY = 51
layersCount = 60


       
def runBinSequence(inRange):
    rules = getBinRuleFromInt(inRange)
    CA = []
    for i, r in enumerate(rules):
        print "position " + str(inRange[i])
        myCA = run(resolutionX, resolutionY, layersCount, r, dirPath, generateRandom, shiftDir, rndBaseRule)
        CA.append([myCA, inRange[i], r])
        print CA[i]
    createImgCollection(CA, dirPath)

def createImgCollection(inCA, inDirPath):
    myCAdata = inCA[0]
    myCAdataLast = inCA[len(inCA)-1]
    startPos = myCAdata[1]
    endPos = myCAdataLast[1]
    myCArule = myCAdata[2]
    myCA = myCAdata[0]
    img0 = myCA[0]
    resX = img0.size[0]
    resY = img0.size[1]
    cols = len(myCA)
    rows = len(inCA)
    gap = 60
    headTextFontSize = 13
    myRules = inCA[0]
    myHeadRule = "".join(myCAdata[2])
    myHeadRule = str(hex(int(myHeadRule, 2)))
    headText = "CA2D9C_" + myHeadRule[2:len(myHeadRule)-1] + "_" + str(resX) + "x" + str(resY) + "x" + str(cols) 
    ruleTextFontSize = 10
    ruleTextFont = ImageFont.truetype("raavi.ttf", ruleTextFontSize)
    headTextFont = ImageFont.truetype("arial.ttf", headTextFontSize)
    ruleTextSize = ruleTextFont.getsize(myCArule)
    headTextSize = headTextFont.getsize(headText)
    ruleTextXsize = ruleTextSize[0]
    ruleTextYsize = ruleTextSize[1]
    documentHeadYsize = headTextSize[1] + 5
    inspArraySequence = getInspArraySeqence(9)
#    IDfieldWidth = ruleTextXsize + 200
    myBRule = "".join(myCAdata[2])
    myHR = str(hex(int(myBRule, 2)))
    myHRule = myHR[2:len(myHR)-1]
    lReadPath = CSV_logPath + "CA2D9C_" + myHRule + "_" + str(resX) + "x" + str(resY) + ".csv"
    myLData = readCSV_Log(lReadPath)
    cIm = getCross(myCAdata[2], inspArraySequence, 2, myLData)
    myAnalyses = neighbourAnalyse(myLData, resX, resY)
    myNbAnalyseImg = myAnalyses[0]
    myOqAnalyseImg = myAnalyses[1]
    canvasXsize = cIm.size[0]
    canvasYsize = documentHeadYsize + cIm.size[1] * len(inCA) + resY*len(inCA) + myNbAnalyseImg.size[1]*len(inCA) + myOqAnalyseImg.size[1]*len(inCA) + 5*len(inCA)
    canvas = Image.new('RGBA', (canvasXsize, canvasYsize))
    drawCanvas = ImageDraw.Draw(canvas)
    drawCanvas.text((0,0), headText,font=headTextFont)
    drawCanvas.rectangle([0, 0, canvasXsize -3, canvasYsize -3],(0,0,0,255))
    fullPath = inDirPath + headText + ".png"
    yPos = documentHeadYsize
    for i, ca in enumerate(inCA):
        sTime = time.time()
        myBinRule = "".join(ca[2])
        myHxRule = str(hex(int(myBinRule, 2)))
        myHexRule = myHxRule[2:len(myHxRule)-1]
        logReadPath = CSV_logPath + "CA2D9C_" + myHexRule + "_" + str(resX) + "x" + str(resY) + ".csv"
        myLogsData = readCSV_Log(logReadPath)
        print "Generating analyse Images: " + str(i) +"..."
        myAnalyses = neighbourAnalyse(myLogsData, resX, resY)
        myNbAnalyseImg = myAnalyses[0]
        myOqAnalyseImg = myAnalyses[1]
        crossIm = getCross(ca[2], inspArraySequence, 2, myLogsData)
        crossImYsize = crossIm.size[1]       
        caImgs = ca[0]
        caImgs = caImgs[::-1]
        canvas.paste(crossIm, (0,yPos))
        yPos += crossImYsize
        for j, img in enumerate(caImgs):
            canvas.paste(img, (resX*j,yPos))        
        yPos += resY
        canvas.paste(myOqAnalyseImg, (resX, yPos))
        yPos += myOqAnalyseImg.size[1]
        canvas.paste(myNbAnalyseImg, (resX, yPos))
        yPos += myNbAnalyseImg.size[1] + 2
        drawCanvas.line([10, yPos , canvasXsize-10, yPos])
        yPos += 3
        eTime = time.time()
        myTime = eTime - sTime
        print "Time for generatinq analyse img was " + str(int(myTime/60)) + " m " + str(int(myTime%60)) + " s"
#        drawCanvas.text((0,yPos), ca[2],font=ruleTextFont)
#        drawCanvas.text((0,yPos + (1*ruleTextYsize*0.7)), "POSITION: " + str(ca[1]),font=headTextFont)
    canvas.save(fullPath)
    
    print "file was saved :" + fullPath
    print "resolution X: "
    print resX
    print "resolution Y: "
    print resY
    print "columns : "
    print cols
    print "rows : "
    print rows
#    print "ruleTextLength : "
#    print ruleTextXsize
#    print "ruleTextHeight : "
#    print ruleTextYsize
#    print "headText : "
#    print headText
#    print "documentHeadYsize : "
#    print documentHeadYsize
#    print "canvasXsize : "
#    print canvasXsize
#    print "canvasYsize : "
#    print canvasYsize

def readCSV_Log(inPath):
    returnArray = []
    coords = []
    inspArrNums = []
    myNbCounts = []
    inspArrayRange = getInspArrayRangeZero(9)
    firstOcure = getInspArrayRangeZero(9)
    if osPath.isfile(inPath) == True:
        print "Log File Exists: " + inPath
        f = open(inPath, "r")
        print "Reading CSV log data..."
        with f:
            reader = csv.reader(f)
            layNum = 0
#            myRows = []
#            myCounts = []
            coord = []
            inspArrNum = []
            myNbCount = []
            inspNbCounts = getNeighbourCounts()
            for i, row in enumerate(reader):  
                if len(row) != 1:                  
#                    myRows.append(row)
                    myInspMatrixNum = int(row[3])
                    inspArrNum.append(myInspMatrixNum)
#                    myCounts.append(myInspMatrixNum)
                    myCount = inspArrayRange[myInspMatrixNum]
                    if myCount == 0:
                        firstOcure[myInspMatrixNum] = layNum + 1
                    myCount += 1
                    inspArrayRange[myInspMatrixNum] = myCount
                    coord.append((int(row[0]),int(row[1])))
                    myNbCount.append(inspNbCounts[myInspMatrixNum])
                else:
#                    returnArray.append(myCounts)
                    layNum = layNum + 1
                    coords.append(coord)
                    coord = []
                    inspArrNums.append(inspArrNum)
                    inspArrNum = []
                    myNbCounts.append(myNbCount)
                    myNbCount = []
#                    myRows = []
#                    myCounts = []
    else:
        print "Log File Doesn't Exist: " + inPath
#    print coords[5]
#    print inspArrNums[5]
#    print myNbCounts[5]
    return [firstOcure, inspArrayRange, coords, inspArrNums, myNbCounts]

def getInspArraySeqence(inArLenght):
    rulesCount = pow(2, inArLenght)
    arRange = range(0, rulesCount)
    binSeqDiv = [pow(2, x) for x in range(0,inArLenght)]
    binSeqDiv.reverse()
    myArray = [[math.trunc(x / y) % 2 for x in arRange] for y in binSeqDiv]
    myArray = map(list, zip(*myArray)) 
    return myArray

def getNeighbourCounts():
    nbCount = getInspArrayRangeZero(9)
    inspArrSeq = getInspArraySeqence(9)
    for i,s in enumerate(inspArrSeq):
        count = 0
        for c in s:
            if c == 1:
                count += 1
        nbCount[i] = count
    return nbCount
    
def get2DpixCoords(inInd, inResX):
    return (inInd % inResX, inInd / inResX)   
    
def get1DpixCoord(in2DCoords, inResX):
    return in2DCoords[0] + in2DCoords[1]*inResX
    
def neighbourAnalyse(inLogData, inXres, inYres):
    myCoords = inLogData[2]
#    print len(myCoords)
#    print "myCoords[0]"
#    print myCoords[0]
#    print "myCoords[1]"
#    print myCoords[1]
#    print "myCoords[2]"
#    print myCoords[2]
    myNbCounts = inLogData[4]
    myInspArrNums = inLogData[3]
    layCount = len(myCoords)
    textHeight = 11
    textGap = int(textHeight*0.3)
    textLine = textHeight + textGap
    textFont = ImageFont.truetype("arial.ttf", textHeight)
    myAnalImg = Image.new('RGBA', (inXres*(layCount+1), inYres+textLine))
    myAnalImgDraw = ImageDraw.Draw(myAnalImg)
    myOqAnalImg = Image.new('RGBA', (inXres*(layCount+1), inYres))
    myOqAnalImgDraw = ImageDraw.Draw(myAnalImg)
    myFirstOcurences = inLogData[0]
    myOcurencesCount = inLogData[1]
    maxOcurenceValue = max(myOcurencesCount)
    scaleCount = 10
    scaleStep = maxOcurenceValue / scaleCount
    if scaleStep > 0:
        scaleRange = range(0,maxOcurenceValue,scaleStep)
    else:
        scaleRange = range(0,10,1)
    hueMin = 0
    hueMax = 150
    satMin = 0
    satMax = 50
    lightMin = 0
    lightMax = 95
    hueOffset = 200
    for i, layCoords in enumerate(myCoords):
        layNbCounts = myNbCounts[i]
        myLayer = Image.new('RGBA', (inXres, inYres), (0,0,0,255))
#        myLayerDraw = ImageDraw.Draw(myLayer)
        npLayerArr = np.array(myLayer.getdata())
#        print npLayerArr
        npLayerArrIt = np.nditer(npLayerArr, flags=['multi_index'],op_flags=['readwrite'])
        myOqLayer = Image.new('RGBA', (inXres, inYres), (0,0,0,255))
        npOqLayerArr = np.array(myOqLayer.getdata())
#        npOqLayerArrIt = np.nditer(npOqLayerArr, flags=['multi_index'],op_flags=['readwrite'])
        myOqLayerDraw = ImageDraw.Draw(myOqLayer)
        ci = 0
        myRGB = (0,0,0,255)
        npLayerArrIt = np.nditer(npLayerArr, flags=['multi_index'],op_flags=['readwrite'])
        while not npLayerArrIt.finished:            
            if ci < len(layCoords):   
                xCoord = int(layCoords[ci][0])
                yCoord = int(layCoords[ci][1])                                  
                if npLayerArrIt.multi_index[0] == get1DpixCoord((xCoord, yCoord), myLayer.size[0]):
                    if npLayerArrIt.multi_index[1] == 0:
#                        print "next pixel :" + str(npLayerArrIt.multi_index[0])
                        pixNbCount = layNbCounts[ci]
                        mappedCount = (remap(pixNbCount, 0, 8, hueMin, hueMax) + hueOffset) % 360
                        mappedSat = (100-remap(pixNbCount, 0, 8, satMin, satMax))
                        mappedLight = 100-remap(pixNbCount, 0, 8, lightMin, lightMax)
                        hslCol = "hsl(" + str(int(mappedCount)) + "," + str(int(mappedSat)) +"%," + str(int(mappedLight)) + "%)"
                        myRGB = ImageColor.getrgb(hslCol)
#                        print hslCol
#                        print myRGB[0]
#                        print npLayerArrIt[0]
                        npLayerArrIt[0] = myRGB[0]
#                        print npLayerArrIt[0]
                    if npLayerArrIt.multi_index[1] == 1:                   
                        npLayerArrIt[0] = myRGB[1]
                    if npLayerArrIt.multi_index[1] == 2:
                        npLayerArrIt[0] = myRGB[2]
                        ci += 1
            npLayerArrIt.iternext()
#        for x in npLayerArr:
#            print x
        myLayerData = list(tuple(pixel) for pixel in npLayerArr)
        myLayer.putdata(myLayerData)
        ci = 0
        myRGB = (0,0,0,255)
        npOqLayerArrIt = np.nditer(npOqLayerArr, flags=['multi_index'],op_flags=['readwrite'])
        while not npOqLayerArrIt.finished:            
            if ci < len(layCoords):   
                xCoord = int(layCoords[ci][0])
                yCoord = int(layCoords[ci][1])                                  
                if npOqLayerArrIt.multi_index[0] == get1DpixCoord((xCoord, yCoord), myOqLayer.size[0]):
                    if npOqLayerArrIt.multi_index[1] == 0:
#                        print "next pixel :" + str(npOqLayerArrIt.multi_index[0])
                        pixInsArNum = myInspArrNums[i][ci]
                        myOqHSLcol = "hsl(" + str(int(remap(myOcurencesCount[pixInsArNum], 0, maxOcurenceValue, 0, 185))) + ",100%, " + str(int(remap(myOcurencesCount[pixInsArNum], 0, maxOcurenceValue, 30, 70))) + "%)"
                        myRGB = ImageColor.getrgb(myOqHSLcol)
#                        print myOqHSLcol
#                        print myRGB[0]
#                        print npOqLayerArrIt[0]
                        npOqLayerArrIt[0] = myRGB[0]
#                        print npOqLayerArrIt[0]
                    if npOqLayerArrIt.multi_index[1] == 1:                   
                        npOqLayerArrIt[0] = myRGB[1]
                    if npOqLayerArrIt.multi_index[1] == 2:
                        npOqLayerArrIt[0] = myRGB[2]
                        ci += 1
            npOqLayerArrIt.iternext()
        myOqLayerData = list(tuple(pixel) for pixel in npOqLayerArr)
        myOqLayer.putdata(myOqLayerData)
#        for j, pix in enumerate(layCoords):
#            pixInsArNum = myInspArrNums[i][j]
#            myOqHSLcol = "hsl(" + str(int(remap(myOcurencesCount[pixInsArNum], 0, maxOcurenceValue, 0, 185))) + ",100%, " + str(int(remap(myOcurencesCount[pixInsArNum], 0, maxOcurenceValue, 30, 70))) + "%)"
#            myOqLayerDraw.point([pix[0], pix[1]], myOqHSLcol)
#        myLayer.save(saveNbAnalImg + str(i) + ".png")
#        print "img was saved"
        myAnalImg.paste(myLayer, ((inXres*layCount) - ((i+1)*inXres),0))
#        myAnalImgDraw.text(((inXres*layCount) - ((i+1)*inXres), 0), str(i),font=textFont, fill="red")
        myOqAnalImg.paste(myOqLayer, ((inXres*layCount) - ((i+1)*inXres),0))
    myText = "NEIGHBOURHOOD_PIXEL_COUNT: "
    myAnalImgDraw.text((0, inYres), myText,font=textFont, fill="white")
    tXOffset = textFont.getsize(myText)[0]
    for f in range(0,9):
        mappedCount = (remap(f, 0, 8, hueMin, hueMax) + hueOffset) % 360
        mappedSat = (100-remap(f, 0, 8, satMin, satMax))
        mappedLight = 100-remap(f, 0, 8, lightMin, lightMax)
        fillColor = ImageColor.getrgb("hsl(" + str(int(mappedCount)) + "," + str(int(mappedSat)) +"%," + str(int(mappedLight)) + "%)")
        pixNum = str(f) + "px"
        tNumXOffset = textFont.getsize(pixNum)[0]
#        print "tNumXOffset"
#        print tNumXOffset
        myAnalImgDraw.text((tXOffset + tNumXOffset*f, inYres), pixNum,font=textFont, fill='white')
#        myAnalImgDraw.rectangle([tXOffset + f*textLine, inYres,tXOffset + f*textLine + textLine, inYres + textLine], myHslCol)
#        myAnalImgDraw.rectangle([tXOffset + f*textLine, inYres, tXOffset + f*textLine + textLine, inYres + textLine], fillColor)
        myAnalImgDraw.text((tXOffset, inYres), pixNum,font=textFont, fill=(255,255,255,255))
        tXOffset += tNumXOffset + int(tNumXOffset*0.3)
        myAnalImgDraw.rectangle([tXOffset, inYres, tXOffset + textLine, inYres + textLine], fillColor)
        tXOffset += textLine + int(tNumXOffset*0.3)
#    myAnalImg.save(saveNbAnal)
#    print "NB analyse img was saved" + saveNbAnal
#    myOqAnalImg.save(saveOqAnal)
#    print "OQ analyse img was saved" + saveOqAnal
    return [myAnalImg, myOqAnalImg]   
    
def getCross(inRule, inInspArraySequence, inRows, inLogData):
    dirPath = r"/storage/emulated/0/CA/_moje pokusy/cross_test.png"  
    rows = inRows
    columns = len(inInspArraySequence) / rows
    recColumns = 5
    recRows = 5
    print "columns:"
    print columns
#    recSize = inWidth / (len(inInspArraySequence)/float(rows)) / 7
    recSize = 4
    fadeValue = 0.35
    crossSize = recSize * 7
    outlineWidth = 3
    gap = recSize
    crossMXCoords5x5 = [[2,0],[2,1],[0,2],[1,2],[2,2],[3,2],[4,2],[2,3],[2,4]]
#    print crossMXCoords5x5[0]
    orderTextFontSize = int(crossSize*0.5)
    ocurenceTextFontSize = int(crossSize*0.7)
    headFontSize = int(crossSize*0.6)
    headLines = 6
    headLineGap = int(headFontSize * 0.5)
    headLineHeight = headFontSize + headLineGap
    headTextHeight = (headLineHeight) * headLines + headLineGap
    headTextX = gap
    headText1Y = 0 * headLineHeight
    headText2Y = 1 * headLineHeight
    headText3Y = 2 * headLineHeight
    headText4Y = 3 * headLineHeight
    headText5Y = 4 * headLineHeight
    headText6Y = 5 * headLineHeight
    orderTextYOffset = orderTextFontSize
    orderTextFont = ImageFont.truetype("raavi.ttf", orderTextFontSize)
    ocurenceTextFont = ImageFont.truetype("arial.ttf", ocurenceTextFontSize)
    headFont = ImageFont.truetype("arial.ttf", headFontSize)
    rowHeight = orderTextYOffset + crossSize + ocurenceTextFontSize
    imHeight = int(headTextHeight + (rowHeight * rows))
    imWidth = columns * crossSize
    print "imWidth: " + str(imWidth)
    myHSLcol = "hsl(0,100%,50%)"
    myFirstOcurences = inLogData[0]
    myOcurencesCount = inLogData[1]
    maxOcurenceValue = max(myOcurencesCount)
    scaleCount = 10
    scaleStep = maxOcurenceValue / scaleCount
    if scaleStep > 0:
        scaleRange = range(0,maxOcurenceValue,scaleStep)
    else:
        scaleRange = range(0,10,1)
    im = Image.new('RGBA', (imWidth + outlineWidth,imHeight + outlineWidth), (0, 0, 0,255))
    imD = ImageDraw.Draw(im)
    canvasBColor = ImageColor.getrgb("Coral")
    crossBColor = "hsl(130,100%,70%)"
    recBColor = "hsl(240,100%,70%)"
    orderTextCollor = (255,255,255,255)
#    imD.rectangle([0,0, imWidth, imHeight],(0,0,255,0), "Coral")
    imD.text((headTextX, headText1Y), "BIN: " + inRule, font=headFont, fill=(255,255,255,255))
    imD.text((headTextX, headText2Y), "INT: " + str(int(inRule, 2)), font=headFont, fill=(255,255,255,255))
    myHex = str(hex(int(inRule, 2)))
    imD.text((headTextX, headText3Y),"HEX: " + myHex[2:len(myHex)-1], font=headFont, fill=(255,255,255,255))
    for i, v in enumerate(inInspArraySequence):
        orderTextSize = imD.textsize(str(i),font=orderTextFont)
        crossXOffset = (i%columns)*crossSize
        crossYOffset = headTextHeight + (i/columns)*rowHeight
#        imD.rectangle([crossXOffset, crossYOffset, crossXOffset+crossSize, crossYOffset+crossSize],(0,0,0,0), crossBColor)
        orderTextX = (crossXOffset + crossSize/2) - orderTextSize[0]/2
        orderTextY = crossYOffset - orderTextYOffset
        imD.text((orderTextX, orderTextY), str(i), font=orderTextFont, fill=(80,80,80,255))
        ocurenceTextSize = imD.textsize(str(myFirstOcurences[i]),font=ocurenceTextFont)
        ocurenceTextX = (crossXOffset + crossSize/2) - ocurenceTextSize[0]/2
        ocurenceTextY = crossYOffset + crossSize
        myHSLcol = "hsl(" + str(int(remap(myOcurencesCount[i], 0, maxOcurenceValue, 0, 185))) + ",100%, " + str(int(remap(myOcurencesCount[i], 0, maxOcurenceValue, 30, 70))) + "%)"
        imD.text((ocurenceTextX, ocurenceTextY), str(myFirstOcurences[i]),font=ocurenceTextFont, fill=myHSLcol)
        for j, h in enumerate(v):
#            print j
            fCComponent = int(255*fadeValue)
            frameColor = (fCComponent, fCComponent, fCComponent, fCComponent)
            fillCComponent = int(int(h)*(255*fadeValue+((1-fadeValue)*int(inRule[i])*255)))
            fillColor = (fillCComponent, fillCComponent, fillCComponent, 255)
            mx5x5Coords = crossMXCoords5x5[j]
            recXCoord = mx5x5Coords[0]
            recYCoord = mx5x5Coords[1]
            recXOffset = crossXOffset + recSize + recXCoord*recSize
            recYOffset = crossYOffset + recSize + recYCoord*recSize
            imD.rectangle([recXOffset, recYOffset, recXOffset+recSize, recYOffset+recSize], fillColor, frameColor)
    textXpos = headTextX
    symGroupCoordStr = "SYMETRY_GROUPS_COORDS:   "
    symGroupStr =      "SYMETRY_GROUPS_POSITIONS:"
    for d in rndSymGroupeCoords:
        symGroupCoordStr += "("+str(d[0])+","+str(d[1])+")"
    imD.text((headTextX, headText4Y), symGroupCoordStr,font=headFont, fill="white")
    for c in myRndSymGroups:
        symGroupStr += str(c)+","
    imD.text((headTextX, headText5Y), symGroupStr,font=headFont, fill="white")
    for s in scaleRange:
        myHSLcol = "hsl(" + str(int(remap(s, 0, maxOcurenceValue, 0, 185))) + ",100%, " + str(int(remap(s, 0, maxOcurenceValue, 30, 70))) + "%)"
        imD.text((textXpos, headText6Y), str(s),font=headFont, fill=myHSLcol)
        myTextSize = imD.textsize(str(s),font=headFont)
        textXpos += (myTextSize[0] + 15)
        
    return im

def getInspArrayRangeZero(inArLenght):
    rulesCount = pow(2, inArLenght)
    returnArray = []
    arRange = range(0, rulesCount) 
    for i in arRange:
        returnArray.append(0)
    return returnArray

def remap(value, minInput, maxInput, minOutput, maxOutput):
    if minInput < maxInput:
        value = maxInput if value > maxInput else value
        value = minInput if value < minInput else value
        inputSpan = maxInput - minInput
        outputSpan = maxOutput - minOutput
        scaledThrust = float(value - minInput) / float(inputSpan)
        return minOutput + (scaledThrust * outputSpan)
    else:
        return minOutput

    
#runBinSequence(range(startRange, endRange))

def runRndSequence(inGroupeSettings):
    rules = []
    CA = []
    num = 0
    overalSTime = time.time()
    myInspArray = getInspArray(9)
    for i in range(0, endRange):
        rules.append(generateRandomRule(myInspArray))
        rules[i] = filterRule(rules[i],sym4axis + sym2axis + groupOne)
        rules[i] = forceSymetryGroups(rules[i], myRndSymGroups)
        position = int(rules[i],2)
        print num
        print "position " + str(position)
        myCA = run(resolutionX, resolutionY, layersCount, rules[i], dirPath, generateRandom, shiftDir, rndBaseRule)
        CA.append([myCA, position, rules[i]])
        num += 1
    createImgCollection(CA, dirPath)
    overalETime = time.time()
    ovTime = overalETime - overalSTime
    print "overal time of generating " + str(endRange) + "CAs is " + str(int(ovTime/60)) + "min " + str(ovTime%60)+ " seconds"
#    for i in rules:
#        print int(i, 2)
         
def runDirSequence(inLoadPath, inRange):
    rules = []
    f = []
    for (path, dirnames, filenames) in walk(inLoadPath): 
        f.extend(dirnames) 
        break
    f.sort()
    rules = getBinRuleFromInt(f)
    CA = []
    for i, r in enumerate(rules[inRange[0] : len(inRange)-1]):
        position = int(r,2)
        print "position " + str(position)
        myCA = run(resolutionX, resolutionY, layersCount, r, dirPath, generateRandom, shiftDir, rndBaseRule)
        CA.append([myCA, position, r])
        print CA[i]
    createImgCollection(CA, dirPath)

#    for i in f[inRange[0]:inRange[len(inRange)-1]]:
#        splitedPath = i.split("_")
#        rules.append(splitedPath[1])
#    for j, s in enumerate(f):
#        f[j] = inDirPath + s
#    for i in rules:
#        run(resolutionX, resolutionY, layersCount, i, dirPath, generateRandom, shiftDir, rndBaseRule)
    print rules
    
#runDirSequence(loadPath, range(0,5))   
runRndSequence(groupeSettings)

