# -*- coding: utf-8 -*-
# Copyright(c) 2021, Daniel Gercak
#Revit Python Shell script for multiple joining elements
#selecting all associated ellements with selected level
#resource_path: https://github.com/Spaceific-Studio/_WORK/REVIT_API/test-getElementsAssociatedWithLevel.py
import sys
""" if "IronPython" in sys.prefix:
	pytPath = r'C:\Program Files (x86)\IronPython 2.7\Lib'
	sys.path.append(pytPath) """
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
	    #import Autodesk
	    #import System
	    #import threading
	    #import System.Drawing
	    import clr
	    clr.AddReferenceByPartialName('System.Windows.Forms')
	    clr.AddReference("System.Drawing")
	    clr.AddReference("System.Collections")
	    #clr.AddReference('System')
	    #import System.Windows.Forms
	    #from System.Threading import ThreadStart, Thread
	    from System.Windows.Forms import *
	    from System.Drawing import *
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
	    doc = DocumentManager.Instance.CurrentDBDocument

# clr.AddReference("RevitAPI")
# import Autodesk
# import Autodesk.Revit.DB as DB

""" try:
	import Autodesk
	sys.modules['Autodesk']
	hasAutodesk = True	
except:
	hasAutodesk = False 
print("module : {0} ; hasMainAttr = {1}".format(__file__, hasMainAttr))
print("module : {0} ; hasAutodesk = {1}".format(__file__, hasAutodesk)) """

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
    print("PythonLibPath was added")

sys.path.append(libPath)
sys.path.append(pythLibPath)

from RevitSelection import getBuiltInParameterInstance


class InfoDialog(Form):
	def __init__(self, inWarningText):
		self.scriptDir = "\\".join(__file__.split("\\")[:-1])
		print(self.scriptDir)
		iconFilename = os.path.join(self.scriptDir, 'LIB\\spaceific_64x64_sat_X9M_icon.ico')
		icon = Icon(iconFilename)
		self.Icon = icon	

		self.warningText = inWarningText
		self.confirmed = False
		self.InitializeComponent()

	def InitializeComponent(self):
		self.Text = "selection of elements associated with selected level by Spaceific-Studio"
		self.Width = 500
		self.Height = 140
		self.StartPosition = FormStartPosition.CenterScreen
		self.TopMost = True
		screenSize = Screen.GetWorkingArea(self)
		#self.Height = screenSize.Height / 5
		#self.Width = screenSize.Width / 3
		self.panelHeight = self.ClientRectangle.Height * 0.75
		self.panelWidth = self.ClientRectangle.Width
		self.bgColor = Color.CadetBlue
		self.textColor = Color.White

		self.setupPanel()
	
	def setupPanel(self):
	
		self.buttonPanel = Panel()
		self.buttonPanel.Dock = DockStyle.Top
		self.buttonPanel.AutoSize = True
		self.buttonPanel.Name = "Button Panel"
		self.buttonPanel.Height = 60
		self.buttonPanel.AutoSizeMode = AutoSizeMode.GrowAndShrink
		self.buttonPanel.AutoScroll = False
		self.buttonPanel.BackColor = Color.White
		#self.buttonPanel.Anchor = (AnchorStyles.Bottom | AnchorStyles.Left | AnchorStyles.Right)
		#self.buttonPanel.ControlAdded += self.control_Added 
		
		self.Controls.Add(self.buttonPanel)

		self.infoLabel = Label()
		self.infoLabel.Width = self.panelWidth
		self.infoLabel.Height = 30
		self.infoLabel.TextAlign = ContentAlignment.MiddleCenter
		self.infoLabel.Text = self.warningText
		self.infoLabel.Location = Point(0,10)
		self.buttonPanel.Controls.Add(self.infoLabel)

		self.confirmButton = Button()
		self.confirmButton.Text = "OK"
		self.confirmButton.Name = "confirmButton"
		self.confirmButton.Height = 30
		self.confirmButton.Width = self.buttonPanel.Width
		self.confirmButton.Click += self.closeDialog
		self.confirmButton.Location = Point(0,60)
		#self.confirmButton.AutoSize = True
		#self.confirmButton.Dock = DockStyle.Top
		#self.confirmButton.Anchor = (AnchorStyles.Top | AnchorStyles.Left)
		self.buttonPanel.Controls.Add(self.confirmButton)

	def closeDialog(self, sender, event):
		
		self.confirmed = True
		if sender.Name =="confirmButton":
			#pass
			#priorityLookup = self.priorityLookup
			print("self.OpenForms {}".format(list(Application.OpenForms)))
			self.rpsOutput = list(Application.OpenForms)[0]
			currentForm = list(Application.OpenForms)[-1]
			print("currentForm.__class__.__name__ {}".format(currentForm.__class__.__name__))
			#self.rpsOutput.Hide()
			self.Close()
			#self.rpsOutput.TopMost = True
			#Application.Exit()

selIds = list(__revit__.ActiveUIDocument.Selection.GetElementIds())
if len(selIds) > 0:
	doc = __revit__.ActiveUIDocument.Document
	selectedElement = doc.GetElement(selIds[0])
	#print(dir(selectedElement))
	print(selectedElement)
	bipLevelName = getBuiltInParameterInstance("DATUM_TEXT")

	bipLevelElev = getBuiltInParameterInstance("LEVEL_ELEV")
	bipLevelUpToLevel = getBuiltInParameterInstance("LEVEL_UP_TO_LEVEL")
	bipElemeCategoryParam = getBuiltInParameterInstance("ELEM_CATEGORY_PARAM")
	print("bipLevelElev {}".format(bipLevelElev))
	paramId = DB.ElementId(bipLevelElev)
	print("paramId {}".format(paramId))

	for i, param in enumerate(selectedElement.Parameters):
		print("{0} - {1}\n parameter type {2}\n storageType {3}\n id {4}\n hasValue {5}\n builtInParam {6}\n".format(i, \
																					param.Definition.Name, \
																					param.Definition.ParameterType, \
																					param.StorageType, \
																					param.Id, \
																					param.HasValue, \
																					param.Definition.BuiltInParameter)) 

	""" hasInternalElement = True if hasattr(selectedElement, "InternalElement") else False
	print("hasInternalElement {}".format(hasInternalElement))
	internalElement = selectedElement.InternalElement if hasattr(selectedElement, "InternalElement") else None
	print("internalElement {}".format(internalElement))

	hasElement = True if hasattr(selectedElement, "Element") else False
	print("hasElement {}".format(hasElement))
	internalElement = selectedElement.Element if hasattr(selectedElement, "Element") else None
	print("internalElement {}".format(internalElement)) """

	if isinstance(selectedElement, DB.Level):
		paramProv = DB.ParameterValueProvider(paramId) if paramId else None
		print("paramProvider {}".format(paramProv))
		isString = paramProv.IsStringValueSupported(selectedElement)
		print("isString {}".format(isString))
		isElementId = paramProv.IsElementIdValueSupported(selectedElement)
		print("IsElementId {}".format(isElementId))
		isInteger = paramProv.IsIntegerValueSupported(selectedElement)
		print("isInteger {}".format(isInteger))
		isDouble = paramProv.IsDoubleValueSupported(selectedElement)
		print("isDouble {}".format(isDouble))
		globalParamValue = paramProv.GetAssociatedGlobalParameterValue(selectedElement)
		print("globalParamValue {}".format(globalParamValue))
		


		#levelNameElementParamId = paramProv.GetElementIdValue(selectedElement)
		#levelNameParam = paramProv.GetStringValue(selectedElement)
		
		print("Selected Level - {0}".format(selectedElement.Name))

		#print bipLevelElev
		if isDouble:
			levelElevParamDouble = selectedElement.Parameter[bipLevelElev].AsDouble()
			levelElevParamDoubleConverted = DB.UnitUtils.ConvertFromInternalUnits(levelElevParamDouble, selectedElement.Parameter[bipLevelElev].DisplayUnitType)
			print("Selected Level elevation - {0}".format(levelElevParamDoubleConverted))

		#print bipLevelName
		levelNameParamString = selectedElement.Parameter[bipLevelName].AsString()
		print("Selected Level Name - {0}".format(levelNameParamString))

		#bipLevelUpToLevel
		levelUpToLevelParamElementId = selectedElement.Parameter[bipLevelUpToLevel].AsElementId()
		levelUpToLevelParamElementToBelong = selectedElement.Parameter[bipLevelUpToLevel].Element.Name
		print("Level Above Id - {0}".format(levelUpToLevelParamElementId if levelUpToLevelParamElementId else None))
		levelUpToLevelParamElement = doc.GetElement(levelUpToLevelParamElementId) if levelUpToLevelParamElementId else None
		print("Level Above - {0}".format(levelUpToLevelParamElement if levelUpToLevelParamElement else None))
		print("Level Above 2- {0}".format(levelUpToLevelParamElementToBelong if levelUpToLevelParamElementToBelong else None))

		# print bipElemeCategoryParam
		elementCategoryParamElementId = selectedElement.Parameter[bipElemeCategoryParam].AsElementId()
		ppElementCategoryParam = DB.ParameterValueProvider(elementCategoryParamElementId)
		print("ppElementCategoryParam  {0}".format(ppElementCategoryParam  if ppElementCategoryParam else None))
		#strValue = ppElementCategoryParam.GetStringValue(selectedElement)
		print("ppElementCategoryParam  IsElementIdValueSupported {0}".format(ppElementCategoryParam.IsElementIdValueSupported(selectedElement)))
		print("Element category parameter Id {0}".format(elementCategoryParamElementId if elementCategoryParamElementId else None))
		elementCategoryParamElement = doc.GetElement(elementCategoryParamElementId)
		print("Element category parameter Element {0}".format(elementCategoryParamElement if elementCategoryParamElement else None))
		print("Element category {0}".format(elementCategoryParamElement if elementCategoryParamElement else None))

		selectedIdsCol = DB.FilteredElementCollector(doc).WherePasses(DB.ElementLevelFilter(selectedElement.Id)).ToElementIds()
		filteredElements = list(selectedIdsCol)
		print(filteredElements)
		if hasattr(filteredElements, "__iter__"):
			for i, v in enumerate(filteredElements):
				print("{0} - {1}".format(i, v.ToString()))
			#selectedIdsCol = Clist[DB.ElementId](self.selectedIds)			
			if selectedIdsCol:
				myDialogWindow = InfoDialog("Click OK to select elements associated with selected level {0} : {1}".format(selectedElement.Name, levelElevParamDoubleConverted))
				Application.Run(myDialogWindow)
				uidoc.Selection.SetElementIds(selectedIdsCol)
				uidoc.ShowElements(selectedIdsCol)
			else:
				myDialogWindow = InfoDialog("No elements are associated with level {0} : {1}".format(selectedElement.Name, levelElevParamDoubleConverted))
				Application.Run(myDialogWindow)
				uidoc.Selection.SetElementIds(Clist[DB.ElementId]([]))
	else:
		myDialogWindow = InfoDialog("Selected element is not of type Autodesk.Revit.DB.Level")
		Application.Run(myDialogWindow)
else:
	myDialogWindow = InfoDialog("You must select Level element")
	Application.Run(myDialogWindow)

