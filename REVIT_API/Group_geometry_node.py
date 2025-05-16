# -*- coding: utf-8 -*-
# Copyright(c) 2019, Daniel Gercak
#Script for selecting and grouping elements by levels and other parameters for dynamo 
#resource_path: H:\_WORK\PYTHON\REVIT_API\Group_geometry_node.py

import sys
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
lib_path = r'H:\_WORK\PYTHON\REVIT_API\LIB'
sys.path.append(pyt_path)
sys.path.append(lib_path)

# from itertools import chain, groupby
# from RevitSelection import *
# import RevitSelection as RevitSelection
# from ListUtils import *
# import ListUtils as ListUtils

from Analyse import *
from AnalyseForm import *
from Errors import *


clr.AddReference("System.Windows.Forms")
clr.AddReference("System.Drawing")
import System.Drawing
import System.Windows.Forms
from System.Drawing import *
from System.Windows.Forms import Application, Button, Form, ComboBox, Label, TextBox, DockStyle, AnchorStyles, FormBorderStyle

# import clr
# Import Element wrapper extension methods
#clr.AddReference("RevitNodes")
#import Revit
#clr.ImportExtensions(Revit.Elements)
# Import geometry conversion extension methods
#clr.ImportExtensions(Revit.GeometryConversion)

# Import DocumentManager and TransactionManager
# clr.AddReference("RevitServices")
# import RevitServices
# from RevitServices.Persistence import DocumentManager
# from RevitServices.Transactions import TransactionManager
# doc = DocumentManager.Instance.CurrentDBDocument

# clr.AddReference("System")
# from System.Collections.Generic import List as Clist
# import System

# Import RevitAPI
# clr.AddReference("RevitAPI")
# import Autodesk
# import Autodesk.Revit.DB
#import Autodesk.Revit.DB as DB

# clr.AddReference('RevitAPIUI')
# from Autodesk.Revit.UI.Selection import *

#clr.AddReference('DSCoreNodes')
#from DSCore import List, Solid

# clr.AddReference('ProtoGeometry')
# from Autodesk.DesignScript.Geometry import *

# def Unwrap(item, *args):
# 	return UnwrapElement(item)

# myUnwrappedElement = UnwrapElement(IN[0][0])
#myModel = RTD_model(doc, IN[0])


#myText = ""
# for k,v in System.__dict__.iteritems():
#  	myText += "{0} - {1}; \n".format(k,v)


# myText3 = ""
# k = [(k,v) for k,v in locals().items()]
# for x in k:
# 	myText3 += "{0} >>> {1} \n".format(*x)
# myText3List = myText3.split("\n")
# sortedList = sorted(myText3List)
# myOutput = sortedList

# myText3 = ""
# k = [(k,v) for k,v in vars(Autodesk.Revit.ApplicationServices.Application).items()]
# for x in k:
# 	myText3 += "{0} >>> {1} \n".format(*x)
# myText3List = myText3.split("\n")
# sortedList = sorted(myText3List)

energyAnalyseObject = EnAnalyse(doc, IN[0])
#2020_05_20 error check >>> Errors.catchVar(energyAnalyseObject.quantities, "energyAnalyseObject.quantities", front=True )

# <Run the form window
Application.EnableVisualStyles()
#2020_05_20 error check >>>appWindow = MainForm(energyAnalyseObject)
#2020_05_20 error check >>>appWindow.FormBorderStyle = FormBorderStyle.FixedSingle
#2020_05_20 error check >>>appWindow.TopMost = True
#2020_05_20 error check >>>appWindow.BackColor = Color.White


#2020_05_20 error check >>>Application.Run(appWindow)
# Run the form window> '''
"""

myOutput = (	"{}".format(appWindow.quantities), \
				energyAnalyseObject.model.unwrappedElements, \
				energyAnalyseObject.outerShellIntersectingSurfaces , \
				energyAnalyseObject.intersectedElements, \
				energyAnalyseObject.myQuantities, \
				energyAnalyseObject.modelMaterials, \
				energyAnalyseObject.outerShellPolysurfaces, \
				energyAnalyseObject.dynamoOpenings, \
				energyAnalyseObject.unitedSolidWithOpenings, \
				energyAnalyseObject.rawOuterShellAreas, \
				energyAnalyseObject.facesArea, \
				energyAnalyseObject.averageHeatTransferCoefficient, \
				energyAnalyseObject.dynamoSolids, \
				energyAnalyseObject.revitElements, \
				energyAnalyseObject.model.openings, \
				energyAnalyseObject.model.openingsFills \
				 )
"""
#myQuantities = energyAnalyseObject.myQuantities

# myOutput = (energyAnalyseObject.outerShellIntersectingElements, \
# 			energyAnalyseObject.myAreas, \
# 			energyAnalyseObject.averageHeatTransferCoefficient
# 			)
#myOutput = [energyAnalyseObject.extractedOpenings, energyAnalyseObject.dynamoSolidsWithOpenings, myQuantities, energyAnalyseObject.outerShellIntersectingElements, energyAnalyseObject.outerShellIntersectingElementsWithOpenings]
# myOutput = (	energyAnalyseObject.model.unwrappedElements, \
# 				energyAnalyseObject.outerShellIntersectingSurfaces , \
# 				energyAnalyseObject.intersectedElements, \
# 				energyAnalyseObject.myQuantities, \
# 				energyAnalyseObject.outerShellIntersectingSurfacesWithOpenings, \
# 				energyAnalyseObject.outerShellIntersectingOpenings )

"""
myOutput = (
				energyAnalyseObject.model.unwrappedElements, \
				energyAnalyseObject.dynamoOpenings, \
				energyAnalyseObject.dynamoSolids, \
				energyAnalyseObject.revitElements, \
				energyAnalyseObject.model.openings, \
				energyAnalyseObject.model.openingFills \
				)


myOutput = (energyAnalyseObject.model.unwrappedElements, \
			energyAnalyseObject.model.openings, \
			energyAnalyseObject.model.openingFills, \
			energyAnalyseObject.model.dynamoSolids, \
			energyAnalyseObject.model.dynamoSolidsWithOpenings, \
			energyAnalyseObject.model.dynamoOpeningSolids, \
			energyAnalyseObject.model.outerShells, \
			energyAnalyseObject.model.unitedSolidWithOpenings, \
			energyAnalyseObject.model.outerShellPolysurfaces, \
			energyAnalyseObject.model.rawOuterShellAreas, \
			energyAnalyseObject.model.outerShellIntersectingSurfaces, \
			energyAnalyseObject.quantities, \
			energyAnalyseObject.overalAreaOfEnvelopeSurfaces, \
			energyAnalyseObject.openingsArea, \
			energyAnalyseObject.nonTransparentConstructionArea, \
			energyAnalyseObject.curtainWallsArea, \
			energyAnalyseObject.overalAreaOfEnvelope, \
			energyAnalyseObject.check)
"""
""" myOutput = (	energyAnalyseObject.model.unwrappedElements, \
				energyAnalyseObject.model.outerShellPolysurfaces, \
				energyAnalyseObject.model.openedOuterShellPolysurfaces, \
				energyAnalyseObject.model.closedOuterShellPolysurfaces, \
				energyAnalyseObject.model.outerShellIntersectingSurfaces,\
				energyAnalyseObject.model.outerShellIntersectingSurfacesAreaSums ,\
			) """


if Errors.hasError():
 	OUT = Errors.report
elif Errors.hasContent():
	OUT = Errors.getConntainerContent()
else:
	OUT = myOutput