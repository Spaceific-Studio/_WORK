# -*- coding: utf-8 -*-
# Copyright(c) 2021, Daniel Gercak
#Revit IronPython script for testing Taskbar from C# evnironment
#resource_path: https://github.com/Spaceific-Studio/_WORK/REVIT_API/runTaskbar.py

import clr
clr.AddReference("RevitAPI")
import Autodesk
import Autodesk.Revit.DB as DB
clr.AddReference('RevitAPIUI')	
import Autodesk.Revit.UI as UI

UI.TaskDialog.Show("From IronPython", "This is taskdialog executed from IronPython !!! Great !!!")
