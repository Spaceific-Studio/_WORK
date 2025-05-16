import sys
import clr
from Autodesk.Revit.DB import *
clr.AddReference("System")
from System.Collections.Generic import List as Clist

pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
lib_path = r'C:\_WORK\PYTHON\REVIT_API\LIB'
sys.path.append(lib_path)
sys.path.append(pyt_path)
import ListUtils as ListUtils

# -*- coding: utf-8 -*-
from Autodesk.Revit.UI import *

import clr

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
selection = [doc.GetElement(elId) for elId in __revit__.ActiveUIDocument.Selection.GetElementIds()]

if len(selection) > 0:
	el = selection[0]


print(selection)

def getInserts(item, *args, **kwargs):
	"""returns inserts of element (Autodesk.Revit.DB.Element) if exist

		args:
			item: Autodesk.Revit.DB.Element
			incopenings: option for included openings - default = True
			incshadows = option for included shadows - default = True
			incwalls = option for included walls - default = True
			incshared = option for included shared element - default = True

		return: list[Autodesk.Revit.DB.Element, ...]
		"""
	incopenings = kwargs["incopenings"] if "incopenings" in kwargs else True
	incshadows = kwargs["incshadows"] if "incshadows" in kwargs else True
	incwalls = kwargs["incwalls"] if "incwalls" in kwargs else True
	incshared = kwargs["incshared"] if "incshared" in kwargs else True

	# Regular host objects
	if hasattr(item, "FindInserts"):
		return [item.Document.GetElement(x) for x in item.FindInserts(incopenings,incshadows,incwalls,incshared)]
	# Railings
	if hasattr(item, "GetAssociatedRailings"):
		return [item.Document.GetElement(x) for x in item.GetAssociatedRailings()]
	else: return []

if 0 == selection.Count:
	TaskDialog.Show("Revit","You haven't selected any elements.")
else:
	pass

myInserts = ListUtils.processList(getInserts, selection)
print(len(myInserts))
insertedElementsIds = []
for selectedElement in myInserts:
	for el in list(selectedElement):
		print("element ID: {0};\n element category: {1}".format(el.Id, el.Category.Name))
		insertedElementsIds.append(el.Id)
	
element_collection = Clist[ElementId](insertedElementsIds)

print("element_collection {0} type {1}".format(element_collection, type(element_collection)))

for elId in element_collection:
	print("elId {0}; type {1} ".format(elId, type(elId)))
	#myElement.append(__revit__.ActiveUIDocument.Document.GetElement)
#__window__.Close()

#transaction = Transaction(doc, "selection")
#transaction.Start()
uidoc.Selection.SetElementIds(element_collection)
#transaction.Commit()


