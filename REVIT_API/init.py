# -*- coding: utf-8 -*-
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
import sys
#if "Windows" in platform.uname():
	#lib_path = r'H:/_WORK/PYTHON/LIB'
lib_path = r'H:/_WORK/PYTHON/LIB'
#else:
#	lib_path = r"/storage/18D4-6C41/PYTHON/LIB"
revitApiLibPath = r'H:/_WORK/PYTHON/REVIT_API/LIB'
sys.path.append(lib_path)
sys.path.append(revitApiLibPath)

import clr

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
selection = [doc.GetElement(elId) for elId in __revit__.ActiveUIDocument.Selection.GetElementIds()]

allElements = FilteredElementCollector(doc)
allElements.WherePasses(LogicalOrFilter(ElementIsElementTypeFilter(False), ElementIsElementTypeFilter(True)))
allElements.WhereElementIsNotElementType()
print("Number of elements in project {}".format(len(list(allElements))))
# viewIds = {}
# for i, el in enumerate(list(allElements)):
# 	if hasattr(el, "Category") and hasattr(el.Category, "Name"):
# 		if el.OwnerViewId.IntegerValue != -1:
# 			viewName = doc.GetElement(el.OwnerViewId).Name
# 			if viewName not in viewIds:
# 				viewIds[viewName] = el.OwnerViewId
# 			print("{4} - Category {0} ID {1} - Owner view ID {2} Owner view Name {3}".format(el.Category.Name, el.Id, el.OwnerViewId, viewName, i))
# 		else:
# 			print("{3} - Category {0} ID {1} - Owner view ID {2} Not owned by view".format(el.Category.Name, el.Id, el.OwnerViewId, i))
# 	else:
# 		print(el.Name)

# for name, myId in viewIds.items():
# 	print("{0} - {1}".format(myId, name))

if len(selection) > 0:
	el = selection[0]

