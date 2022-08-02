# -*- coding: utf-8 -*-
# Copyright(c) 2022, Daniel Gercak
#Script for parameters update of family "Prostup (SWECO)"
#resource_path: H:\_WORK\PYTHON\REVIT_API\renumberMarkParameter.py
#from typing import Type
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB.Architecture import *
#from Autodesk.Revit.DB.Analysis import *
from Autodesk.Revit.UI import *
from Autodesk.Revit.UI.Selection import *



import sys
from operator import attrgetter
from itertools import groupby
pyt_path = r'C:\Program Files\IronPython 2.7\Lib'
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
from System.Environment import NewLine
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
			viewPhaseParamId = ElementId(BuiltInParameter.VIEW_PHASE)
			param_provider = ParameterValueProvider(viewPhaseParamId)
			self.activeViewPhaseId = param_provider.GetElementIdValue(doc.ActiveView)
			self.myElementPhaseStatusNew_Filter = ElementPhaseStatusFilter(self.activeViewPhaseId, ElementOnPhaseStatus.New,False)

			elements = FilteredElementCollector(doc,doc.ActiveView.Id).WhereElementIsNotElementType().ToElements()
			#self.tableViewLabel.Text = "ActiveViewType {0}".format(type(doc.ActiveView))
			tableData = doc.ActiveView.GetTableData()
			tableSectionData = tableData.GetSectionData(SectionType.Body)
			if len(elements) > 0:
				try:
					self.markParamName = elements[0].Parameter[BuiltInParameter.DOOR_NUMBER].Definition.Name
					markParamId = elements[0].Parameter[BuiltInParameter.DOOR_NUMBER].Id
					self.markParamValueProvider = ParameterValueProvider(markParamId)
				except:
					self.markParamName = None
					self.markParamValueProvider = None
				
				try:
					markTypeParamId = ElementId(BuiltInParameter.ALL_MODEL_TYPE_MARK)
					print("markTypeParamId {0}".format(markTypeParamId))
					self.markTypeParamValueProvider = ParameterValueProvider(markTypeParamId)
					print("markTypeParamValueProvider {0}".format(self.markTypeParamValueProvider))
				except:
					self.markTypeParamValueProvider = None

				try:
					assemblyCodeParamId = ElementId(BuiltInParameter.UNIFORMAT_CODE)
					print("assemblyCodeParamId {0}".format(assemblyCodeParamId))
					self.assemblyCodeValueProvider = ParameterValueProvider(assemblyCodeParamId)
					print("assemblyCodeParamValueProvider {0}".format(self.assemblyCodeValueProvider))
				except:
					self.assemblyCodeValueProvider = None
				"""
				self.markName = None
				self.markName = elements[0].Parameter[BuiltInParameter.DOOR_NUMBER].Definition.Name
				"""
				markParamName = None
			print("tableSectionData {0}".format(tableSectionData.NumberOfRows))
			print("elements len: {0}".format(len(elements)))
			#for el in elements:
				#print("el.Id: {0}, category: {1}".format(el.Id, el.Category.Name))
		self.typeMarkFilteredElements = self.filterElementsByMarkType()
		print("len(self.typeMarkfilteredElements) {0}".format(len(self.typeMarkFilteredElements)))
		for el in self.typeMarkFilteredElements:
			print("markTypeParamValue = {0} - {1} - {2} - {3}".format(self.markTypeParamValueProvider.GetStringValue(el), el.Id, el.Name, el.Category.Name))
   
		self.filteredElements = self.filterElementsByParameterName(elements, self.markParamName)
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
		self.Height = 300
		self.StartPosition = FormStartPosition.CenterScreen
		self.TopMost = True
		self.Resize += self.configureButtons

		self.buttonFrame = Panel()
		self.buttonFrame.Parent = self
		self.buttonFrame.Anchor = AnchorStyles.Top
		self.buttonFrame.Dock = DockStyle.Bottom
		self.buttonFrame.Height = 50

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
  
		self.markTypeTextBox = TextBox()
		self.markTypeTextBox.Height = 100
		self.markTypeTextBox.Text = self.majorMark
		self.markTypeTextBox.Name = "Major type mark"
		#self.setParameterTextBox.ScrollBars = ScrollBars.Vertical
		#self.setParameterTextBox.Location = Point(0,0)
		self.markTypeTextBox.Multiline = False
		self.markTypeTextBox.TextChanged += self.setParameterSubmit
		self.markTypeTextBox.Parent = self.textFrame
		self.markTypeTextBox.Dock = DockStyle.Top

		self.markTypeTextBoxLabel = Label()
		self.markTypeTextBoxLabel.Text = "Filter elements by pattern of first two chars mark type parameter (1U...):"
		self.markTypeTextBoxLabel.Font = Font(self.markTypeTextBoxLabel.Font.FontFamily, self.markTypeTextBoxLabel.Font.Size, FontStyle.Bold)
		self.markTypeTextBoxLabel.Width = 250
		self.markTypeTextBoxLabel.Parent = self.textFrame
		self.markTypeTextBoxLabel.Anchor = AnchorStyles.Top
		self.markTypeTextBoxLabel.Dock = DockStyle.Top
  


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
		self.startFromLabel.Font = Font(self.startFromLabel.Font.FontFamily, self.startFromLabel.Font.Size, FontStyle.Bold)
		self.startFromLabel.Parent = self.textFrame
		self.startFromLabel.Anchor = AnchorStyles.Top
		self.startFromLabel.Dock = DockStyle.Top
		
  		self.parameterCB = ComboBox()
		self.parameterCB.Width = 150
		self.parameterCB.Parent = self.textFrame
		self.parameterCB.Anchor = AnchorStyles.Top
		self.parameterCB.Dock = DockStyle.Top
		self.parameterCB.Items.AddRange(tuple([k for k in sorted(uniqueParams.keys())]))
		self.parameterCB.SelectionChangeCommitted += self.OnChanged
		if self.markParamName:
			self.parameterCB.Text = self.markParamName
		else:
			self.parameterCB.Text = "--SELECT--"
		self.parameterCB.DrawMode = DrawMode.OwnerDrawVariable
		self.parameterCB.DropDownStyle = ComboBoxStyle.DropDown
		self.parameterCB.DrawItem += self.comboBoxDrawItem

		self.parameterCBLabel = Label()
		self.parameterCBLabel.Text = "Select parameter"
		self.parameterCBLabel.Font = Font(self.parameterCBLabel.Font.FontFamily, self.parameterCBLabel.Font.Size, FontStyle.Bold)
		self.parameterCBLabel.Width = 250
		self.parameterCBLabel.Parent = self.textFrame
		self.parameterCBLabel.Anchor = AnchorStyles.Top
		self.parameterCBLabel.Dock = DockStyle.Top
  
		# for item in self.parameterCB.Controls:
		# 	print("self.parameterCB.item {}".format(item.Text.BackColor))
		


		self.label = Label()
		self.label.Text = "Select parameter from list where to write sequence - parameter must be of type string"
		self.label.Width = 250
		self.label.Parent = self.textFrame
		self.label.Anchor = AnchorStyles.Top
		self.label.Dock = DockStyle.Top
		''' 
		self.viewLabel = Label()
		self.viewLabel.Text = "Select parameter from list to create table of all elements with this parameter"
		self.viewLabel.Width = 250
		self.viewLabel.Parent = self.textFrame
		self.viewLabel.Anchor = AnchorStyles.Top
		self.viewLabel.Dock = DockStyle.Top 
  		'''

		''' self.tableViewLabel = Label()
		self.tableViewLabel.Text = "table view"
		self.tableViewLabel.Width = 250
		self.tableViewLabel.Parent = self.textFrame
		self.tableViewLabel.Anchor = AnchorStyles.Top
		self.tableViewLabel.Dock = DockStyle.Top
		'''

		

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

		self.writeChB = CheckBox()
		self.writeChB.Text = "Write values"
		self.writeChB.Height = 30
		self.writeChB.Width = 150
		self.writeChB.AutoSize = True
		self.writeChB.Parent = self.buttonFrame
		#self.allInstancesChB.Location = (Point(10,30))
		#self.writeChB.CheckedChanged += self.allInstancesChanged
		self.writeChB.Checked = False
		self.writeChB.Anchor = AnchorStyles.Top
		self.writeChB.Dock = DockStyle.Top

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

		myPattern = self.markTypeTextBox.Text
		self.typeMarkFilteredElements = self.filterElementsByMarkType(pattern = myPattern)
		
		#myParameterValue = self.paramaterValueTB.Text

		print("\nYou selected: {0}".format(writeParamName))
		print("Number of Elements: {0}\n".format(len(self.typeMarkFilteredElements)))

		#for el in self.typeMarkFilteredElements:
		#	print("udate markTypeParamValue = {0} - {1} - {2} - {3} - {4}".format(self.markTypeParamValueProvider.GetStringValue(el), self.markParamValueProvider.GetStringValue(el), el.Id, el.Name, el.Category.Name))
		# 	print("{0} - \n".format(el.Id.ToString()))
		
		#self.values = getValuesByParameterName(self.filteredElements, writeParamName, doc)
		#for i, val in enumerate(self.values):
		#	print("val {0}, el.Id {1}, name: {2}, paramName{3}".format(val, self.filteredElements[i].Id, self.filteredElements[i].Name, self.filteredElements[i].Parameter[BuiltInParameter.ALL_MODEL_MARK].Definition.Name))
		#markParamVals = [self.markParamValueProvider.GetStringValue(x) for x in self.typeMarkFilteredElements]
		
		#assemblyCodeParamVals = [self.assemblyCodeValueProvider.Get.GetStringValue(x) for x in self.typeMarkFilteredElements]
		markParamVals = []
		assemblyCodeParamVals = []
		for el in self.typeMarkFilteredElements:
			#print("markTypeParamValue = {0} - {1} - {2} - {3}".format(self.markTypeParamValueProvider.GetStringValue(el), el.Id, el.Name, el.Category.Name))
			markParamVals.append(self.markTypeParamValueProvider.GetStringValue(el))
		for el in self.typeMarkFilteredElements:
			#print("assemblyCodeParamVals = {0} - {1} - {2} - {3}".format(self.assemblyCodeValueProvider.GetStringValue(el), el.Id, el.Name, el.Category.Name))
			assemblyCodeParamVals.append(self.assemblyCodeValueProvider.GetStringValue(el))

		grComp = zip(assemblyCodeParamVals, markParamVals, self.filteredElements)
		grComp = sorted(grComp, key = lambda x: x[0])
		key_func = lambda x: x[0]
		self.groups = {}
		
		for key, group in groupby(grComp, key_func):
			self.groups[key] = list(group)

		if self.writeChB.Checked:
			t = Transaction(doc, "Renumber parametr")
			t.Start()
			results = []
			try:
				indx = 0
				for k,group in self.groups.items():
					for i, item in enumerate(group):
						if startPosition:
							writeStr = "{0:0>3}".format(startPosition + i)
						else:
							writeStr = "{0:0>3}".format(i+1)
						result = setValueByParameterName(item[2], writeStr, writeParamName, doc)
						results.append(result)
						print(results[-1])
		
						#print("{0} - Group {1}, item {2}, typeMark {3}, mark {4}, ID {5}, name{6}".format(indx, k, i, self.markTypeParamValueProvider.GetStringValue(item[2]), writeStr, item[2].Id, item[2].Name))
						indx +=1
		
			except Exception as ex:
				print("Exception in MainForm.update(): {0}".format(sys.exc_info()))
				
			t.Commit()
			print("parameter changed")
		else:
			self.Width = 800
			self.Height = 500
			strOut = ""
			indx = 0
			self.checkListTB = TextBox()
			#self.setParameterTextBox.FontHeight = 20
			self.checkListTB.Height = 200
			self.checkListTB.Text = strOut
			self.checkListTB.Name = "Check list"
			self.checkListTB.ScrollBars = ScrollBars.Vertical
			#self.setParameterTextBox.Location = Point(0,0)
			self.checkListTB.Multiline = True
			#self.setParameterTextBox.TextChanged += self.setParameterSubmit
			self.checkListTB.Parent = self.textFrame
			self.checkListTB.Dock = DockStyle.Bottom
			for k,group in self.groups.items():
				for i, item in enumerate(group):
					if startPosition:
						writeStr = "{0:0>3}".format(startPosition + i)
					else:
						writeStr = "{0:0>3}".format(i+1)
					#result = setValueByParameterName(item[2], writeStr, writeParamName, doc)
					#results.append(result)
					#print(results[-1])
					self.checkListTB.Text += "{0} - Group {1}, item {2}, typeMark {3}, mark {4}, ID {5}, name{6}\n".format(indx, k, i, self.markTypeParamValueProvider.GetStringValue(item[2]), writeStr, item[2].Id, item[2].Name)
					self.checkListTB.Text = self.checkListTB.Text + NewLine
					indx +=1
			
			print(strOut)
		
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

	def filterElementsByMarkType(self, **kwargs):
		stringPattern = kwargs['pattern'] if 'pattern' in kwargs else None
		if self.markTypeParamValueProvider != None:
			self.dictOfMarks = {}
			self.scheduleElementsCol = FilteredElementCollector(doc,doc.ActiveView.Id). \
													WherePasses(self.myElementPhaseStatusNew_Filter). \
													WhereElementIsNotElementType().ToElements()
			for el in list(self.scheduleElementsCol):
				markTypeParamValue = self.markTypeParamValueProvider.GetStringValue(el)
				twoChars = markTypeParamValue[:2]
				self.dictOfMarks[twoChars] = self.dictOfMarks[twoChars] + 1 if twoChars in self.dictOfMarks else 0
				#print("schedule markTypeParamValue {0}".format(markTypeParamValue))
	
			print(self.dictOfMarks)
			self.majorMark = sorted(self.dictOfMarks.items(), key=lambda kv:(kv[1], kv[0]), reverse=True)[0][0] if not stringPattern else stringPattern 
			print("self.majorMark {0}".format(self.majorMark))
			filteredScheduleElements_markType = list(FilteredElementCollector(doc,doc.ActiveView.Id). \
													WherePasses(self.myElementPhaseStatusNew_Filter). \
													WherePasses(ElementParameterFilter(FilterStringRule(self.markTypeParamValueProvider, FilterStringBeginsWith(), self.majorMark))). \
													WhereElementIsNotElementType(). \
													ToElements())
			return filteredScheduleElements_markType
		else:
			return None
			

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
	myDialogWindow.Close()








