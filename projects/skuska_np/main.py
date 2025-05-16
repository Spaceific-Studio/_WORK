# -*- coding: utf-8 -*-
import random
import math
#import Image as sImage
from PIL import Image, ImageDraw, ImageFont, ImageColor
from os import walk
import os
import os.path as osPath
import sys
import csv
import numpy as np

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
    
def getBinRuleFromInt(inInt):
    returnBins = []
    zeroes32 = []
    for x in range(0,512):
        zeroes = ""
        for y in range(0,x):
            zeroes += "0"
        zeroes32.append(zeroes)
#    for i in inRange:
    myBin = "{0:b}".format(inInt)
    myBinFull = zeroes32[511 - (len(myBin)-1)] + myBin
    returnBins.append(myBinFull)
    return myBinFull
    
def getInspArrayRangeZero(inArLenght):
    rulesCount = pow(2, inArLenght)
    returnArray = []
    arRange = range(0, rulesCount) 
    for i in arRange:
        returnArray.append(0)
    return returnArray
    

readDirPath = r"/storage/emulated/0/CA/_moje pokusy/IMG2"
logPath = r"/storage/emulated/0/CA/_moje pokusy/CELULAR_AUTOMAT-2D/CSV_log/CA2D9C_34fc6e3bedc38f68adc4866fd0c36d42e6e83920bd4281b41d478c0b0dc1efbb302f56f3359d392b5a9cde647883270fe60f2dbaf113fdb37bd70a644b10c00_51x51.csv"
saveSeqPath = r"/storage/emulated/0/CA/_moje pokusy/CELULAR_AUTOMAT-2D/RND-sequence/"
saveNbAnal = r"/storage/emulated/0/CA/_moje pokusy/CELULAR_AUTOMAT-2D/zaloha/analNbTest10.png"
saveNbAnalImg = r"/storage/emulated/0/CA/_moje pokusy/CELULAR_AUTOMAT-2D/zaloha/"
saveOqAnal = r"/storage/emulated/0/CA/_moje pokusy/CELULAR_AUTOMAT-2D/zaloha/analOqTest10.png"
saveNPtestImg = r"/storage/emulated/0/CA/_moje pokusy/CELULAR_AUTOMAT-2D/zaloha/saveNPtestImg3.png"
loadTestImg	 = r"/storage/emulated/0/CA/_moje pokusy/CELULAR_AUTOMAT-2D/zaloha/analNbTest10.png"
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
    print coords[5]
    print inspArrNums[5]
    print myNbCounts[5]
    return [firstOcure, inspArrayRange, coords, inspArrNums, myNbCounts]

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

def getInspArraySeqence(inArLenght):
    rulesCount = pow(2, inArLenght)
    arRange = range(0, rulesCount)
    binSeqDiv = [pow(2, x) for x in range(0,inArLenght)]
    binSeqDiv.reverse()
    myArray = [[math.trunc(x / y) % 2 for x in arRange] for y in binSeqDiv]
    myArray = map(list, zip(*myArray)) 
    return myArray

def neighbourAnalyse(inLogData, inXres, inYres):
    myCoords = inLogData[2]
    myNbCounts = inLogData[4]
    myInspArrNums = inLogData[3]
    layCount = len(myCoords)
    textHeight = 11
    textGap = int(textHeight*0.3)
    textLine = textHeight + textGap
    textFont = ImageFont.truetype("arial.ttf", textHeight)
    myAnalImg = Image.new('RGBA', (inXres*layCount, inYres+textLine))
    myAnalImgDraw = ImageDraw.Draw(myAnalImg)
    myOqAnalImg = Image.new('RGBA', (inXres*layCount, inYres+textLine))
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
        myLayer = Image.new('RGBA', (inXres, inYres))
        myLayerDraw = ImageDraw.Draw(myLayer)
        myOqLayer = Image.new('RGBA', (inXres, inYres))
        myOqLayerDraw = ImageDraw.Draw(myOqLayer)
        for j, pix in enumerate(layCoords):
            pixNbCount = layNbCounts[j]
            pixInsArNum = myInspArrNums[i][j]
            myOqHSLcol = "hsl(" + str(int(remap(myOcurencesCount[pixInsArNum], 0, maxOcurenceValue, 0, 185))) + ",100%, " + str(int(remap(myOcurencesCount[pixInsArNum], 0, maxOcurenceValue, 30, 70))) + "%)"
            mappedCount = (remap(pixNbCount, 0, 8, hueMin, hueMax) + hueOffset) % 360
            mappedSat = (100-remap(pixNbCount, 0, 8, satMin, satMax))
            mappedLight = 100-remap(pixNbCount, 0, 8, lightMin, lightMax)
            hslCol = "hsl(" + str(int(mappedCount)) + "," + str(int(mappedSat)) +"%," + str(int(mappedLight)) + "%)"
            myLayerDraw.point([pix[0], pix[1]], hslCol)
            myOqLayerDraw.point([pix[0], pix[1]], myOqHSLcol)
#        myLayer.save(saveNbAnalImg + str(i) + ".png")
#        print "img was saved"
        myAnalImg.paste(myLayer, (i*inXres,0))
        myOqAnalImg.paste(myOqLayer, (i*inXres,0))
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
        print "tNumXOffset"
        print tNumXOffset
        myAnalImgDraw.text((tXOffset + tNumXOffset*f, inYres), pixNum,font=textFont, fill='white')
#        myAnalImgDraw.rectangle([tXOffset + f*textLine, inYres,tXOffset + f*textLine + textLine, inYres + textLine], myHslCol)
#        myAnalImgDraw.rectangle([tXOffset + f*textLine, inYres, tXOffset + f*textLine + textLine, inYres + textLine], fillColor)
        myAnalImgDraw.text((tXOffset, inYres), pixNum,font=textFont, fill=(255,255,255,255))
        tXOffset += tNumXOffset + int(tNumXOffset*0.3)
        myAnalImgDraw.rectangle([tXOffset, inYres, tXOffset + textLine, inYres + textLine], fillColor)
        tXOffset += textLine + int(tNumXOffset*0.3)
    myAnalImg.save(saveNbAnal)
    print "NB analyse img was saved" + saveNbAnal
    myOqAnalImg.save(saveOqAnal)
    print "OQ analyse img was saved" + saveOqAnal

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
    
myLogsData = readCSV_Log(logPath)
myHexRule = "dcea8e9feb96e75c9bdc757b3a870a6d73bf39e2380db3856d3895ae54716223f345586a12b1b00ca2db8a1571e70203317ee812e9b1d4dc314db96165c7ffb8"
rule = getBinRuleFromInt(int(myHexRule, 16))
print rule
#myRule = "".join(rule)
#print type(myRule)
def filterGroupe(inGroupe):
    myInspArr = getInspArray(9)
    
    if (inGroupe in myInspArr):
        return True
    else:
        return False
def filterRule(inRule, inGroupe):
    zeroRule = getInspArrayRangeZero(9)
    print len(zeroRule)
    print len(inRule)
    for g in inGroupe:
        print "G: " + str(g)
        zeroRule[g] = inRule[g]
    return zeroRule
    
             
groupOne = [1,2,4,8,16,32,64,128,256]
groupTwo = [3,5,6,9,10,12,17,18,20,
            24,33,34,36,40,48,65,66,
            68,72,80,96,129,130,132,
            136,144,160,192,257,258,
            260,264,272,288,320,384]
searchArray = np.array([72,80,129])
groupThreeNp = np.array([7,11,13,14,19,21,22,25,
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
              388,392,400,416,448])
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
sym4axis = [0,16,170,186,325,341,495,511]
sym2axis = [40,56,68,84,108,124,130,
            146,198,214,238,254,257,
            273,297,313,365,381,427,
            443,455,471]
            
def get2DpixCoords(inInd, inResX):
    return (inInd % inResX, inInd / inResX)
    
def get1DpixCoord(in2DCoords, inResX):
    return in2DCoords[0] + in2DCoords[1]*inResX
    
def array2PIL(arr, size):
    mode = 'RGBA' 
#    arr = arr.reshape(arr.shape[0]*arr.shape[1], arr.shape[2]) 
    if len(arr[0]) == 3: 
        arr = numpy.c_[arr, 255*numpy.ones((len(arr),1), numpy.uint8)]
#    return Image.frombuffer(mode, size, arr.tostring(), 'raw', mode, 0, 1)
    return Image.fromstring('RGBA', (51,51),arr.tostring())
    
myCoords = myLogsData[2]
layCoords = myCoords[29]
myImg = Image.new('RGBA',(51,51),(0,0,0,255))
npImgArr = np.array(myImg.getdata())
print npImgArr
it = np.nditer(npImgArr, flags=['multi_index'],op_flags=['readwrite'])
myArray = []
i = 0
while not it.finished:
    putArray = (0,0,0,255)
    if i < len(layCoords):        
        xCoord = int(layCoords[i][0])
        yCoord = int(layCoords[i][1])
        if it.multi_index[0] == get1DpixCoord((xCoord, yCoord), myImg.size[0]) and it.multi_index[1] == 0:
            it[0] = 255
            putArray = (255,0,0,255)
            i += 1
    print "%d <%s>" % (it[0], it.multi_index),
    if it.multi_index[0] >0 and it.multi_index[0] % 4 == 0:
        myArray.append(putArray)
    it.iternext()
for x in np.nditer(npImgArr):
    print x

data = list(tuple(pixel) for pixel in npImgArr)
print myArray
print len(myArray)
print npImgArr.tostring()
myImg.putdata(data)
#myImg = array2PIL(npImgArr, myImg.size)
print myImg
myImg.save(saveNPtestImg)

    	
print get2DpixCoords(0, 51)
print get1DpixCoord(get2DpixCoords(0, 51), 51)

#for x in np.nditer(npImgArr, order='C'):
#    print(x)
#mySearch = np.where(groupThreeNp == 41)
#mySearch2 = np.any(searchArray == 80)
#npWhere = [np.where(groupThreeNp == x) for x in searchArray]
#print npWhere
#filteredRuleByGroupe = filterRule(rule, groupThreeNp)
#myFilteredRuleStr = ""
#for i in filteredRuleByGroupe:
#    myFilteredRuleStr += str(i)
#print "myFilteredRuleStr"    
#print myFilteredRuleStr
#print getNeighbourCounts()
#neighbourAnalyse(myLogsData, 51, 51)
#myInspArrSeq = getInspArraySeqence(9)