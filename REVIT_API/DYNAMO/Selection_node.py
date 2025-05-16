# Povolit podporu Python a načíst knihovnu DesignScript
import clr
clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *

clr.AddReference("RevitAPI")
import Autodesk
import Autodesk.Revit.DB

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

# Vstupní údaje k tomuto uzlu budou uloženy jako seznam proměnných IN.
curtainWall = UnwrapElement(IN[1])

elementsRef = ReferenceArray()
a = []
opt = Options()
opt.ComputeReferences = True
opt.IncludeNonVisibleObjects = True
opt.View = doc.ActiveView

for obj in curtainWall.get_Geometry(opt):
	a.append(obj)
# Umístit kód pod tento řádek

# Přiřaďte výstup k proměnné OUT.
OUT = a