import random
import numpy


random.seed()
class Random():
    
    def __init__(self):
        pass
    def getRandomNumber(self, *args, **kwargs):
        self.minRange = args[0]
        self.maxRange = args[1]
        self.butcher = kwargs['butcher'] if "butcher" in kwargs else 1
        else:
            self.butcher = 1
        if "fibrilioza" in kwargs:
            self.fibrilioza = kwargs['fibrilioza']
        else:
            self.fibrilioza = 1
        return random.randint(self.minRange, self.maxRange*self.butcher)
        #return self.butcher

def ProcessList(_func, _list = [], level=0, *args, **kwargs):
    return map( lambda x: ProcessList(_func, x, level+1, *args, **kwargs) if type(x)==list else _func(x, *args, **kwargs), _list )

rnd = Random()
myList = [0, 1, [2, []], 3,	 [4, 5, [[6,7]]]]
pList = ProcessList(rnd.getRandomNumber,myList,10, 70000, butcher=23, fibrilioza = 65)
print("pList {0}\n".format(pList))
