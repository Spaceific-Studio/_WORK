import sys
import os
savePath = r"//storage//emulated//0//download//"
saveName = "revit_classes.txt"


def ensure_dir(file_path):
    directory = os.path.dirname(file_path) 
    if not os.path.exists(directory):
        os.makedirs(directory)

def get_all_objects(**kwargs):
	"""Return a list of all live Python
	objects, not including the list itself."""
	#gcl = gc.get_objects()
	maxLevel = kwargs['maxLevel'] if 'maxLevel' in kwargs else 2
	gcl = [[attr, getattr(__file__, attr)] for attr in dir(__file__)]
	olist = []
	seen = {}
	# Just in case:
	seen[id(gcl)] = None
	seen[id(olist)] = None
	seen[id(seen)] = None
	# _getr does the real work.
	get_refs(gcl, olist, seen, maxLevel = maxLevel)
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
		tl = [["{0}>>{1}".format(e[0], attr), getattr(e[1], attr)] for attr in dir(e[1])]
		if tl and level < maxLevel:
			get_refs(tl, olist, seen, level=level+1, maxLevel = maxLevel, onlyNames = onlyNames)
#dirOneLevel(__file__)
#print(dirTree(__file__, maxLevel = 2))
#gcl = [getattr(__file__, attr) for attr in dir(__file__)]
#print(gcl)
allObjects = get_all_objects(maxLevel = 6)

#print("len(allObjects) - {0} : {1}".format(len(allObjects), allObjects))
outStr = ""
for i, v in enumerate(allObjects):
	outStr += "\n{0:0>5} : {1}".format(i, v)
#print(outStr)
ensure_dir(savePath)
try:
	with open(os.path.join(savePath, saveName),'w') as sFile:
		sFile.write(outStr)
except Exception as ex:
	import traceback
	exc_info = sys.exc_info()
	traceback.print_exception(*exc_info)


#print("{0}".format(dir(__file__.istitle.__name__)))

#for attr in dir(__file__): print(attr +'()') if callable(getattr(__file__, attr)) else print(attr)