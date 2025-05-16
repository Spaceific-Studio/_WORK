# -*- coding: utf-8 -*-
# Copyright(c) 2019, Daniel Gercak
#Script for selecting elements by levels for dynamo 
#resource_path: D:\DANO\_WORK_ARCHIV\BIM_MANAGMENT_STUFF\ENERG_ANALYZY\pythonScripts\Selection_node.py

import sys
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)
from itertools import chain, groupby

import clr
# Import Element wrapper extension methods
clr.AddReference("RevitNodes")
import Revit
clr.ImportExtensions(Revit.Elements)
clr.ImportExtensions(Revit.GeometryConversion)

# Import DocumentManager and TransactionManager
clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
doc = DocumentManager.Instance.CurrentDBDocument



clr.AddReference("System")
from System.Collections.Generic import List as Clist

# Import RevitAPI
clr.AddReference("RevitAPI")
import Autodesk
import Autodesk.Revit.DB as DB

#clr.AddReference('DSCoreNodes')
#from DSCore import List, Solid

clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *

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

items = UnwrapElement(IN[0])
incopenings = True
incshadows = False
incwalls = True
incshared = True

def GetInserts(item,incopenings = True, incshadows = True, incwalls = True, incshared = True):
	# Regular host objects
	if hasattr(item, "FindInserts"):
		return [item.Document.GetElement(x) for x in item.FindInserts(incopenings,incshadows,incwalls,incshared)]
	# Railings
	if hasattr(item, "GetAssociatedRailings"):
		return [item.Document.GetElement(x) for x in item.GetAssociatedRailings()]
	else: return []

def convert_geometry_instance(geo, elementlist):
	for g in geo:
		if str(g.GetType()) == 'Autodesk.Revit.DB.GeometryInstance':
			elementlist = convert_geometry_instance(g.GetInstanceGeometry(), elementlist)
		else:
			try: 
				if g.Volume != 0:
					elementlist.append(g)
			except:
				pass
	return elementlist

def ProcessList(_func, _list):
    return map( lambda x: ProcessList(_func, x) if type(x)==list else _func(x), _list )

def ProcessEidList(_func, _list):
    return map( lambda x: ProcessEidList(_func, x) if type(x)==list else _func(x.Id), _list )

def Unwrap(item):
	return UnwrapElement(item)

def notMoreThanOne(inItem):
	if isinstance(inItem, list):
		if len(inItem) > 1:
			return False
		else:
			return True
	else:
		return False

def getDynamoSolid(item):
	pass

def getDynamoSolids():
	#TransactionManager.Instance.EnsureInTransaction(doc)
	#trans = DB.SubTransaction(doc)
	#trans.Start()
	pass

def getUniqueElements(items):
	#make list of unique by filtering inserts list 
	# first 3 * flatten 
	flattenInserts = list(chain.from_iterable(chain.from_iterable(chain.from_iterable(inserts))))
	#sort by ID
	myIds = zip(map(lambda x: x.Id, flattenInserts), flattenInserts)
	myIds.sort(key = lambda a: a[0])
	#make groups of same ids
	myGroupedIds = []
	for k, g in groupby(myIds, lambda a: a[0]):
		myGroupedIds.append(list(g))
	#map grupped items by notMoreThanOne function - if item is list of more than one element with same Id, get only first element 
	uniqueInsertIds = map(lambda x: x[0] if notMoreThanOne(x) else x[0], myGroupedIds)
	#unzip tuple
	stringIds, returnInserts = zip(*uniqueInsertIds)
	return returnInserts

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

	myElements = [getElementByClassNameAtLevels(roofCNs), \
			  getElementByClassNameAtLevels(floorCNs), \
			  getElementByClassNameAtLevels(wallCNs), \
			  getElementByCategoryAtLevels(columnCgs), \
			  getElementByCategoryAtLevels(structFrameCgs)]
	unWrappedElements = ProcessList(Unwrap, myElements)
	inserts = ProcessList(GetInserts, unWrappedElements)
	#myOutput = unWrappedElements
#output = flattened
except:
	# if error accurs anywhere in the process catch it
	import traceback
	errorReport = traceback.format_exc()

detail_lvl = DB.ViewDetailLevel.Coarse
#include invisible objects
inc_invis = False
view = None
remove_inserts = True
revitlist = list()
dynlist = list()
myText = []
myText.append("{0}". format(len(unWrappedElements)))
#make list of unique by filtering inserts list 
# first 3 * flatten 
flattenInserts = list(chain.from_iterable(chain.from_iterable(chain.from_iterable(inserts))))
#sort by ID
myIds = zip(map(lambda x: x.Id, flattenInserts), flattenInserts)
myIds.sort(key = lambda a: a[0])
#make groups of same ids
myGroupedIds = []
for k, g in groupby(myIds, lambda a: a[0]):
	myGroupedIds.append(list(g))
#map grupped items by notMoreThanOne function - if item is list of more than one element with same Id, get only first element 
uniqueInsertIds = map(lambda x: x[0] if notMoreThanOne(x) else x[0], myGroupedIds)
#unzip tuple
stringIds, uniqueInserts = zip(*uniqueInsertIds) 
uniqueInserts = getUniqueElements(inserts)
# for x in myGroupedIds:
# 	if x.Id not in uniqueInserts:
# 		uniqueInserts.append(x)
TransactionManager.Instance.EnsureInTransaction(doc)
trans = DB.SubTransaction(doc)
trans.Start()
i = 0
if remove_inserts == True:
	try:
		for insert in uniqueInserts:
			doc.Delete(insert.Id)
			#ProcessEidList(doc.Delete,inserts)
		doc.Regenerate()
	except:
		import traceback
		errorReport = traceback.sys.exc_info()
#	finally:
#		trans.RollBack()
#		TransactionManager.Instance.TransactionTaskDone()
for elementCategory in unWrappedElements:
	for levels in elementCategory:
		for item in levels:
			geo_options = DB.Options()
			if view == None: geo_options.DetailLevel = detail_lvl
			geo_options.IncludeNonVisibleObjects = inc_invis
			if view != None: geo_options.View = view
			if type(item) !=list:
				revitGeo = item.Geometry[geo_options]
				try:		
					revit_geos = convert_geometry_instance(revitGeo, list())
					revitlist.append(revit_geos)
					dyn_geos = list()
					cats = list()
					for geo in revit_geos:
						try:
							dyn_geos.append((geo.ToProtoType(), item.Id))
						except:
							import traceback
							errorReport = traceback.sys.exc_info()
							#print "error_type: {0}, error_instance{1}, traceback -{2}".format(error_type, error_instance, traceback)
							dyn_geos.append(None)
					dynlist.append(dyn_geos)
				except:
					revitlist.append(list())
					dynlist.append(list())
				i += 1
			else:
				myText.append("{0}".format(type(item)))
trans.RollBack()
TransactionManager.Instance.TransactionTaskDone()
solids = list(chain.from_iterable(dynlist))
#solid = Solid.ByUnion(solids)
#polySurface = PolySurface.BySolid(solid)
#surfaces = PolySurface.Surfaces(polySurface)
myOutput = (unWrappedElements, dynlist, uniqueInserts)
#myOutput = myText

#Assign your output to the OUT variable
if errorReport == None:
	OUT = myOutput
else:
	OUT = errorReport