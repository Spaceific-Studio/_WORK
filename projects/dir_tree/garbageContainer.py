import gc
# Recursively expand slist's objects
# into olist, using seen to track
# already processed objects.
def _getr(slist, olist, seen):
  for e in slist:
    if id(e) in seen:
      continue
    seen[id(e)] = None
    olist.append(e)
    tl = gc.get_referents(e)
    if tl:
      _getr(tl, olist, seen)

# The public function.
def get_all_objects():
  """Return a list of all live Python
  objects, not including the list itself."""
  gcl = gc.get_objects()
  olist = []
  seen = {}
  # Just in case:
  seen[id(gcl)] = None
  seen[id(olist)] = None
  seen[id(seen)] = None
  # _getr does the real work.
  _getr(gcl, olist, seen)
  return olist

def variable_for_value(value):
    for n,v in globals().items():
        if v == value:
            return n
    return None

def variable():
    for n,v in globals().items():
        print("global {0}:{1}".format(n, v))

  
gcl = gc.get_objects()
print("len(gcl) - {0}".format(len(gcl)))
#print(["{0:0>5} - {1}".format(x, gcl[x]) for x in range(20)])
allObjects = get_all_objects()
print("len(allObjects) - {0}".format(len(allObjects)))
searchString = "Selection"
printNames = True
count = 0
for i, x in enumerate(allObjects):
	strObj = str(x)
	if searchString in str(x):
		indx = strObj.find(searchString)
		count +=1
		if printNames:
			print("\n{3:0>3} found {0} at {1:0>4} of {4} : {5} - {2})".format(searchString, i, str(x)[indx-20:indx+150], count, len(str(x)), x.__class__.__name__ if x.__class__.__name__ else None))
		else:
			print("\n{2:0>3} found {0} at {1:0>4} {3} - {4}".format(searchString, i, count, x.__class__.__name__))
			
#variable()