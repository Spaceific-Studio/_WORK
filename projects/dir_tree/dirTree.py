def dirTree(inObj, **kwargs):
	objList = kwargs['objList'] if 'objList' in kwargs else []
	level = kwargs['level'] if 'level' in kwargs else 0
	maxLevel = kwargs['maxLevel'] if 'maxLevel' in kwargs else 2
	#print("objList")
	#print(objList)
	#print("level - {0}".format(level))
	if level < maxLevel:
		for attr in dir(inObj):
			if hasattr(getattr(inObj, attr), "__call__"):
				attrObject = getattr(inObj, attr)
				#print("attr - {0} - {1}".format(attr, attrObject))
				returnList = dirTree(attrObject, objList = objList.append(attrObject) if objList else [], level = level +1, maxLevel = maxLevel)
			else:
				returnList = attr
		return returnList
	else:
		return None

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
print(dirTree(__file__))

#print("{0}".format(dir(__file__.istitle.__name__)))

#for attr in dir(__file__): print(attr +'()') if callable(getattr(__file__, attr)) else print(attr)