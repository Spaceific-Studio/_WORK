# -*- coding: utf-8 -*-
import numpy as np
np.set_printoptions(threshold='nan')
import os
from os import walk
import os.path as osPath
import math
import csv
import random
random.seed()
from PIL import Image, ImageDraw, ImageFont, ImageColor

def generateRandomRule():
    myRule = ""
    for i in range(0,32):
         myRule += str(random.randint(0,1))
    return myRule
    
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
                   truePixs.append((a / liWidth, a % liWidth))
#                   truePixs.append((a % liWidth, a / liWidth))
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
#    print "CURRENT RULE: \n" + sourceRule
    slashChar = r"/"
#    finalDirPath = inDirPath + "CA2D2_" + sourceRule + "_" + resXstr + "x" + resYstr + slashChar
    finalDirPath = inDirPath
#    layNum = 0
#    print "CURRENT GENERATION: " + str(layNum)
    myInspArray = getInspArray(5)
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

dirPath = r"/storage/emulated/0/CA/_moje pokusy/CELULAR_AUTOMAT-2D/SWITCH-sequence/"
loadPath = r"/storage/emulated/0/CA/_moje pokusy/CELULAR_AUTOMAT-2D/interesting3/"
CSV_logPath = r"/storage/emulated/0/CA/_moje pokusy/CELULAR_AUTOMAT-2D/CSV_log/SWITCH-sequence-r/"
writeLogFile = True
generateRandom = False
invertedRule = False
shiftDir = "N"
rndBaseRule = 0
myRule = "01110110100010001001000010000000"
startRange = 2145370000
endRange = 2145370100
#myCurrentRule = myRule

resolutionX = 51
resolutionY = 51
layersCount = 50
        
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
    headText = "CA2D2r_" + str(int(myRule, 2)) + "_" + str(myRule) + "_" + str(resX) + "x" + str(resY) + "x" + str(cols) 
    ruleTextFontSize = 15
    ruleTextFont = ImageFont.truetype("raavi.ttf", ruleTextFontSize)
    headTextFont = ImageFont.truetype("arial.ttf", headTextFontSize)
    ruleTextSize = ruleTextFont.getsize(myCArule)
    headTextSize = headTextFont.getsize(headText)
    ruleTextXsize = ruleTextSize[0]
    ruleTextYsize = ruleTextSize[1]
    documentHeadYsize = headTextSize[1] + 5
    IDfieldWidth = ruleTextXsize + 200
    canvasXsize = IDfieldWidth + (cols * resX)
    canvasYsize = documentHeadYsize + (rows * (resY + 70))
    canvas = Image.new('RGBA', (canvasXsize, canvasYsize))
    drawCanvas = ImageDraw.Draw(canvas)
    drawCanvas.text((0,0), headText,font=headTextFont)
    fullPath = inDirPath + headText + ".png"
   
    for i, ca in enumerate(inCA):
        logReadPath = CSV_logPath +ca[2] + "_" + str(resX) + "x" + str(resY) + ".csv"
        myLogsData = readCSV_Log(logReadPath)
        crossIm = getCross(ca[2], getInspArraySeqence(5), IDfieldWidth, myLogsData)
        crossImYsize = crossIm.size[1]
        yPos = documentHeadYsize + (i*(resY+gap)) + crossImYsize
        caImgs = ca[0]
        caImgs = caImgs[::-1]
        for j, img in enumerate(caImgs):
            canvas.paste(img, (IDfieldWidth + (resX*j),yPos))
        canvas.paste(crossIm, (0,int(yPos + (2*ruleTextYsize*0.7))))
        drawCanvas.line([10, yPos - 10, canvasXsize-10, yPos - 10])
        drawCanvas.text((0,yPos), ca[2],font=ruleTextFont)
        drawCanvas.text((0,yPos + (1*ruleTextYsize*0.7)), "POSITION: " + str(ca[1]),font=headTextFont)
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
    print "ruleTextLength : "
    print ruleTextXsize
    print "ruleTextHeight : "
    print ruleTextYsize
    print "headText : "
    print headText
    print "documentHeadYsize : "
    print documentHeadYsize
    print "canvasXsize : "
    print canvasXsize
    print "canvasYsize : "
    print canvasYsize

def readCSV_Log(inPath):
    returnArray = []
    inspArrayRange = getInspArrayRangeZero(5)
    firstOcure = getInspArrayRangeZero(5)
    if osPath.isfile(inPath) == True:
        print "Log File Exists: " + inPath
        f = open(inPath, "r")
        with f:
            reader = csv.reader(f)
            layNum = 0
#            myRows = []
#            myCounts = []
            for i, row in enumerate(reader):   
                if len(row) != 1: 
#                    myRows.append(row)
                    myInspMatrixNum = int(row[3])
#                    myCounts.append(myInspMatrixNum)
                    myCount = inspArrayRange[myInspMatrixNum]
                    if myCount == 0:
                        firstOcure[myInspMatrixNum] = layNum + 1
                    myCount += 1
                    inspArrayRange[myInspMatrixNum] = myCount
                else:
#                    returnArray.append(myCounts)
                    layNum = layNum + 1
#                    myRows = []
#                    myCounts = []
    else:
        print "Log File Doesn't Exist: "
    return [firstOcure, inspArrayRange]

def getCross(inRules, inInspArraySequence, inWidth, inLogData):
    dirPath = r"/storage/emulated/0/CA/_moje pokusy/cross_test.png"  
    recSize = inWidth / (len(inRules)*4+1.0)
    crossSize = recSize * 3
    gap = recSize
    fontSize = int(crossSize*0.8)
    crossOffset0Vert = fontSize + int(recSize)
    crossOffset0=0
    crossOffset1=recSize
    crossOffset2=recSize*2
    crossOffset3=crossSize  
    text2Offset = crossOffset0Vert + int(crossOffset3) + int(recSize)+15
    imHeight = text2Offset + fontSize + int(recSize)
    fadeValue = 0.18
    returnArray = []
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
    font = ImageFont.truetype("raavi.ttf", fontSize)
    im = Image.new('RGB', (inWidth,imHeight), (0, 0, 0))
    imD = ImageDraw.Draw(im)
    for i, s in enumerate(inInspArraySequence):
        fillColor0 = int(s[0]*(255*fadeValue+((1-fadeValue)*int(inRules[i])*255)))
#        frameColor = int(255*fadeValue+((1-fadeValue)*int(inRules[i])*255))
        frameColor = int(255*fadeValue)
        imD.rectangle([((crossSize*i+gap*i)+crossOffset1,crossOffset0Vert), (int((crossSize*i+gap*i)+crossOffset2), int(crossOffset0Vert+crossOffset1))], (fillColor0, fillColor0,fillColor0),(frameColor,frameColor,frameColor))
        returnArray.append(int((crossSize*i+gap*i)+crossOffset1))
        fillColor0 = int(s[1]*(255*fadeValue+((1-fadeValue)*int(inRules[i])*255)))
        imD.rectangle([((crossSize*i+gap*i)+crossOffset0,crossOffset0Vert + crossOffset1), ((crossSize*i+gap*i)+crossOffset1,crossOffset0Vert + crossOffset2)], (fillColor0, fillColor0,fillColor0),(frameColor,frameColor,frameColor))
        fillColor0 = int(s[2]*(255*fadeValue+((1-fadeValue)*int(inRules[i])*255)))
        imD.rectangle([((crossSize*i+gap*i)+crossOffset1,crossOffset0Vert + crossOffset1), ((crossSize*i+gap*i)+crossOffset2, crossOffset0Vert + crossOffset2)], (fillColor0, fillColor0,fillColor0),(frameColor,frameColor,frameColor))
        fillColor0 = int(s[3]*(255*fadeValue+((1-fadeValue)*int(inRules[i])*255)))
        imD.rectangle([((crossSize*i+gap*i)+crossOffset2,crossOffset0Vert + crossOffset1), ((crossSize*i+gap*i)+crossOffset3, crossOffset0Vert + crossOffset2)], (fillColor0, fillColor0,fillColor0),(frameColor,frameColor,frameColor))
        fillColor0 = int(s[4]*(255*fadeValue+((1-fadeValue)*int(inRules[i])*255)))
        imD.rectangle([((crossSize*i+gap*i)+crossOffset1,crossOffset0Vert + crossOffset2), ((crossSize*i+gap*i)+crossOffset2, crossOffset0Vert + crossOffset3)], (fillColor0, fillColor0,fillColor0),(frameColor,frameColor,frameColor))
        imD.text((int((crossSize*i+gap*i)+crossOffset1), text2Offset - fontSize),inRules[i],font=font, fill=(255,255,255,255))
        imD.text((int((crossSize*i+gap*i)+crossOffset1), 0), str(i),font=font, fill=(255,255,255,255))
        myHSLcol = "hsl(" + str(int(remap(myOcurencesCount[i], 0, maxOcurenceValue, 0, 185))) + ",100%, " + str(int(remap(myOcurencesCount[i], 0, maxOcurenceValue, 30, 70))) + "%)"
        imD.text((int((crossSize*i+gap*i)+crossOffset1), text2Offset - fontSize*2), str(myFirstOcurences[i]),font=font, fill=myHSLcol)
        textXpos = 3
        for s in scaleRange:
            myHSLcol = "hsl(" + str(int(remap(s, 0, maxOcurenceValue, 0, 185))) + ",100%, " + str(int(remap(s, 0, maxOcurenceValue, 30, 70))) + "%)"
            imD.text((textXpos, text2Offset), str(s),font=font, fill=myHSLcol)
            myTextSize = imD.textsize(str(s),font=font)
            textXpos += (myTextSize[0] + 15)
#    im.save(dirPath)
    return im

def getInspArraySeqence(inArLenght):
    rulesCount = pow(2, inArLenght)
    arRange = range(0, rulesCount)
    binSeqDiv = [pow(2, x) for x in range(0,inArLenght)]
    binSeqDiv.reverse()
    myArray = [[math.trunc(x / y) % 2 for x in arRange] for y in binSeqDiv]
    myArray = map(list, zip(*myArray)) 
    return myArray

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

def runRndSequence():
    rules = []
    CA = []
    num = 0
    rules.append(myRule)
    for i in range(0, len(myRule)):
        rules.append(getInvertedDigit(myRule, i))
        position = int(rules[i],2)
        print num
        print "position " + str(position)
        myCA = run(resolutionX, resolutionY, layersCount, rules[i], dirPath, generateRandom, shiftDir, rndBaseRule)
        CA.append([myCA, position, rules[i]])
        num += 1
    createImgCollection(CA, dirPath)
    for i in rules:
        print int(i, 2)
         
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