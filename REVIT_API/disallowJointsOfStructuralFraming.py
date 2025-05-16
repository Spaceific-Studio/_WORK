# -*- coding: utf-8 -*-
# Copyright(c) 2021, Daniel Gercak
#Revit Python Shell script to disallow joins for selected elements of structural framing
#Moves point cloud to point defined by XYZ() object and aplying rotation around Z axis 
#resource_path: https://github.com/Spaceific-Studio/_WORK/REVIT_API/disallowJointsOfStructuralFraming.py

#!!! Leave moveElement False If you don't want to move selected element only find out coordinates
import sys
if "IronPython" in sys.prefix:
	pytPath = r'C:\Program Files (x86)\IronPython 2.7\Lib'
	sys.path.append(pytPath)
import os
import platform
import time

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
	    import Autodesk
	    import System
	    #import threading
	    from System.Collections.Generic import List as Clist
	    #import System.Drawing
	    import clr
	    #clr.AddReferenceByPartialName('System.Windows.Forms')
	    #clr.AddReference("System.Drawing")
	    clr.AddReference('System')
	    #import System.Windows.Forms
	    #from System.Threading import ThreadStart, Thread
	    #from System.Windows.Forms import *
	    #from System.Drawing import *
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

import math

selIds = list(__revit__.ActiveUIDocument.Selection.GetElementIds())
doc = __revit__.ActiveUIDocument.Document
#element = doc.GetElement(selIds[0])
elements = [doc.GetElement(x) for x in selIds]
print(dir(elements[0]))
print(elements[0].Category.Name)

bic = System.Enum.GetValues(DB.BuiltInCategory)
#print(bic)

""" cats = {}
for i in bic:
	#print(type(i))
	try:
		cat = DB.Category.GetCategory(doc, i)
		print("bic - {0} - {1}".format(i, cat.Name if cat else i.ToString()))
		cats[cat.Name] = i
	except:
		cat = None """
sfBuiltInCategory = DB.BuiltInCategory.OST_StructuralFraming
sfCategory = DB.Category.GetCategory(doc, sfBuiltInCategory)
print("sfBuiltInCategory {0} sfCategory {1}".format(sfBuiltInCategory, sfCategory.Name))
""" 
for k,v in cats:
	print("{0} - {1}".format(k,v)) """
t = DB.Transaction(doc, 'Dissalowing joints')
t.Start()


for beam in elements:
	if isinstance(beam, Autodesk.Revit.DB.FamilyInstance) and beam.Category.Name ==  sfCategory.Name:
		print("beam {0} of {1} is familyInstance".format(beam.Id, beam.Category.Name))
		try:
			DB.Structure.StructuralFramingUtils.DisallowJoinAtEnd(beam,0)
			DB.Structure.StructuralFramingUtils.DisallowJoinAtEnd(beam,1)
			print("Joints have been disallowed")
		except:
			print("Couldn't dissalowe joints")
			print("Traceback content >> \n {0}".format(sys.exc_info()))
			
t.Commit()
