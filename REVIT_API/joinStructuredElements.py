# -*- coding: utf-8 -*-
# Copyright(c) 2020, Daniel Gercak
#Classes for organizing elements in space and for space analases
#e.g. kD_Trees...
#resource_path: https://github.com/Spaceific-Arch/_WORK/REVIT_API/joinStructuredElements.py
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
	    doc = __revit__.ActiveUIDocument.Document
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

sys.path.append(libPath)

from Errors import *

""" Errors.catchVar(sys.platform, "sys.platform")
Errors.catchVar(sys.prefix, "sys.prefix")
Errors.catchVar(os.name, "os.name")
Errors.catchVar(platform.sys, "platform.sys")
Errors.catchVar(platform.os, "platform.os")
Errors.catchVar(platform.platform(), "platform.platform()") """

import SpaceOrganize

structuredElements = IN[0]
bPoints = []
#TransactionManager.Instance.EnsureInTransaction(doc)
#t = DB.SubTransaction(doc)

# Begin new transaction
#t.Start()
for i, el in enumerate(list(structuredElements[1])):
	#raise TypeError("{0}".format(type(DB.ElementId(el.Id))))
	#Errors.catchVar(el.Id, "{1} el.Id - {0}".format(el.Id, i))
	docEl = doc.GetElement(DB.ElementId(el.Id))
	# Get the Bounding Box of the selected element.
	el_bb = docEl.get_BoundingBox(doc.ActiveView)
	#Errors.catchVar(el_bb, "{1} dir(el.Geometry) - {0}".format(dir(el.Geometry[options]), i))
	#Errors.catchVar(el_bb.Max.X, "{1} el_bb.Max.X - {0}".format(el_bb.Max.X, i))
	bPoint = ((el_bb.Max.X - el_bb.Min.X) / 2.0, (el_bb.Max.Y - el_bb.Min.Y) / 2.0, (el_bb.Max.Z - el_bb.Min.Z) / 2.0)
	bPoints.append(bPoint)

# Close the transaction
#t.Commit()
#TransactionManager.Instance.TransactionTaskDone()

if Errors.hasError():
 	OUT = Errors.report
elif Errors.hasContent():
	OUT = Errors.getConntainerContent()
else:
	OUT = (structuredElements[1], bPoints)




