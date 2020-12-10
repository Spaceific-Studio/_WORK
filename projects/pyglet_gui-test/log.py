from ca_func import *
import os.path as osPath
import csv

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