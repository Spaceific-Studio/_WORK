import random
random.seed()
class Surface():
    
    def __init__(self, *args, **kwargs):
        self.minRange = args[0] if len(args) > 0 else 1
        self.maxRange = args[1] if len(args) > 1 else 100
        self.setRandomArea(self.minRange, self.maxRange)
    def setRandomArea(self, *args, **kwargs):
        
        self.area = random.randint(self.minRange, self.maxRange)
        #return self.butcher

def getArea(item, *args, **kwargs):
    """
        function for use in processListSum() to get area values 
        and their sum from Surface objects
        
        item: type tuple(tuple(Surface, ...), element name type: string, ...)
        
        returns tuple(tuple(Surface.area,...), sum of areas type: float or int)
    """
    
    #item must be not empty tuple with not empty tuple of Surface objects
    if item.__class__.__name__ == "tuple":
        #item must be not empty tuple with not empty tuple of Surface objects
        if len(item) > 0 and len(item[0]) > 0 and item[0][0].__class__.__name__ == "Surface":
            areas = [e.area for e in item[0]]
            return (tuple(areas), sum(areas))
        else:
            return (None, 0)
        
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

    
categoriesEnum = ["roofs", "floors", "walls", "frames", "columns", "curtain walls", "openings"]
#categoriesEnum = ["roofs", "floors"]
objects = []
for obj in range(0,2):
    categories = []
    for category in categoriesEnum:
        elements = []
        for element in range(0,3):
            surfaces = []
            for surface in range(0,5):
                surfaces.append(Surface())
            elements.append((surfaces,"element-{0}".format(element)))
        categories.append(elements)
    objects.append(categories)
print(objects)
myList = [0, 1, [2, []], 3,	 [4, 5, [[6,7]]]]
pList = processListSum(getArea, objects)
print(pList)
