import Autodesk.Revit.DB
myFilter = FilteredElementCollector(doc)
elements = myFilter.OfCategory(BuiltInCategory.OST_ProjectInformation).ToElements()
print "Length of elements list: {0}".format(len(list(elements)))
print "Length of elements - GetElementCount(): {0}".format(myFilter.GetElementCount())
for element in elements:
	print element