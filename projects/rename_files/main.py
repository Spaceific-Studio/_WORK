from os import walk
import os
import os.path as osPath
import sys
import shutil
from itertools import chain
import itertools
import numpy as np

"""
    utilitka na premenovanie suborov pomocou shiftovania znakov z tabulky ascii_letters
    je treba davat pozor aby sifrovanie prebehlo bez chyby na cely adresar len raz
    v pripade ze sa nieco nepodari, je potreba spustit fciu renameFilesReversed(inFiles)
    ktora shiftne znaky do povodneho stavu

"""

#dirPath = r"D:/DANO/FDATA/_OTHER/ME"
dirPath = r"D:/DANO/MDATA/Metallica"

def readDirFiles(inDirPath):
    myFiles = []
    myDirs = []
    myPath = ""
    for (path, dirnames, filenames) in walk(inDirPath): 
        myFiles.extend(filenames) 
        myDirs.extend(dirnames)
        myPath = path
        break
    return (myDirs,myFiles,myPath)

def walkDirs(inDirPath,inLevel):
    
    myFiles = []
    myDirs = []
    myPath = inDirPath
    myPaths = []
    returnDirs = []
    myLevel = inLevel
    for (path, dirnames, filenames) in walk(myPath): 
        if len(dirnames) > 0:
            for d in dirnames:            
                newPath = "{path}/{dir}".format(path = myPath, dir = d)
                returnDirs.insert(0, walkDirs(newPath, myLevel+1))
            
        for f in filenames:
            myFiles.insert(0, "{mPath}/{file}".format(mPath = myPath, file = f))
        returnDirs.insert(0, myFiles)
        return returnDirs
        
        


# def getFileIndex(inFileName):        
#     return inFileName.split("_")[0]

# def adjustFileName(inFName, inReqDigCount, inPos):
#     myIndex = getFileIndex(inFName)
#     zeroesInsert = ""
#     newFName = ""
#     if len(myIndex) < inReqDigCount:
#         reqZeroes = inReqDigCount - len(myIndex)
#         for i in range(0, reqZeroes):
#             zeroesInsert += "0"
#         newFName = zeroesInsert + inFName
#         os.rename(dirPath + inFName, dirPath + newFName)
#         print "the file: " + dirPath + inFName + " was renamed to: " + newFName
# #            os.rename(dirPath + inFName, dirPath + newFName)
# #            print "the file: " + dirPath + inFName + " was renamed to: " + newFName
# #            print "the file: " + dirPath + inFName + " WAS NOT RENAMED"
#     else:
#         newFName = inFName
# #        print "the file: " + dirPath + inFName + " has correct format"
#     return newFName

# def addZeroes(inFiles, inRequiredDigitCount):
#     returnList = []
#     for i, f in  enumerate(inFiles):
#         returnList.append(adjustFilyeName(f, inRequiredDigitCount, i))
#     return returnList

def flatten(l): 
    if type(l) is list:
        if len(l) > 1:
            return flatten(l[0]) + flatten(l[1:])
        elif len(l) == 1:
            return flatten(l[0]) + []
        else: 
            return []
    else:
        return [l]     
    # return flatten(l[0]) + (flatten(l[1:]) if len(l) > 1 else []) if type(l) is list else [l]

def renameFiles(inFiles):
    newNames = []
    for f in inFiles:        
        newFname = ""
        newFext = ""
 #       print f
        splitedPath = f.split("/")
        fName = splitedPath[-1].split(".")[-2]
        #print fName
        fExt = splitedPath[-1].split(".")[-1]
        #print fExt
        for ch in fName: 
            if ch in ascii_letters:
                charPos = ascii_letters.find(ch)        
                newFname += ascii_letters[(charPos + 1) % len(ascii_letters)]
            else:
                newFname += ch
            #print ord(ch)
        #print newFname
        for ch in fExt: 
            if ch in ascii_letters:
                charPos = ascii_letters.find(ch)           
                newFext += ascii_letters[(charPos + 1) % len(ascii_letters)]
            else:           
                newFext += ch
            #print ord(ch)
        #print newFext
        myPath = "/".join(splitedPath[:-1])
        returnName = myPath + "/" + newFname + "." + newFext
        os.rename(f, returnName)
        print ("file {oldName} was renamed to : {nName}".format(oldName = f, nName = returnName))

        newNames.append(returnName)

#    print newNames
    return newNames

def renameFilesReversed(inFiles):
    newNames = []
    for f in inFiles:        
        newFname = ""
        newFext = ""
#        print f
        splitedPath = f.split("/")
        fName = splitedPath[-1].split(".")[-2]
        #print fName
        fExt = splitedPath[-1].split(".")[-1]
        #print fExt
        for ch in fName: 
            if ch in ascii_letters:
                charPos = ascii_letters.find(ch)        
                newFname += ascii_letters[(charPos - 1) % len(ascii_letters)]
            else:
                newFname += ch
            #print ord(ch)
        #print newFname
        for ch in fExt: 
            if ch in ascii_letters:
                charPos = ascii_letters.find(ch)           
                newFext += ascii_letters[(charPos - 1) % len(ascii_letters)]
            else:           
                newFext += ch
            #print ord(ch)
        #print newFext
        myPath = "/".join(splitedPath[:-1])
        returnName = myPath + "/" + newFname + "." + newFext
        os.rename(f, returnName)
        print ("file {oldName} was renamed to : {nName}".format(oldName = f, nName = returnName))
        newNames.append(returnName)
 #   print newNames
    return newNames

inputText = "Do you really want to rename all files in " + dirPath + " ? - Yes / No\n"
myInput = input(inputText)
if myInput == "y" or myInput == "Y" or myInput == "yes" or myInput == "YES":
    inputText = "Do you want to rename or reverse_rename " + dirPath + " ? - R / REV\n"
    my2Input = input(inputText)
    myOldList = walkDirs(dirPath, 0)
    #myNewList = addZeroes(myOldList, requiredDigitCount)
    #print "myOldList"
    #print myOldList
    #print "flattened list"
    #flattened = [val for sublist in myOldList for val in sublist]
    #myList = [0,1,[2,[3,4],3],4,5,[6,7,8,[[9]],[10]]]
    flattened = flatten(myOldList)
    ascii_letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    if my2Input == "r" or my2Input == "R" or my2Input == "rename" or my2Input == "RENAME":
        renameFiles = renameFiles(flattened)
    elif my2Input == "REV" or my2Input == "rev" or my2Input == "reversed" or my2Input == "REVERSED":
        renameFilesReversed = renameFilesReversed(flattened)
    #reRenamedFiles = renameFilesReversed(renamedFiles)



# def ensure_dir(file_path):
#     directory = os.path.dirname(file_path) 
#     if not os.path.exists(directory):
#         os.makedirs(directory)
#         print "directory was created: " + directory
#     else:
#         print "directory has allready been created: " + directory

# def createSubDirs(inDirList, inDirPath, inSubDirsAmount, inCreateSubDirs):
#     splitedPath = inDirPath.split("/")
#     basePath = ""
#     subLists = []
#     for i in splitedPath[1:len(splitedPath)-2]:
#         basePath += "/" + i
#     basePath += "/"
#     if inCreateSubDirs == True:
#         print inCreateSubDirs
#         myRange = range(0, len(inDirList), inSubDirsAmount)
#         mySubLists = [inDirList[j:j+inSubDirsAmount] for j in range(0, len(inDirList), inSubDirsAmount)]
#         print myRange
#         print len(mySubLists)
#         currentDirName = splitedPath[len(splitedPath)-2]
# #        subLists = mySubLists
# #        ensure_dir(newDirPath)
#         for i, subContent in enumerate(mySubLists):
#             newDirPath = basePath + currentDirName + "_" + str(i * inSubDirsAmount) + "_" + str(i * inSubDirsAmount + (inSubDirsAmount -1)) + "/"
#             ensure_dir(newDirPath)
#             for fileName in subContent:
#                 shutil.copyfile(inDirPath + fileName, newDirPath + fileName)
#     return newDirPath
    
#path = createSubDirs(myNewList, dirPath, subDirsAmount, doCreateSubDirs)
#print path
#print subLists
#for i, f in enumerate(myNewList):
#    print "old - " + myOldList[i]
#    print f

