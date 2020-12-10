import random
import math
#import Image as sImage
from PIL import Image, ImageDraw, ImageFont, ImageColor
from os import walk
import os
import os.path as osPath
import sys
import csv
#from kivy.app import App
#from kivy.uix.button import Button
#from kivy.uix.image import Image as kImage
#class TestApp(App):
#    def build(self):
#        return Button(text='hello world')
#TestApp().run()
random.seed()
myImg = r"/storage/emulated/0/CA/_moje pokusy/CELULAR_AUTOMAT-2D/RND-sequence/CA2D2_1697936302_01100101001101000111001110101110_51x51x50.png"
#myKImg = kImage(source=myImg)
#dImage = sImage.open(r"/storage/emulated/0/CA/_moje pokusy/CELULAR_AUTOMAT-2D/RND-sequence/CA2D2_1697936302_01100101001101000111001110101110_51x51x50.png")
#dImage.show()
#os.system("xdg-open CA2D2_1697936302_01100101001101000111001110101110_51x51x50.png")
rule = ""
#PILimage = Image.open(myImg)
#print PILimage
#PILimage.show()
for i in range(0,32):
  rule += str(random.randint(0,1))
print rule
os.system('cd data')
#print sys.platform
#print sys.version_info
#print sys.builtin_module_names
#print help(sys)
code = bin(36)
print code
a = [1,2,3]
#print range(0, len(a))
myString = "0"
#if myString == "0":
#    print "TO FACHA"
    
def getInvertedRule(inRule):
    returnString = ""
    for i in inRule:
        if i == "0":
            returnString += "1"
        elif i == "1":
            returnString += "0"
    return returnString
    
def getInvertedDigit(inRule, inPos):
    returnString = ""
    listString = list(inRule)   
    if listString[inPos] == '0':
        listString[inPos] = '1'
    elif listString[inPos] == '1':
        listString[inPos] = '0'
    return ''.join(listString)
print "invRule"
print getInvertedDigit(rule, 5)
    
#print getInvertedRule(rule)

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
    return returnBins
    

sRule = shiftRule(rule, "R")
print "ShiftedRuleR: \n" + sRule
sRule = shiftRule(rule, "L")
print "ShiftedRuleL: \n" + sRule
print len(sRule)
rRule = randomizeRule(rule, 3)
print "RandomizedRule: \n" + rRule
print rule

def remap(value, minInput, maxInput, minOutput, maxOutput):
    value = maxInput if value > maxInput else value
    value = minInput if value < minInput else value
    inputSpan = maxInput - minInput
    outputSpan = maxOutput - minOutput
    scaledThrust = float(value - minInput) / float(inputSpan)
    return minOutput + (scaledThrust * outputSpan)

print remap(3, 0, 10, 0, 1)
#def drawImage():
#    dirPath = r"/storage/emulated/0/CA/_moje pokusy/000000.bmp"
#    dirPath2 = r"/storage/emulated/0/CA/_moje pokusy/697_51x51.bmp"
#    im = Image.new('RGB', (100,100), (20,200,80))
#    im2 = Image.open(dirPath2)
#    print im2.size
#    imD = ImageDraw.Draw(im)
#    imD.rectangle([(0,0), (10,10)], (10,60,100))
#    imD.rectangle([(10.5,0.78), (20.324,50.98)], (0,0,100))
#    im.paste(im2, (60,80))
#    im.save(dirPath)
#drawImage()
print math.sqrt(4)

def getInspArray(inArLenght):
    rulesCount = pow(2, inArLenght)
    arRange = range(0, rulesCount) 
    return arRange

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
    
def getCross(inRules, inInspArraySequence, inWidth):
    dirPath = r"/storage/emulated/0/CA/_moje pokusy/cross_test.png"  
    recSize = inWidth / (len(inRules)*4+1.0)
    crossSize = recSize * 3
    gap = recSize
    fontSize = int(crossSize*0.8)
    textSize =0
    crossOffset0Vert = fontSize + int(recSize)
    crossOffset0=0
    crossOffset1=recSize
    crossOffset2=recSize*2
    crossOffset3=crossSize  
    text2Offset = crossOffset0Vert + int(crossOffset3) + int(recSize)
    imHeight = text2Offset + fontSize + int(recSize)
    fadeValue = 0.3
    returnArray = []
    font = ImageFont.truetype("raavi.ttf", fontSize)
    im = Image.new('RGB', (inWidth,imHeight), (0, 0, 0))
    imD = ImageDraw.Draw(im)
    textSize = imD.textsize("petronel", font=font)
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
        imD.text((int((crossSize*i+gap*i)+crossOffset1), text2Offset),inRules[i],font=font, fill=(255,255,255,255))
        imD.text((int((crossSize*i+gap*i)+crossOffset1), 0), str(i),font=font, fill=(255,255,255,255))
    im.save(dirPath)
    return textSize

print getInspArraySeqence(5)
print "TEXT SIZE: "
print getCross(rule, getInspArraySeqence(5), 510)
readDirPath = r"/storage/emulated/0/CA/_moje pokusy/IMG2"
logPath = r"/storage/emulated/0/CA/_moje pokusy/CELULAR_AUTOMAT-2D/CSV_log/CA2D9C_dcea8e9feb96e75c9bdc757b3a870a6d73bf39e2380db3856d3895ae54716223f345586a12b1b00ca2db8a1571e70203317ee812e9b1d4dc314db96165c7ffb8_51x51.csv"
saveSeqPath = r"/storage/emulated/0/CA/_moje pokusy/CELULAR_AUTOMAT-2D/RND-sequence/"

def readCSV_Log(inPath):
    returnArray = []
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
        print "Log File Doesn't Exist: " + inPath
    return [firstOcure, inspArrayRange]

def getInspArraySeqence(inArLenght):
    rulesCount = pow(2, inArLenght)
    arRange = range(0, rulesCount)
    binSeqDiv = [pow(2, x) for x in range(0,inArLenght)]
    binSeqDiv.reverse()
    myArray = [[math.trunc(x / y) % 2 for x in arRange] for y in binSeqDiv]
    myArray = map(list, zip(*myArray)) 
    return myArray
   
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
    print crossMXCoords5x5[0]
    orderTextFontSize = int(crossSize*0.5)
    ocurenceTextFontSize = int(crossSize*0.7)
    headFontSize = int(crossSize*0.6)
    headLines = 4
    headLineGap = int(headFontSize * 0.5)
    headLineHeight = headFontSize + headLineGap
    headTextHeight = (headLineHeight) * headLines + headLineGap
    headTextX = gap
    headText1Y = 0 * headLineHeight
    headText2Y = 1 * headLineHeight
    headText3Y = 2 * headLineHeight
    headText4Y = 3 * headLineHeight
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
    for s in scaleRange:
        myHSLcol = "hsl(" + str(int(remap(s, 0, maxOcurenceValue, 0, 185))) + ",100%, " + str(int(remap(s, 0, maxOcurenceValue, 30, 70))) + "%)"
        imD.text((textXpos, headText4Y), str(s),font=headFont, fill=myHSLcol)
        myTextSize = imD.textsize(str(s),font=headFont)
        textXpos += (myTextSize[0] + 15)
        
    return im   
    
myLogsData = readCSV_Log(logPath)
myHexRule = "dcea8e9feb96e75c9bdc757b3a870a6d73bf39e2380db3856d3895ae54716223f345586a12b1b00ca2db8a1571e70203317ee812e9b1d4dc314db96165c7ffb8"
rule = getBinRuleFromInt(int(myHexRule, 16))
myRule = "".join(rule)
print type(myRule)
#myCrossIm = getCross(myRule, getInspArraySeqence(9), 2, myLogsData)
#myCrossIm.save(saveSeqPath + "testCross.png")
print getInspArraySeqence(9)

#print myCSVdata[:20]
#          012345678910...15...20...25...30
print int("01110110100101011011011100100100", 2)
L = [1, 2 ,3 ,4 ,5]
print L[::-1]
print "bin rule"
print getBinRuleFromInt(36)
#print "{0:b}".format(500)
mystr = str(hex(int("1000", 2)))
print mystr[2:len(mystr)]
myrule = "11111111111111111111"
myListRule = [x for x in myrule]
mySplitedRule = slice(myrule, 8)
print myListRule
#help("string")
def getFirstHalfZeroRule(inRule):
    returnArray = []
    for i, v in enumerate(inRule):
        if i < len(inRule) / 2:
            returnArray.append("0")
        else:
            returnArray.append(inRule[i])
    return "".join(returnArray)

print getFirstHalfZeroRule(myrule)
print (257 % 256)

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
    
def getRndSymetryGroups(inGroups, inOnes):
    lev1positions = range(0,len(inGroups))
    lev1OnesPositions = range(0,len(inOnes))
    lev1RNDCount = random.randint(0,len(inGroups))
    lev1OnesRNDCount = random.randint(1,len(inOnes))
    random.shuffle(lev1positions)
    random.shuffle(lev1OnesPositions)
    lev1positions = lev1positions[0:lev1RNDCount]
    lev1OnesPositions = lev1OnesPositions[0:lev1OnesRNDCount]
    print "lev1positions"
    print lev1positions
    print "lev1OnesPositions"
    print lev1OnesPositions
    lev2positions = []
    posCoords = []
    returnGroups = []
    returnOneGroups = []
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
    for i,x in enumerate(lev1OnesPositions):
        returnOneGroups +=  inOnes[x]
    print "lev2positions"
    print lev2positions
    print "returnOneGroups"
    print returnOneGroups
    print "posCoords"
    print posCoords
    print "returnGroups"
    print returnGroups
    allPositions = returnOneGroups + returnGroups
    print "allPositions"
    print allPositions
    return [allPositions, posCoords]
    
groupOneSym = [[1,256],[2,128],[4,64],[8,32],[16]]
sym1axG = [[],
           [[1,4,64,256],[2,8,32,128]],
           [[5,65,260,320],[10,34,136,160],
            [17,20,80,272],[18,24,48,144]],
           [[7,73,292,448],[11,38,200,416],
            [21,81,276,336],[26,50,152,176],
            [42,138,162,168],[69,261,321,324],
            [97,133,268,322],[98,140,161,266]],
           [[23,89,308,464],[27,54,216,482],
            [45,195,360,390],[58,154,178,184],
            [78,228,291,393],[85,277,337,340],
            [102,204,267,417],[105,135,300,450],
            [113,149,284,338],[114,156,177,282]],
           [[47,203,422,488],[61,211,376,406],
            [79,295,457,484],[94,244,307,409],
            [118,220,283,433],[121,151,316,466],
            [171,174,234,426],[173,227,362,398],
            [327,333,357,453],[229,334,355,397]],
           [[95,311,473,500],[175,235,430,490],
            [187,190,250,442],[189,243,378,414],
            [63,219,438,504],[335,359,461,485],
            [343,349,373,469],[245,350,371,413]],
           [[191,251,446,506],[239,431,491,494],
            [351,375,477,501],[367,463,487,493]],
           [[255,447,507,510],[383,479,503,509]]]
           
rndSymetryGroups = getRndSymetryGroups(sym1axG, groupOneSym)          
myInspArray = getInspArray(9)
myRule = generateRandomRule(myInspArray)
print "myRule after generate random:"
print myRule