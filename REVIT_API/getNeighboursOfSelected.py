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

if sys.platform.startswith('linux'):
    libPath = r"/storage/emulated/0/_WORK/REVIT_API/LIB"
elif sys.platform.startswith('win') or sys.platform.startswith('cli'):
    scriptDir = "\\".join(__file__.split("\\")[:-1])
    scriptDisk = __file__.split(":")[0]
    if scriptDisk == "B" or scriptDisk == "b":
        libPath = r"B:/Podpora Revit/Rodiny/141/_STAVEBNI/_REVITPYTHONSHELL/LIB"
    elif scriptDisk == "H" or scriptDisk == "h":
        libPath = r"H:/_WORK/PYTHON/REVIT_API/LIB"

if sys.platform.startswith('linux'):
    pythLibPath = r"/storage/emulated/0/_WORK/LIB"
elif sys.platform.startswith('win') or sys.platform.startswith('cli'):
    pythLibPath = r"H:/_WORK/PYTHON/LIB"

sys.path.append(libPath)
sys.path.append(pythLibPath)



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
	colOfBIC = Clist[DB.BuiltInCategory](listOfCategories)
	multiCategoryFilter = DB.ElementMulticategoryFilter(colOfBIC)
	return multiCategoryFilter

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

def getNeighbours(inElement, multiCatFilter, multiClassFilter, exclusionFilter):
	inElementBBox = inElement.get_BoundingBox(doc.ActiveView)
	inElementOutline = DB.Outline(inElementBBox.Min, inElementBBox.Max)
	bboxIntersectingFilter = DB.BoundingBoxIntersectsFilter(inElementOutline)
	selfElementExclusionFilter = DB.ExclusionFilter(Clist[DB.ElementId]([inElement.Id]))
	
	insideElementsMulitCatIdsCol = DB.FilteredElementCollector(doc) \
									.WherePasses(multiCatFilter) \
									.WherePasses(exclusionFilter) \
									.WherePasses(bboxIntersectingFilter) \
									.WherePasses(selfElementExclusionFilter) \
									.WhereElementIsNotElementType() \
									.ToElementIds()
	insideElementsMulitClassIdsCol = DB.FilteredElementCollector(doc) \
										.WherePasses(multiClassFilter) \
										.WherePasses(exclusionFilter) \
										.WherePasses(bboxIntersectingFilter) \
										.WherePasses(selfElementExclusionFilter) \
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
allExcludedIds = DB.FilteredElementCollector(doc).WherePasses(multiExclCategoryFilter).ToElementIds()
exclusionFilter = DB.ExclusionFilter(allExcludedIds)


print("allExcludedIds length {}".format(len(allExcludedIds)))
#uidoc.Selection.SetElementIds(allExcludedIds)
#input("waiting for enter...")

firstSelectionMultiCatIdsCol = DB.FilteredElementCollector(doc, __revit__.ActiveUIDocument.Selection.GetElementIds()) \
									.WherePasses(multiCatFilter) \
									.WherePasses(exclusionFilter) \
									.WhereElementIsNotElementType() \
									.ToElementIds()
firstSelectionMultiClassIdsCol = DB.FilteredElementCollector(doc, __revit__.ActiveUIDocument.Selection.GetElementIds()) \
									.WherePasses(multiClassFilter) \
									.WherePasses(exclusionFilter) \
									.WhereElementIsNotElementType() \
									.ToElementIds()
firstSelectionMultiCat = [doc.GetElement(elId) for elId in firstSelectionMultiCatIdsCol]
firstSelectionMultiClass = [doc.GetElement(elId) for elId in firstSelectionMultiClassIdsCol]
firstSelection = firstSelectionMultiCat + firstSelectionMultiClass
firstSelectionIdsCol = Clist[DB.ElementId]([x.Id for x in firstSelection])

selNeighbours = getNeighbours(firstSelection[0], multiCatFilter, multiClassFilter, exclusionFilter)
for i, neighbour in enumerate([doc.GetElement(x) for x in selNeighbours]):
	#print(neighbour)
	print("{0}-{1}-{2}".format(i, neighbour.Id, neighbour.Category.Name))
selNeighboursCol = Clist[DB.ElementId](selNeighbours + [firstSelection[0].Id])
t = DB.Transaction(doc, "Isolate neighbours")
t.Start()
uidoc.ActiveView.IsolateElementsTemporary(selNeighboursCol)
t.Commit()
#input("Waiting for keypress...")
