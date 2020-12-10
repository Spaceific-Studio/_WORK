from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory
#  Creating collector instance and collecting all the walls from the model
wall_collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsNotElementType()

# Iterate over wall and collect Volume data
total_volume = 0.0

# Get all properties of wall
for wall in wall_collector:
	param_set = wall.GetOrderedParameters()
	for param in list(param_set):
		print ("ParamName - {name}; unitType - {unitType}".format(name=param.Definition.Name, unitType=param.Definition.UnitType))
	print ("-----------")		
