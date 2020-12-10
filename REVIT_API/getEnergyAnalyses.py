# -*- coding: utf-8 -*-
# Copyright(c) 2020, Daniel Gercak
#Script for selecting and grouping elements by levels and other parameters for dynamo 
#resource_path: H:\_WORK\PYTHON\REVIT_API\getEnergyAnalyses.py

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



energyAnalyseObject = EnAnalyse(doc, IN[0])
#Errors.catchVar(energyAnalyseObject.quantities, "energyAnalyseObject.quantities", front=True )

# <Run the form window
Application.EnableVisualStyles()
appWindow = MainForm(energyAnalyseObject)
appWindow.FormBorderStyle = FormBorderStyle.FixedSingle
appWindow.TopMost = True
appWindow.BackColor = Color.White


Application.Run(appWindow)

myOutput = "Vážení pŕátelé ANO"

if Errors.hasError():
 	OUT = Errors.report
# elif Errors.hasContent():
# 	OUT = Errors.getConntainerContent()
else:
	OUT = myOutput