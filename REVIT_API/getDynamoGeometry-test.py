# Povolit podporu Python a načíst knihovnu DesignScript
import clr
clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *

import sys
#import traceback
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
lib_path = r'H:\_WORK\PYTHON\REVIT_API\LIB'
sys.path.append(pyt_path)
sys.path.append(lib_path)

import ListUtils as ListUtils
from Errors import * 

clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
doc = DocumentManager.Instance.CurrentDBDocument

from RevitSelection import *
import RevitSelection as RevitSelection
clr.AddReference('RevitNodes')
import Revit
clr.ImportExtensions(Revit.GeometryConversion)
from Revit import GeometryConversion as gp
clr.ImportExtensions(Revit.Graphics)
text = "{}".format(dir(Revit.GeometryConversion))

clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *

# Vstupní údaje k tomuto uzlu budou uloženy jako seznam proměnných IN.
dataEnteringNode = IN
#inElements = IN[0] if isinstance(IN[0], list) else [IN[0]]
windowsCgs = [Autodesk.Revit.DB.BuiltInCategory.OST_Windows]
windows = list(RevitSelection.getElementByCategory(windowsCgs))
doorsCgs = [Autodesk.Revit.DB.BuiltInCategory.OST_Doors]
doors = list(RevitSelection.getElementByCategory(doorsCgs))
oneWindow = windows[-2]
element = UnwrapElement(oneWindow)
gopt = Options()
geo1 = element.get_Geometry(gopt)
enum1 = geo1.GetEnumerator()
geos = []
geosNot3D = []
geosOther = []
while enum1.MoveNext():
	geos2 = []
	geo2 = enum1.Current.GetInstanceGeometry()
	geosNot3d2 = []
	geosOther2 = []
	for g in geo2:
		if hasattr(g, "Volume"):
			if g.Volume > 0:
				solid = g.Convert()
				geos2.append(solid)
			else:
				geosNot3d2.append(g)
		else:
			geosOther2.append(g.ToProtoType()) if hasattr(g, "ToProtoType") else geosOther2.append(g)
	geos.append(geos2)
	geosNot3D.append(geosNot3d2)
	geosOther.append(geosOther2)

def getDynamoGeometry(inElement, *args, **kwargs):
	"""
		get dynamo geometry from revit element

		inElement: type: Autodesk.Revit.DB.Element
		kwargs['only3D'] type: bool - returns only solid objects if true, else returns also 2D geometry, default = True
		kwargs['united'] type: bool - returns united solid of all solids in element if True, else returns separated geometry, default = True
		Returns: list[Autodesk.DesignScript.Geometry.Solid, ...] if only3D == True, else returns 
					tuple(list[Autodesk.DesignScript.Geometry.Solid] - all 3D solids,
						  list[Autodesk.DesignScript.Geometry.Solid] - Solids with zero Volume, 
						  list[Autodesk.DesignScript.Geometry...], other geometry)
		"""
	only3D = kwargs['only3D'] if 'only3D' in kwargs else True
	united = kwargs['united'] if 'united' in kwargs else True
	gopt = Options()	
	element = UnwrapElement(inElement)		
	geo1 = element.get_Geometry(gopt)
	enum1 = geo1.GetEnumerator()
	geos = []
	geosNot3D = []
	geosOther = []
	unitedSolid = None
	first = True
	while enum1.MoveNext():
		geos2 = []
		geo2 = enum1.Current.GetInstanceGeometry()
		geosNot3d2 = []
		geosOther2 = []
		for i, g in enumerate(geo2):
			if hasattr(g, "Volume"):
				if g.Volume > 0:
					solid = g.Convert()
					if united:
						if first:
							unitedSolid = solid
							first = False
						else:
							try:
								unitedSolid = Autodesk.DesignScript.Geometry.Solid.Union(unitedSolid, solid)
							except Exception as ex:
								pass
								#Errors.catch(ex, "Unable to make union of solids in element {0} of geometry object {1}".format(inElement.Id.IntegerValue, i))
					else:
						geos2.append(solid)
				else:
					geosNot3d2.append(g)
			else:
				geosOther2.append(g.ToProtoType()) if hasattr(g, "ToProtoType") else geosOther2.append(g)
		geos.append(geos2) if united == False else geos.append(unitedSolid)
		geosNot3D.append(geosNot3d2)
		geosOther.append(geosOther2)
	if only3D:
		return ListUtils.flatList(geos)
	else:
		return (geos, geosNot3D, geosOther) 

#uwWindows = [x.Geometry.ToProtoType() for x in windows]
#phases = doc.Phases

#phase = phases[phases.Size - 1]

#fwindows = []
#for window in windows:
#	froom = window.FromRoom[phase]
#	troom = window.ToRoom[phase]
#	fwindows.append((froom,troom))
#    TaskDialog.Show("Revit","%s, %s" %(froom, troom))`

#inElements = windows
#output1 = []
#for el in inElements:
#	output1.append(el.Geometry())
	
#output2 = []
#for el in inElements:
#	el = UnwrapElement(el)
#	gopt = Options()
#	geo1 = el.get_Geometry(gopt)
#	enum1 = geo1.GetEnumerator()
#	enum1.MoveNext()
#	geo2 = enum1.Current.GetInstanceGeometry()
#	for g in geo2:
#		s1 = g.Convert()
#		if s1 != None:
#			output2.append(s1)
# Umístit kód pod tento řádek

# Přiřaďte výstup k proměnné OUT.
#OUT = ("{}".format(type(windows[0])), "{}".format(type(IN[0][0])))
#OUT = ("{}".format(dir(windows[0].Geometry)), "{}".format(dir(IN[0][0].Geometry)))
#OUT = ("{}".format(uwWindows[0].Geometry.__doc__), "{}".format(IN[0][0].Geometry.__doc__))
myOutput = (ListUtils.flatList(ListUtils.processList(getDynamoGeometry, windows)), ListUtils.processList(getDynamoGeometry, doors))
if Errors.hasError():
 	OUT = Errors.report
elif Errors.hasContent():
	OUT = Errors.getConntainerContent()
else:
	OUT = myOutput
