# -*- coding: utf-8 -*-
# Copyright(c) 2020, Daniel Gercak
#Script for parameters update of family "Prostup (SWECO)"
#resource_path: H:\_WORK\PYTHON\REVIT_API\vyska_prostupu.py
#from typing import Type
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB.Architecture import *
#from Autodesk.Revit.DB.Analysis import *
from Autodesk.Revit.UI import *
from Autodesk.Revit.UI.Selection import PickBoxStyle, ObjectType
import Autodesk.Revit.UI.Selection as Selection
import Autodesk.Revit.DB as DB



import sys
import time
import re
from operator import attrgetter
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

try:
	runFromCsharp = True if "__csharp__" in dir() else False
	#UI.TaskDialog.Show("Run from C#", "Script is running from C#")
except:
	runFromCsharp = False

from RevitSelection import getValueByParameterName, getAllElements, setValueByParameterName, getBuiltInParameterInstance

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
openedForms = list(Application.OpenForms)
for i, oForm in enumerate(openedForms):
	#print(str(i))
	#print(oForm)
	if "RevitPythonShell" in str(oForm):
		#print("Totot je oForm {0}".format(oForm))
		rpsOutput = oForm
	else:
		rpsOutput = None

	if rpsOutput:
		pass
		rpsOutput.Hide()
	else:
		pass
	
#print("__main__.OpenForms {}".format(list(Application.OpenForms)))
#rpsOutput = list(Application.OpenForms)[0]

class Dic2obj(object):
	def __init__(self, dictionary):
		for key in dictionary:
			setattr(self, key, dictionary[key])

class MainForm(Form):
	def __init__(self, inSelectedElement):
		#self.scriptDir = "\\".join(__file__.split("\\")[:-1])
		#print(self.scriptDir)
		#cwd = os.getcwd()
		if hasMainAttr:
			try:
				#if script runs within C# IronPython hosting environment
				cwd = __scriptDir__
			except Exception as ex:
				#if script runs within RevitPythonShell environment
				cwd = "\\".join(__file__.split("\\")[:-1]) + "LIB\\"
		else:
			cwd = os.getcwd()
		iconFilename = os.path.join(lib_path, 'spaceific_64x64_sat_X9M_icon.ico')
		icon = Icon(iconFilename)
		self.Icon = icon	
		"""
		self.priorityLookup = inPriorityLookup
		"""
		self.paramName = "ALL_MODEL_INSTANCE_COMMENTS"
		self.selectedElement = inSelectedElement
		self.commentLayers = self.getCommentLayers(self.selectedElement)
		self.originalCommentLayers = self.getCommentLayers(self.selectedElement)
		self.allInstances = self.getAllInstances(self.selectedElement)
		self.confirmed = False

		
		self.InitializeComponent()

	def InitializeComponent(self):
		self.Text = "Compound construction editor by Spaceific-Studio"
		self.Width = 500
		self.Height = 400
		self.StartPosition = FormStartPosition.CenterScreen
		self.TopMost = True
		screenSize = Screen.GetWorkingArea(self)
		#self.Height = screenSize.Height / 5
		self.Width = screenSize.Width / 3
		self.panelHeight = self.ClientRectangle.Height * 0.75
		self.panelWidth = self.ClientRectangle.Width / 3
		self.bgColor = Color.CadetBlue
		self.textColor = Color.White
		self.SizeChanged += self.update

		self.setupDataGridView()
	
	def setupDataGridView(self):
		self.dgvPanel = Panel()
		self.dgvPanel.Dock = DockStyle.Fill
		self.dgvPanel.AutoSize = False
		self.dgvPanel.AutoSizeMode = AutoSizeMode.GrowAndShrink
		self.dgvPanel.AutoScroll = True
		self.dgvPanel.BackColor = Color.Blue

		self.inputTextPanel = Panel()
		self.inputTextPanel.Dock = DockStyle.Bottom
		self.inputTextPanel.AutoSize = True
		self.inputTextPanel.Name = "Info Panel"
		self.inputTextPanel.AutoSizeMode = AutoSizeMode.GrowAndShrink
		self.inputTextPanel.AutoScroll = True
		self.inputTextPanel.BackColor = Color.White
		
		self.buttonPanel = Panel()
		self.buttonPanel.Dock = DockStyle.Bottom
		self.buttonPanel.AutoSize = True
		self.buttonPanel.Name = "Button Panel"
		self.buttonPanel.Height = 90
		self.buttonPanel.AutoSizeMode = AutoSizeMode.GrowAndShrink
		self.buttonPanel.AutoScroll = True
		self.buttonPanel.BackColor = Color.White
		#self.buttonPanel.Anchor = (AnchorStyles.Bottom | AnchorStyles.Left | AnchorStyles.Right)
		#self.buttonPanel.ControlAdded += self.control_Added 
		
		
		self.dgv = DataGridView()
		self.dgv.SelectionMode = DataGridViewSelectionMode.FullRowSelect
		#self.dgv.AutoGenerateColumns = True
		self.dgv.BackColor = Color.Yellow
		#self.dgv.ColumnAdded += self.ColumnAdded
		

		self.dgv.AutoSizeRowsMode = DataGridViewAutoSizeRowsMode.DisplayedCellsExceptHeaders
		self.dgv.RowHeadersVisible = False
		self.dgv.AutoSizeRowsMode = DataGridViewAutoSizeRowsMode.DisplayedCellsExceptHeaders
		self.dgv.AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.Fill
		
		self.dgv.BorderStyle = BorderStyle.Fixed3D
		self.dgv.EditMode = DataGridViewEditMode.EditOnEnter
		self.dgv.Anchor = (AnchorStyles.Bottom | AnchorStyles.Left | AnchorStyles.Right)
		self.dgv.Dock = DockStyle.Fill
		self.dgv.AutoResizeColumns()
		self.dgv.ColumnHeadersDefaultCellStyle.Font = Font(self.dgv.ColumnHeadersDefaultCellStyle.Font, FontStyle.Bold)
		headerCellStyle = self.dgv.ColumnHeadersDefaultCellStyle.Clone()
		headerCellStyle.BackColor = Color.LightSkyBlue

		self.dgv.RowsDefaultCellStyle.BackColor = Color.White
		self.dgv.AlternatingRowsDefaultCellStyle.BackColor = Color.AliceBlue
		self.dgv.ColumnHeadersDefaultCellStyle = headerCellStyle
		self.dgv.AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.Fill
		self.dgv.Dock = DockStyle.Fill
		self.dgv.AutoResizeColumns()
		self.dgv.CellClick += self.cellClick
		self.dgv.CellValueChanged += self.cellChanged
		self.dgv.DataBindingComplete += self.DataBindingComplete
		
		#self.dgv.SelectionChanged += self.selectionChanged
		#self.dgv.DataBindingComplete += self.setSelectedRowsEvent	

		#self.columnNames = ("Priority", "Category", "Builtin Category or Class")
		self.columnNames = ("Order", "Layer comment")
		"""
		tableDicList, tableObjectList = self.getDataSources(self.priorityLookup)
		"""
		tableDicList, tableObjectList = self.getDataSources(self.commentLayers)
		#self.createDGVbyRows(tableDicList)
		self.createDGVbyDataSource(tableObjectList)
		#print("self.dgv.DataSource {0}".format(self.dgv.DataSource))
		
		

		self.infoLabel = Label()
		
		self.infoLabel.Height = 30
		self.infoLabel.TextAlign = ContentAlignment.MiddleLeft
		#self.infoLabel.Text = "wewe"
		self.infoLabel.AutoSize = True
		#elementType = doc.GetElement(self.selectedElement.GetTypeId())
		elementType = self.selectedElement.GetType()
		elTypeFamily = doc.GetElement(self.selectedElement.GetTypeId())
		print("Element type {0} - name() {1}".format(elementType, elementType.Name))
		self.infoLabel.Text = "{0} ({1}) - {2}.{3} - {4}".format(elementType.Name, elTypeFamily.FamilyName, self.elTypeMarkParamValue, self.elMarkParamValue, self.selectedElement.Name)
		self.infoLabel.Anchor = (AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right)
		# self.selectedElement.Name, doc.GetElement(self.selectedElement.GetTypeId()).Name)
		self.infoLabel.Location = (Point(0,0))
		self.inputTextPanel.Controls.Add(self.infoLabel)

		self.allInstancesChB = CheckBox()
		self.allInstancesChB.Text = "Apply to all instances ({0})".format(len(self.allInstances))
		self.allInstancesChB.Height = 30
		self.allInstancesChB.Width = 150
		self.allInstancesChB.AutoSize = True
		self.allInstancesChB.Location = (Point(10,30))
		self.allInstancesChB.CheckedChanged += self.allInstancesChanged
		self.allInstancesChB.Checked = True
		self.inputTextPanel.Controls.Add(self.allInstancesChB)


		self.confirmButton = Button()
		self.confirmButton.Text = "Confirm"
		self.confirmButton.Height = 30
		self.confirmButton.AutoSize = True
		self.confirmButton.Width = self.buttonPanel.Width/2	
		self.confirmButton.Click += self.confirmChanges

		self.resetButton = Button()
		self.resetButton.Text = "Reset Changes"
		self.resetButton.Height = 30
		self.resetButton.AutoSize = True
		self.resetButton.Width = self.buttonPanel.Width
		self.resetButton.Click += self.close
		
		#self.confirmButton.AutoSize = True
		#self.confirmButton.Dock = DockStyle.Top
		#self.confirmButton.Anchor = (AnchorStyles.Top | AnchorStyles.Left)
		self.buttonPanel.Controls.Add(self.confirmButton)
		self.buttonPanel.Controls.Add(self.resetButton)

		self.insertButton = Button()
		self.insertButton.Text = "INSERT ROW"
		self.insertButton.Height = 30
		self.insertButton.Click += self.insertDeleteRow
		self.insertButton.AutoSize = True
		self.insertButton.Width = self.buttonPanel.Width/2
		self.insertButton.Location = Point(0,30)
		
		#self.upButton.AutoSize = True
		#self.upButton.Dock = DockStyle.Left
		#self.upButton.Anchor = (AnchorStyles.Bottom| AnchorStyles.Right)
		self.buttonPanel.Controls.Add(self.insertButton)

		#self.downButton.AutoSize = True
		#self.downButton.Dock = DockStyle.Right
		#self.downButton.Anchor = (AnchorStyles.Bottom | AnchorStyles.Right)
		
		self.dgvPanel.Controls.Add(self.dgv)
		
		self.Controls.Add(self.dgvPanel)
		self.Controls.Add(self.inputTextPanel)
		self.Controls.Add(self.buttonPanel)

		self.insertButton.Width = self.buttonPanel.Width / 2

		self.deleteButton = Button()
		self.deleteButton.Text = "DELETE ROW"
		self.deleteButton.Height = 30
		self.insertButton.AutoSize = True
		self.deleteButton.Click += self.insertDeleteRow		
		
		self.deleteButton.Location = Point(0,0)
		self.deleteButton.Width = self.buttonPanel.Width/2		
		self.insertButton.Location = Point(self.buttonPanel.Width/2,0)
		self.confirmButton.Location = Point(self.buttonPanel.Width/2,self.deleteButton.Height)
		self.confirmButton.Width = self.buttonPanel.Width /2
		self.resetButton.Location = Point(0,self.deleteButton.Height)
		self.resetButton.Width = self.buttonPanel.Width /2
		self.infoLabel.Width = self.inputTextPanel.Width
		self.buttonPanel.Controls.Add(self.deleteButton)
		

		
	def getAllInstances(self, inElement):
		typeIntId = inElement.GetTypeId().IntegerValue
		allElementsIds = getAllElements(doc, inActiveView = False, toId = True)
		allInstances = []
		for elId in allElementsIds:
			el = doc.GetElement(elId)
			elTypeIntId = el.GetTypeId().IntegerValue
			#elIntId = elId.IntegerValue
			if elTypeIntId == typeIntId:
				allInstances.append(el)
		return allInstances

	def createDGVbyDataSource(self, inObjList):
		"""
		inObjList type: list of objects [object, object...]
		"""
		#bindingList = BindingList[object]()
		#for obj in inObjList:
		#	bindingList.Add(obj)
		self.dgv.DataSource = Clist[object](inObjList)
		for col in self.dgv.Columns:
			col.SortMode = DataGridViewColumnSortMode.Automatic
		#self.dgv.DataSource = bindingList

	''' def createDGVbyRows(self, inDicList):
		"""
		inDicList type: list of dictionaries [{"ab": "AB"}, {"cd":"CD"}, {"ef":"EF"}]
		"""
		if isinstance(inDicList, list):
			if len(inDicList) > 0:
				colNames = [x for x in inDicList[0].keys()]
				#print("colNames {}".format(colNames))
				self.dgv.ColumnCount = len(colNames)
				for j, colName in enumerate(colNames):
					self.dgv.Columns[j].Name = self.columnNames[j]
				for i,dic in enumerate(inDicList):
					rowValues = (dic[self.columnNames[0]], dic[self.columnNames[1]])
					self.dgv.Rows.Add(*rowValues)
				rowToDelete = self.dgv.Rows.GetLastRow(DataGridViewElementStates.None)
			else:
				raise IndexError("inDicList is empty list")
		else:
			raise TypeError("input argument inDicList not of type list") '''

	def getCommentLayers(self, inSelectedElement):
		returnStrList = []
		#self.paramName = "ALL_MODEL_INSTANCE_COMMENTS"
		markParamName = "ALL_MODEL_MARK"
		typeMarkParamName = "ALL_MODEL_TYPE_MARK"
		elParamValue = getValueByParameterName(inSelectedElement, self.paramName, doc)
		self.elMarkParamValue = getValueByParameterName(inSelectedElement, markParamName, doc, bip=DB.BuiltInParameter.ALL_MODEL_MARK)
		self.elTypeMarkParamValue = getValueByParameterName(inSelectedElement, typeMarkParamName, doc, bip=DB.BuiltInParameter.ALL_MODEL_TYPE_MARK)
		#print("elParamValue {0} - {1}".format(self.paramName, elParamValue))
		#print('Remove all spaces using RegEx:\n{0}'.format(re.sub("\s{2,50}", "", elParamValue)))
		separatedString = re.sub("\s{2,15}", "", elParamValue)
		#print("separatedString {0}".format(separatedString))
		strList = separatedString.split("- ")
		#print("strList {0}".format(strList))
		for i, line in enumerate(strList[1:]):
			strippedLine = line.strip()
			returnStrList.append(strippedLine)
		return returnStrList
			

	def getDataSources(self, inTableData):
		tableObjectList = []
		tableDicList = []
		''' #priorityCategoriesNames = getPriorityCategoriesNames(inTableData)
		elParamValue = getValueByParameterName(inTableData, self.paramName, doc)
		#print("{0} - {1}".format(self.paramName, elParamValue))
		#print('Remove all spaces using RegEx:\n{0}'.format(re.sub("\s{2,50}", "", elParamValue)))
		separatedString = re.sub("\s{2,15}", "", elParamValue)
		strList = separatedString.split("- ") '''
		for i, line in enumerate(inTableData):
			dic = {self.columnNames[0] : i, \
					self.columnNames[1] : line}
			print("{0} - {1}".format(i,line))
			rowObj = Dic2obj(dic)
			tableDicList.append(dic)
			tableObjectList.append(rowObj)

		"""
		for i,v in enumerate(inTableData):
			if not hasattr(v, "__iter__"):
				#print("toString {}".format(dir(v)))
				builtInPriorityCategory = str(v)
			else:
				builtInPriorityCategory = ", ".join([str(x) for x in v])
			priorityCategory = priorityCategoriesNames[i]
			dic = {self.columnNames[0] : i, \
					self.columnNames[1] : priorityCategory, \
					self.columnNames[2] : builtInPriorityCategory}
			rowObj = Dic2obj(dic)
			tableDicList.append(dic)
			tableObjectList.append(rowObj)
		"""
		return (tableDicList, tableObjectList)

	def DataBindingComplete(self, sender, event):
		self.arangeColumns()
		#for i, row in enumerate(self.dgv.Rows):
		#	row.Cells[1].OnDataGridViewChanged += self.cellChanged
		#self.dgv.Columns[1] += self.cellChanged
		#self.dgvPanel.AutoScroll = True
		#self.dgvPanel.Height = self.Height - self.buttonPanel.Height
		#self.dgv.Refresh()
		#print("DataBindingComplete {0} {1}".format(sender, event))	

	def arangeColumns(self):
		for col in self.dgv.Columns:
			if col.Name == self.columnNames[0]:
				#print("column {0} was updated".format(col.Name))
				col.SortMode = DataGridViewColumnSortMode.Programmatic
				col.DisplayIndex = 0
				col.ReadOnly = True
				col.Width = 65
			elif col.Name == self.columnNames[1]:
				#print("column {0} was updated".format(col.Name))
				col.SortMode = DataGridViewColumnSortMode.Programmatic
				col.DisplayIndex = 1
				col.ReadOnly = False

	def cellClick(self, sender, e):

		if e.RowIndex >=0:
			pass
			#print("{0} Row, {1} Column button clicked".format(e.RowIndex +1, e.ColumnIndex +1))

	def cellChanged(self, sender, event):
		print("changed RowIndex {0}".format(event.RowIndex))
		#print("dir(event {0} dir(sender) - {1} sender.Text {2})".format(dir(event), dir(sender), sender.Text))
		cellValue = self.dgv.Rows[event.RowIndex].Cells[0].Value
		self.commentLayers[event.RowIndex] = cellValue if cellValue else ""
		#tableDicList, tableObjectList = self.getDataSources(self.commentLayers)
		##self.createDGVbyRows(tableDicList)
		#self.createDGVbyDataSource(tableObjectList)

	def allInstancesChanged(self, sender, event):
		print("{0}".format(self.allInstancesChB.Checked))

	def update(self, sender, event):		
		self.dgv.Refresh()
		self.deleteButton.Width = self.buttonPanel.Width/2
		self.insertButton.Width = self.buttonPanel.Width/2
		self.confirmButton.Width = self.buttonPanel.Width/2
		self.confirmButton.Location = Point(self.buttonPanel.Width/2,self.deleteButton.Height)
		self.insertButton.Location = Point(self.buttonPanel.Width/2,0)
		self.resetButton.Location = Point(0,self.deleteButton.Height)
		self.resetButton.Width = self.buttonPanel.Width /2
		self.infoLabel.Width = self.inputTextPanel.Width
		#self.buttonPanel.Height = 120
		#self.dgvPanel.Height = self.Height - self.buttonPanel.Height

	def confirmChanges(self, sender, event):
		returnStrList = []
		for i, line in enumerate(self.commentLayers):
			newLine = "- {0: <140}".format(line)
			print(newLine)
			returnStrList.append(newLine)
		
		returnStr = "".join(returnStrList)
		t = Transaction(doc, "Set the parameter {0} value to element {1}".format(self.paramName, self.selectedElement.Id))
		
		if self.allInstancesChB.Checked:			
			#allInstances = DB.FilteredElementCollector(doc).WherePasses(ElementParameterFilter(FilterElementIdRule())).ToElements()
			#transaction Start
			t.Start()
			for el in self.allInstances:
				setValueByParameterName(el, returnStr, self.paramName, doc)
				print("Parameter comments has been updated for element {1} {0} ".format(el.Name, el.Id.IntegerValue))
				#time.sleep(3)
			#transaction Commit
			t.Commit()
		#transaction Start
		t.Start()
		setValueByParameterName(self.selectedElement, returnStr, self.paramName, doc)
		#transaction Commit
		t.Commit()
		#time.sleep(3)
		print("Parameter comments has been updated for element {1} {0} ".format(self.selectedElement.Name, self.selectedElement.Id.IntegerValue))
		self.Close()


	def insertDeleteRow(self, sender, e):
		#print("sender.Name {0}, e {1}".format(sender.Text, e))
		if sender.Text == "INSERT ROW":
			insert = True
			delete = False
		elif sender.Text == "DELETE ROW":
			insert = False
			delete = True
		else:
			insert = False
			delete = False
		movementDone = False
		insertDone = False
		deleteDone = False
		selectedRow = self.dgv.SelectedRows
		#print("selectedRow.Index {0}".format(selectedRow[0].Index if len(selectedRow)>0 else None))
		if len(selectedRow) > 0:
			if insert:
				if selectedRow[0].Index < len(self.commentLayers):
					self.commentLayers.insert(selectedRow[0].Index + 1, "")
					holderIndex = selectedRow[0].Index + 1 
					''' holder = self.commentLayers[][upperIndex]
					self.priorityLookup[upperIndex] = self.priorityLookup[selectedRow[0].Index]
					self.priorityLookup[selectedRow[0].Index] = holder'''
					insertDone = True 
				else:
					holderIndex = None
					insertDone = False
				#print("self.priorityLookup {}".format(self.priorityLookup))
			elif delete:
				if self.dgv.RowCount > 1 and selectedRow[0].Index < len(self.commentLayers):
					self.commentLayers.pop(selectedRow[0].Index)
					holderIndex = selectedRow[0].Index
					deleteDone = True
				else:
					holderIndex = None
			''' else:
				if selectedRow[0].Index < len(self.priorityLookup) -1:
					belowIndex = selectedRow[0].Index + 1
					holder = self.priorityLookup[belowIndex]
					self.priorityLookup[belowIndex] = self.priorityLookup[selectedRow[0].Index]
					self.priorityLookup[selectedRow[0].Index] = holder
					movementDone = True '''
		else:
			holderIndex = None
		#print("self.priorityLookup {}".format(self.priorityLookup))
		newObjList = self.getDataSources(self.commentLayers)[1]
		self.dgv.DataSource = Clist[object](newObjList)
		#self.dgv.SelectedRows.Clear()
		if holderIndex:
			for i, row in enumerate(self.dgv.Rows):
				if insert and insertDone:
					if i == holderIndex:
						row.Selected = True
					else:
						row.Selected = False
				elif delete and deleteDone:
					if i == holderIndex-1:
						row.Selected = True
					else:
						row.Selected = False
				else:
					row.Selected = False
		#print("sender dir {0}".format(dir(sender)))

	"""
	def itemUp(self, sender, e):
		#print("sender.Name {0}, e {1}".format(sender.Text, e))
		if sender.Text == "UP":
			up = True
		else:
			up = False
		movementDone = False
		selectedRow = self.dgv.SelectedRows
		#print("selectedRow.Index {0}".format(selectedRow[0].Index if len(selectedRow)>0 else None))
		if len(selectedRow) > 0:
			if up:
				if selectedRow[0].Index > 0:
					upperIndex = selectedRow[0].Index - 1
					holder = self.priorityLookup[upperIndex]
					self.priorityLookup[upperIndex] = self.priorityLookup[selectedRow[0].Index]
					self.priorityLookup[selectedRow[0].Index] = holder
					movementDone = True
				#print("self.priorityLookup {}".format(self.priorityLookup))
			else:
				if selectedRow[0].Index < len(self.priorityLookup) -1:
					belowIndex = selectedRow[0].Index + 1
					holder = self.priorityLookup[belowIndex]
					self.priorityLookup[belowIndex] = self.priorityLookup[selectedRow[0].Index]
					self.priorityLookup[selectedRow[0].Index] = holder
					movementDone = True
				#print("self.priorityLookup {}".format(self.priorityLookup))
		newObjList = self.getDataSources(self.priorityLookup)[1]
		self.dgv.DataSource = Clist[object](newObjList)
		#self.dgv.SelectedRows.Clear()
		for i, row in enumerate(self.dgv.Rows):
			if up and movementDone:
				if i == upperIndex:
					row.Selected = True
				else:
					row.Selected = False
			elif not up and movementDone:
				if i == belowIndex:
					row.Selected = True
				else:
					row.Selected = False
			else:
				row.Selected = False
		#print("sender dir {0}".format(dir(sender)))
	"""
	def updateInfoLabel(self, inText):
		self.infoLabel.Text = str(inText)

	def close(self, sender, event):
		"""
		priorityLookup = self.priorityLookup
		"""
		self.confirmed = True
		self.Close()

class InfoDialog(Form):
	def __init__(self, **kwargs):
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
		self.infoText = kwargs['infoText'] if 'infoText' in kwargs else ""
		self.showSelectionButton = kwargs['showSelectionButton'] if 'showSelectionButton' in kwargs else False
		self.selectedElements = []
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
		self.Text = self.infoText
		self.Width = 500
		self.Height = 100
		self.StartPosition = FormStartPosition.CenterScreen
		self.TopMost = True
		self.Resize += self.configureButtons

		self.buttonFrame = Panel()
		self.buttonFrame.Parent = self
		self.buttonFrame.Anchor = AnchorStyles.Top
		self.buttonFrame.Dock = DockStyle.Bottom
		self.buttonFrame.Height = 30
		

		self.selectButton = Button()
		self.selectButton.Text = 'Select'
		self.selectButton.Location = Point(25, 125)
		self.selectButton.Click += self.doSelection
		self.selectButton.Width = self.Width/2
		self.selectButton.Parent = self.buttonFrame
		#self.submitButton.Anchor = AnchorStyles.Right
		self.selectButton.Dock = DockStyle.Right

		self.closeButton = Button()
		self.closeButton.Text = 'Cancel'
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
		self.textFrame.Height = 55

		#self.Controls.Add(self.textFrame)
		#self.Controls.Add(self.buttonFrame)		

		''' self.scheduleViewCB = ComboBox()
		self.scheduleViewCB.Width = 150
		self.scheduleViewCB.Parent = self.textFrame
		self.scheduleViewCB.Location = Point(0,50)
		self.scheduleViewCB.Anchor = AnchorStyles.Top
		self.scheduleViewCB.Dock = DockStyle.Top
		self.scheduleViewCB.Items.AddRange(tuple(self.scheduleNames))
		self.scheduleViewCB.Focus() '''
		
		
		#self.parameterCB.SelectionChangeCommitted += self.OnChanged
		''' self.scheduleViewCB.Text = self.scheduleNames[0]
		self.scheduleViewCB.DropDownStyle = ComboBoxStyle.DropDown '''

		self.parameterCBLabel = Label()
		self.parameterCBLabel.Text = "Please select one element:"
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
		''' selectedScheduleViewName = self.scheduleViewCB.SelectedItem
		uidoc.ActiveView = self.scheduleViewDict[selectedScheduleViewName] '''
		self.Close()
	def doSelection(self, sender, event):
		self.Hide()
		
		#self.selectedElements = [doc.GetElement(x.ElementId) for x in __revit__.ActiveUIDocument.Selection.PickObjects(ObjectType.Element)]
		self.selectedElements = [doc.GetElement(__revit__.ActiveUIDocument.Selection.PickObject(ObjectType.Element).ElementId)]
		print("len(selectedElements) {0} - {1}".format(len(self.selectedElements), self.selectedElements))
		if runFromCsharp == False:
			openedForms = list(Application.OpenForms)
			infotext = ""
			rpsOpenedForms = []
			for i, oForm in enumerate(openedForms):
				#print(str(i))
				#print(oForm)
				infotext += "; {}".format(oForm)
				if "RevitPythonShell" in str(oForm):
					#print("Totot je oForm {0}".format(oForm))
					rpsOutput = oForm.Show()
					rpsOpenedForms.append(oForm)
				else:
					rpsOutput = None
			#self.infoLabel2.Text = infotext
			if len(rpsOpenedForms) > 0:
				lastForm = rpsOpenedForms[-1]
				lastForm.Show()
				if len(rpsOpenedForms) > 1:
					rpsOFormsToClose = rpsOpenedForms[:-1]
					for oFormToClose in rpsOFormsToClose:
						oFormToClose.Close()
				lastForm.Show()
				self.Close()
				#lastForm.Close()
		else:
			lastForm = None
			self.Close()
		
		

	def configureButtons(self, sender, event):
		''' self.scheduleViewCB.Focus() '''
		self.closeButton.Width = self.buttonFrame.Width/2
		self.selectButton.Width = self.buttonFrame.Width/2
		#self.textFrame.Width = self.buttonFrame.Width


	def close(self, sender, event):
		self.Close()
#i=0
#while len(mySelection) == 0 or i < 2:

	#i += 1

if len(mySelection) == 0:	
	print("len(mySelection) {0} - {1}".format(len(mySelection), mySelection))
	myDialogWindow = InfoDialog(infoText = "Selection error", showSelectionButton = True)
	Application.Run(myDialogWindow)
	mySelection = myDialogWindow.selectedElements
	if len(mySelection) > 0:
		myDialog = TaskDialog("Selection OK");
		elType = mySelection[0].GetType()
		myDialog.MainInstruction = "Element {0} Selected".format(elType.Name)
		myDialog.Show();
		mainWindow = MainForm(mySelection[0])
		Application.Run(mainWindow)
	else:
		myDialog = TaskDialog("Selection error");
		myDialog.MainInstruction = "No element Selected"
		myDialog.Show();
	''' Application.Exit()
	
	print("oneElement dialog len(mySelection) {0} - {1}".format(len(mySelection), mySelection))
	paramName = "ALL_MODEL_INSTANCE_COMMENTS"
	elParamValue = getValueByParameterName(mySelection[0], paramName, doc)
	print("{0} - {1}".format(paramName, elParamValue))
	infoWindow = InfoDialog(infoText = "{0} - {1}".format(paramName, elParamValue), showSelectionButton = True)
	Application.Run(infoWindow)
	openedForms = list(Application.OpenForms)
	rpsOpenedForms = []
	for i, oForm in enumerate(openedForms):
		if "RevitPythonShell" in str(oForm):
			oForm.Show()
	#mySelection = myDialogWindow.selectedElements '''
	print("after selection one element dialog len(mySelection) {0} - {1}".format(len(mySelection), mySelection))

elif len(mySelection) == 1:
	print("oneElement dialog len(mySelection) {0} - {1}".format(len(mySelection), mySelection))
	mainWindow = MainForm(mySelection[0])
	Application.Run(mainWindow)
	''' paramName = "ALL_MODEL_INSTANCE_COMMENTS"
	elParamValue = getValueByParameterName(mySelection[0], paramName, doc)
	print("{0} - {1}".format(paramName, elParamValue))
	print('Remove all spaces using RegEx:\n{0}'.format(re.sub("\s{2,50}", "", elParamValue)))
	separatedString = re.sub("\s{2,15}", "", elParamValue)
	strList = separatedString.split("- ")
	for i, line in enumerate(strList[1:]):
		print("{0} - {1}".format(i,line.strip())) '''
else:
	print("use multiElement dialog len(mySelection) {0} - {1}".format(len(mySelection), mySelection))

openedForms = list(Application.OpenForms)
rpsOpenedForms = []
for i, oForm in enumerate(openedForms):
	if "RevitPythonShell" in str(oForm):
		oForm.Hide()
		rpsOpenedForms.append(oForm)

if len(rpsOpenedForms) > 0:
	lastForm = rpsOpenedForms[-1]
	lastForm.Hide()
	if len(rpsOpenedForms) > 1:
		rpsOFormsToClose = rpsOpenedForms[:-1]
		print("Script was cancelled")
		#time.sleep(5)
		for oFormToClose in rpsOFormsToClose:
			oFormToClose.Close()

#if runFromCsharp == False or "rpsOutput" in dir():
#	if rpsOutput:
#		rpsOutput.Show()
