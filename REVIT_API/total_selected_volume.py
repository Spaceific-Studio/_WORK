"""Calculates total volume of all selected elements."""

__title__ = 'Total\nVolume'


from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, BuiltInParameter, UnitType, UnitUtils, DisplayUnitType

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
selection = [doc.GetElement(elId) for elId in __revit__.ActiveUIDocument.Selection.GetElementIds()]

# Creating collector instance and collecting all the walls from the model
wall_collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsNotElementType()


# Iterate over wall and collect Volume data
projectBasePt = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_ProjectBasePoint).ToElements()
bipEW = BuiltInParameter.BASEPOINT_EASTWEST_PARAM
PBeastWest = projectBasePt[0].get_Parameter(bipEW).AsDouble()

total_volume = 0.0
values = []
unitTypes = []
for el in selection:
	vol_param = el.Parameter[BuiltInParameter.HOST_VOLUME_COMPUTED]
	if vol_param:
		unitTypes.append(vol_param.DisplayUnitType)
		values.append((UnitUtils.ConvertFromInternalUnits(vol_param.AsDouble(), DisplayUnitType.DUT_CUBIC_METERS), el.Id))
		total_volume = total_volume + vol_param.AsDouble()

# now that results are collected, print the total
#docUnits = doc.GetUnits()
#displayUnits = docUnits.GetFormatOptions(UnitType.UT_Volume).DisplayUnits
unitConversion = UnitUtils.ConvertFromInternalUnits(total_volume, DisplayUnitType.DUT_CUBIC_METERS)
#print("docUnits {0}".format(docUnits))
#print("unitConversion {0}".format(unitConversion))
for i, v in enumerate(values):
	print("{pos} - {volume} - {id}".format(pos = i, volume = v[0], id = v[1]))
print("Number of all selected elements: {}".format(len(selection)))
print("Number of elements with volume parameter: {}".format(len(values)))
print("Total Volume is: {} m3".format(unitConversion))
#print(unitTypes)
