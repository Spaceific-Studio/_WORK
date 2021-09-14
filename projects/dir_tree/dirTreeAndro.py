import sys
import os
#import numpy as np
savePath = r"/storage/emulated/0/download/"
saveName = "revit_classes.txt"
logFileName = "log.txt"
exceptions = []

def ensure_dir(file_path):
    directory = os.path.dirname(file_path) 
    if not os.path.exists(directory):
        os.makedirs(directory)

def get_all_objects(**kwargs):
	"""Return a list of all live Python
	objects, not including the list itself."""
	#gcl = gc.get_objects()
	#print(globalObjs)
	maxLevel = kwargs['maxLevel'] if 'maxLevel' in kwargs else 2
	initObj = kwargs['initObj'] if 'initObj' in kwargs else None
	globalObjs = [[k,v] for k, v in globals().items()]if not initObj else [[attr, getattr(initObj, attr)] for attr in dir(initObj)]
	#gcl = [[attr, getattr(__file__, attr)] for attr in dir(__file__)]
	olist = []
	seen = {}
	# Just in case:
	seen[id(globalObjs)] = None
	seen[id(olist)] = None
	seen[id(seen)] = None
	# _getr does the real work.
	get_refs(sorted(globalObjs, reverse=True), olist, seen, maxLevel = maxLevel)
	return olist

def get_refs(slist, olist, seen, **kwargs):
	level = kwargs['level'] if 'level' in kwargs else 0
	maxLevel = kwargs['maxLevel'] if 'maxLevel' in kwargs else 2
	onlyNames = kwargs['onlyNames'] if 'onlyNames' in kwargs else True
	for e in slist:
		if id(e[1]) in seen:
			continue
		seen[id(e[1])] = None
		
		olist.append(e[1]) if not onlyNames else olist.append(e[0])
		#tl = gc.get_referents(e)
		#tl = [["{0}>>{1}".format(e[0], attr), getattr(e[1], attr)] for attr in dir(e[1])]
		tl = []
		for attr in dir(e[1]):
			#print("{0}{1}".format(">" *level, attr))
			if attr != "__abstractmethods__":
				hasError = False
				try:
					nextObj = getattr(e[1], attr)
				except Exception as ex:
					exceptions.append(ex)
					hasError = True
				if not hasError:
					tl.append(["{0}.{1}".format(e[0], attr), nextObj])			
		if len(tl)!=0 and level < maxLevel:
			get_refs(tl, olist, seen, level=level+1, maxLevel = maxLevel, onlyNames = onlyNames)

#def printLocals():
#	a = {}
#	print("printLocals.locals() {}".format(locals()))
#	print("printLocals.globals() {}".format(globals()))
#dirOneLevel(__file__)
#print(dirTree(__file__, maxLevel = 2))
#gcl = [getattr(__file__, attr) for attr in dir(__file__)]
#print(gcl)
allObjects = get_all_objects(initObj=os, maxLevel = 5)
#print("len(allObjects) - {0} : {1}".format(len(allObjects), allObjects))
outStr = ""
logStr = ""
for i, v in enumerate(allObjects):
	outStr += "\n{0:0>5} : {1}".format(i, v)

for i, v in enumerate(exceptions):
	logStr += "\n{0:0>5} : {1}".format(i, v)
print(outStr)
"""
#print("dir() {}".format(dir()))
#print("locals() {}".format(locals()))
#print("globals() {}".format(globals()))
#print("dir(__name__) {}".format(dir(__name__)))
#printLocals()
ensure_dir(savePath)
"""
try:
	with open(os.path.join(savePath, saveName),'w') as sFile:
		sFile.write(outStr)
	with open(os.path.join(savePath, logFileName),'w') as sFile:
		sFile.write(logStr)
	print("{0} and {1} has been saved into {2}".format(saveName, logFileName, savePath))
except Exception as ex:
	import traceback
	exc_info = sys.exc_info()
	traceback.print_exception(*exc_info)


#print("{0}".format(dir(__file__.istitle.__name__)))

#for attr in dir(__file__): print(attr +'()') if callable(getattr(__file__, attr)) else print(attr)