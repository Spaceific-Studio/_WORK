# -*- coding: utf-8 -*-
import numpy as np
np.set_printoptions(threshold='nan')
import os
from os import walk
import os.path as osPath
import math
import csv
from PIL import Image, ImageDraw, ImageFont, ImageColor

def generateRandomRule():
    myRule = ""
    for i in range(0,32):
         myRule += str(random.randint(0,1))
    return myRule
    
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

def getInspArrayRangeZero(inArLenght):
    rulesCount = pow(2, inArLenght)
    returnArray = []
    arRange = range(0, rulesCount) 
    for i in arRange:
        returnArray.append(0)
    return returnArray
    
def getInspArraySeqence(inArLenght):
    rulesCount = pow(2, inArLenght)
    arRange = range(0, rulesCount)
    binSeqDiv = [pow(2, x) for x in range(0,inArLenght)]
    binSeqDiv.reverse()
    myArray = [[math.trunc(x / y) % 2 for x in arRange] for y in binSeqDiv]
    myArray = map(list, zip(*myArray)) 
    return myArray
    
def returnOne(inNum):
    if inNum > 1:
        return 1
    else:
        return inNum
def loadLayers(inDirPath):
    myDir = []
    truePixs = [[]]
    returnImages = []
    returnData = []
    lastImgSize = 0
    for i in inDirPath:
        myImgColors = []
        myImgs = []
        if os.path.isdir(i):
            myDir = os.listdir(i)
            myDir.sort()
#        print myDir
        if len(myDir) != 0:
            for j in myDir:
                lastImg = Image.open(i + "/" + j)
                lastImg.convert("1")
                lastImg.tobitmap(lastImg)
                lastImgSize = lastImg.size
                myImgColors.append(lastImg.getcolors())
                myImgs.append(lastImg)
#                print "LAST LOADED IMAGE: " + j
#                print "colors = rs = " + str(lastImg.getcolors())
        else:
            return []
        splitString = i.split("_")
        ruleNum = splitString[len(splitString)-2]
        returnData.append([myImgColors, lastImgSize[0], lastImgSize[1], ruleNum, myImgs])
    return returnData
    
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
    for j, s in enumerate(f):
        f[j] = inDirPath + s
#    print myDirs[: inRange[len(inRange)-1]]
#    print f[inRange[0]:inRange[len(inRange)-1]]
    f.sort()
#    print f[inRange[0]:inRange[len(inRange)-1]]
    print "endLayer: " + str(endLayer)
    return f[inRange[0]: (inRange[len(inRange)-1])+1]
    
def getCross(inRules, inInspArraySequence, inWidth, inLogData):
    print "inRules"
    print inRules
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
    text2Offset = crossOffset0Vert + int(crossOffset3) + int(recSize)+30
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
    
def createColorAnalyze(inColData, inSavePath, logReadDir):
    returnArray = []
    for i, imgs in enumerate(inColData):
        textHeight = 10
        resX = imgs[1]
        resY = imgs[2]
        columns = max(math.trunc(math.sqrt(len(imgs[4]))),20)
        maxValue = resX * resY
        nResX = resX * columns
        nResY = 600
        myValues =[]
        mySavePath = inSavePath + str(int(imgs[3],2)) + "_" + imgs[3] + "_" + str(resX) + "x" + str(resY) +"_analyse.png"
        mySavePathBig = inSavePath + str(int(imgs[3],2)) + "_" + imgs[3] + "_" + str(resX) + "x" + str(resY) +"_analyse_big.png"
        logReadPath = logReadDir +imgs[3] + "_" + str(resX) + "x" + str(resY) + ".csv"
        myLogsData = readCSV_Log(logReadPath)
        crossIm = getCross(imgs[3], getInspArraySeqence(5), nResX, myLogsData)
        pColXStart = 0
        pRowYStart = nResY + textHeight*10 + crossIm.size[1]
        mySAnal = Image.new("RGB",(nResX,nResY))
        myBAnal = Image.new("RGB",(columns * resX,nResY + textHeight*10 + int(len(imgs[4])/columns*resY + crossIm.size[1])),(0,0,0))
        myFont = ImageFont.truetype("raavi.ttf", textHeight)
        myFont2 = ImageFont.truetype("arial.ttf", textHeight)
 #+ textHeight + int(math.ceil(len(imgs[4])/columns))))
        mySAnalDraw = ImageDraw.Draw(mySAnal)
        myBAnalDraw = ImageDraw.Draw(myBAnal)
        myImgs = imgs[4]
        for j, cols in enumerate(imgs[0]):    
            blackValue = 0
            whiteValue = 0
            bX = nResX / float(len(imgs[0]))
            pColX = pColXStart + ((j % columns)*resX)
            pRowY =	pRowYStart + math.trunc(j/columns)*resY
            for k, vals in enumerate(cols):
                if vals[1] == 0:
                    blackValue = vals[0]
                elif vals[1] == 255:
                    whiteValue = vals[0]
            myValues.append((pColX, pRowY))
            mySAnalDraw.rectangle([bX*j, 0, (bX*j)+bX, remap(whiteValue, 0, maxValue, 0, nResY)], (255,255,255))
            myBAnal.paste(myImgs[j], (pColX, pRowY))
        returnArray.append(myValues)
        myBAnal.paste(mySAnal, (0,0))       
        myBAnal.paste(crossIm, (0,mySAnal.size[1]))
        myBAnalDraw.text((3,nResY+crossIm.size[1]), "RULE BINAR CODE: " + imgs[3],font=myFont2)
        myBAnalDraw.text((3,nResY+crossIm.size[1] + textHeight), "GENERATION COUNT: " + str(len(imgs[0])),font=myFont2)
        if len(myLogsData) != 0:
            myFirstOcurences = myLogsData[0]
            myOcurencesCount = myLogsData[1]
            myBAnalDraw.text((3,nResY+crossIm.size[1] + textHeight*2), "GENERATION OF FIRST OCURENCE: " + str(myFirstOcurences),font=myFont2)
            myBAnalDraw.text((3,nResY+crossIm.size[1] + textHeight*3), "OCURENCE COUNT: " + str(myOcurencesCount),font=myFont2)
        mySAnal.save(mySavePath)
        myBAnal.save(mySavePathBig)
    return returnArray

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
                if len(row) != 1 and len(row) >= 4: 
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

def run(inDirPath):
    myDirs = loadDirs(inDirPath, range(0, 40))
    for i in myDirs:
        print i
    myData = loadLayers(myDirs)
    print "\n" 
    print "myData: " 
    print "myDataLen " + str(len(myData))
    for i, d in enumerate(myData):
        print "DIR_NUMBER: " + str(i)
        print "resX: " + str(d[1])
        print "resY: " + str(d[2])
        print "ruleNumber: " 
        print d[4]
#        print myDirs[i]
        a=0
        for j in d[0]:
            print str(a)
            print j
            a += 1
    myAnalyzeData = createColorAnalyze(myData, savePath, logReadDir)
    for i in myAnalyzeData:
        print i
     
def getInvertedDigit(inRule, inPos):
    returnString = ""
    listString = list(inRule)   
    if listString[inPos] == '0':
        listString[inPos] = '1'
    elif listString[inPos] == '1':
        listString[inPos] = '0'
    return ''.join(listString)

dirPath = r"/storage/emulated/0/CA/_moje pokusy/CELULAR_AUTOMAT-2D/zaloha/z/"
savePath = r"/storage/emulated/0/CA/_moje pokusy/CELULAR_AUTOMAT-2D/analyse/interesting2/"
logReadDir = r"/storage/emulated/0/CA/_moje pokusy/CELULAR_AUTOMAT-2D/CSV_log/"

resolutionX = 51
resolutionY = 51
layersCount = 100
run(dirPath)