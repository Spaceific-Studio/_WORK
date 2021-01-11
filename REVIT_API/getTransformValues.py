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
	    clr.AddReference('RevitNodes')
	    import Revit
	    clr.ImportExtensions(Revit.Elements)
	    clr.ImportExtensions(Revit.GeometryConversion)
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

def toList(obj1):
	if hasattr(obj1, "__iter__"):
		return obj1
		""" if len(obj1) > 0:
			if hasattr(obj1[0], "__iter__"):
				return obj1[0]
			else:
				return [obj1[0]]
		else:
			return None """
	else:
		return [obj1]

def createCoordinateSystem(t):
	return Autodesk.DesignScript.Geometry.CoordinateSystem.ByOriginVectors(t.Origin.ToPoint(), t.BasisX.ToVector(), t.BasisY.ToVector(), t.BasisZ.ToVector())

def visualizeAxes(t, l):
	o = t.Origin.ToPoint()
	xAxis = Autodesk.DesignScript.Geometry.Line.ByStartPointDirectionLength(o, t.BasisX.ToVector(),l)
	yAxis = Autodesk.DesignScript.Geometry.Line.ByStartPointDirectionLength(o, t.BasisY.ToVector(),l)
	zAxis = Autodesk.DesignScript.Geometry.Line.ByStartPointDirectionLength(o, t.BasisZ.ToVector(),l)
	return xAxis, yAxis, zAxis

structuredElements = toList(IN[0])
#raise TypeError("len(structuredElements) {0} , len(IN[0]) {1}".format(len(structuredElements), len(IN[0])))
bPoints = []
bbs = []
intersectedElements = []
intersectedSolids = []
revitGeos = []
TransactionManager.Instance.EnsureInTransaction(doc)
t = DB.SubTransaction(doc)

# Begin new transaction
""" t.Start()
delels = []
for delel in structuredElements:
	delels.append(doc.Delete(DB.ElementId(delel.Id)))
t.RollBack() """

unwraped = ListUtils.processList(UnwrapElement, structuredElements)
opt = DB.Options()
opt.View = doc.ActiveView
#raise TypeError("{0}".format(type(DB.ElementId(el.Id))))
""" delEls = []
for delEl in delel:
	delEls.append(doc.GetElement(delEl)) """
#docEl = doc.GetElement(DB.ElementId(structuredElements.Id))
unwrapedGeom = ListUtils.processList(Autodesk.Revit.DB.Element.get_Geometry, unwraped, opt)
#dynamoGeom = unwrapedGeom.ToProtoType()
#unwrapedTrans = unwrapedGeom.GetTransformed()
unwrapedLocation = [x.Location for x in unwraped]
#Errors.catchVar(unwrapedLocation, "unwrapedLocation.__class__{0}".format(unwrapedLocation.GetType()))
unwrapedEnums = [geom.GetEnumerator() for geom in unwrapedGeom]
geos = []
for enum in unwrapedEnums:
	geos2 = []
	while enum.MoveNext():
		geo = None
		if hasattr(enum.Current, "GetInstanceGeometry"):
			geo = enum.Current.GetInstanceGeometry()
		geos2.append(geo)
	geos.append(geos2)
#docElemType = docEl.GetType()
#elemType = structuredElements.GetType()
""" transform = docEl.GetType().Geometry[opt].GetTransformed()
transformEnum = docEl.Geometry.GetEnumerator
geoms = []
for x in transformEnum:
	axis = (transform.BasisX, transform.BasisY. transform.BasisZ) """


# Close the transaction
#t.Commit()
TransactionManager.Instance.TransactionTaskDone()

elems = toList(UnwrapElement(IN[0]))
#elems = toList(IN[0])
l = 500

cSystems = []
vGeom = []

for e in elems:
	if hasattr(e, "GetTransform"):
		t = e.GetTransform()
		docElGeom = e.get_Geometry(opt)
	else:
		#docEl = doc.GetElement(e.Id)
		docEl = e #doc.GetElement(e.Id)
		docElGeom = docEl.get_Geometry(opt)
		docElGeomToDSTypeF = docEl.ToDSType(False)
		docElGeomToDSTypeT = docEl.ToDSType(True)
		t = docElGeom.GetBoundingBox().Transform
	
	#Errors.catchVar(t.Origin, "Transform.Origin {0}".format(t.Origin))
	cSystems.append(createCoordinateSystem(t))
	vGeom.append(visualizeAxes(t,l))


if Errors.hasError():
 	OUT = Errors.report
elif Errors.hasContent():
	OUT = Errors.getConntainerContent()
else:
	#OUT = (dir(docElemType), unwrapedGeom, geos,dir(unwrapedLocation), unwrapedLocation.GetType(), delel, delEls)
	#OUT = cSystems, vGeom
	#OUT = (elems[0], elems[0].ToDSType(False).Geometry(), "docElGeomToDSTypeF\n {0}\ndocElGeomToDSTypeF.Geometry {1}\n".format(dir(docElGeomToDSTypeF), "dir(docElGeomToDSTypeF.Geometry())\n {0}".format(dir(docElGeomToDSTypeF.Geometry())), docElGeomToDSTypeF.Geometry()), docElGeomToDSTypeF.Geometry, "docElGeomToDSTypeT\n {}".format(dir(docElGeomToDSTypeT)), "docElGeom\n {}".format(dir(docElGeom)), t.Origin)
	OUT = ([elem for elem in elems], [elem.ToDSType(False).Geometry() for elem in elems], "docElGeom\n {}".format(dir(docElGeom)), t.Origin)



