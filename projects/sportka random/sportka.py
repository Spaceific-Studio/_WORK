from math import *
from time import sleep
import numpy as np
from numpy.random import default_rng
import random
import os

YELLOW ='\033[93m'
ENDC = '\033[0m'
GREEN = '\033[92m'
MAGENTA = '\033[95m' 
BLUE = '\033[94m'
RED = '\033[91m'
GRAY = '\033[90m'
CYAN = '\033[96m'
BLACK= '\033[30m'
WHITE= '\033[37m'
BOLD = '\033[1m'
BACKGROUND_GRAY = '\033[100m'
BACKGROUND_RED = '\033[101m'
BACKGROUND_GREEN = '\033[102m'
BACKGROUND_YELLOW = '\033[103m'
BACKGROUND_BLUE = '\033[104m'
BACKGROUND_MAGENTA = '\033[105m'
BACKGROUND_CYAN = '\033[106m'
BACKGROUND_WHITE = '\033[107m'

def screenClear():
   # for mac and linux(here, os.name is 'posix')
   if os.name == 'posix':
      _ = os.system('clear')
   else:
      # for windows platfrom
      _ = os.system('cls')

def getUniqueRnds(inMax):
    returnNums = []
    while len(returnNums) < inMax:
        num = random.randint(1,49)
        if num not in returnNums:
            returnNums.append(num)
    return returnNums

def getAllSetUniqueNums(inSets):
    returnSets = []
    for set in inSets:
        for num in set:
            if num not in returnSets:
                returnSets.append(num)
    return returnSets

class NpSetsGenerator():
    def __init__(self, inCount):
        self.setCount = inCount
        self.colCount = 7
        self.rowCount = 7
        self.rndNumsPerBox = 6
        self.genCount = 1000000
        rng = default_rng()
        #self.generatedSets
        
        #testGen = rng.choice(range(1,49), size=(10000,8,self.rndNumsPerBox), axis=0, replace=True)
        nrow, ncol = 5, 5
        uarray = (np.random.permutation(7*7) + 1).reshape(7,7)
        print(uarray)
        testGen =  rng.choice(49, size=(self.genCount,self.rndNumsPerBox), replace=True, axis=1)
        #testGen = np.random.uniform(low=1,high=49,size=(10,6))
        print(testGen)
       # self.generatedSets = np.zeros(dtype = np.int8, shape=(self.setCount*self.genCount, self.rndNumsPerBox))
        #self.generatedSets = np.random.randint(low=1, high=self.colCount*self.rowCount, size=(self.genCount,self.setCount,self.rndNumsPerBox), dtype=np.int8)
        print("{0} {1}".format(self.generatedSets, self.generatedSets.size))
        
        #for i in range(self.generatedSets.shape[0]): 
            #line = rng.choice(range(low=1,high=49)), size=(self.rndNumsPerBox), replace=False)
            #self.generatedSets[i] = line
        #print("{0} {1}".format(self.generatedSets, self.generatedSets.size))
        """
        #self.generatedSets = [self.generateSet() for x in range(self.genCount)]
        self.setsData = self.getSetsData()
        for k,v in self.setsData.items():
            print("{0}-{1}".format(k, v))
        self.uniqueNumsLengthOccurence = self.getUniqueNumsLengthOccurence()
        for k,v in self.uniqueNumsLengthOccurence.items():
            print("{0}-{1}".format(k, v))
        self.sumsMin = self.getSumsExtremes()
        self.sumsMax = self.getSumsExtremes(False)
        print("sums min = {0}, max = {1}".format(self.sumsMin, self.sumsMax))"""
            
        
    def generateSets(self):
        while True:
            yield self.generateSet()
    
    def generateSet(self):
        while True:
            return [getUniqueRnds(self.rndNumsPerBox) for x in range(self.setCount)]

        
    def getUniqueRnds(self, inMax):
        returnNums = []
        while len(returnNums) < inMax:
            num = random.randint(1,49)
            if num not in returnNums:
                returnNums.append(num)
        return returnNums
        
    def getSumsExtremes(self, *args):
        #returnMin = True if args[0] or args not set
        returnMin = args[0] if len(args) > 0 else True
        returnMax = not returnMin
        return min(self.setsData["setSums"]) if returnMin else max(self.setsData["setSums"])
        
        
        
    def getUniqueNumsLengthOccurence(self):
        returnOccurences = {}
        for i in range(self.rowCount*self.colCount):
            occurence = self.setsData["setUniqueNumsLength"].count(i+1)
            returnOccurences[i+1] = occurence
        return returnOccurences
        
    
    def getSetsData(self):
        returnSetsData = {}
        returnSetsData["setUniqueNums"] = []
        returnSetsData["setSums"] = []
        returnSetsData["setUniqueNumsLength"] = []
        for set in self.generatedSets:
            setUniqueNums = []
            setUniqueNumsLength = []
            for box in set:
                for num in box:
                    if num not in setUniqueNums:
                        setUniqueNums.append(num)
            returnSetsData["setUniqueNums"].append(setUniqueNums)
            returnSetsData["setUniqueNumsLength"].append(len(setUniqueNums))
            
            returnSetsData["setSums"].append(sum(setUniqueNums))
        return returnSetsData
    
    def printSetsData():
        pass
        
class SetsGenerator():
    def __init__(self, inCount):
        self.setCount = inCount
        self.colCount = 7
        self.rowCount = 7
        self.rndNumsPerBox = 6
        self.genCount = 10000
        self.generatedSets = [self.generateSet() for x in range(self.genCount)]
        self.setsData = self.getSetsData()
        for k,v in self.setsData.items():
            print("{0}-{1}".format(k, v))
        self.uniqueNumsLengthOccurence = self.getUniqueNumsLengthOccurence()
        for k,v in self.uniqueNumsLengthOccurence.items():
            print("{0}-{1}".format(k, v))
        self.sumsMin = self.getSumsExtremes()
        self.sumsMax = self.getSumsExtremes(False)
        print("sums min = {0}, max = {1}".format(self.sumsMin, self.sumsMax))
            
        
    def generateSets(self):
        while True:
            yield self.generateSet()
    
    def generateSet(self):
        while True:
            return [getUniqueRnds(self.rndNumsPerBox) for x in range(self.setCount)]

        
    def getUniqueRnds(self, inMax):
        returnNums = []
        while len(returnNums) < inMax:
            num = random.randint(1,49)
            if num not in returnNums:
                returnNums.append(num)
        return returnNums
        
    def getSumsExtremes(self, *args):
        #returnMin = True if args[0] or args not set
        returnMin = args[0] if len(args) > 0 else True
        returnMax = not returnMin
        return min(self.setsData["setSums"]) if returnMin else max(self.setsData["setSums"])
        
        
        
    def getUniqueNumsLengthOccurence(self):
        returnOccurences = {}
        for i in range(self.rowCount*self.colCount):
            occurence = self.setsData["setUniqueNumsLength"].count(i+1)
            returnOccurences[i+1] = occurence
        return returnOccurences
        
    
    def getSetsData(self):
        returnSetsData = {}
        returnSetsData["setUniqueNums"] = []
        returnSetsData["setSums"] = []
        returnSetsData["setUniqueNumsLength"] = []
        for set in self.generatedSets:
            setUniqueNums = []
            setUniqueNumsLength = []
            for box in set:
                for num in box:
                    if num not in setUniqueNums:
                        setUniqueNums.append(num)
            returnSetsData["setUniqueNums"].append(setUniqueNums)
            returnSetsData["setUniqueNumsLength"].append(len(setUniqueNums))
            
            returnSetsData["setSums"].append(sum(setUniqueNums))
        return returnSetsData
    
    def printSetsData():
        pass
        
#npRndGenerator = NpSetsGenerator(8)
myRndGenerator = SetsGenerator(8)

    
inputText = "q - quit\ng - generate random number\ns - generate random sets\n"
#cDailyData = getCountryData(allData, coutriesOfIterest[0][0])
myInput = input(inputText)
screenClear()
while myInput != "q" or myInput != "Q":
    
    if myInput == "g" or myInput == "G":
        num = random.randint(1,49)
        print("{}".format(num))
        myInput = input(inputText)
    elif myInput == "s" or myInput == "S":
        setCount = 8
        colCount = 7
        rowCount = 7
        rndNumsPerSet = 6
        print()
        sets = []
        for set in range(setCount):
            rndNums = getUniqueRnds(rndNumsPerSet)
            sets.append(rndNums)
            print("{0} {1:_>19}{2}".format(set+1, "", sorted(rndNums)))
            str = ""
            for row in range(rowCount):
                for col in range(colCount):
                    curNum = (row*colCount)+(col+1)
                    if curNum in rndNums:
                        str += " " + YELLOW
                    else:
                        str += " " + GRAY + BOLD
                    str += "{0: >2}".format(curNum)
                    str += ENDC
                str += "\n"
            
            print(str)
            #sleep(0.01)
            #screenClear()
        allUniqueNums = getAllSetUniqueNums(sets)
        print("Unique numbers: {0} of {1} - {2: >.2f}%".format(len(allUniqueNums), setCount*rndNumsPerSet, (len(allUniqueNums)/(setCount*rndNumsPerSet))*100))
        str = ""
        for row in range(rowCount):
            for col in range(colCount):
                curNum = (row*colCount)+(col+1)
                if curNum in allUniqueNums:
                    str += " " + CYAN
                else:
                    str += " " + GRAY + BOLD
                str += "{0: >2}".format(curNum)
                str += ENDC
            str += "\n"
            
        print(str)
        myInput = input(inputText)
        #screenClear()
        
    else:
        break
                    
            