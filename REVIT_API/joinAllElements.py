# -*- coding: utf-8 -*-
# Copyright(c) 2020, Daniel Gercak
#Revit Python Shell script for multiple joining elements
#joins all selected elements by brute force applying join to all pair combinations
#resource_path: https://github.com/Spaceific-Arch/_WORK/REVIT_API/joinAllElements.py
import sys
if "IronPython" in sys.prefix:
	pytPath = r'C:\Program Files (x86)\IronPython 2.7\Lib'
	sys.path.append(pytPath)
import os
import platform

try:
	sys.modules['__main__']
	hasMainAttr = True	
except:
	hasMainAttr = False

if hasMainAttr:
	#import clr
	if "pydroid" in sys.prefix:
	    pass
	elif "Python38" in sys.prefix:
	    pass
	else:
	    from Autodesk.Revit.UI.Selection import *
	    import Autodesk.Revit.DB as DB
	    import Autodesk.Revit.UI as UI
	    doc = __revit__.ActiveUIDocument.Document
	    uidoc = __revit__.ActiveUIDocument
	    #clr.AddReference("RevitServices")
	    #import RevitServices
	    #from RevitServices.Transactions import TransactionManager
	    pass

else:
	if "pydroid" in sys.prefix:
	    pass
	elif "Python38" in sys.prefix:
	    pass
	else:
	    import clr
	    clr.AddReference('ProtoGeometry')
	    from Autodesk.DesignScript.Geometry import *
	    clr.AddReference("RevitAPI")
	    import Autodesk
	    import Autodesk.Revit.DB as DB
	    clr.AddReference("RevitServices")
	    import RevitServices
	    from RevitServices.Persistence import DocumentManager
	    from RevitServices.Transactions import TransactionManager
	    doc = DocumentManager.Instance.CurrentDBDocument

# clr.AddReference("RevitAPI")
# import Autodesk
# import Autodesk.Revit.DB as DB

try:
	import Autodesk
	sys.modules['Autodesk']
	hasAutodesk = True	
except:
	hasAutodesk = False

print("module : {0} ; hasMainAttr = {1}".format(__file__, hasMainAttr))
print("module : {0} ; hasAutodesk = {1}".format(__file__, hasAutodesk))

if sys.platform.startswith('linux'):
    libPath = r"/storage/emulated/0/_WORK/REVIT_API/LIB"
elif sys.platform.startswith('win') or sys.platform.startswith('cli'):
    libPath = r"H:/_WORK/PYTHON/REVIT_API/LIB"

if sys.platform.startswith('linux'):
    pythLibPath = r"/storage/emulated/0/_WORK/LIB"
elif sys.platform.startswith('win') or sys.platform.startswith('cli'):
    pythLibPath = r"H:/_WORK/PYTHON/LIB"

sys.path.append(libPath)
sys.path.append(pythLibPath)

from Errors import *

""" Errors.catchVar(sys.platform, "sys.platform")
Errors.catchVar(sys.prefix, "sys.prefix")
Errors.catchVar(os.name, "os.name")
Errors.catchVar(platform.sys, "platform.sys")
Errors.catchVar(platform.os, "platform.os")
Errors.catchVar(platform.platform(), "platform.platform()") """

import SpaceOrganize
import RevitSelection as RS
import ListUtils
import heapq
from itertools import combinations

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document


def pickobjects(inStatus):
    __window__.Hide()
    picked = uidoc.Selection.PickElementsByRectangle(inStatus)
    __window__.Show()
    #__window__.Topmost = True
    return picked

def pickobject(inStatus):
    from Autodesk.Revit.UI.Selection import ObjectType
    __window__.Hide()
    picked = uidoc.Selection.PickObject(ObjectType.Element, inStatus)
    __window__.Show()
    #__window__.Topmost = True
    return picked



firstSelection = [doc.GetElement(elId) for elId in __revit__.ActiveUIDocument.Selection.GetElementIds()]
print("firstSelection len {0} - {1}".format(len(firstSelection), firstSelection))
selComb = list(combinations(firstSelection, 2))
#while next(selComb):
#    print("selComb \n{0}".format(selComb))
#print("selComb \n{0}".format(selComb))
print("selComb len {0} - {1}".format(len(selComb), selComb))

""" bPoints = []
bbs = []
intersectedElements = []
intersectedSolids = []
revitGeos = []
#TransactionManager.Instance.EnsureInTransaction(doc)
#t = DB.SubTransaction(doc)

# Begin new transaction
#t.Start()
#t = DB.Transaction(doc, "Select element to join with")
#t.Start()
secondSelection = doc.GetElement(pickobject("Select objects to join element with").ElementId)

#t.Commit()

if hasattr(secondSelection, "__iter__"):
	for i in secondSelection:
		print("You have selected {0} elements".format(len(secondSelection)))
else:
	print("You have selected 1 element {0}".format(secondSelection.Id))
"""
t = DB.Transaction(doc, "Join all selected elements")
t.Start()

for i, pair in enumerate(selComb):
	print("{0} - Element_0: {1} <> Element_1 {2}".format(i, pair[0].Id, pair[1].Id))
	areJoined = DB.JoinGeometryUtils.AreElementsJoined(doc, pair[0], pair[1])
	if not areJoined:
		try:
			DB.JoinGeometryUtils.JoinGeometry(doc, pair[0], pair[1])
			print("element {0} is joined with element {1} - areJoined > {2}".format(pair[0].Id, pair[1].Id, areJoined))
		except Exception as ex:
			import traceback
			print("ELEMENT {0} WAS NOT JOINED WITH ELEMENT {1} - {2}".format(pair[0].Id, pair[1].Id, areJoined))
			print("Traceback content >> \n {0}".format(sys.exc_info()))
			#exc_info = sys.exc_info()
			#traceback.print_exception(*exc_info)
			#del exc_info
t.Commit()