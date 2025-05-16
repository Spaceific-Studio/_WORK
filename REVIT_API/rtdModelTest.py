# -*- coding: utf-8 -*-
# Copyright(c) 2020, Daniel Gercak
#Script for selecting and grouping elements by levels and other parameters for dynamo 
#resource_path: https://github.com/Spaceific-Studio/_WORK/REVIT_API/rtdModelTest.py

import sys
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
lib_path = r'H:\_WORK\PYTHON\REVIT_API\LIB'
sys.path.append(pyt_path)
sys.path.append(lib_path)

from Analyse import *
from AnalyseForm import *
from Errors import *

clr.AddReference("System.Windows.Forms")
clr.AddReference("System.Drawing")
import System.Drawing
import System.Windows.Forms
from System.Drawing import *
from System.Windows.Forms import Application, Button, Form, ComboBox, Label, TextBox, DockStyle, AnchorStyles, FormBorderStyle



rtdModel = IN[0]
#Errors.catchVar(energyAnalyseObject.quantities, "energyAnalyseObject.quantities", front=True )

# <Run the form window


myOutput = ( \
			rtdModel.structuredElements, \
			rtdModel.dynamoSolids, \
			rtdModel.dynamoSolidsWithOpenings, \
			rtdModel.unitedSolid \
			)
#myOutput = (rtdModel.structuredElements, rtdModel.dynamoSolids)
if Errors.hasError():
 	OUT = Errors.report
elif Errors.hasContent():
 	OUT = Errors.getConntainerContent()
else:
	OUT = myOutput