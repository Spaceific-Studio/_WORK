# -*- coding: utf-8 -*-
# Copyright(c) 2019, Daniel Gercak
#Script for selecting elements by levels for dynamo 
#resource_path: D:\DANO\_WORK_ARCHIV\BIM_MANAGMENT_STUFF\ENERG_ANALYZY\pythonScripts\Selection_node.py

import sys
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)
from itertools import chain

import clr
# Import Element wrapper extension methods
#clr.AddReference("RevitNodes")
#import Revit
#clr.ImportExtensions(Revit.Elements)

# Import DocumentManager and TransactionManager
clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
doc = DocumentManager.Instance.CurrentDBDocument

clr.AddReference("System")
from System.Collections.Generic import List as Clist

# Import RevitAPI
clr.AddReference("RevitAPI")
import Autodesk
import Autodesk.Revit.DB as DB

#clr.AddReference('DSCoreNodes')
#from DSCore import List

def Unwrap(item):
	return UnwrapElement(item)

def ProcessList(_func, _list):
    return map( lambda x: ProcessList(_func, x) if type(x)==list else _func(x), _list )

#The inputs to this node will be stored as a list in the IN variable.
dataEnteringNode = IN

# exclude elements (we don't want them in selection)
if IN[0] != None:
	if isinstance(IN[0], list):
		#excludeElements = ProcessList(Unwrap, IN[0])
		excludeElements = IN[0]
	else:
		#excludeElements = [Unwrap(IN[0])]
		excludeElements = [IN[0]]
else:
	excludeElements = []


"""
def GetLevelAbove(e):
	allLevels = DB.FilteredElementCollector(doc) \
				.OfCategory(BuiltInCategory.OST_Levels) \
				.WhereElementIsNotElementType() \
				.ToElements()

	elevations = [i.Elevation for i in allLevels]
	sortedLevels = [x for (y,x) in sorted(zip(elevations,allLevels))]
	sortedLevelNames = [i.Name for i in sortedLevels]
	index = sortedLevelNames.index(e.Name)
	if index + 1 >= len(sortedLevels):
		return None
	else:
		return sortedLevels[index+1]
"""

def GetLevels():
	allLevels = DB.FilteredElementCollector(doc) \
				.OfCategory(DB.BuiltInCategory.OST_Levels) \
				.WhereElementIsNotElementType() \
				.ToElements()

	elevations = [i.Elevation for i in allLevels]
	sortedLevels = [x for (y,x) in sorted(zip(elevations,allLevels))]
	return sortedLevels

def getElementByClassName(inClass):
    elements = DB.FilteredElementCollector(doc) \
                 .OfClass(inClass) \
                 .ToElements()
    return elements

def getElementByClassNameAtLevels(inClass):
	elements = []
	if isinstance(inClass, list):
		notFlattened = []
		for i in inClass:
			if len(exclude_element_collection) != 0:
				myElements = DB.FilteredElementCollector(doc) \
							.OfClass(i) \
							.WherePasses(DB.ExclusionFilter(exclude_element_collection)) \
							.ToElements()
			else:
				myElements = DB.FilteredElementCollector(doc) \
							.OfClass(i) \
							.ToElements()
			notFlattened.append(myElements)
		elements = list(chain.from_iterable(notFlattened))
	else:
		if len(exclude_element_collection) != 0:
			elements = DB.FilteredElementCollector(doc) \
						.OfClass(inClass) \
						.WherePasses(DB.ExclusionFilter(exclude_element_collection)) \
						.ToElements()
		else:
			elements = DB.FilteredElementCollector(doc) \
						.OfClass(inClass) \
						.ToElements()
	elementsAtLevel = [[] for i in range(len(allLevels))] 
	for i, element in enumerate(elements):
		elemLevId = int(str(element.LevelId)) 
		levIdIndex = 0  
		if elemLevId != -1:
			levIdIndex = levelIds.index(elemLevId)
		else:
			if inClass in roofCNs:
				levIdIndex = levelIds.index(levelIds[len(allLevels) - 1])
		elementsAtLevel[levIdIndex].append(element)
	return elementsAtLevel

def getElementByCategoryAtLevels(inCategory):
	elements = []
	if isinstance(inCategory, list):
		notFlattened = []
		for i in inCategory:
			if len(exclude_element_collection) != 0:
				myElements = DB.FilteredElementCollector(doc) \
							   .OfCategory(i) \
							   .WherePasses(DB.ExclusionFilter(exclude_element_collection)) \
							   .WhereElementIsNotElementType() \
							   .ToElements()
			else:
				myElements = DB.FilteredElementCollector(doc) \
							   .OfCategory(i) \
							   .WhereElementIsNotElementType() \
							   .ToElements()
			notFlattened.append(myElements)
		elements = list(chain.from_iterable(notFlattened))
	else:
		if len(exclude_element_collection) != 0:
			elements = DB.FilteredElementCollector(doc) \
						 .OfCategory(inCategory) \
						 .WherePasses(DB.ExclusionFilter(exclude_element_collection)) \
						 .ToElements()
		else:
			elements = DB.FilteredElementCollector(doc) \
						 .OfCategory(inCategory) \
						 .ToElements()
	elementsAtLevel = [[] for i in range(len(allLevels))] 
	for i, element in enumerate(elements):
		elemLevId = int(str(element.LevelId)) 
		levIdIndex = 0  
		if elemLevId != -1:
			levIdIndex = levelIds.index(elemLevId)
		else:
			if inCategory in columnCgs:
				levIdIndex = levelIds.index(levelIds[len(allLevels) - 1])
		elementsAtLevel[levIdIndex].append(element)
	return elementsAtLevel

# creating ICollection of exxcluded elements used in FilteredElmentCollector
#elementSet = DB.ElementSet()
myElementIds = []
if excludeElements != None or excludeElements != []:
	excludeElementIds = []
	
	for x in excludeElements:
		myId = x.Id
		#when elements not unwrapped
		myElementId = DB.ElementId(myId)
		myElementIds.append(myElementId)
		#when elements unwrapped
		#myElementIds.append(myId)

#		myElement = doc.GetElement(myId)		
#		elementSet.Insert(myId)
	exclude_element_collection = Clist[DB.ElementId](myElementIds)
else:
	exclude_element_collection = Clist([])

# roof class names
roofCNs = [DB.ExtrusionRoof, DB.FootPrintRoof]
# floor class names
floorCNs = [DB.Floor, DB.HostedSweep]
# wall class names
wallCNs = [DB.Wall]
# column categories 
columnCgs = [DB.BuiltInCategory.OST_Columns, DB.BuiltInCategory.OST_StructuralColumns]
# structural frame categories 
structFrameCgs = [DB.BuiltInCategory.OST_StructuralFraming]

#get level Ids
allLevels = GetLevels()
#levelIdNames = []
levelIds = []

for level in allLevels:
#	levelIdNames.append(str(level.Name))
	levelIds.append(int(str(level.Id)))

try:
	errorReport = None
	output = [getElementByClassNameAtLevels(roofCNs), \
			  getElementByClassNameAtLevels(floorCNs), \
			  getElementByClassNameAtLevels(wallCNs), \
			  getElementByCategoryAtLevels(columnCgs), \
			  getElementByCategoryAtLevels(structFrameCgs)]
	#output = flattened
except:
	# if error accurs anywhere in the process catch it
	import traceback
	errorReport = traceback.format_exc()

#Assign your output to the OUT variable
if errorReport == None:
	OUT = output
else:
	OUT = errorReport