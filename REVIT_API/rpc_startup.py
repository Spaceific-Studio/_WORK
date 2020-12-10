# script that is run when Revit starts in the IExternalApplication.Startup event.

import sys 
# import subprocess

lib_path = r'H:\_WORK\PYTHON\REVIT_API\LIB'
# startUp_path = r'H:\_WORK\PYTHON\REVIT_API\LIB\Startup'
sys.path.append(lib_path)
# sys.path.append(startUp_path)

# import clr
# clr.AddReference("System.Windows.Forms")
# clr.AddReference("System.Drawing")
# import System.Drawing
# import System.Windows.Forms
# from System.Drawing import *
# from System.Windows.Forms import Application, Button, Form, ComboBox, Label, TextBox, DockStyle, AnchorStyles
# Import RevitAPI
# clr.AddReference("RevitAPI")
# import Autodesk.Revit.ApplicationServices as revit
from Startup import *

startup = RunStartup(__revit__)
startup.run()


