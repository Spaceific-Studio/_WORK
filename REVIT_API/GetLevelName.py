import Autodesk.Revit.DB as DB

levelElements = DB.FilteredElementCollector(doc) \
				 .OfCategory(DB.BuiltInCategory \
				 .OST_Levels) \
				 .WhereElementIsNotElementType() \
				 .ToElements()
levelIdNames = {}
for level in levelElements:
	levelIdNames.update({str(level.Id) : level.Name})
#levelIdNames = zip()

print ("list of documents Level Ids an names:")
for k,v in levelIdNames.items():
	print ("Level ID - {0} ; Level Name - {1}".format(k,v))
	
print len(selection)
if len(selection) > 1:
	print ("you have selected more than one element")
	for element in selection:
		levelId = element.LevelId
		if int(levelId.ToString()) != -1:
			levelName = levelIdNames[str(levelId)]
		else:
			levelName = "Level Unassigned"
		elementId = element.Id
		elementCategory = element.Category
		elementName = element.Name
		print ("Element ID - {0} ; Element Category - {1} ; Element Name - {2} ; level ID - {3} ; Level Name - {4}".format(elementId, elementCategory, elementName, levelId, levelName))
else:
	print ("you have selected only one element")
	levelId = selection[0].LevelId
	print levelId
	


