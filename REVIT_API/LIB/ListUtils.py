def processList(_func, _list, *args, **kwargs):
	"""Iterates trough input list and aplies a function to each item of the list

		args:
			_func: name of the func type: callable
			_list: input list - type: list 
			*args: arguments for input function

		return: list of the same structure as input list - type: list
	"""
	return map( lambda x: processList(_func, x, *args, **kwargs) if type(x)==list else _func(x, *args, **kwargs), _list )

def processListSum(_func, _list = [], level=0, *args, **kwargs):
    """
        function to get structured list with values of sum of 
        object properties at each level of tree structure
        main condition is to have tuple or other object than list
        at the botom of list structure
        
        _func: name of function which returns tuple(tuple(value type: int or float,...), sum of values type: float or int)
        _list: structured list of tuple at the botom of structure list[list[list[tuple(tuple(Object or value of type: int or float, ...), ...), ...], ...], ...]
        level: type: int, level of recursion set default as 0
        
    """
    kwargs['myLevel'] = level
    return [map(lambda x: processListSum( \
                                            _func, \
                                            x, \
                                            level+1, \
                                            *args, \
                                            **kwargs\
                                            ) \
                   if type(x)==list else _func(x, *args, **kwargs) \
                    , _list \
                   ), \
              sum([x[1] for x in \
                   map(lambda x: processListSum(_func, \
                                                       x, \
                                                       level+1, \
                                                       *args, \
                                                       **kwargs \
                                                      ) \
                          if type(x)==list else \
                          _func(x, \
                             	  *args, \
                                **kwargs \
                               ), \
                          _list \
                         ) \
                     ] \
                    ) \
           ]

def notMoreThanOne(inItem):
	"""Returns True if input list has maximum one item

		args:
			inItem: type: list

		return: type: bool
	"""
	if isinstance(inItem, list):
		if len(inItem) > 1:
			return False
		else:
			return True
	else:
		return False

def flatList(inList, *args, **kwargs):
    """returns 1D list of items. flattens only list objects Tuple not List
		flattens from up to deep - flattenList([1,2,[3,[4,5]]], maxLevel = 1) >>  [1, 2, 3, [4, 5]]
       
       args:
            arg_0: list of lists
            *args[0]: type: int - optional current level of recursion 
            **kwargs: maxLevel type: int -  maximum level of required flatten recursion. 
                                If not set, function returns only not list items
                                value 0 returns unflattened list
            
       return: flattened list according to maxLevel argument
    """
    levelItems = []
    returnItems = []
    myLevels = []
    if len(args) != 0:
        inLevel = args[0]
    else:
        inLevel = 0
    if "maxLevel" in kwargs:
        mLevel = kwargs["maxLevel"]-1
    else:
        mLevel = inLevel +200
    if type(inList) == list:
     for item in inList:
      if type(item) == list:
       if inLevel <= mLevel:
        returnItem = flatList(item, inLevel + 1, maxLevel = mLevel)
       else:
        returnItem = [item]
      else:
       returnItem = [item]
      returnItems = returnItems + returnItem
    else:
     returnItems = [inList]
    return returnItems

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
    
    #outLog = ""
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
        #outLog += BACKGROUND_GRAY + "\nLevel {0} type({1}) == {2} \n".format(inLevel, myList, type(myList)) + ENDC
        #print("Level - {0}, mLevel {1} top = {2}".format(inLevel, mLevel, top))  
        if type(inList) == list:
         for i, item in enumerate(inList):
          if type(item) == list:
           #outLog += GREEN + "{0} - type(1) == {2} - returnItem = flattenList(item {1}, inLevel {3} + 1, minLevel = mLevel {4}) >>".format(i,item,type(item), inLevel, mLevel) + ENDC
           if inLevel < mLevel:
            #print("Top flattenList({0}, {1}, {2}, {3})".format(item, inLevel + 1, mLevel, top))
            returnItemL = flattenList(item, inLevel + 1, level = mLevel, top = top)
            returnItem = returnItemL[0]
            #outLog += YELLOW + " {0}\n".format(returnItem) +ENDC
            #outLog += returnItemL[1]
            
            #print("Top returnItem >> {0}".format(returnItem))
           else:
            #outLog += BACKGROUND_RED + "inLevel {0} >= mLevel {1} \n".format(inLevel,mLevel) + ENDC
            returnItem = [item]
            
            #outLog += YELLOW + "{3}\n".format(i,returnItems,returnItem, returnItems) +ENDC
            #print("Top inLevel <= mLevel returnItem >> {0}".format(returnItem))
          else:
           returnItem = [item]
           #outLog += CYAN + "{0} - type{1} == {2} - returnItem = ".format(i,item,type(item)) + YELLOW + "{1} \n".format(i,item,type(item), inLevel, mLevel,returnItem) + ENDC
           #print("Top !list returnItem >> {0}".format(returnItem))
          returnItems = returnItems + returnItem
          #outLog += "returnItem >>" + YELLOW + "{3}\n".format(i,returnItems,returnItem, returnItems) +ENDC
          #print("returnItems >> {0}".format(returnItems))
        else:
         
         returnItems = [inList]
    else:
       # print("Level - {0}, mLevel {1} bottom kwargs {2}".format(inLevel, mLevel, kwargs["level"]))    
        #outLog += BACKGROUND_GRAY + "\nLevel {0} type({1}) == {2} \n".format(inLevel, inList, type(inList)) + ENDC    
        if type(inList) == list:
         for i, item in enumerate(inList):
            if type(item) == list:
                #outLog += GREEN + "{0} - type({1}) == {2} - returnItem = flattenList(item {1}, inLevel {3} + 1, minLevel = mLevel {4}) >>".format(i,item,type(item), inLevel, mLevel) + ENDC
                returnItemL = flattenList(item, inLevel + 1, level = mLevel)
                returnItem = returnItemL[0]
                #outLog += YELLOW + " {0}\n".format(returnItem) +ENDC
                #outLog += returnItemL[1]
               # print("Bottom returnItem >> {0}".format(returnItem))
                if inLevel >= mLevel:
                    #outLog += MAGENTA + "inLevel {0} >= mLevel {1} \n".format(inLevel,mLevel) + ENDC
                    #outLog += "returnItems " + GREEN + "{0} ".format(returnItems) + ENDC
                    #outLog += " + returnItem " + GREEN + "{0} ".format(returnItem) + ENDC
                    returnItems = returnItems + [returnItem]
                    #outLog += " >>" + YELLOW + "{0}\n".format(returnItems) + ENDC
                else:
                    #outLog += BACKGROUND_RED + "inLevel {0} < mLevel {1} \n".format(inLevel,mLevel) + ENDC
                    #outLog += "returnItems " + GREEN + "{0} ".format(returnItems) + ENDC
                    returnItems.append(returnItem)
                    #outLog += ".append(returnItem " + GREEN + "{0}".format(returnItem) + ENDC + ") >>" + YELLOW + "{3}\n".format(i,returnItems,returnItem, returnItems) +ENDC
            else:
                returnItem = item
                #outLog += CYAN + "{0} - type({1}) == {2} - returnItem >> ".format(i,item,type(item)) + YELLOW + "{1} \n".format(i,item,type(item), inLevel, mLevel,returnItem) + ENDC
                if inLevel >= mLevel:
                    #outLog += BLUE + "inLevel {0} >= mLevel {1} \n".format(inLevel,mLevel) + ENDC
                    #outLog += "returnItems " + GREEN + "{0} ".format(returnItems) + ENDC
                    #outLog += " + [returnItem] " + GREEN + "[{0}] ".format(returnItem) + ENDC
                    returnItems = returnItems + [returnItem]
                    #outLog += " >>" + YELLOW + "{0}\n".format(returnItems) + ENDC
                else:
                    #outLog += BACKGROUND_RED + "inLevel {0} < mLevel {1} \n".format(inLevel,mLevel) + ENDC
                    #outLog += "returnItems " + GREEN + "{0} ".format(returnItems) + ENDC
                    returnItems.append(returnItem)
                    #outLog += ".append(" + GREEN + "{0}".format(returnItem) + ENDC + ") >> " + YELLOW + "{0}\n\n".format(returnItems) +ENDC
        else:
            returnItems = [inList]
    
    if  inLevel == 0:
     #print outLog
     return returnItems
    else:
     return returnItems
    
def isIterable(p_object):
    try:
        it = iter(p_object)
    except TypeError: 
        return False
    return True
