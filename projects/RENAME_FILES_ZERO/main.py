from os import walk
import os
import os.path as osPath
import sys
import shutil

dirPath = r"/storage/emulated/0/CA/_moje pokusy/CELULAR_AUTOMAT-2D/zaloha/z/CA2D2_1960164845_01110100110101011011110111101101_51x51/"
requiredDigitCount = 4
doCreateSubDirs = True
subDirsAmount = 200
subLists  = []


def readDirFiles(inDirPath):
    myFiles = []
    for (path, dirnames, filenames) in walk(inDirPath): 
        myFiles.extend(filenames) 
        break
    return myFiles

def getFileIndex(inFileName):        
    return inFileName.split("_")[0]

def adjustFileName(inFName, inReqDigCount, inPos):
    myIndex = getFileIndex(inFName)
    zeroesInsert = ""
    newFName = ""
    if len(myIndex) < inReqDigCount:
        reqZeroes = inReqDigCount - len(myIndex)
        for i in range(0, reqZeroes):
            zeroesInsert += "0"
        newFName = zeroesInsert + inFName
        os.rename(dirPath + inFName, dirPath + newFName)
        print "the file: " + dirPath + inFName + " was renamed to: " + newFName
#            os.rename(dirPath + inFName, dirPath + newFName)
#            print "the file: " + dirPath + inFName + " was renamed to: " + newFName
#            print "the file: " + dirPath + inFName + " WAS NOT RENAMED"
    else:
        newFName = inFName
#        print "the file: " + dirPath + inFName + " has correct format"
    return newFName

def addZeroes(inFiles, inRequiredDigitCount):
    returnList = []
    for i, f in  enumerate(inFiles):
        returnList.append(adjustFileName(f, inRequiredDigitCount, i))
    return returnList

myOldList = readDirFiles(dirPath)
myNewList = addZeroes(myOldList, requiredDigitCount)

def ensure_dir(file_path):
    directory = os.path.dirname(file_path) 
    if not os.path.exists(directory):
        os.makedirs(directory)
        print "directory was created: " + directory
    else:
        print "directory has allready been created: " + directory

def createSubDirs(inDirList, inDirPath, inSubDirsAmount, inCreateSubDirs):
    splitedPath = inDirPath.split("/")
    basePath = ""
    subLists = []
    for i in splitedPath[1:len(splitedPath)-2]:
        basePath += "/" + i
    basePath += "/"
    if inCreateSubDirs == True:
        print inCreateSubDirs
        myRange = range(0, len(inDirList), inSubDirsAmount)
        mySubLists = [inDirList[j:j+inSubDirsAmount] for j in range(0, len(inDirList), inSubDirsAmount)]
        print myRange
        print len(mySubLists)
        currentDirName = splitedPath[len(splitedPath)-2]
#        subLists = mySubLists
#        ensure_dir(newDirPath)
        for i, subContent in enumerate(mySubLists):
            newDirPath = basePath + currentDirName + "_" + str(i * inSubDirsAmount) + "_" + str(i * inSubDirsAmount + (inSubDirsAmount -1)) + "/"
            ensure_dir(newDirPath)
            for fileName in subContent:
                shutil.copyfile(inDirPath + fileName, newDirPath + fileName)
    return newDirPath
    
path = createSubDirs(myNewList, dirPath, subDirsAmount, doCreateSubDirs)
print path
#print subLists
#for i, f in enumerate(myNewList):
#    print "old - " + myOldList[i]
#    print f

