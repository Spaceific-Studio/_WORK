# -*- coding: utf-8 -*-
# Copyright(c) 2021, Daniel Gercak
#Revit Python Shell script for multiple joining elements
#get the neighbours of selected element using the BoundingBoxIntersectsFilter 
#resource_path: https://github.com/Spaceific-Studio/_WORK/REVIT_API/getNeighboursOfSelected.py
import sys
if "IronPython" in sys.prefix:
	pytPath = r'C:\Program Files (x86)\IronPython 2.7\Lib'
	sys.path.append(pytPath)
import os

print("cwd: {}".format(os.getcwd()))

#searches for directory for library used by RevitPythonShell. Example h:\_WORK\PYTHON\REVIT_API\LIB\__init__.py
splittedFile = __file__.split("\\")
rpsFileDir = "\\".join(splittedFile[:-1]) if len(splittedFile) > 2 else ""
#rpsPyFilePath, rpsPyFileDNames, rpsPyFileFNames = walkDir(rpsFileDir)
rpsPyFilePath, rpsPyFileDNames, rpsPyFileFNames = next(os.walk(rpsFileDir))

#searches for library in Spaceific-Studio addin folder. Example: C:\users\CZDAGE\AppData\Roaming\Autodesk\Revit\Addins\2020\Spaceific-Studio\__init__.py
splittedFile = __file__.split("\\")
addinPyFileLibDir = "\\".join(splittedFile[:-2]) if len(splittedFile) > 2 else ""
#addinPyFileLibPath, addinPyFileDNames, addinPyFileFNames = walkDir(addinPyFileLibDir)
addinPyFileLibPath, addinPyFileDNames, addinPyFileFNames = next(os.walk(addinPyFileLibDir))

if "LIB" in rpsPyFileDNames:
	lib_path = os.path.join(rpsPyFilePath, "LIB")
elif "__init__.py" in addinPyFileFNames:
	lib_path = addinPyFileLibPath
else:
	lib_path = r'H:\_WORK\PYTHON\REVIT_API\LIB'
print("__file__: {}".format(__file__))
print("rpsFileDir: {}".format(rpsFileDir))
print("rpsPyFilePath: {}".format(rpsPyFilePath))
print("rpsPyFileDNames: {}".format(rpsPyFileDNames))
print("rpsPyFileFNames: {}".format(rpsPyFileFNames))
print("addinPyFileLibDir: {}".format(addinPyFileLibDir))
print("addinPyFileLibPath: {}".format(addinPyFileLibPath))
print("addinPyFileFNames: {}".format(addinPyFileFNames))
print("addinPyFileDNames: {}".format(addinPyFileDNames))
#print("pyFilePath: {}".format(pyFilePath))
#lib_path = r'H:\_WORK\PYTHON\REVIT_API\LIB'
print("lib_path: {}".format(lib_path))
sys.path.append(lib_path)

import platform
import time

try:
	sys.modules['__main__']
	hasMainAttr = True	
except:
	hasMainAttr = False

if hasMainAttr:
	#import clr
	if "pydroid" in sys.prefix:
		pass
	elif "Python38" in sys.prefix:
		pass
	else:
		from Autodesk.Revit.UI.Selection import *
		import Autodesk.Revit.DB as DB
		import Autodesk.Revit.UI as UI
		import Autodesk
		import System
		import threading
		from System.Collections.Generic import List as Clist
		from System import Type
		#from System.Collections.Generic import Ilist
		#import System.Drawing
		import clr
		clr.AddReferenceByPartialName('System.Windows.Forms')
		clr.AddReference("System.Drawing")
		clr.AddReference('System')
		#import System.Windows.Forms
		from System.Threading import ThreadStart, Thread
		from System.Windows.Forms import *
		from System.Drawing import *
		doc = __revit__.ActiveUIDocument.Document
		uidoc = __revit__.ActiveUIDocument
		#clr.AddReference("RevitServices")
		#import RevitServices
		#from RevitServices.Transactions import TransactionManager
		pass

else:
	if "pydroid" in sys.prefix:
		pass
	elif "Python38" in sys.prefix:
		pass
	else:
		import clr
		clr.AddReference('ProtoGeometry')
		from Autodesk.DesignScript.Geometry import *
		clr.AddReference("RevitAPI")
		import Autodesk
		import Autodesk.Revit.DB as DB
		clr.AddReference("RevitServices")
		import RevitServices
		from RevitServices.Persistence import DocumentManager
		from RevitServices.Transactions import TransactionManager
		doc = DocumentManager.Instance.CurrentDBDocument

# clr.AddReference("RevitAPI")
# import Autodesk
# import Autodesk.Revit.DB as DB

try:
	import Autodesk
	sys.modules['Autodesk']
	hasAutodesk = True	
except:
	hasAutodesk = False

print("module : {0} ; hasMainAttr = {1}".format(__file__, hasMainAttr))
print("module : {0} ; hasAutodesk = {1}".format(__file__, hasAutodesk))

#if sys.platform.startswith('linux'):
#	libPath = r"/storage/emulated/0/_WORK/REVIT_API/LIB"
#elif sys.platform.startswith('win') or sys.platform.startswith('cli'):
#	scriptDir = "\\".join(__file__.split("\\")[:-1])
#	scriptDisk = __file__.split(":")[0]
#	if scriptDisk == "B" or scriptDisk == "b":
#		libPath = r"B:/Podpora Revit/Rodiny/141/_STAVEBNI/_REVITPYTHONSHELL/LIB"
#	elif scriptDisk == "H" or scriptDisk == "h":
#		libPath = r"H:/_WORK/PYTHON/REVIT_API/LIB"

#if sys.platform.startswith('linux'):
#	pythLibPath = r"/storage/emulated/0/_WORK/LIB"
#elif sys.platform.startswith('win') or sys.platform.startswith('cli'):
#	pythLibPath = r"H:/_WORK/PYTHON/LIB"

#sys.path.append(libPath)
#sys.path.append(pythLibPath)



""" Errors.catchVar(sys.platform, "sys.platform")
Errors.catchVar(sys.prefix, "sys.prefix")
Errors.catchVar(os.name, "os.name")
Errors.catchVar(platform.sys, "platform.sys")
Errors.catchVar(platform.os, "platform.os")
Errors.catchVar(platform.platform(), "platform.platform()") """

#import SpaceOrganize
#import RevitSelection as RS

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document


def pickobjects(inStatus):
	__window__.Hide()
	picked = uidoc.Selection.PickElementsByRectangle(inStatus)
	__window__.Show()
	#__window__.Topmost = True
	return picked

def pickobject(inStatus):
	from Autodesk.Revit.UI.Selection import ObjectType
	__window__.Hide()
	picked = uidoc.Selection.PickObject(ObjectType.Element, inStatus)
	__window__.Show()
	#__window__.Topmost = True
	return picked

priorityLookup = [	[Autodesk.Revit.DB.BuiltInCategory.OST_Columns, Autodesk.Revit.DB.BuiltInCategory.OST_StructuralColumns], \
					Autodesk.Revit.DB.BuiltInCategory.OST_StructuralFraming, \
					[Autodesk.Revit.DB.FootPrintRoof, Autodesk.Revit.DB.ExtrusionRoof], \
					Autodesk.Revit.DB.Wall, \
					[Autodesk.Revit.DB.Floor, Autodesk.Revit.DB.SlabEdge], \
					Autodesk.Revit.DB.BuiltInCategory.OST_Ceilings]

def createMultiCategoryFilter():
	listOfCategories = list()
	#listOfCategories.append(DB.BuiltInCategory.OST_Floors)
	listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_Columns)
	listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_StructuralColumns)
	listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_StructuralFraming)
	listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_StructuralFoundation)
	#listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_Walls)
	#listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_Floors)
	#listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_Roofs)
	listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_Ceilings)
	colOfBIC = Clist[DB.BuiltInCategory](listOfCategories)
	multiCategoryFilter = DB.ElementMulticategoryFilter(colOfBIC)
	return multiCategoryFilter

def createExclusionMultiCategoryFilter():
	listOfCategories = list()
	#listOfCategories.append(DB.BuiltInCategory.OST_Floors)
	listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_IOSModelGroups)
	listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_MassOpening)
	listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_ArcWallRectOpening)
	listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_SWallRectOpening)
	listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_ShaftOpening)
	listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_StructuralFramingOpening)
	listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_ColumnOpening)
	listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_CeilingOpening)
	listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_FloorOpening)
	listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_RoofOpening)
	listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_IOSOpening)
	listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_WindowsOpeningCut)
	listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_DoorsOpeningCut)
	listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_CurtainGrids)
	listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_CurtainWallMullionsCut)
	listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_CurtainWallMullions)
	listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_CurtainWallPanels)
	listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_CurtainWallMullionsHiddenLines)
	listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_CurtainWallPanelsHiddenLines)
	colOfBIC = Clist[DB.BuiltInCategory](listOfCategories)
	multiCategoryFilter = DB.ElementMulticategoryFilter(colOfBIC)
	return multiCategoryFilter

def getActiveViewPhaseStatusFilter():
	paramId = Autodesk.Revit.DB.ElementId(Autodesk.Revit.DB.BuiltInParameter.VIEW_PHASE)
	param_provider = Autodesk.Revit.DB.ParameterValueProvider(paramId)
	activeViewPhaseId = param_provider.GetElementIdValue(doc.ActiveView)
	docPhases =  Autodesk.Revit.DB.FilteredElementCollector(doc) \
								.OfCategory(Autodesk.Revit.DB.BuiltInCategory.OST_Phases) \
								.WhereElementIsNotElementType() \
								.ToElements()

	#Filter inserts visible only in active view and of Existing phase status - (ignore demolished elements in previous phases) 
	myElementPhaseStatusFilter1 = Autodesk.Revit.DB.ElementPhaseStatusFilter(activeViewPhaseId, Autodesk.Revit.DB.ElementOnPhaseStatus.Existing, False)
	myElementPhaseStatusFilter2 = Autodesk.Revit.DB.ElementPhaseStatusFilter(activeViewPhaseId, Autodesk.Revit.DB.ElementOnPhaseStatus.New,False)
	return DB.LogicalOrFilter(myElementPhaseStatusFilter1, myElementPhaseStatusFilter2)

def createMultiClassFilter():
	listOfClasses = list()
	listOfClasses.append(Autodesk.Revit.DB.FootPrintRoof)
	listOfClasses.append(Autodesk.Revit.DB.ExtrusionRoof)
	listOfClasses.append(Autodesk.Revit.DB.Wall)
	listOfClasses.append(Autodesk.Revit.DB.Floor)
	#due to an exception: Autodesk.Revit.Exceptions.ArgumentException: Input type(Autodesk.Revit.DB.SlabEdge)
	# is of an element type that exists in the API, but not in Revit's native object model. 
	# Try using Autodesk.Revit.DB.HostedSweep instead, and then postprocessing the results to find the elements of interest.
	#listOfClasses.append(Autodesk.Revit.DB.SlabEdge)
	listOfClasses.append(Autodesk.Revit.DB.HostedSweep)
	#colOfClasses = Clist[IronPython.Runtime.Types.PythonType](listOfClasses)
	typeList = Clist[System.Type]()
	for item in listOfClasses:
		typeList.Add(item)
	multiClassFilter = DB.ElementMulticlassFilter(typeList)
	return multiClassFilter

def getAllModelElements(doc):
	multiCatFilter = createMultiCategoryFilter()
	allIdsOfModelElements = DB.FilteredElementCollector(doc).WherePasses(multiCatFilter).WhereElementIsNotElementType().ToElementIds()
	allElementsOfModel = map(lambda x: doc.GetElement(x), allIdsOfModelElements)
	return allElementsOfModel

def convertFromInternal(inValue):
	displayUnitType = uidoc.Document.GetUnits().GetFormatOptions(DB.UnitType.UT_Length).DisplayUnits
	#print("displayUnitType {}".format(displayUnitType))
	return DB.UnitUtils.ConvertFromInternalUnits(inValue, displayUnitType)

def convertToInternal(inValue):
	displayUnitType = uidoc.Document.GetUnits().GetFormatOptions(DB.UnitType.UT_Length).DisplayUnits
	#print("displayUnitType {}".format(displayUnitType))
	return DB.UnitUtils.ConvertToInternalUnits(inValue, displayUnitType)

def getNeighbours(inElement, multiCatFilter, multiClassFilter, exclusionFilter, activeViewPhaseStatusFilter):
	inElementBBox = inElement.get_BoundingBox(doc.ActiveView)
	virtualBBoxOffset = 50
	newMin = DB.XYZ(convertToInternal(convertFromInternal(inElementBBox.Min.X)-virtualBBoxOffset), \
					convertToInternal(convertFromInternal(inElementBBox.Min.Y)-virtualBBoxOffset), \
					convertToInternal(convertFromInternal(inElementBBox.Min.Z)-virtualBBoxOffset))
	newMax = DB.XYZ(convertToInternal(convertFromInternal(inElementBBox.Max.X)+virtualBBoxOffset), \
					convertToInternal(convertFromInternal(inElementBBox.Max.Y)+virtualBBoxOffset), \
					convertToInternal(convertFromInternal(inElementBBox.Max.Z)+virtualBBoxOffset))
	print("inElementBBox.Min.X = {0}\n \
			inElementBBox.Min.Y = {1}\n \
			inElementBBox.Min.Z = {2}\n \
			inElementBBox.Min.BasisX = {3}\n \
			inElementBBox.Min.BasisY = {4}\n \
			inElementBBox.Min.BasisZ = {5}\n \
			inElementBBox.Max.X = {6}\n \
			inElementBBox.Max.Y = {7}\n \
			inElementBBox.Max.Z = {8}\n \
			inElementBBox.Max.BasisX = {9}\n \
			inElementBBox.Max.BasisY = {10}\n \
			inElementBBox.Max.BasisZ = {11}\n \
			newMin.X = {12}\n \
			newMin.Y = {13}\n \
			newMin.Z = {14}\n \
			newMax.X = {15}\n \
			newMax.Y = {16}\n \
			newMax.Z = {17}\n \
				".format(\
				convertFromInternal(inElementBBox.Min.X), \
				convertFromInternal(inElementBBox.Min.Y), \
				convertFromInternal(inElementBBox.Min.Z), \
				inElementBBox.Min.BasisX, \
				inElementBBox.Min.BasisY, \
				inElementBBox.Min.BasisZ, \
				convertFromInternal(inElementBBox.Max.X), \
				convertFromInternal(inElementBBox.Max.Y), \
				convertFromInternal(inElementBBox.Max.Z), \
				inElementBBox.Max.BasisX, \
				inElementBBox.Max.BasisY, \
				inElementBBox.Max.BasisZ, \
				convertFromInternal(newMin.X), \
				convertFromInternal(newMin.Y), \
				convertFromInternal(newMin.Z), \
				convertFromInternal(newMax.X), \
				convertFromInternal(newMax.Y), \
				convertFromInternal(newMax.Z)))
	#inElementOutline = DB.Outline(inElementBBox.Min, inElementBBox.Max)
	inElementOutline = DB.Outline(newMin, newMax)
	bboxIntersectingFilter = DB.BoundingBoxIntersectsFilter(inElementOutline)
	selfElementExclusionFilter = DB.ExclusionFilter(Clist[DB.ElementId]([inElement.Id]))
	
	insideElementsMulitCatIdsCol = DB.FilteredElementCollector(doc) \
									.WherePasses(multiCatFilter) \
									.WherePasses(exclusionFilter) \
									.WherePasses(bboxIntersectingFilter) \
									.WherePasses(selfElementExclusionFilter) \
									.WherePasses(activeViewPhaseStatusFilter) \
									.WhereElementIsNotElementType() \
									.ToElementIds()
	insideElementsMulitClassIdsCol = DB.FilteredElementCollector(doc) \
										.WherePasses(multiClassFilter) \
										.WherePasses(exclusionFilter) \
										.WherePasses(bboxIntersectingFilter) \
										.WherePasses(selfElementExclusionFilter) \
										.WherePasses(activeViewPhaseStatusFilter) \
										.WhereElementIsNotElementType() \
										.ToElementIds()

	""" if insideElementsMulitCatIdsCol.Count > 0:
		excludeElementsCol1 = DB.FilteredElementCollector(doc, insideElementsMulitCatIdsCol).WherePasses(multiExclCategoryFilter).ToElementIds()
		if excludeElementsCol1.Count > 0:
			detailGroupsExclFilter1 = DB.ExclusionFilter(excludeElementsCol1)
			insideElementsMulitCatIdsCol = DB.FilteredElementCollector(doc, insideElementsMulitCatIdsCol).WherePasses(detailGroupsExclFilter1).ToElementIds()
	if insideElementsMulitClassIdsCol.Count:
		excludeElementsCol2 = DB.FilteredElementCollector(doc, insideElementsMulitClassIdsCol).WherePasses(multiExclCategoryFilter).ToElementIds()
		if excludeElementsCol2.Count > 0:
			detailGroupsExclFilter2 = DB.ExclusionFilter(excludeElementsCol2)
			insideElementsMulitClassIdsCol = DB.FilteredElementCollector(doc, insideElementsMulitClassIdsCol).WherePasses(detailGroupsExclFilter2).ToElementIds() """

	insideElementsMulitCatIds = list(insideElementsMulitCatIdsCol)
	insideElementsMulitClassIds = list(insideElementsMulitClassIdsCol)

	return insideElementsMulitCatIds + insideElementsMulitClassIds


allElementsCol = Clist[DB.Element](getAllModelElements(doc))

multiCatFilter = createMultiCategoryFilter()
multiClassFilter = createMultiClassFilter()
multiExclCategoryFilter = createExclusionMultiCategoryFilter()
allExcludedIds = list(DB.FilteredElementCollector(doc).WherePasses(multiExclCategoryFilter).ToElementIds())
#filter out all curtain walls
allExcludedWallsIds = list(DB.FilteredElementCollector(doc).OfClass(Autodesk.Revit.DB.Wall))
wallIdsToExclude = []
for el in allExcludedWallsIds:
	#print("allExcludedWalls {}".format(dir(el)))
	if hasattr(el, "CurtainGrid"):
		if el.CurtainGrid:
			wallIdsToExclude.append(el.Id)
allExcludedIds += wallIdsToExclude

exclusionFilter = DB.ExclusionFilter(Clist[DB.ElementId](allExcludedIds))
activeViewPhaseStatusFilter = getActiveViewPhaseStatusFilter()

print("allExcludedIds length {}".format(len(allExcludedIds)))
#uidoc.Selection.SetElementIds(allExcludedIds)
#input("waiting for enter...")

firstSelectionMultiCatIdsCol = DB.FilteredElementCollector(doc, __revit__.ActiveUIDocument.Selection.GetElementIds()) \
									.WherePasses(multiCatFilter) \
									.WherePasses(exclusionFilter) \
									.WherePasses(activeViewPhaseStatusFilter) \
									.WhereElementIsNotElementType() \
									.ToElementIds()
firstSelectionMultiClassIdsCol = DB.FilteredElementCollector(doc, __revit__.ActiveUIDocument.Selection.GetElementIds()) \
									.WherePasses(multiClassFilter) \
									.WherePasses(exclusionFilter) \
									.WherePasses(activeViewPhaseStatusFilter) \
									.WhereElementIsNotElementType() \
									.ToElementIds()
firstSelectionMultiCat = [doc.GetElement(elId) for elId in firstSelectionMultiCatIdsCol]
firstSelectionMultiClass = [doc.GetElement(elId) for elId in firstSelectionMultiClassIdsCol]
firstSelection = firstSelectionMultiCat + firstSelectionMultiClass
firstSelectionIdsCol = Clist[DB.ElementId]([x.Id for x in firstSelection])

selNeighbours = getNeighbours(firstSelection[0], multiCatFilter, multiClassFilter, exclusionFilter, activeViewPhaseStatusFilter)
for i, neighbour in enumerate([doc.GetElement(x) for x in selNeighbours]):
	#print(neighbour)
	print("{0}-{1}-{2}".format(i, neighbour.Id, neighbour.Category.Name))
selNeighboursCol = Clist[DB.ElementId](selNeighbours + [firstSelection[0].Id])
t = DB.Transaction(doc, "Isolate neighbours")
t.Start()
uidoc.ActiveView.IsolateElementsTemporary(selNeighboursCol)
t.Commit()
#input("Waiting for keypress...")
