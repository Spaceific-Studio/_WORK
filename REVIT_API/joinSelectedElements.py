# -*- coding: utf-8 -*-
# Copyright(c) 2020, Daniel Gercak
#Classes for organizing elements in space and for space analases
#e.g. kD_Trees...
#resource_path: https://github.com/Spaceific-Arch/_WORK/REVIT_API/joinStructuredElements.py
import sys
if "IronPython" in sys.prefix:
	pytPath = r'C:\Program Files (x86)\IronPython 2.7\Lib'
	sys.path.append(pytPath)
import os
import platform

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
	    doc = __revit__.ActiveUIDocument.Document
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
    libPath = r"H:/_WORK/PYTHON/REVIT_API/LIB"

if sys.platform.startswith('linux'):
    pythLibPath = r"/storage/emulated/0/_WORK/LIB"
elif sys.platform.startswith('win') or sys.platform.startswith('cli'):
    pythLibPath = r"H:/_WORK/PYTHON/LIB"

sys.path.append(libPath)
sys.path.append(pythLibPath)

from Errors import *

""" Errors.catchVar(sys.platform, "sys.platform")
Errors.catchVar(sys.prefix, "sys.prefix")
Errors.catchVar(os.name, "os.name")
Errors.catchVar(platform.sys, "platform.sys")
Errors.catchVar(platform.os, "platform.os")
Errors.catchVar(platform.platform(), "platform.platform()") """

import SpaceOrganize
import RevitSelection as RS
import ListUtils
import heapq

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document

def groupByDistance(inRevitElements):
	baseElement = inRevitElements[0]
	baseSolid = RS.getRevitGeometry(baseElement, asDynamoGeo = True)
	restElements = inRevitElements[1:]
	distanceOrdered = []
	for restElement in restElements:
		restSolid = RS.getRevitGeometry(restElement, asDynamoGeo = True)
		raise TypeError ("dir(Solid) {0}".format(dir(baseSolid)))
		dist = baseSolid.DistanceTo(restSolid)
		heappush(distanceOrdered, (dist, (restSolid, restElement)))
		
	return distanceOrdered

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



firstSelection = [doc.GetElement(elId) for elId in __revit__.ActiveUIDocument.Selection.GetElementIds()]

bPoints = []
bbs = []
intersectedElements = []
intersectedSolids = []
revitGeos = []
#TransactionManager.Instance.EnsureInTransaction(doc)
#t = DB.SubTransaction(doc)

# Begin new transaction
#t.Start()
#t = DB.Transaction(doc, "Select element to join with")
#t.Start()
secondSelection = doc.GetElement(pickobject("Select objects to join element with").ElementId)

#t.Commit()

if hasattr(secondSelection, "__iter__"):
	for i in secondSelection:
		print("You have selected {0} elements".format(len(secondSelection)))
else:
	print("You have selected 1 element {0}".format(secondSelection.Id))

t = DB.Transaction(doc, "Join selected elements")
t.Start()

for i, el in enumerate(firstSelection):
	print(el.Id)
	areJoined = DB.JoinGeometryUtils.AreElementsJoined(doc, el, secondSelection)
	if not areJoined:
		try:
			DB.JoinGeometryUtils.JoinGeometry(doc, el, secondSelection)
			print("element {0} is joined with element {1} - {2}".format(el.Id, secondSelection.Id, areJoined))
		except Exception as ex:
			import traceback
			print("element {0} was not joined with element {1} - {2}".format(el.Id, secondSelection.Id, areJoined))
			exc_info = sys.exc_info()
			traceback.print_exception(*exc_info)
			del exc_info
t.Commit()



"""
for i, el in enumerate(list(structuredElements[0])):
	
	#raise TypeError("{0}".format(type(DB.ElementId(el.Id))))
	#Errors.catchVar(el.Id, "{1} el.Id - {0}".format(el.Id, i))
	docEl = doc.GetElement(DB.ElementId(el.Id))
	try:
		revitGeo = RS.getRevitGeometry(el)
	except Exception as ex:
		Errors.catch(ex, "Error in getRevitGeo(docEl) dir(el){0}\ndir(docEl){1}".format(dir(el), dir(docEl)))
		revitGeo = None
	revitGeos.append(revitGeo)
	elIntFilter = 	DB.ElementIntersectsElementFilter(docEl)
	#reference = DB.Reference(docEl)
	#solid = docEl.GetGeometryObjectFromReference(reference)
	solidIntFilter = DB.ElementIntersectsSolidFilter(revitGeo)
	intElements = DB.FilteredElementCollector(doc).WherePasses(elIntFilter).WhereElementIsNotElementType().ToElements()
	intSolids = DB.FilteredElementCollector(doc).WherePasses(solidIntFilter).WhereElementIsNotElementType().ToElements()
	intersectedElements.append(intElements)
	intersectedSolids.append(intSolids)
	# Get the Bounding Box of the selected element.
	el_bb = docEl.get_BoundingBox(doc.ActiveView)
	bbs.append(docEl)
	#Errors.catchVar(el_bb, "{1} dir(el.Geometry) - {0}".format(dir(el.Geometry[options]), i))
	#Errors.catchVar(el_bb.Max.X, "{1} el_bb.Max.X - {0}".format(el_bb.Max.X, i))
	bPoint = ( \
				DB.UnitUtils.ConvertFromInternalUnits((el_bb.Max.X - el_bb.Min.X) / 2.0, DB.DisplayUnitType.DUT_MILLIMETERS), \
				DB.UnitUtils.ConvertFromInternalUnits((el_bb.Max.Y - el_bb.Min.Y) / 2.0, DB.DisplayUnitType.DUT_MILLIMETERS), \
				DB.UnitUtils.ConvertFromInternalUnits((el_bb.Max.Z - el_bb.Min.Z) / 2.0, DB.DisplayUnitType.DUT_MILLIMETERS) \
			)
	bPoints.append(bPoint)

# Close the transaction
#t.Commit()
#TransactionManager.Instance.TransactionTaskDone()

groupedByDistance = groupByDistance(list(structuredElements[0]))

if Errors.hasError():
 	OUT = Errors.report
elif Errors.hasContent():
	OUT = Errors.getConntainerContent()
else:
	OUT = (structuredElements[1], bPoints, bbs, intersectedElements, intersectedSolids, revitGeos, groupedByDistance) """




