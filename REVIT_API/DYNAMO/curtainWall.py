# Povolit podporu Python a načíst knihovnu DesignScript
import clr
clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *

clr.AddReference("RevitAPI")
import Autodesk
from Autodesk.Revit.DB import *

clr.AddReference("RevitNodes")
import Revit

clr.ImportExtensions(Revit.Elements)
#Import geometry conversion extension methods
clr.ImportExtensions(Revit.GeometryConversion)

clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
doc = DocumentManager.Instance.CurrentDBDocument

import sys
#import traceback
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
lib_path = r'C:\_WORK\PYTHON\REVIT_API\LIB'
sys.path.append(pyt_path)
sys.path.append(lib_path)

import ListUtils as ListUtils

# Vstupní údaje k tomuto uzlu budou uloženy jako seznam proměnných IN.
curtainSystem = UnwrapElement(IN[0][0])
curtainSystemType = UnwrapElement(IN[1][0])
curtainSystemLocation = curtainSystem.CurtainGrids.Size
curtainSystemGridsIterator = curtainSystem.CurtainGrids.ForwardIterator()
cells = []
for curtainGrid in curtainSystemGridsIterator:
	curtainSystemLoops = []
	for cell in curtainGrid.GetCurtainCells():
		curtainSystemLoops += [[y.ToProtoType() for y in x] for x in cell.CurveLoops]
	cells.append(curtainSystemLoops)
		

#curtainSystemLoops = []
#for cell in cells:
#	curtainSystemLoops += [[y.ToProtoType() for y in x] for x in cell.CurveLoops]

curtainWall = UnwrapElement(IN[2][0])
curtainWallGridCells = curtainWall.CurtainGrid.GetCurtainCells()
loops = []
for cell in curtainWallGridCells:
	loops += [[y.ToProtoType() for y in x] for x in cell.CurveLoops]


elementsRef = ReferenceArray()
a = []
opt = Options()
opt.ComputeReferences = True
opt.IncludeNonVisibleObjects = True
opt.View = doc.ActiveView

walls = list(FilteredElementCollector(doc).OfClass(Wall))
wallTypes = [x.WallType for x in walls]

geometry = 	curtainSystem.FindInserts(True,True,True,True)
for obj in curtainSystem.get_Geometry(opt):
	a.append((obj, obj.ToProtoType()))


result = a[-1]

def getCurtainWallSimplyfiedGeometry(inElement, **kwargs):
	thickness = kwargs["thickness"] if "thickness" in kwargs else 25
	if inElement.GetType().Name == "CurtainSystem":
		curtainSystemGridsIterator = curtainSystem.CurtainGrids.ForwardIterator()
		cells = []
		for curtainGrid in curtainSystemGridsIterator:
			curtainSystemSurfaces = []
			for cell in curtainGrid.GetCurtainCells():				
				curtainSystemSurfaces += [Autodesk.DesignScript.Geometry.Surface.ByPatch(Autodesk.DesignScript.Geometry.PolyCurve.ByJoinedCurves([y.ToProtoType() for y in x])) for x in cell.CurveLoops]
			cells += ListUtils.flatList(curtainSystemSurfaces)
		polySurface = Autodesk.DesignScript.Geometry.PolySurface.ByJoinedSurfaces(cells)
		solid = Autodesk.DesignScript.Geometry.Surface.Thicken(polySurface, thickness, False)
		return solid
	elif inElement.GetType().Name == "Wall":		
		curtainWallGridCells = inElement.CurtainGrid.GetCurtainCells()
		curtainSystemSurfaces = []
		for cell in curtainWallGridCells:				
			curtainSystemSurfaces += [Autodesk.DesignScript.Geometry.Surface.ByPatch(Autodesk.DesignScript.Geometry.PolyCurve.ByJoinedCurves([y.ToProtoType() for y in x])) for x in cell.CurveLoops]
		polySurface = Autodesk.DesignScript.Geometry.PolySurface.ByJoinedSurfaces(curtainSystemSurfaces)
		solid = Autodesk.DesignScript.Geometry.Surface.Thicken(polySurface, thickness, False)
		return solid
# Umístit kód pod tento řádek

geometry = getCurtainWallSimplyfiedGeometry(curtainWall, thickness=80)

# Přiřaďte výstup k proměnné OUT.Parameter.Definition.Name
OUT = geometry