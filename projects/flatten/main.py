# -*- coding: utf-8 -*-
# Copyright(c) 2019, Daniel Gercak
#Script for selecting and grouping elements by levels and other parameter for dynamo 
#resource_path: D:\DANO\_WORK_ARCHIV\BIM_MANAGMENT_STUFF\ENERG_ANALYZY\pythonScripts\Group_geometry_node.py

#from termcolor import colored
YELLOW ='\033[93m'
ENDC = '\033[0m'
GREEN = '\033[92m'
MAGENTA = '\033[95m' 
BLUE = '\033[94m'
RED = '\033[91m'
GRAY = '\033[90m'
CYAN = '\033[96m'
BACKGROUND_GRAY = '\033[100m'
BACKGROUND_RED = '\033[101m'
BACKGROUND_GREEN = '\033[102m'
BACKGROUND_YELLOW = '\033[103m'
BACKGROUND_BLUE = '\033[104m'
BACKGROUND_MAGENTA = '\033[105m'
BACKGROUND_CYAN = '\033[106m'
BACKGROUND_WHITE = '\033[107m'
#def flattenList(inList, inLevel = 0):
#	nextLevelItems = []
#	returnItems = []
#	myLevels = []
#	if type(inList) == list:
#		for item in inList:
#			nextLevelItems = flattenList(item, inLevel + 1)
#			returnItems = nextLevelItems
#	else:
#		returnItems = [inList]
#	if returnItems != [] or nextLevelItems != None:
		#if len(nextLevelItems) == 0 and inLevel == 1:
		#    nextLevelItems.pop()
#		return returnItems + nextLevelItems

def flattenList(inList, *args, **kwargs):
    """returns 1D list of items. flattens only list objects Tuple not List
		flattens from up to deep - flattenList([1,2,[3,[4,5]]], level = 1, top=True) >>  [1, 2, 3, [4, 5]]
       
       args:
            arg_0: list of lists
            *args[0]: type: int - optional current level of recursion 
            **kwargs: level type: int -  maximum level of required flatten recursion. 
                                If not set, function returns only not list items
                      top type: bool - if False or not set the function will start flatten from bottom
                                       flattenList([1,2,[3,[4,5]]], level = 1) >>  [1, 2, [3, 4, 5]]
                                       flattenList([1,2,[3,[4,5]]], level = 1, top=True) >>  [1, 2, 3, [4, 5]]
            
       return: flattened list according to maxLevel argument
    """
    
    outLog = ""
    returnItems = []
    myLevels = []
    if len(args) != 0:
        inLevel = args[0]
    else:
        inLevel = 0
    #for key, value in kwargs.items(): 
         #print("level-{2} key-{0} = value-{1}".format(key, value, inLevel))
    if "top" in kwargs and kwargs["top"] == True:
        top = True
        if "level" in kwargs:
         mLevel = kwargs["level"]
        else:
         mLevel = inLevel +200
    else:
        top = False
        if "level" in kwargs:
         mLevel = kwargs["level"]
        else:
         mLevel = 0
    if top: 
        outLog += BACKGROUND_GRAY + "\nLevel {0} type({1}) == {2} \n".format(inLevel, myList, type(myList)) + ENDC
        #print("Level - {0}, mLevel {1} top = {2}".format(inLevel, mLevel, top))  
        if type(inList) == list:
         for i, item in enumerate(inList):
          if type(item) == list:
           outLog += GREEN + "{0} - type(1) == {2} - returnItem = flattenList(item {1}, inLevel {3} + 1, minLevel = mLevel {4}) >>".format(i,item,type(item), inLevel, mLevel) + ENDC
           if inLevel < mLevel:
            #print("Top flattenList({0}, {1}, {2}, {3})".format(item, inLevel + 1, mLevel, top))
            returnItemL = flattenList(item, inLevel + 1, level = mLevel, top = top)
            returnItem = returnItemL[0]
            outLog += YELLOW + " {0}\n".format(returnItem) +ENDC
            outLog += returnItemL[1]
            
            #print("Top returnItem >> {0}".format(returnItem))
           else:
            outLog += BACKGROUND_RED + "inLevel {0} >= mLevel {1} \n".format(inLevel,mLevel) + ENDC
            returnItem = [item]
            
            outLog += YELLOW + "{3}\n".format(i,returnItems,returnItem, returnItems) +ENDC
            #print("Top inLevel <= mLevel returnItem >> {0}".format(returnItem))
          else:
           returnItem = [item]
           outLog += CYAN + "{0} - type{1} == {2} - returnItem = ".format(i,item,type(item)) + YELLOW + "{1} \n".format(i,item,type(item), inLevel, mLevel,returnItem) + ENDC
           #print("Top !list returnItem >> {0}".format(returnItem))
          returnItems = returnItems + returnItem
          outLog += "returnItem >>" + YELLOW + "{3}\n".format(i,returnItems,returnItem, returnItems) +ENDC
          #print("returnItems >> {0}".format(returnItems))
        else:
         
         returnItems = [inList]
    else:
       # print("Level - {0}, mLevel {1} bottom kwargs {2}".format(inLevel, mLevel, kwargs["level"]))    
        outLog += BACKGROUND_GRAY + "\nLevel {0} type({1}) == {2} \n".format(inLevel, inList, type(inList)) + ENDC    
        if type(inList) == list:
         for i, item in enumerate(inList):
            if type(item) == list:
                outLog += GREEN + "{0} - type({1}) == {2} - returnItem = flattenList(item {1}, inLevel {3} + 1, minLevel = mLevel {4}) >>".format(i,item,type(item), inLevel, mLevel) + ENDC
                returnItemL = flattenList(item, inLevel + 1, level = mLevel)
                returnItem = returnItemL[0]
                outLog += YELLOW + " {0}\n".format(returnItem) +ENDC
                outLog += returnItemL[1]
               # print("Bottom returnItem >> {0}".format(returnItem))
                if inLevel >= mLevel:
                    outLog += MAGENTA + "inLevel {0} >= mLevel {1} \n".format(inLevel,mLevel) + ENDC
                    outLog += "returnItems " + GREEN + "{0} ".format(returnItems) + ENDC
                    outLog += " + returnItem " + GREEN + "{0} ".format(returnItem) + ENDC
                    returnItems = returnItems + returnItem
                    outLog += " >>" + YELLOW + "{0}\n".format(returnItems) + ENDC
                else:
                    outLog += BACKGROUND_RED + "inLevel {0} < mLevel {1} \n".format(inLevel,mLevel) + ENDC
                    outLog += "returnItems " + GREEN + "{0} ".format(returnItems) + ENDC
                    returnItems.append(returnItem)
                    outLog += ".append(returnItem " + GREEN + "{0}".format(returnItem) + ENDC + ") >>" + YELLOW + "{3}\n".format(i,returnItems,returnItem, returnItems) +ENDC
            else:
                returnItem = item
                outLog += CYAN + "{0} - type({1}) == {2} - returnItem >> ".format(i,item,type(item)) + YELLOW + "{1} \n".format(i,item,type(item), inLevel, mLevel,returnItem) + ENDC
                if inLevel >= mLevel:
                    outLog += BLUE + "inLevel {0} >= mLevel {1} \n".format(inLevel,mLevel) + ENDC
                    outLog += "returnItems " + GREEN + "{0} ".format(returnItems) + ENDC
                    outLog += " + [returnItem] " + GREEN + "[{0}] ".format(returnItem) + ENDC
                    returnItems = returnItems + [returnItem]
                    outLog += " >>" + YELLOW + "{0}\n".format(returnItems) + ENDC
                else:
                    outLog += BACKGROUND_RED + "inLevel {0} < mLevel {1} \n".format(inLevel,mLevel) + ENDC
                    outLog += "returnItems " + GREEN + "{0} ".format(returnItems) + ENDC
                    returnItems.append(returnItem)
                    outLog += ".append(" + GREEN + "{0}".format(returnItem) + ENDC + ") >> " + YELLOW + "{0}\n\n".format(returnItems) +ENDC
        else:
            returnItems = [inList]
    
    if  inLevel == 0:
     print (outLog)
     return returnItems
    else:
     return (returnItems, outLog)


def flattenBottomList(inList, *args, **kwargs):
    """returns 1D list of items. flattens only list objects tuples not
       
       args:
            arg_0: list of lists
            *args_0: optional (int) current level of recursion
            **kwargs: maxLevel (int): maximum level of flatten recursion. 
                                If not set, function returns only not list items
                                value -1 returns unflattened list
            
       return: flattened list according to maxLevel argument
    """
    outLog = ""
    returnItems = []
    myList = inList
    myLevels = []
    if len(args) != 0:
        inLevel = args[0]
    else:
        inLevel = 0
    if "minLevel" in kwargs:
        miLevel = kwargs["minLevel"]
    else:
        miLevel = 0
    if type(myList) == list:
     outLog += BACKGROUND_GRAY + "\nLevel {0} type({1}) == {2} \n".format(inLevel, myList, type(myList)) + ENDC
     for i, item in enumerate(inList):
      if type(item) == list:
       outLog += GREEN + "{0} - type(1) == {2} - returnItem = flattenBottomList(item {1}, inLevel {3} + 1, minLevel = miLevel {4}) >>".format(i,item,type(item), inLevel, miLevel)
       returnItemL = flattenBottomList(item, inLevel + 1, minLevel = miLevel)
       returnItem = returnItemL[0]
       outLog += MAGENTA + "{5}\n".format(i,item,type(item), inLevel, miLevel,returnItem) + ENDC
       outLog += returnItemL[1]
       if inLevel >= miLevel:
        outLog += "inLevel {0} >= miLevel {1} \n".format(inLevel,miLevel)
        returnItems = returnItems + returnItem
        outLog += YELLOW + "{3}\n".format(i,returnItems,returnItem, returnItems) + ENDC
       else:
        outLog += BACKGROUND_RED + "inLevel {0} < miLevel {1} \n".format(inLevel,miLevel) + ENDC
        returnItems.append(returnItem)
        outLog += YELLOW + "{3}\n".format(i,returnItems,returnItem, returnItems) +ENDC
      else:
       returnItem = item
       outLog += CYAN + "{0} - type(1) == {2} - returnItem = {1} \n".format(i,item,type(item), inLevel, miLevel,returnItem) + ENDC
       if inLevel >= miLevel:
        outLog += "inLevel {0} >= miLevel {1} returnItems {2} = returnItems {2} + returnItem {3} >> \n".format(inLevel,miLevel,returnItems,returnItem)
        returnItems = returnItems + [returnItem]
        outLog += "{2}) \n".format(inLevel,miLevel,returnItems,returnItem)
       else:
        outLog += "inLevel {0} < miLevel {1} returnItems {2} .append(returnItem {3}) >> \n".format(inLevel,miLevel,returnItems,returnItem)
        returnItems.append(returnItem)
        outLog += YELLOW + "{2}) \n".format(inLevel,miLevel,returnItems,returnItem) +ENDC    
    else:
     returnItems = [inList]
    if  inLevel == 0:
     print (outLog)
     return returnItems
    else:
     return (returnItems, outLog)

def testKwargs(inList = [], *args, **kwargs):
    if len(args) > 1:
        maxLevels = args[1]
    else:
        maxLevels = 5
    if len(args) > 0:
        level = args[0]
    else:
        level = 0
    if "top" in kwargs and kwargs["top"] == True:
        top = kwargs["top"]
    else:
        top = False
    print("level {0}, top {2}, maxLevels {1}".format(level, maxLevels, top))
    if level < 4:
        testKwargs(inList, level +1, maxLevels, top = top)
        
testKwargs([0,1], top = False)        

testList = [0, "a", \
			["b", 2, \
			 [3, "c", 4], \
			5, "dodo",5.9, []] \
			]
testlist2 = [[[78],[54,[[43,[567,(67,67)]],(65,78,"lk")],[[[52,[53]]]]],56]]
myList = [1,2,[[8,11],[9,10,[[11,14],12]]],("den", "mes",(77,"102")),[3,[4,[5,6]]]]
testlist3 = ['a',['b', ['c', ['d',['e', ['f', ['g', ['h', ['i'], 'j'], 'k'], 'l'], 'm'], 'n'], 'o'], 'p'], 'q']
for i in range(0,6):
 outList = flattenList(testlist3, level=i, top=True)
 print(BACKGROUND_GRAY + "myList = {0}".format(myList)+ ENDC)
 print(BACKGROUND_GRAY + CYAN + "outList i_{1} = {0}".format(outList,i)+ ENDC)
outList = flattenList(myList, top=True)
print(BACKGROUND_GRAY + "myList = {0}".format(myList)+ ENDC)
print(BACKGROUND_GRAY + CYAN + "outList Top = {0}".format(outList,i)+ ENDC)
print ("\n")
print ("___________________________________\n")
print ("\n")
for i in range(0,6):
 outList = flattenList(testlist3, level=i)
 print(BACKGROUND_GRAY + "myList = {0}".format(myList)+ ENDC)
 print(BACKGROUND_GRAY + CYAN + "outList level_{1} = {0}".format(outList,i) + ENDC)
print ("\n")

