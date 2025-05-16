import clr
clr.AddReference("RevitAPI")
import Autodesk
import Autodesk.Revit.DB as DB

clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
doc = DocumentManager.Instance.CurrentDBDocument

def GetLevels():
	allLevels = DB.FilteredElementCollector(doc) \
				.OfCategory(DB.BuiltInCategory.OST_Levels) \
				.WhereElementIsNotElementType() \
				.ToElements()

	elevations = [i.Elevation for i in allLevels]
	sortedLevels = [x for (y,x) in sorted(zip(elevations,allLevels))]
	return sortedLevels

