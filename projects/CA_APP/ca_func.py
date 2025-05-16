import math
from PIL import Image, ImageDraw, ImageFont, ImageColor, ImageTk
import time
import numpy as np
import os.path as osPath
import csv
import os

def getBinRuleFromHex(inHex):
    returnBins = []
    zeroes512 = []
    for x in range(0,512):
        zeroes = ""
        for y in range(0,x):
            zeroes += "0"
        zeroes512.append(zeroes)
#    for i in inRange:
    myBin = "{0:b}".format(int(inHex,16))
#    print "myBin: " + myBin
#    myBin = bin(inHex)
    myBinFull = zeroes512[511 - (len(myBin)-1)] + myBin
#    print "type myBinFull:"
#    print type(myBinFull)
#   print "myBinFull :" + myBinFull
#   print "len myBin: " + str(len(myBin))
#   print "len myBinFull: " + str(len(myBinFull))
#    returnBins.append(myBinFull)
    return myBinFull   

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

def returnOne(inNum):
    if inNum > 1:
        return 1
    else:
        return inNum

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
    myArray = list(map(list, zip(*myArray)))
    return myArray

def getRule(inRules, inInspArray, XYuf, XYu, XYub, XYf, XY, XYb, XYdf, XYd, XYdb):
    myPixels = str(XYuf) + str(XYu) + str(XYub) + str(XYf) + str(XY) + str(XYb) + str(XYdf) + str(XYd) + str(XYdb)
    rulePosition = int(myPixels, 2)
    return inRules[rulePosition]

def createFirstLayerFromScratch(inResX, inResY):
    firstLayer = Image.new("RGBA",(inResX,inResY), (0,0,0,255))
    firstLayerDraw = ImageDraw.Draw(firstLayer)
    firstLayerDraw.point((inResX/2, inResY/2), (255,255,255,255))
    return firstLayer

def createNextLayer(inFormerImg, inRules, inInspArray, inLaysCount, inCSV_logPath, inWriteLogFile):
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
    if inWriteLogFile == True:
        f = open(inCSV_logPath, 'w')
        writer = csv.writer(f)
    for l in range(0, inLaysCount):
        truePixs = []
        nextImg = Image.new("RGBA",(liWidth, liHeight), (0, 0, 0,255))
        nextImgDraw = ImageDraw.Draw(nextImg)
        myPixData = []
        for b in myFImgData:
            myPixData.append((0,0,0,255))
        if inWriteLogFile == True:
            writer.writerow([l])
        for a, x in enumerate(myFImgData):   
            if (a % liWidth > 0) and (a % liWidth < liWidth -1) and a > liWidth and a < liLength - liWidth:
 #               print "myFImgData[(a - liWidth - 1)]"
 #               print myFImgData[(a - liWidth - 1)]
                XYuf = returnOne(myFImgData[(a - liWidth - 1)][0])
                XYu = returnOne(myFImgData[a - liWidth][0])
                XYub = returnOne(myFImgData[a - liWidth + 1][0])
                XYf = returnOne(myFImgData[a - 1][0])
                XY = returnOne(myFImgData[a][0])
                XYb = returnOne(myFImgData[a + 1][0])
                XYdf = returnOne(myFImgData[a + liWidth - 1][0])
                XYd = returnOne(myFImgData[a + liWidth][0])
                XYdb = returnOne(myFImgData[a + liWidth + 1][0])
                rule = getRule(inRules, inInspArray, XYuf, XYu, XYub, XYf, XY, XYb, XYdf, XYd, XYdb)
                if rule == 1:
#                  truePixs.append([a / liWidth, a % liWidth])
                   truePixs.append((a % liWidth, a / liWidth))
                   myStrInspArray = str(XYuf) + str(XYu) + str(XYub) + str(XYf) + str(XY) + str(XYb) + str(XYdf) + str(XYd)  + str(XYdb)
                   if inWriteLogFile == True:
                       writer.writerow([str(a % liWidth), str(a / liWidth), myStrInspArray, int(myStrInspArray, 2)])
        nextImgDraw.point(truePixs, (255, 255, 255,255))
        myFImgData = np.array(nextImg.getdata())
#        testImg.save(r"/storage/emulated/0/CA/_moje pokusy/testPix.png")
        returnImgs.append(nextImg)
        myPixDatasLog.append(myPixData.append)
        
#    nextImgData = np.array(nextImg.getdata())
    eTime = time.time()
    myTime = eTime -sTime
    print ("Time of creating "+str(inLaysCount)+" CA layers is " + str(int(myTime/60))+" m " +str(int(myTime%60)) + " s")
    return returnImgs

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

def ensure_dir(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.mkdir(directory)

def run(inResX, inResY, inLayCount, inMyRule, inCSV_logPath, inWriteLogFile):
    resXstr = str(inResX)
    resYstr = str(inResY)
    myInspArray = getInspArray(9)
    sourceRule = inMyRule
    sourceRuleArray = [int(x) for x in sourceRule]
#    print "CURRENT RULE: \n" + sourceRule
    slashChar = r"/"
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
    myLayers = createNextLayer(myLastImg, sourceRuleArray, myInspArray, inLayCount-1, inCSV_logPath, inWriteLogFile)
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

def runWithLayer(inFirstLayer, inResX, inResY, inLayCount, inMyRule, inCSV_logPath, inWriteLogFile):
    resXstr = str(inResX)
    resYstr = str(inResY)
    myInspArray = getInspArray(9)
    sourceRule = inMyRule
    sourceRuleArray = [int(x) for x in sourceRule]
#    print "CURRENT RULE: \n" + sourceRule
    slashChar = r"/"
#    layNum = 0
#    print "CURRENT GENERATION: " + str(layNum)
#    properLayNum = getProperLayNum(layNum)
    imageFormat = "bmp"
    myLayers = []
    
#    if layNum == 0:
    firstLayer = inFirstLayer
#    myLayers.append(firstLayer)
#    ensure_dir(finalDirPath)
#    firstLayer.save(finalDirPath + properLayNum + "_" + resXstr + "x" + resYstr + "." + imageFormat)
#    layNum += 1
    myLastImg = firstLayer
    myLayers = createNextLayer(myLastImg, sourceRuleArray, myInspArray, inLayCount-1, inCSV_logPath, inWriteLogFile)
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

def getCross(inRule, inInspArraySequence, inRows, inLogData):
#    dirPath = r"/storage/emulated/0/CA/_moje pokusy/cross_test.png"  
    rows = inRows
    columns = len(inInspArraySequence) / rows
    recColumns = 3
    recRows = 3
    print ("columns:")
    print (columns)
#    recSize = inWidth / (len(inInspArraySequence)/float(rows)) / 7
    recSize = 4
    fadeValue = 0.35
    crossSize = recSize * 7
    outlineWidth = 3
    gap = recSize
    crossMXCoords3x3 = [[0,0],[1,0],[2,0],[0,1],[1,1],[2,1],[0,2],[1,2],[2,2]]
#    print (crossMXCoords3x3[0])
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
    print ("imWidth: " + str(imWidth))
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
            mx3x3Coords = crossMXCoords3x3[j]
            recXCoord = mx3x3Coords[0]
            recYCoord = mx3x3Coords[1]
            recXOffset = crossXOffset + recSize + recXCoord*recSize
            recYOffset = crossYOffset + recSize + recYCoord*recSize
            imD.rectangle([recXOffset, recYOffset, recXOffset+recSize, recYOffset+recSize], fillColor, frameColor)
    textXpos = headTextX
    symGroupCoordStr = "SYMETRY_GROUPS_COORDS:   "
    # symGroupStr =      "SYMETRY_GROUPS_POSITIONS:"
    # for d in rndSymGroupeCoords:
    #     symGroupCoordStr += "("+str(d[0])+","+str(d[1])+")"
    # imD.text((headTextX, headText4Y), symGroupCoordStr,font=headFont, fill="white")
    # for c in myRndSymGroups:
    #     symGroupStr += str(c)+","
    # imD.text((headTextX, headText5Y), symGroupStr,font=headFont, fill="white")
    for s in scaleRange:
        myHSLcol = "hsl(" + str(int(remap(s, 0, maxOcurenceValue, 0, 185))) + ",100%, " + str(int(remap(s, 0, maxOcurenceValue, 30, 70))) + "%)"
        imD.text((textXpos, headText6Y), str(s),font=headFont, fill=myHSLcol)
        myTextSize = imD.textsize(str(s),font=headFont)
        textXpos += (myTextSize[0] + 15)
        
    return im

def getCrossImgs(inRule, inInspArraySequence, inRows, inLogData):
#    dirPath = r"/storage/emulated/0/CA/_moje pokusy/cross_test.png"  
    rows = inRows
    columns = len(inInspArraySequence) / rows
    recColumns = 3
    recRows = 3
    print ("columns:")
    print (columns)
#    recSize = inWidth / (len(inInspArraySequence)/float(rows)) / 7
    recSize = 5
    fadeValue = 0.35
    crossSize = recSize * 3
    outlineWidth = 3
    gap = recSize
    crossMXCoords3x3 = [[0,0],[1,0],[2,0],[0,1],[1,1],[2,1],[0,2],[1,2],[2,2]]
#    print (crossMXCoords3x3[0])
    orderTextFontSize = int(crossSize*0.65)
    ocurenceTextFontSize = int(crossSize*0.8)
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
    orderTextFont = ImageFont.truetype("arial.ttf", orderTextFontSize)
    ocurenceTextFont = ImageFont.truetype("arial.ttf", ocurenceTextFontSize)
    headFont = ImageFont.truetype("arial.ttf", headFontSize)
    rowHeight = orderTextYOffset + crossSize + ocurenceTextFontSize
    imHeight = int(headTextHeight + (rowHeight * rows))
    imWidth = columns * crossSize
    print ("imWidth: " + str(imWidth))
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
#    im = Image.new('RGBA', (imWidth + outlineWidth,imHeight + outlineWidth), (0, 0, 0,255))
    imgs = []
#    imD = ImageDraw.Draw(im)
#    imD.text((headTextX, headText1Y), "BIN: " + inRule, font=headFont, fill=(255,255,255,255))
#    imD.text((headTextX, headText2Y), "INT: " + str(int(inRule, 2)), font=headFont, fill=(255,255,255,255))
#    myHex = str(hex(int(inRule, 2)))
#    imD.text((headTextX, headText3Y),"HEX: " + myHex[2:len(myHex)-1], font=headFont, fill=(255,255,255,255))
    for i, v in enumerate(inInspArraySequence):

#        crossXOffset = (i%columns)*crossSize
#        crossYOffset = headTextHeight + (i/columns)*rowHeight
#        imD.rectangle([crossXOffset, crossYOffset, crossXOffset+crossSize, crossYOffset+crossSize],(0,0,0,0), crossBColor)
##        orderTextX = (crossSize/2) - orderTextSize[0]/2
##        orderTextY = orderTextYOffset
##        imD.text((orderTextX, orderTextY), str(i), font=orderTextFont, fill=(80,80,80,255))
        myMatrixImg = Image.new('RGBA', (crossSize, orderTextFontSize + gap + ocurenceTextFontSize + crossSize), (0, 0, 0,255))
        myMatrixImgD = ImageDraw.Draw(myMatrixImg)
        ocurenceTextSize = myMatrixImgD.textsize(str(myFirstOcurences[i]),font=ocurenceTextFont)
        ocurenceTextX = (crossSize/2) - ocurenceTextSize[0]/2
        ocurenceTextY = orderTextFontSize + gap + crossSize        
        orderTextSize = myMatrixImgD.textsize(str(i),font=orderTextFont)
        orderTextX = (crossSize/2) - orderTextSize[0]/2
        orderTextY = orderTextFontSize
        myHSLcol = "hsl(" + str(int(remap(myOcurencesCount[i], 0, maxOcurenceValue, 0, 185))) + ",100%, " + str(int(remap(myOcurencesCount[i], 0, maxOcurenceValue, 30, 70))) + "%)"
        orderTextColComponent = int(255*0.55)
        orderTextCol = (orderTextColComponent, orderTextColComponent, orderTextColComponent, 255)
        myMatrixImgD.text((orderTextX, 0), str(i),font=orderTextFont, fill=orderTextCol)
        myMatrixImgD.text((ocurenceTextX, ocurenceTextY), str(myFirstOcurences[i]),font=ocurenceTextFont, fill=myHSLcol)
        
        for j, h in enumerate(v):
#            print j
            fCComponent = int(255*fadeValue)
#            frameColor = (fCComponent, fCComponent, fCComponent, fCComponent)
            frameColor = (0, 0, 0, 255)
            fillCComponent = int(int(h)*(255*fadeValue+((1-fadeValue)*int(inRule[i])*255)))
            fillColor = (fillCComponent, fillCComponent, fillCComponent, 255)
            mx3x3Coords = crossMXCoords3x3[j]
            recXCoord = mx3x3Coords[0]
            recYCoord = mx3x3Coords[1]
            recXOffset = recXCoord*recSize
            recYOffset = recYCoord*recSize + orderTextFontSize + gap
            myMatrixImgD.rectangle([recXOffset, recYOffset, recXOffset+recSize, recYOffset+recSize], fillColor, frameColor)
        imgs.append(ImageTk.PhotoImage(myMatrixImg))
    textXpos = headTextX
    symGroupCoordStr = "SYMETRY_GROUPS_COORDS:   "
    # symGroupStr =      "SYMETRY_GROUPS_POSITIONS:"
    # for d in rndSymGroupeCoords:
    #     symGroupCoordStr += "("+str(d[0])+","+str(d[1])+")"
    # imD.text((headTextX, headText4Y), symGroupCoordStr,font=headFont, fill="white")
    # for c in myRndSymGroups:
    #     symGroupStr += str(c)+","
    # imD.text((headTextX, headText5Y), symGroupStr,font=headFont, fill="white")
    # for s in scaleRange:
    #     myHSLcol = "hsl(" + str(int(remap(s, 0, maxOcurenceValue, 0, 185))) + ",100%, " + str(int(remap(s, 0, maxOcurenceValue, 30, 70))) + "%)"
    #     imD.text((textXpos, headText6Y), str(s),font=headFont, fill=myHSLcol)
    #     myTextSize = imD.textsize(str(s),font=headFont)
    #     textXpos += (myTextSize[0] + 15)
    print ("imgs done")
    return imgs

def getCrossImg(inInspArraySequence, inButtonValue, inButtonID, inLogData):
#    dirPath = r"/storage/emulated/0/CA/_moje pokusy/cross_test.png"  
#    rows = inRows
#    columns = len(inInspArraySequence) / rows
    sTime1 = time.time()
    recColumns = 3
    recRows = 3
#    print ("columns:")
#    print (columns)
#    recSize = inWidth / (len(inInspArraySequence)/float(rows)) / 7
    recSize = 5
    fadeValue = 0.35
    crossSize = recSize * 3
    outlineWidth = 3
    gap = recSize
    crossMXCoords3x3 = [[0,0],[1,0],[2,0],[0,1],[1,1],[2,1],[0,2],[1,2],[2,2]]
#    (print crossMXCoords3x3[0])
    
    orderTextFontSize = int(crossSize*0.5)
    ocurenceTextFontSize = int(crossSize*0.8)
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
    eTime2 = time.time()
#   orderTextFont = ImageFont.truetype("raavi.ttf", orderTextFontSize)
    ocurenceTextFont = ImageFont.truetype("arial.ttf", ocurenceTextFontSize)
#    headFont = ImageFont.truetype("arial.ttf", headFontSize)
#    rowHeight = orderTextYOffset + crossSize + ocurenceTextFontSize
#    imHeight = int(headTextHeight + (rowHeight * rows))
#    imWidth = columns * crossSize
#    print ("imWidth: " + str(imWidth))
    
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
    
#    im = Image.new('RGBA', (imWidth + outlineWidth,imHeight + outlineWidth), (0, 0, 0,255))
#    imgs = []
#    imD = ImageDraw.Draw(im)
#    imD.text((headTextX, headText1Y), "BIN: " + inRule, font=headFont, fill=(255,255,255,255))
#    imD.text((headTextX, headText2Y), "INT: " + str(int(inRule, 2)), font=headFont, fill=(255,255,255,255))
#    myHex = str(hex(int(inRule, 2)))
#    imD.text((headTextX, headText3Y),"HEX: " + myHex[2:len(myHex)-1], font=headFont, fill=(255,255,255,255))
#    for i, v in enumerate(inInspArraySequence):

#        crossXOffset = (i%columns)*crossSize
#        crossYOffset = headTextHeight + (i/columns)*rowHeight
#        imD.rectangle([crossXOffset, crossYOffset, crossXOffset+crossSize, crossYOffset+crossSize],(0,0,0,0), crossBColor)
##        orderTextX = (crossSize/2) - orderTextSize[0]/2
##        orderTextY = orderTextYOffset
##        imD.text((orderTextX, orderTextY), str(i), font=orderTextFont, fill=(80,80,80,255))
    myMatrixImg = Image.new('RGBA', (crossSize, ocurenceTextFontSize + crossSize), (0, 0, 0,255))
    myMatrixImgD = ImageDraw.Draw(myMatrixImg)
    ocurenceTextSize = myMatrixImgD.textsize(str(myFirstOcurences[inButtonID]),font=ocurenceTextFont)
    ocurenceTextX = (crossSize/2) - ocurenceTextSize[0]/2
    ocurenceTextY = crossSize        
#    orderTextSize = myMatrixImgD.textsize(str(inButtonID),font=orderTextFont)
    myHSLcol = "hsl(" + str(int(remap(myOcurencesCount[inButtonID], 0, maxOcurenceValue, 0, 185))) + ",100%, " + str(int(remap(myOcurencesCount[inButtonID], 0, maxOcurenceValue, 30, 70))) + "%)"
    myMatrixImgD.text((ocurenceTextX, ocurenceTextY), str(myFirstOcurences[inButtonID]),font=ocurenceTextFont, fill=myHSLcol)
    v = inInspArraySequence[inButtonID]
    eTime3 = time.time()
    sTime = time.time()
    for j, h in enumerate(v):
#            print (j)
        fCComponent = int(255*fadeValue)
#            frameColor = (fCComponent, fCComponent, fCComponent, fCComponent)
        frameColor = (0, 0, 0, 255)
        fillCComponent = int(int(h)*(255*fadeValue+((1-fadeValue)*int(inButtonValue)*255)))
        fillColor = (fillCComponent, fillCComponent, fillCComponent, 255)
        mx3x3Coords = crossMXCoords3x3[j]
        recXCoord = mx3x3Coords[0]
        recYCoord = mx3x3Coords[1]
        recXOffset = recXCoord*recSize
        recYOffset = recYCoord*recSize
        myMatrixImgD.rectangle([recXOffset, recYOffset, recXOffset+recSize, recYOffset+recSize], fillColor, frameColor)
    eTime = time.time()
    myTime = eTime - sTime
    print ("Time of creating one matrix image was" + str(myTime) + " s")
#    imgs.append(myMatrixImg)
#    textXpos = headTextX
#    symGroupCoordStr = "SYMETRY_GROUPS_COORDS:   "
    # symGroupStr =      "SYMETRY_GROUPS_POSITIONS:"
    # for d in rndSymGroupeCoords:
    #     symGroupCoordStr += "("+str(d[0])+","+str(d[1])+")"
    # imD.text((headTextX, headText4Y), symGroupCoordStr,font=headFont, fill="white")
    # for c in myRndSymGroups:
    #     symGroupStr += str(c)+","
    # imD.text((headTextX, headText5Y), symGroupStr,font=headFont, fill="white")
    # for s in scaleRange:
    #     myHSLcol = "hsl(" + str(int(remap(s, 0, maxOcurenceValue, 0, 185))) + ",100%, " + str(int(remap(s, 0, maxOcurenceValue, 30, 70))) + "%)"
    #     imD.text((textXpos, headText6Y), str(s),font=headFont, fill=myHSLcol)
    #     myTextSize = imD.textsize(str(s),font=headFont)
    #     textXpos += (myTextSize[0] + 15)
    eTime1 = time.time()
    myTime1 = eTime1 - sTime1
    print ("Time of completing getCrossImg() was" + str(myTime1) + " s")
    myTime2 = eTime2 - sTime1
    myTime3 = eTime3 - sTime1
    print ("Time2 was" + str(myTime2) + " s")
    print ("Time3 was" + str(myTime3) + " s")

    return myMatrixImg

def readCSV_Log(inPath):
    returnArray = []
    coords = []
    inspArrNums = []
    myNbCounts = []
    inspArrayRange = getInspArrayRangeZero(9)
    firstOcure = getInspArrayRangeZero(9)
    try:
        if osPath.isfile(inPath) == True:
            print ("Log File Exists: " + inPath)
            f = open(inPath, "r")
            print ("Reading CSV log data...")
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
            print("Log File Doesn't Exist: " + inPath)
    #    print (coords[5])
    #    print (inspArrNums[5])
    #    print (myNbCounts[5])
    except:
        pass
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

def getSym4axisGroup():
    sym4AxisG = [16,170,186,325,341,495,511]
    return sym4AxisG

def getSym2axisGroup():
    sym2AxisG = [[[0,511],[16,495],[170,341],[186,325]],
                 [[40,130],[68,257]],
                 [[56,146],[84,273]],
                 [[238,427],[365,455]],
                 [[254,443],[381,471]],
                 [[297,198],[108,387],[313,214],[403,124]]]
    return sym2AxisG

def getSymetryOneAxisGroups():
    sym1axG = [[],
           [[1,256,4,64],[2,128,8,32]],
           [[5,320,260,65],[10,160,34,136],
            [17,272,20,80],[18,144,24,48]],
           [[7,448,292,73],[11,416,38,200],
            [21,336,276,81],[26,176,50,152],
            [42,168,162,138],[69,324,261,321],
            [97,268,133,322],[98,140,161,266]],
           [[23,464,308,89],[27,432,54,216],
            [45,360,390,195],[58,184,178,154],
            [78,228,291,393],[85,340,277,337],
            [102,204,267,417],[105,300,135,450],
            [113,284,149,338],[114,156,177,282]],
           [[47,488,422,203],[61,376,406,211],
            [79,484,295,457],[94,244,307,409],
            [118,220,283,433],[121,316,151,466],
            [171,426,174,234],[173,362,227,398],
            [327,453,357,333],[229,334,355,397]],
           [[95,500,311,473],[175,490,235,430],
            [187,442,190,250],[189,378,414,243],
            [63,504,438,219],[335,485,359,461],
            [343,469,373,349],[245,350,371,413]],
           [[191,506,446,251],[239,494,431,491],
            [351,501,375,477],[367,493,487,463]],
           [[255,510,507,447],[383,509,503,479]]]
    return sym1axG

def getAsymetryGroups():
    asymG = [[],
             [],
             [[3,384,36,72],[6,192,288,9],
              [12,96,129,258],[33,264,66,132]],
             [[352,13,193,262],[14,224,137,290],
              [400,19,52,88],[22,208,25,304],
              [28,112,145,274],[35,392,164,74],
              [37,328,388,67],[296,41,134,194],
              [44,104,131,386],[49,280,82,148],
              [70,196,289,265],[100,76,259,385]],
             [[480,15,294,201],[29,209,278,368],
              [306,30,153,240],[39,456,420,75],
              [424,43,166,202],[46,232,418,139],
              [51,408,180,90],[53,344,83,404],
              [57,312,210,150],[120,60,147,402],
              [452,71,293,329],[263,449,356,77,],
              [212,86,305,281],[116,92,275,401],
              [396,99,165,330],[332,101,323,389],
              [172,106,163,394],[354,141,270,225],
              [226,142,298,169],[326,197,269,353]],
             [[31,217,310,496],[55,91,436,472],
              [59,182,218,440],[62,155,248,434],
              [87,309,345,468],[93,279,372,465],
              [103,331,421,460],[107,167,428,458],
              [109,364,391,451],[110,395,236,419],
              [115,181,412,346],[117,339,348,405],
              [122,179,188,410],[143,302,233,482],
              [157,286,370,241],[158,185,242,314],
              [199,361,301,454],[206,425,230,299],
              [213,369,342,285],[271,205,358,481]],
             [[111,423,459,492],[119,347,437,476],
              [123,183,444,474],[125,380,407,467],
              [126,252,435,411],[215,317,377,470],
              [221,287,374,497],[222,246,315,441],
              [231,363,429,462],[237,366,399,483],
              [249,159,318,498],[303,207,486,489]],
             [[127,475,439,508],[223,319,502,505],
              [247,379,445,478],[253,382,415,499]]]

    return asymG

def get2DpixCoords(inInd, inResX):
    return (inInd % inResX, inInd / inResX)   
    
def get1DpixCoord(in2DCoords, inResX):
    return in2DCoords[0] + in2DCoords[1]*inResX