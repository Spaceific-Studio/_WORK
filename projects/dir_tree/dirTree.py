def dirTree(inObj, **kwargs):
	objList = kwargs['objList'] if 'objList' in kwargs else []
	level = kwargs['level'] if 'level' in kwargs else 0
	maxLevel = kwargs['maxLevel'] if 'maxLevel' in kwargs else 2
	#print("objList")
	#print(objList)
	#print("level - {0}".format(level))
	stringReturn = True
	returnList = []
	returnString = ""
	if level < maxLevel:
		for attr in sorted(dir(inObj), reverse=True):
			if hasattr(getattr(inObj, attr), "__call__"):
				attrObject = getattr(inObj, attr)
				#print("attr - {0} - {1}".format(attr, attrObject))
				returnList.append(dirTree(attrObject, objList = objList.append(attrObject) if objList else [], level = level +1, maxLevel = maxLevel))
				offset = "\t" * level
				offset = offset + attr
				print(offset + "<>")
				returnString = ", ".join(dirTree(attrObject, objList = objList.append(attrObject) if objList else [], level = level +1, maxLevel = maxLevel))
			else:
				returnList.append(attr)
			returnItem = returnString if stringReturn else returnList
		return returnItem
	else:
		return inObj.__class__.__name__

def dirOneLevel(inObj, **kwargs):
	objList = kwargs['objList'] if 'objList' in kwargs else []
	#print("objList")
	#print(objList)
	for attr in dir(inObj):
		if hasattr(getattr(inObj, attr), "__call__"):
			attrstring = " a - "
			for a in dir(getattr(inObj, attr)):
				attrstring += "{0}".format(a)
			print(attrstring)
		attrObject = getattr(inObj, attr)
		print("attrObject")
		print("{0} - {1}".format(attr, attrObject))


#dirOneLevel(__file__)
print(dirTree(__file__, maxLevel = 2))

#print("{0}".format(dir(__file__.istitle.__name__)))

#for attr in dir(__file__): print(attr +'()') if callable(getattr(__file__, attr)) else print(attr)