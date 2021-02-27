# -*- coding: utf-8 -*-
# Copyright(c) 2021, Daniel Gercak
#Revit Python Shell script to change join order of elements joined with current selected elements
#resource_path: https://github.com/Spaceific-Studio/_WORK/REVIT_API/changeOrderOfJoinedElements.py
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
	    from System.Collections.Generic import List as Clist
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
	    from System.Collections.Generic import List as Clist
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
    scriptDir = "\\".join(__file__.split("\\")[:-1])
    scriptDisk = __file__.split(":")[0]
    if scriptDisk == "B" or scriptDisk == "b":
        libPath = r"B:/Podpora Revit/Rodiny/141/_STAVEBNI/_REVITPYTHONSHELL/LIB"
    elif scriptDisk == "H" or scriptDisk == "h":
        libPath = r"H:/_WORK/PYTHON/REVIT_API/LIB"

if sys.platform.startswith('linux'):
    pythLibPath = r"/storage/emulated/0/_WORK/LIB"
elif sys.platform.startswith('win') or sys.platform.startswith('cli'):
    pythLibPath = r"H:/_WORK/PYTHON/LIB"

sys.path.append(libPath)
sys.path.append(pythLibPath)

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
print("firstSlection len - {0} - {1}".format(len(firstSelection), firstSelection))
# all elements connected with selected element
conElements = []
for selEl in firstSelection:
	# current connected elements
	conEls = DB.JoinGeometryUtils.GetJoinedElements(doc, selEl)
	conElements += list(conEls)
	print("conElements len - {0} - {1}".format(len(conElements), conElements))

print("Connected Elements of selected :")
t = DB.Transaction(doc, "Change join order")
t.Start()

for i, elId in enumerate(conElements):
	el = doc.GetElement(elId)
	for selEl in firstSelection:
		if DB.JoinGeometryUtils.AreElementsJoined(doc, el, selEl):
			try:
				DB.JoinGeometryUtils.SwitchJoinOrder(doc, el, selEl)
				print("{0} - {1} changed order with {2}".format(i, elId, selEl.Id))
			except Exception as ex:
				import traceback
				print("Traceback content >> \n {0}".format(sys.exc_info()))
				exc_info = sys.exc_info()
				traceback.print_exception(*exc_info)
				del exc_info
		

t.Commit()

elementsCol = Clist[DB.ElementId](conElements)
uidoc.Selection.SetElementIds(elementsCol)
	





