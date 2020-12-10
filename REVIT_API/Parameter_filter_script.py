"""Returns list of filtered elements by ElementParameterFilter"""

__title__ = "Element\nparameter\nfilter"
__author__ = "Daniel Gercak"

from pyrevit.coreutils import Timer
timer = Timer()

import Autodesk.Revit.DB as DB
#  Creating collector instance and collecting all the walls from the model
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

param_ID = DB.ElementId(DB.BuiltInParameter.WALL_USER_HEIGHT_PARAM)
paramCat = DB.Category.GetCategory(doc, param_ID)
param_provider = DB.ParameterValueProvider(param_ID)

filterEvaluator = DB.FilterNumericEquals()

#height in display units
heigthDU = 10000.0

#heigth in internal units
heigthIU = DB.UnitUtils.ConvertToInternalUnits(heigthDU, DB.DisplayUnitType.DUT_MILLIMETERS)

print ("required height in internal units {0} - and in display units - {1}".format(heigthIU, heigthDU))

height_value_rule = DB.FilterDoubleRule(param_provider, \
										filterEvaluator, \
										heigthIU, \
										1E-6)
										
param_filter = DB.ElementParameterFilter(height_value_rule)

wall_collector_ids = DB.FilteredElementCollector(doc).WherePasses(param_filter).ToElementIds()
wall_collector = DB.FilteredElementCollector(doc).WherePasses(param_filter).ToElements()
print ("parameter ID - {0} - {1} - category {2}".format(param_ID, param_provider.GetAssociatedGlobalParameterValue(wall_collector[0]), paramCat ))
for i, el in enumerate(wall_collector):
	elementID = el.Id
	print ("category - {0} - id - {1} - elementID - {2}".format(el.Category.Name ,elementID, wall_collector_ids[i]))
uidoc.Selection.SetElementIds(wall_collector_ids)

endTime = timer.get_time()
print("selection time {0:6}".format(endTime))
