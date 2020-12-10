import random
import time

class Solid():
    count = 0
    def __init__(self):
        self.name = "solid_{0}".format(Solid.count)
        Solid.count += 1
        
class Opening():
    count = 0
    def __init__(self):
        self.name = "opening_{0}".format(Opening.count)
        Opening.count += 1

pairSolids = [Solid() for x in range(900)]
random.shuffle(pairSolids)
randomSolids = pairSolids.copy()
random.shuffle(randomSolids)
print("solids:")
print([x.name for x in pairSolids])
print("randomSolids:")
print([x.name for x in randomSolids])

pairOpenings = [Opening() for x in range(900)]
random.shuffle(pairOpenings)
randomOpenings = pairOpenings.copy()
random.shuffle(randomOpenings)
print("openings:")
print([x.name for x in pairOpenings])
print("randomSolids:")
print([x.name for x in randomOpenings])

pairs = ["{2}.{0}>{1}".format(x.name, pairSolids[i].name, i) for i, x in enumerate(pairOpenings)]
print("pairs")
print(pairs)

pairsDict = {o.name:pairSolids[i].name for i, o in enumerate(pairOpenings)}
print(pairsDict)
#print(["{0}<>{1}".format(x[0].name, x[1].name) for x in pairs])

def findPairs(inOpenings, inSolids):
    results = []
    for i, o in enumerate(inOpenings):
        for j, s in enumerate(inSolids):
            if doesIntersect(o, s):
                pairOpeningsIndex = pairOpenings.index(o)
                results.append("pairOpeningIndex_{4}>({2}){0}~({3}){1}".format(o.name, s.name, i, j,  pairOpeningsIndex))
                break
    return results

def findPairsRecursive(inOpenings, inSolids):
    results = []
    if len(inOpenings) > 0:
        for i, o in enumerate(inOpenings):
            for j, s in enumerate(inSolids):
                if doesIntersect(o, s):
                    pairOpeningsIndex = pairOpenings.index(o)
                    #results.append("pairOpeningIndex_{4}>({2}){0}~({3}){1}".format(o.name, s.name, i, j,  pairOpeningsIndex))
                    iOpening = inOpenings.pop(i)
                    iSolid = inSolids.pop(j)
                    returnPair = findPairsRecursive(inOpenings, inSolids)
                    return [(iOpening.name, iSolid.name)] + returnPair if returnPair != None else [(iOpening.name, iSolid.name)]
    #return results

def doesIntersect(inOpening, inSolid):
    pairOpeningsIndex = pairOpenings.index(inOpening)
    if inSolid.name == pairSolids[pairOpeningsIndex].name:
        return True
    else:
        return False
sTime = time.time()
myPairs = findPairs(randomOpenings, randomSolids)
eTime = time.time()
myTime = eTime - sTime
print("myPairs {0}".format(myTime))
print(myPairs)
sTime = time.time()
myPairsRecursive = findPairsRecursive(randomOpenings, randomSolids)
eTime = time.time()
myTime = eTime - sTime
print("myPairsRecursive {0}".format(myTime))
print(myPairsRecursive)
            