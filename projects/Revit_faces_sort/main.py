from operator import itemgetter 
from itertools import groupby 
#print "globals".format(globals())


class Solid:
    def __init__(self, name, volume, isOuter, intersectsWith = None):
        self.name = name
        self.volume = volume
        self.isOuter = isOuter
    def __repr__(self):
        return repr((self.name, self.volume, self.isOuter))
solid_objects = [[Solid("Outer_01", 25000, ("lev_1", \
	                                           "lev_2", \
	                                           "lev_3"), \
	                                           True), \
                  Solid("Inner_01", 6000, False), \
                  Solid("Inner_02", 5400, False)], \
	                [Solid("Outer_02", 5000, True), \
	                 Solid("Inner_03", 4800, False), \
	                 Solid("Inner_04", 4600, False), \
	                 Solid("Inner_05", 4500, False)]]

ungruppedObjects = [(1,"Inner_07", 6000, ("lev_1", \
	                                           "lev_2", \
	                                           "lev_3"), False), \
                    (1,"Inner_01", 5400, False), \
	                   (2,"Outer_02", 5000, True), \
	                   (1,"Outer_01", 25000, True), \
	                   (3,"Inner_12", 450, False), \
	                   (0,"Inner_08", 4700, False), \
	                   (2,"Inner_06", 4500, False), \
	                   (1,"Inner_03", 4800, False), \
	                   (3,"Inner_11", 300, False), \
	                   (1,"Inner_04", 4600, False), \
	                   (0,"Outer_00", 45000, True), \
	                   (0,"Inner_09", 600, False), \
	                   (3,"Outer_03", 500, True), \
	                   (0,"Inner_10", 9000, False), \
	                   (2,"Inner_05", 4500, False)]
#help(filter)
myItems = itemgetter(solid_objects)
ungruppedObjects.sort(key = lambda a: a[2], reverse=True)
filtered_1 = filter(lambda x: x[0] == 0,ungruppedObjects)
filtered_1_false = filter(lambda x: x[0] != 0,ungruppedObjects)
filtered_2 = filter(lambda x: x[0] == 1,filtered_1_false)
filtered_2_false = filter(lambda x: x[0] != 1,filtered_1_false)
#print("first sort {0}\n".format(ungruppedObjects))
#print("filtered_1 {0}\n".format(filtered_1))
#print("filtered_1_false {0}\n".format(filtered_1_false))
#print("filtered_2 {0}\n".format(filtered_2))
#print("filtered_2_false {0}\n".format(filtered_2_false))

#list must be sorted
def groupSolids(inList, inLevel = 0):
    nextLevelItems = []
    returnItems = []
    if len(inList) > 0:
        trueItems = filter(lambda x: x[0] == inLevel, ungruppedObjects)
        falseItems = filter(lambda x: x[0] != inLevel, ungruppedObjects)
        if len(trueItems) > 0:
            returnItems = [trueItems]
            nextLevelItems = groupSolids(falseItems, inLevel + 1)
            #print("level {1} - nextLevelItems {0}\n".format(nextLevelItems,inLevel))    
    if returnItems != [] or nextLevelItems != None:
        #if len(nextLevelItems) == 0 and inLevel == 1:
        #    nextLevelItems.pop()
        return returnItems + nextLevelItems

revitElements = (["walls", [],[]], "")
#dynamoElement = (eId, geometry, parentOuterVolume, level)
#surface = (eId, geometry, parentOuterVolume, level)

def flattenList(inList, prevItem = [], inLevel = 0):
	nextLevelItems = []
	returnItems = []
	myLevels = []
	if type(inList) == list:
		for item in inList:
            if type(item) == list:
                returnItems = prevItem + flattenList(item, prevItems, inListinLevel + 1)
            else:
                returnItems = prevItem + [item]
	else:
        returnItems = prevItems + [item]
	return returnItems

testList = [0, "a", \
            ["b", 2, \
             [3, "c", 4], \
            5, "d"] \
           ]
outList = flattenList(testList)

print("outList = {0}".format(outList))
myGroupedSolids = groupSolids(ungruppedObjects)
#myGroupedSolids.pop()
#print ("myGroupedSolids {0}\n".format(myGroupedSolids))
#print ("len(myGroupedSolids) {0}\n".format(len(myGroupedSolids)))
myList = [[(0,1),(0,2)],[(0,3)]]
myList.append([(5,5),(6,6)])
solid_objects.append(ungruppedObjects)
#print("appended lists {0}\n".format(myList))
groups = []
uniqueKeys = []
for k, g in groupby(ungruppedObjects, lambda a: a[2]):
    groups.append(list(g))
    uniqueKeys.append(k)
#print "groups {0}\n".format(groups)
#print "uniqueKeys{0}\n".format(uniqueKeys)
#print myItems
#y = groupby(ungruppedObjects, itemgetter(0))
#for elt, items in groupby(ungruppedObjects, itemgetter(2)):
#    print("elt {0}, items {1}".format(elt, items)) 
#    for i in items:
#         print(i)
#stud_objects.sort(key = lambda c : c.grade, reverse=True)


#a = [5,2,3,4,5,6]
#b = ["timber", "beton", "beblo", "dyka","dyla","fuck"]
#zipped = zip(a, b)
#myList = sorted(zipped, key = lambda a: a[0])
#aSorted, bSorted = zip(*myList)
