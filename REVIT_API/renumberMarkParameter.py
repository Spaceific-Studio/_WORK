# -*- coding: utf-8 -*-
# Copyright(c) 2020, Daniel Gercak
#Script for parameters update of family "Prostup (SWECO)"
#resource_path: H:\_WORK\PYTHON\REVIT_API\vyska_prostupu.py
#from typing import Type
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB.Architecture import *
#from Autodesk.Revit.DB.Analysis import *
from Autodesk.Revit.UI import *
from Autodesk.Revit.UI.Selection import *



import sys
from operator import attrgetter
from itertools import groupby
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)

import os

print("cwd: {}".format(os.getcwd()))

#searches for directory for library used by RevitPythonShell. Example h:\_WORK\PYTHON\REVIT_API\LIB\__init__.py
splittedFile = __file__.split("\\")
rpsFileDir = "\\".join(splittedFile[:-1]) if len(splittedFile) > 2 else ""
#rpsPyFilePath, rpsPyFileDNames, rpsPyFileFNames = walkDir(rpsFileDir)
rpsPyFilePath, rpsPyFileDNames, rpsPyFileFNames = next(os.walk(rpsFileDir))

#searches for library in Spaceific-Studio addin folder. Example: C:\users\CZDAGE\AppData\Roaming\Autodesk\Revit\Addins\2020\Spaceific-Studio\__init__.py
splittedFile = __file__.split("\\")
addinPyFileLibDir = "\\".join(splittedFile[:-2]) if len(splittedFile) > 2 else ""
#addinPyFileLibPath, addinPyFileDNames, addinPyFileFNames = walkDir(addinPyFileLibDir)
addinPyFileLibPath, addinPyFileDNames, addinPyFileFNames = next(os.walk(addinPyFileLibDir))

if "LIB" in rpsPyFileDNames:
	lib_path = os.path.join(rpsPyFilePath, "LIB")
elif "__init__.py" in addinPyFileFNames:
	lib_path = addinPyFileLibPath
else:
	lib_path = r'H:\_WORK\PYTHON\REVIT_API\LIB'
print("__file__: {}".format(__file__))
print("rpsFileDir: {}".format(rpsFileDir))
print("rpsPyFilePath: {}".format(rpsPyFilePath))
print("rpsPyFileDNames: {}".format(rpsPyFileDNames))
print("rpsPyFileFNames: {}".format(rpsPyFileFNames))
print("addinPyFileLibDir: {}".format(addinPyFileLibDir))
print("addinPyFileLibPath: {}".format(addinPyFileLibPath))
print("addinPyFileFNames: {}".format(addinPyFileFNames))
print("addinPyFileDNames: {}".format(addinPyFileDNames))
#print("pyFilePath: {}".format(pyFilePath))
#lib_path = r'H:\_WORK\PYTHON\REVIT_API\LIB'
print("lib_path: {}".format(lib_path))
sys.path.append(lib_path)

#if "Windows" in platform.uname():
	#lib_path = r'H:/_WORK/PYTHON/LIB'

try:
	sys.modules['__main__']
	hasMainAttr = True	
except:
	hasMainAttr = False

from RevitSelection import getValueByParameterName, getValuesByParameterName, setValueByParameterName, getBuiltInParameterInstance
from ListUtils import processList

import clr
clr.AddReference("System")
from System.Collections.Generic import List as Clist

#clr.AddReferenceByPartialName('PresentationCore')
#clr.AddReferenceByPartialName('PresentationFramework')
clr.AddReferenceByPartialName('System.Windows.Forms')
clr.AddReferenceByPartialName('System.Drawing')
#import System.Windows
#import System.Drawing
#from System.Reflection import BindingFlags
from System.Drawing import *
from System.Windows.Forms import *
from System import Enum
#from System.ComponentModel import BindingList


uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
mySelection = [doc.GetElement(elId) for elId in __revit__.ActiveUIDocument.Selection.GetElementIds()]

class Dic2obj(object):
	def __init__(self, dictionary):
		for key in dictionary:
			setattr(self, key, dictionary[key])


class MainForm(Form):
	userSelectedStrIds = []
	selectedRowStrIds = []
	def __init__(self, tableData, elements, inViewSelectionIdStrings):
		if hasMainAttr:
			try:
				#if script runs within C# IronPython hosting environment
				cwd = __scriptDir__
			except Exception as ex:
				#if script runs within RevitPythonShell environment
				cwd = "\\".join(__file__.split("\\")[:-1]) + "LIB\\"
		else:
			cwd = os.getcwd()
		#self.scriptDir = "\\".join(__file__.split("\\")[:-1]) 
		#print("script directory: {}".format(self.scriptDir))
		#print("cwd: {}".format(cwd))
		iconFilename = os.path.join(lib_path, 'spaceific_64x64_sat_X9M_icon.ico')
		icon = Icon(iconFilename)
		self.Icon = icon	

		self.tableData = tableData
		self.elements = elements
		self.viewSelectionIdStrings = inViewSelectionIdStrings
		self.inSelectedParameters = {k : True if k in selectedParams else False for k, v in uniqueParams.items()}
		self.Setup()
		self.InitializeComponent()
		

	def Setup(self):
		self.activeViewType = doc.ActiveView.ViewType
		self.markBipName = "ALL_MODEL_MARK"
		self.assemblyCodeBipName = "UNIFORMAT_CODE"
		self.markBip = BuiltInParameter.ALL_MODEL_MARK
		print("markBip {0}".format(self.markBip))
		self.assemblyCodeBip = getBuiltInParameterInstance(self.assemblyCodeBipName)
		
		#composite for grouping tuple(markParamVals, assemblyCodeParamVals, elementsCol)		
		if self.activeViewType == ViewType.Schedule:
			elements = FilteredElementCollector(doc,doc.ActiveView.Id).WhereElementIsNotElementType().ToElements()
			#self.tableViewLabel.Text = "ActiveViewType {0}".format(type(doc.ActiveView))
			tableData = doc.ActiveView.GetTableData()
			tableSectionData = tableData.GetSectionData(SectionType.Body)
			if len(elements) > 0:
				try:
					self.markName = elements[0].Parameter[BuiltInParameter.ALL_MODEL_MARK].Definition.Name
				except:
					self.markName = None
			print("tableSectionData {0}".format(tableSectionData.NumberOfRows))
			print("elements len: {0}".format(len(elements)))
			#for el in elements:
				#print("el.Id: {0}, category: {1}".format(el.Id, el.Category.Name))
		self.filteredElements = self.filterElementsByParameterName(elements, self.markName)
		self.filteredElements = self.filterElementsByParameterName(self.filteredElements, self.assemblyCodeBipName)
		print("self.filteredElements len: {0}, elements len: {1} ".format(len(self.filteredElements), len(elements)))
		
		markParamVals = processList(getValueByParameterName, self.filteredElements, self.markBipName, doc, bip = self.markBip)
		
		assemblyCodeParamVals = processList(getValueByParameterName, self.filteredElements, self.assemblyCodeBipName, doc, bip = self.assemblyCodeBip)
		
		grComp = zip(assemblyCodeParamVals, markParamVals, self.filteredElements)
		grComp = sorted(grComp, key = lambda x: x[0])
		key_func = lambda x: x[0]
		self.groups = {}
		
		for key, group in groupby(grComp, key_func):
			self.groups[key] = list(group)
		#print("groups {0}, self.filteredElements len: {1}".format(self.groups, len(self.filteredElements)))



	def InitializeComponent(self):
		self.Text = "Renumbering of parameter in active schedule"
		self.Width = 500
		self.Height = 250
		self.StartPosition = FormStartPosition.CenterScreen
		self.TopMost = True
		self.Resize += self.configureButtons

		self.buttonFrame = Panel()
		self.buttonFrame.Parent = self
		self.buttonFrame.Anchor = AnchorStyles.Top
		self.buttonFrame.Dock = DockStyle.Bottom
		self.buttonFrame.Height = 30

		# self.paramaterValueTB = TextBox()
		# self.paramaterValueTB.Text = "Enter value"
		# #self.paramaterValueTB.Location = Point(5, 55)
		# self.paramaterValueTB.Width = 150
		# self.paramaterValueTB.Parent = self
		# self.paramaterValueTB.Anchor = AnchorStyles.Top
		# self.paramaterValueTB.Dock = DockStyle.Top		

		self.textFrame = Panel()
		self.textFrame.Parent = self
		self.textFrame.Anchor = AnchorStyles.Top
		self.textFrame.Dock = DockStyle.Top
		self.textFrame.AutoSize = True
		self.parameterCB = ComboBox()
		self.parameterCB.Width = 150
		self.parameterCB.Parent = self.textFrame
		self.parameterCB.Anchor = AnchorStyles.Top
		self.parameterCB.Dock = DockStyle.Top
		self.parameterCB.Items.AddRange(tuple([k for k in sorted(uniqueParams.keys())]))
		self.parameterCB.SelectionChangeCommitted += self.OnChanged
		if self.markName:
			self.parameterCB.Text = self.markName
		else:
			self.parameterCB.Text = "--SELECT--"
		self.parameterCB.DrawMode = DrawMode.OwnerDrawVariable
		self.parameterCB.DropDownStyle = ComboBoxStyle.DropDown
		self.parameterCB.DrawItem += self.comboBoxDrawItem

		# for item in self.parameterCB.Controls:
		# 	print("self.parameterCB.item {}".format(item.Text.BackColor))
		
		self.parameterCBLabel = Label()
		self.parameterCBLabel.Text = "Select parameter"
		self.parameterCBLabel.Font = Font(self.parameterCBLabel.Font.FontFamily, self.parameterCBLabel.Font.Size, FontStyle.Bold)
		self.parameterCBLabel.Width = 250
		self.parameterCBLabel.Parent = self.textFrame
		self.parameterCBLabel.Anchor = AnchorStyles.Top
		self.parameterCBLabel.Dock = DockStyle.Top

		self.setParameterTextBox = TextBox()
		#self.setParameterTextBox.FontHeight = 20
		self.setParameterTextBox.Height = 100
		self.setParameterTextBox.Text = "0"
		self.setParameterTextBox.Name = "startFrom"
		#self.setParameterTextBox.ScrollBars = ScrollBars.Vertical
		#self.setParameterTextBox.Location = Point(0,0)
		self.setParameterTextBox.Multiline = False
		self.setParameterTextBox.TextChanged += self.setParameterSubmit
		self.setParameterTextBox.Parent = self.textFrame
		self.setParameterTextBox.Dock = DockStyle.Top

		self.startFromLabel = Label()
		self.startFromLabel.Text = "Start sequence from:"
		self.startFromLabel.Width = 250
		self.startFromLabel.Font = Font(self.parameterCBLabel.Font.FontFamily, self.parameterCBLabel.Font.Size, FontStyle.Bold)
		self.startFromLabel.Parent = self.textFrame
		self.startFromLabel.Anchor = AnchorStyles.Top
		self.startFromLabel.Dock = DockStyle.Top
		
		self.label = Label()
		self.label.Text = "Select parameter from list to create table of all elements with this parameter"
		self.label.Width = 250
		self.label.Parent = self.textFrame
		self.label.Anchor = AnchorStyles.Top
		self.label.Dock = DockStyle.Top

		self.viewLabel = Label()
		self.viewLabel.Text = "Select parameter from list to create table of all elements with this parameter"
		self.viewLabel.Width = 250
		self.viewLabel.Parent = self.textFrame
		self.viewLabel.Anchor = AnchorStyles.Top
		self.viewLabel.Dock = DockStyle.Top

		self.tableViewLabel = Label()
		self.tableViewLabel.Text = "table view"
		self.tableViewLabel.Width = 250
		self.tableViewLabel.Parent = self.textFrame
		self.tableViewLabel.Anchor = AnchorStyles.Top
		self.tableViewLabel.Dock = DockStyle.Top

		

		# self.paramaterNameTB = TextBox()
		# self.paramaterNameTB.Text = "Enter parameter Name"
		# #self.paramaterNameTB.Location = Point(5, 30)
		# self.paramaterNameTB.Width = 150
		# self.paramaterNameTB.Dock = DockStyle.Top

		self.submitButton = Button()
		self.submitButton.Text = 'OK'
		self.submitButton.Location = Point(25, 125)
		self.submitButton.Click += self.update
		self.submitButton.Parent = self.buttonFrame
		self.submitButton.Width = self.Width/2
		self.submitButton.Anchor = AnchorStyles.Right
		self.submitButton.Dock = DockStyle.Right

		self.closeButton = Button()
		self.closeButton.Text = 'Close'
		self.closeButton.Click += self.close
		self.closeButton.Parent = self.buttonFrame
		self.closeButton.Width = self.Width/2
		self.closeButton.Anchor = AnchorStyles.Left
		self.closeButton.Dock = DockStyle.Left

		self.AcceptButton = self.submitButton
		self.CancelButton = self.closeButton

		# self.Controls.Add(self.label)
		# self.Controls.Add(self.parameterCBLabel)
		# self.Controls.Add(self.paramaterNameTB)
		# self.Controls.Add(self.paramaterValueTB)
		# self.Controls.Add(self.submitButton)

	def setParameterSubmit(self, sender, event):
		#print("key was pressed in {0}, dir(event): {1}".format(sender.Name, dir(event)))
		print("text was changed {0}".format(self.setParameterTextBox.Text))
		#if event.KeyValue == 13:
		#	self.setParametersOfSelected(self.setParameterTextBox, event)

	def comboBoxDrawItem(self, sender, event):
		#for i, item in enumerate(event):
		#	pass
		event.DrawBackground()
		rectangle = Rectangle(2, event.Bounds.Top+2, 1, event.Bounds.Height-4)
		#event.Graphics.FillRectangle(SolidBrush(Color.Blue), rectangle)
		myFont = event.Font.Clone()
		myBoldFont = Font(event.Font, FontStyle.Bold)
		#print("event text {}".format(self.parameterCB.Items[event.Index]))
		if len(selectedParams) > 0 and self.inSelectedParameters[self.parameterCB.Items[event.Index]]:
			#event.Graphics.DrawString(sorted(uniqueParams.keys())[event.Index], myFont, Brushes.Red, RectangleF(event.Bounds.X+rectangle.Width, event.Bounds.Y, event.Bounds.Width, event.Bounds.Height))
			#event.Graphics.Clear(Color.LightSkyBlue)
			#event.Graphics.DrawString(sorted(uniqueParams.keys())[event.Index], myFont, Brushes.Black, RectangleF(event.Bounds.X+rectangle.Width, event.Bounds.Y, event.Bounds.Width, event.Bounds.Height))
			event.Graphics.DrawString(sorted(uniqueParams.keys())[event.Index], myBoldFont, Brushes.Black, RectangleF(event.Bounds.X+rectangle.Width, event.Bounds.Y, event.Bounds.Width, event.Bounds.Height))
		elif len(selectedParams) > 0 and self.parameterCB.Items[event.Index] not in selectedParams:
			event.Graphics.DrawString(sorted(uniqueParams.keys())[event.Index], myFont, Brushes.Gray, RectangleF(event.Bounds.X+rectangle.Width, event.Bounds.Y, event.Bounds.Width, event.Bounds.Height))
		else:
			#event.Graphics.Clear(Color.White)
			event.Graphics.DrawString(sorted(uniqueParams.keys())[event.Index], myBoldFont, Brushes.Black, RectangleF(event.Bounds.X+rectangle.Width, event.Bounds.Y, event.Bounds.Width, event.Bounds.Height))

	def update(self, sender, event):
		#self.label.Text = self.paramaterValueTB.Text
		#selectedScheduleViewName = self.scheduleViewCB.SelectedItem
		writeParamName = self.parameterCB.SelectedItem
		try:
			startPosition = int(self.setParameterTextBox.Text)
		except Exception as ex:
			raise ValueError("Cannot convert input text to int", ex)
		self.filteredElements = self.filterElementsByParameterName(self.filteredElements, writeParamName)
		#myParameterValue = self.paramaterValueTB.Text

		print("\nYou selected: {0}".format(writeParamName))
		print("Number of Elements: {0}\n".format(len(self.elements)))

				# for el in self.filteredElements:
		# 	print("{0} - \n".format(el.Id.ToString()))
		
		#self.values = getValuesByParameterName(self.filteredElements, writeParamName, doc)
		#for i, val in enumerate(self.values):
		#	print("val {0}, el.Id {1}, name: {2}, paramName{3}".format(val, self.filteredElements[i].Id, self.filteredElements[i].Name, self.filteredElements[i].Parameter[BuiltInParameter.ALL_MODEL_MARK].Definition.Name))
		
		t = Transaction(doc, "Renumber parametr")
		t.Start()
		results = []
		for k,group in self.groups.items():
			for i, item in enumerate(group):
				if startPosition:
					writeStr = "{0:0>3}".format(startPosition + i)
				else:
					writeStr = "{0:0>3}".format(i+1)
				results.append(setValueByParameterName(item[2], writeStr, writeParamName, doc))

		t.Commit()
		
		#self.elementTab = TabForm(self.tableData, self.filteredElements, writeParamName, self.viewSelectionIdStrings)
		#self.elementTab.ShowDialog()
		
		# t = Transaction(doc, "Filter elements by parameter name and value")
		# #transaction Start
		# t.Start()
		# selection.Clear()
		# __revit__.ActiveUIDocument.Selection.SetElementIds(myCollection)
		# #uidoc.ShowElements(myCollection)
		# #transaction commit
		# t.Commit()
		#close the form window
		#self.Close()

	def configureButtons(self, sender, event):
		self.parameterCB.Focus()
		self.closeButton.Width = self.buttonFrame.Width/2
		self.submitButton.Width = self.buttonFrame.Width/2

	def filterElementsByParameterName(self, inElements, inParameterName):
		filteredElements = []
		bip = getBuiltInParameterInstance(inParameterName)
		print("bip1 {0}".format(bip))
		for el in inElements:
			if el.GetTypeId().IntegerValue > -1:
				typeElement = doc.GetElement(el.GetTypeId()) 
				if el.LookupParameter(inParameterName):
					filteredElements.append(el)
				elif typeElement.LookupParameter(inParameterName):
					filteredElements.append(el)
				elif bip:
					#print("bip2 {0}".format(bip))
					if el.Parameter[bip]:
						filteredElements.append(el)
					elif typeElement.Parameter[bip]:
						filteredElements.append(el)

		return filteredElements

	def close(self, sender, event):
		self.Close()
	def OnChanged(self, sender, event):
		self.label.Text = sender.Text

def getMembers(inElements):
	uniqueParams = {}
	uniqueTypeIds = []
	uniqueFamilies = {}
	for el in inElements:
		if el.GetTypeId().IntegerValue > -1:
			if el.GetTypeId() not in uniqueTypeIds:
				uniqueTypeIds.append(el.GetTypeId())
			familyName = doc.GetElement(el.GetTypeId()).FamilyName
			if familyName not in uniqueFamilies:
				uniqueFamilies[familyName] = el.GetTypeId()
		elParams = el.GetOrderedParameters()
		for elParam in elParams:
			if elParam.Definition.Name not in uniqueParams and elParam.StorageType == StorageType.String:
				uniqueParams[elParam.Definition.Name] = elParam
				nameToParamDic[elParam.Definition.Name] = elParam

	for k, elId in uniqueFamilies.items():
		el = doc.GetElement(elId)
		elParams = el.GetOrderedParameters()
		for elParam in elParams:
			if elParam.Definition.Name not in uniqueParams:
				uniqueParams[elParam.Definition.Name] = elParam
				nameToParamDic[elParam.Definition.Name] = elParam
	
	return uniqueParams

class InfoDialog(Form):
	def __init__(self):
		if hasMainAttr:
			try:
				#if script runs within C# IronPython hosting environment
				cwd = __scriptDir__
			except Exception as ex:
				#if script runs within RevitPythonShell environment
				cwd = "\\".join(__file__.split("\\")[:-1]) + "LIB\\"
		else:
			cwd = os.getcwd()
		#self.scriptDir = "\\".join(__file__.split("\\")[:-1]) 
		#print("script directory: {}".format(self.scriptDir))
		#print("cwd: {}".format(cwd))
		iconFilename = os.path.join(lib_path, 'spaceific_64x64_sat_X9M_icon.ico')
		icon = Icon(iconFilename)
		self.Icon = icon	

		self.Setup()
		self.InitializeComponent()
		

	def Setup(self):
		self.activeViewType = doc.ActiveView.ViewType
		self.sheduleViewElements = FilteredElementCollector(doc).OfClass(ViewSchedule).WhereElementIsNotElementType().ToElements()
		self.scheduleViewDict = {}
		self.scheduleNames = []
		# self.viewLabel.Text = "ActiveViewType {0}".format(self.activeViewType)
		# if self.activeViewType == ViewType.Schedule:
		# 	elements = FilteredElementCollector(doc,doc.ActiveView.Id).WhereElementIsNotElementType().ToElements()
		# 	self.tableViewLabel.Text = "ActiveViewType {0}".format(type(doc.ActiveView))
		# 	tableData = doc.ActiveView.GetTableData()
		# 	tableSectionData = tableData.GetSectionData(SectionType.Body)
		# 	print("tableSectionData {0}".format(tableSectionData.NumberOfRows))
		# 	print("elements len: {0}".format(len(elements)))
		for el in self.sheduleViewElements:
			self.scheduleViewDict[el.Name] = el
			self.scheduleNames.append(el.Name)
			#print("el.Id: {0}, category: {1} name:{2}, type: {3}".format(el.Id, el.Category.Name, el.Name, el.GetType()))
		self.scheduleNames.sort()


	def InitializeComponent(self):
		self.Text = "Select schedule view for renumbering process"
		self.Width = 500
		self.Height = 190
		self.StartPosition = FormStartPosition.CenterScreen
		self.TopMost = True
		self.Resize += self.configureButtons

		self.buttonFrame = Panel()
		self.buttonFrame.Parent = self
		self.buttonFrame.Anchor = AnchorStyles.Top
		self.buttonFrame.Dock = DockStyle.Bottom
		self.buttonFrame.Height = 30
		

		self.submitButton = Button()
		self.submitButton.Text = 'OK'
		self.submitButton.Location = Point(25, 125)
		self.submitButton.Click += self.update
		self.submitButton.Width = self.Width/2
		self.submitButton.Parent = self.buttonFrame
		#self.submitButton.Anchor = AnchorStyles.Right
		self.submitButton.Dock = DockStyle.Right

		self.closeButton = Button()
		self.closeButton.Text = 'Close'
		self.closeButton.Click += self.close
		self.closeButton.Parent = self.buttonFrame
		self.closeButton.Width = self.Width/2
		#self.closeButton.Anchor = AnchorStyles.Left
		self.closeButton.Dock = DockStyle.Left

		#self.buttonFrame.ControlAdded += self.configureButtons

		self.textFrame = Panel()
		self.textFrame.Parent = self
		self.textFrame.Anchor = AnchorStyles.Top
		self.textFrame.Dock = DockStyle.Top

		#self.Controls.Add(self.textFrame)
		#self.Controls.Add(self.buttonFrame)		

		self.scheduleViewCB = ComboBox()
		self.scheduleViewCB.Width = 150
		self.scheduleViewCB.Parent = self.textFrame
		self.scheduleViewCB.Location = Point(0,50)
		self.scheduleViewCB.Anchor = AnchorStyles.Top
		self.scheduleViewCB.Dock = DockStyle.Top
		self.scheduleViewCB.Items.AddRange(tuple(self.scheduleNames))
		self.scheduleViewCB.Focus()
		
		#self.parameterCB.SelectionChangeCommitted += self.OnChanged
		self.scheduleViewCB.Text = self.scheduleNames[0]
		self.scheduleViewCB.DropDownStyle = ComboBoxStyle.DropDown

		self.parameterCBLabel = Label()
		self.parameterCBLabel.Text = "THE ACTIVE VIEW IS NOT OF SCHEDULE TYPE\n\nPlease select one:"
		#lFont = self.parameterCBLabel.Font.Clone()
		#lFont.Size = 14
		#fStyle = lFont.Style
		#self.parameterCBLabel.Font = Font(lFont, FontStyle.Bold)
		#print("fontFamily {0}".format(lFont.FontFamily.ToString()))
		self.parameterCBLabel.Font = Font(self.parameterCBLabel.Font.FontFamily, self.parameterCBLabel.Font.Size, FontStyle.Bold)
		#self.parameterCBLabel.ForeColor = Color.Red
		self.parameterCBLabel.Width = 250
		self.parameterCBLabel.Height = 50
		self.parameterCBLabel.Parent = self.textFrame
		self.parameterCBLabel.Anchor = AnchorStyles.Top
		self.parameterCBLabel.Dock = DockStyle.Top
	
	def update(self, sender, event):
		selectedScheduleViewName = self.scheduleViewCB.SelectedItem
		uidoc.ActiveView = self.scheduleViewDict[selectedScheduleViewName]
		self.Close()
	
	def configureButtons(self, sender, event):
		self.scheduleViewCB.Focus()
		self.closeButton.Width = self.buttonFrame.Width/2
		self.submitButton.Width = self.buttonFrame.Width/2

	def close(self, sender, event):
		self.Dispose()

if "rpsOutput" in dir():
	rpsOutput.Show()

openedForms = list(Application.OpenForms)
rpsOpenedForms = []
for i, oForm in enumerate(openedForms):
	if "RevitPythonShell" in str(oForm):
		rpsOpenedForms.append(oForm)

if len(rpsOpenedForms) > 0:
	lastForm = rpsOpenedForms[-1]
	lastForm.Show()

allElements = []




nameToParamDic = {}
activeViewType = doc.ActiveView.ViewType
Application.EnableVisualStyles()

if activeViewType != ViewType.Schedule:
	myDialogWindow = InfoDialog()
	Application.Run(myDialogWindow)

activeViewType = doc.ActiveView.ViewType
if activeViewType == ViewType.Schedule:
	allElements = list(FilteredElementCollector(doc,doc.ActiveView.Id).WhereElementIsNotElementType().ToElements())
	uniqueParams = getMembers(allElements)
	viewSelection = uidoc.Selection
	viewSelectionIds = list(viewSelection.GetElementIds())
	viewSelectionIdStrings = [x.ToString() for x in viewSelectionIds]

	viewSelectionElements = []
	print("Selected Elements {}".format(len(viewSelectionIds)))
	for i, elId in enumerate(viewSelectionIds):
		#print("{0} - {1} - {2}".format(i, elId.IntegerValue, doc.GetElement(elId).Name))
		viewSelectionElements.append(doc.GetElement(elId))
	selectedParams = getMembers(viewSelectionElements)
	selectedParamsIds = {v.Id.ToString():v for k,v in selectedParams.items()}

	print("elements len: {0}".format(len(allElements)))
	#for el in allElements:
	#	print("el.Id: {0}, category: {1}".format(el.Id, el.Category.Name))

	myDialogWindow = MainForm(uniqueParams, allElements, viewSelectionIdStrings)
	Application.Run(myDialogWindow)








