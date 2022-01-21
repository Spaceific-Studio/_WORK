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
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)
lib_path = r'H:\_WORK\PYTHON\REVIT_API\LIB'
sys.path.append(lib_path)
import os
#if "Windows" in platform.uname():
	#lib_path = r'H:/_WORK/PYTHON/LIB'

try:
	sys.modules['__main__']
	hasMainAttr = True	
except:
	hasMainAttr = False

from RevitSelection import getFamilyInstancesByName, getValuesByParameterName, setValuesByParameterName, filterElementsByActiveViewIds, getAllElements

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

class TabForm(Form):
	selectedRowIndices = []
	selectedRowStrIds = []
	userSelectedStrIds = []
	userSelectedRowIndices = []

	def __init__(self, tableData, elements, parameterName, inUserSelectedStrIds):
		self.initialSetup = True
		if hasMainAttr:
			try:
				#if script runs within C# IronPython hosting environment
				cwd = __scriptDir__
			except Exception as ex:
				#if script runs within RevitPythonShell environment
				cwd = "\\".join(__file__.split("\\")[:-1]) + "LIB\\"
		else:
			cwd = os.getcwd()
		self.scriptDir = "\\".join(__file__.split("\\")[:-1]) 
		print("script directory: {}".format(self.scriptDir))
		iconFilename = os.path.join(self.scriptDir, 'spaceific_64x64_sat_X9M_icon.ico')
		icon = Icon(iconFilename)
		self.Icon = icon	

		self.tableData = tableData
		self.elements = elements
		self.elementsNumber = len(self.elements)
		self.parameterName = parameterName
		self.parameter = nameToParamDic[self.parameterName]
		#self.strSelectedIdsHolder = []
		TabForm.userSelectedStrIds = inUserSelectedStrIds
		#self.ControlAdded += self.control_Added
		self.cCount = 0
		
		self.InitializeComponent()
		
	def InitializeComponent(self):
		self.Text = "Table of elements with selected parameter: " + self.parameterName
		self.Width = 1200
		self.Height = 800
		self.StartPosition = FormStartPosition.CenterScreen
		self.TopMost = True
		self.filteredElements = 0
		
		self.setupDataGridView()		
		
	def setupDataGridView(self):
		self.dgvPanel = Panel()
		self.dgvPanel.Dock = DockStyle.Fill
		self.dgvPanel.AutoSize = False
		self.dgvPanel.AutoSizeMode = AutoSizeMode.GrowAndShrink
		self.dgvPanel.AutoScroll = True

		self.inputTextPanel = Panel()
		self.inputTextPanel.Dock = DockStyle.Bottom
		self.inputTextPanel.AutoSize = True
		self.inputTextPanel.Name = "Button Panel"
		self.inputTextPanel.AutoSizeMode = AutoSizeMode.GrowAndShrink
		self.inputTextPanel.AutoScroll = True
		self.inputTextPanel.BackColor = Color.White

		self.buttonPanel = Panel()
		self.buttonPanel.Dock = DockStyle.Bottom
		self.buttonPanel.AutoSize = True
		self.buttonPanel.Name = "Button Panel"
		self.buttonPanel.Height = 80
		self.buttonPanel.AutoSizeMode = AutoSizeMode.GrowAndShrink
		self.buttonPanel.AutoScroll = True
		self.buttonPanel.BackColor = Color.White
		#self.buttonPanel.ControlAdded += self.control_Added
		
		self.dgv = DataGridView()
		self.dgv.SelectionMode = DataGridViewSelectionMode.FullRowSelect
		#self.dgv.AutoGenerateColumns = True
		self.dgv.ColumnAdded += self.ColumnAdded

		self.dgv.AutoSizeRowsMode = DataGridViewAutoSizeRowsMode.DisplayedCellsExceptHeaders
		self.dgv.RowHeadersVisible = False
		self.dgv.AutoSizeRowsMode = DataGridViewAutoSizeRowsMode.DisplayedCellsExceptHeaders
		self.dgv.BorderStyle = BorderStyle.Fixed3D
		self.dgv.EditMode = DataGridViewEditMode.EditOnEnter
		self.dgv.Anchor = (AnchorStyles.Bottom | AnchorStyles.Left | AnchorStyles.Right)
		#self.dgv.Dock = DockStyle.Fill
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
		self.dgv.ColumnHeaderMouseClick += self.ColumnHeaderMouseClick
		self.dgv.SelectionChanged += self.selectionChanged
		self.dgv.DataBindingComplete += self.DataBindingComplete
		#self.markBip = getBuiltInParameterInstance("ALL_MODEL_MARK")
		#self.typeMarkBip = getBuiltInParameterInstance("ALL_MODEL_TYPE_MARK")

		self.columnNames = ("Element_Id", "Category", "Element_Name", "parameter_{}".format(self.parameterName), "Mark", "Type mark")
		self.columnAscendingSort = {}
		for colName in self.columnNames:
			self.columnAscendingSort[colName] = True

		
		""" bipNames = Enum.GetNames(BuiltInParameter)
		bipNamesStr = []
		bipParsed = []
		for i, bipName in enumerate(bipNames):
			bipP = Enum.TryParse(bipName, BuiltInParameter)
			bipParsed.append(bipP)
			bipNamesStr.append(bipName)
		bipNamesStrSorted = sorted(bipNamesStr)
		for i, bP in bipParsed:
			print("bipParsed {0} - {1} - {2}".format(i, bP, type(bP)))
		for i, bipNameStr in enumerate(bipNamesStrSorted):
			print("bipNames {0} - {1}".format(i, bipNameStr))
		bips = Enum.GetValues(BuiltInParameter)
		bipsStr = []
		for i, bip in enumerate(bips):
			bipsStr.append(bip.ToString())
			#print("{0} - {1} - {2}".format(i, bip.ToString(), type(bip)))
			if bip.ToString() == "EDITED_BY":
				print("EDITED_BY- {0}".format(i))
		bipsStrSorted = sorted(bipsStr)
		for bipStr in bipsStrSorted:
			print("{}".format(bipStr))
		raise TypeError("sss") """

		self.values = getValuesByParameterName(self.elements, self.parameterName, doc)
		self.markBip = BuiltInParameter.ALL_MODEL_MARK
		self.typeMarkBip = BuiltInParameter.ALL_MODEL_TYPE_MARK
		self.markValues = getValuesByParameterName(self.elements, "ALL_MODEL_MARK", doc, bip = self.markBip)
		self.typeMarkValues = getValuesByParameterName(self.elements, "ALL_MODEL_TYPE_MARK", doc, bip = self.typeMarkBip)
		#for i, value in enumerate(self.markValues):
			#print("self.markValues {0} - {1}".format(i, value))
		#for i, value in enumerate(self.typeMarkValues):
			#print("self.typeMarkValues {0} - {1}".format(i, value))
		""" tableObjectList = []
		tableDicList = []
		for i,v in enumerate(self.elements):
			elId = v.Id.ToString()
			elCategory = "{}".format(v.Category.Name)
			parameterValue = "{}".format(self.values[i])
			elName = "{}".format(v.Name if hasattr(v, "Name") else v.FamilyName)
			dic = {self.columnNames[0] : elId, \
											self.columnNames[1] : elCategory, \
											self.columnNames[2] : elName, \
											self.columnNames[3] : parameterValue}
			rowObj = Dic2obj(dic)
			tableDicList.append(dic)
			tableObjectList.append(rowObj) """
		
		print("setDataSources 1")
		tableDicList, tableObjectList = self.getDataSources(self.elements)
		""" for i, obj in enumerate(tableObjectList):
			print("{0} - {1} - {2} - {3}".format(i, obj.Element_Id, obj.Category, obj.Element_Name)) """

		""" for col in self.dgv.Columns:
			col.SortMode = DataGridViewColumnSortMode.Automatic """
		#self.dgv.DataSource = Clist[object](tableObjectList)
		
		#print("tableDicList - {}".format(tableDicList))
		
		self.createDGVbyDataSource(tableObjectList)
		self.isolateButton = Button()
		self.isolateButton.Text = "Isolate selected elements"
		self.isolateButton.Height = 30
		self.isolateButton.Click += self.isolateSelectedElements
		self.isolateButton.Location = Point(0,30)
		self.isolateButton.AutoSize = True
		self.buttonPanel.Controls.Add(self.isolateButton)

		self.setParameterButton = Button()
		self.setParameterButton.Text = "Set Value For Selected"
		self.setParameterButton.Height = 60
		self.setParameterButton.Click += self.setParametersOfSelected
		self.buttonPanel.Controls.Add(self.setParameterButton)

		self.setParameterTextBox = TextBox()
		#self.setParameterTextBox.FontHeight = 20
		self.setParameterTextBox.Height = 100
		self.setParameterTextBox.Text = "Text"
		self.setParameterTextBox.Name = "setParameterTextBox"
		self.setParameterTextBox.ScrollBars = ScrollBars.Vertical
		self.setParameterTextBox.Location = Point(0,0)
		self.setParameterTextBox.Multiline = True
		self.setParameterTextBox.KeyDown += self.setParameterSubmit

		#self.buttonPanel.Controls.Add(self.setParameterTextBox)		
		self.dgvPanel.Controls.Add(self.dgv)
		self.inputTextPanel.Controls.Add(self.setParameterTextBox)

		self.Controls.Add(self.dgvPanel)
		self.Controls.Add(self.inputTextPanel)
		self.Controls.Add(self.buttonPanel)
		

		#self.isolateButton.Width = self.buttonPanel.Width
		self.setParameterButton.Width = self.buttonPanel.Width / 2
		self.setParameterButton.Location = Point(self.buttonPanel.Width/2,0)
		self.setParameterTextBox.Width = self.buttonPanel.Width
		self.isolateButton.Width = self.buttonPanel.Width / 2
		self.setParameterTextBox.Location = Point(0,0)

		
		#self.createDGVbyRows(tableDicList)

		self.testButton = Button()
		self.testButton.Text = "Select and return"
		self.testButton.Height = 30
		self.testButton.Location = Point(0,0)
		self.testButton.Click += self.selectAndReturn

		self.testButton.Width = self.buttonPanel.Width / 2
		self.buttonPanel.Controls.Add(self.testButton)	
		#self.setParameterButton.Enabled = False
		#self.setParameterButton.Enabled = True
		


	def createDGVbyDataSource(self, inObjList):
		"""
		inObjList type: list of objects [object, object...]
		"""
		self.dgv.DataSource = Clist[object](inObjList)


	def createDGVbyRows(self, inDicList):
		"""
		inDicList type: list of dictionaries [{"ab": "AB"}, {"cd":"CD"}, {"ef":"EF"}]
		"""
		if isinstance(inDicList, list):
			if len(inDicList) > 0:
				colNames = [x for x in inDicList[0].keys()]
				print("colNames {}".format(colNames))
				self.dgv.ColumnCount = len(colNames)
				for j, colName in enumerate(colNames):
					self.dgv.Columns[j].Name = self.columnNames[j]
				for i,dic in enumerate(inDicList):
					rowValues = (dic[self.columnNames[0]], dic[self.columnNames[1]], dic[self.columnNames[2]], dic[self.columnNames[3]])
					#cRows.Item[cRows.Count - 1].CreateCells(self.dgv,Clist[dict](dic))

					self.dgv.Rows.Add(*rowValues)
			
				rowToDelete = self.dgv.Rows.GetLastRow(DataGridViewElementStates.None)
			else:
				raise IndexError("inDicList is empty list")
		else:
			raise TypeError("input argument inDicList not of type list")

	def getDataSources(self, inTableData, **kwargs):
		tableObjectList = []
		tableDicList = []
		sortColumnIndex = kwargs["sortColumnIndex"] if "sortColumnIndex" in kwargs else None		
		for i,v in enumerate(inTableData):
			elId = v.Id.ToString()
			elCategory = "{}".format(v.Category.Name)
			parameterValue = "{}".format(self.values[i])
			markValue = "{}".format(self.markValues[i])
			typeMarkValue = "{}".format(self.typeMarkValues[i])
			elName = "{}".format(v.Name if hasattr(v, "Name") else v.FamilyName)
			dic = {self.columnNames[0] : elId, \
											self.columnNames[1] : elCategory, \
											self.columnNames[2] : elName, \
											self.columnNames[3] : parameterValue, \
											self.columnNames[4] : markValue, \
											self.columnNames[5] : typeMarkValue}
			rowObj = Dic2obj(dic)
			tableDicList.append(dic)
			tableObjectList.append(rowObj)
		if sortColumnIndex >=0:
			sortColumnName = self.dgv.Columns[sortColumnIndex].Name
			#print("Sorting columnIndex {0} - columnName {1}".format(sortColumnIndex, sortColumnName))
			#print("Current ascending direction of column {0} - {1}".format(sortColumnName, self.columnAscendingSort[sortColumnName]))
			tableObjectListSorted = sorted(tableObjectList[:], key = attrgetter(sortColumnName), reverse = self.columnAscendingSort[sortColumnName])
			tableDicListSorted = sorted(tableDicList[:], key= lambda x: x[sortColumnName], reverse = self.columnAscendingSort[sortColumnName])
			self.columnAscendingSort[sortColumnName] = not self.columnAscendingSort[sortColumnName]
			#print("New ascending direction of column {0} - {1}".format(sortColumnName, self.columnAscendingSort[sortColumnName]))
			#return (tableDicList.sort(key= lambda x: x[sortColumnName]) ,tableObjectList.sort(key = attrgetter(sortColumnName)))
			return (tableDicListSorted , tableObjectListSorted)
		else:
			return (tableDicList, tableObjectList)

	def control_Added(self, sender, e):
		print("The control named " + e.Control.Text + " has been added to the form.")
		#if e.Control.Name == "Button Panel":
		#	self.setSelectedRows()

	def selectAndReturn(self, sender, event):
		elNames = []
		selectedElements = []
		selectedElementsId = []
		strIds = []
		for i,row in enumerate(self.dgv.SelectedRows):
			elementName = self.dgv.Rows[row.Index].Cells[self.elementNameColumnIndex].FormattedValue
			#print("X SelectionChanged Rows[row.Index].Cells[2].FormattedValue - {}".format(elementName))
			if elementName not in elNames:
				elNames.append(elementName)
			strId = self.dgv.Rows[row.Index].Cells[self.idColumnIndex].FormattedValue
			elId = viewElementsIdsDict[strId]
			strIds.append(strId)
			#print("SelectionChanged viewElementsIdsDict[self.dgv.Rows[row.Index].Cells[1].FormattedValue] - {}".format(elId))
			selectedElements.append(doc.GetElement(elId))
			selectedElementsId.append(elId)
			TabForm.selectedRowIndices.append(row.Index)
			TabForm.selectedRowStrIds.append(self.dgv.Rows[row.Index].Cells[self.idColumnIndex].FormattedValue)
		
		#print("SelectionChanged selectedElementsId - {}".format(selectedElementsId))
		elementIdsCol = Clist[ElementId](selectedElementsId)
		uidoc.Selection.SetElementIds(elementIdsCol)
		MainForm.selectedRowStrIds = strIds
		print("MainForm.selectedRowStrIds {}".format(MainForm.selectedRowStrIds))
		self.Close()

	def DataBindingComplete(self, sender, event):
		self.arangeColumns()
		TabForm.userSelectedRowIndices = self.getRowIndiciesFromStrIds(TabForm.userSelectedStrIds)
		TabForm.selectedRowIndices = self.getRowIndiciesFromStrIds(TabForm.selectedRowStrIds)
		print("DataBindingComplete {0} {1}".format(sender, event))
		#self.markSelected()
		TabForm.selectedRowStrIds = MainForm.selectedRowStrIds
		self.dgv.ClearSelection()

		self.setSelectedRows()
		self.initialSetup = False
		
	
	def ColumnHeaderMouseClick(self, sender, event):
		#print("ColumnHeader {0} was clicked".format(event.ColumnIndex))
		#tableDicList, tableObjectList = self.getDataSources(self.ids, sortColumnIndex = event.ColumnIndex)
		print("Column.DisplayIndex {0} - ColumnIndex {1}".format(self.dgv.Columns[event.ColumnIndex].DisplayIndex, event.ColumnIndex))
		print("ColumnHeaderMouseClick TabForm.selectedRowStrIds {0}".format(TabForm.selectedRowStrIds[:]))
		MainForm.selectedRowStrIds = TabForm.selectedRowStrIds[:]
		tableDicList, tableObjectList = self.getDataSources(self.elements, sortColumnIndex = event.ColumnIndex)
		""" for item in tableObjectList:
			print("{0} - {1} - {2}".format(item.Num, item.Id, item.Category)) """
		""" for item in tableDicList:
			print("{0} - {1} - {2}".format(item["Num"], item["Id"], item["Category"])) """
		#self.createDGVbyRows(tableDicList)
		#self.selectedRowsHolder = self.dgv.SelectedRows
				
		#print("idColumnIndex {0}".format(self.idColumnIndex))
		#self.selectedRowsIds = [self.dgv.Rows[x.Index].Cells[self.idColumnIndex].FormattedValue for x in self.dgv.SelectedRows]
		#print("selectedRowsIds {0}".format(self.selectedRowsIds))		
		self.dgv.DataSource = tableObjectList

	def arangeColumns(self):
		for col in self.dgv.Columns:
			if col.Name == self.columnNames[0]:
				print("column {0} was updated".format(col.Name))
				col.SortMode = DataGridViewColumnSortMode.Programmatic
				col.DisplayIndex = 0
				col.ReadOnly = True
			elif col.Name == self.columnNames[1]:
				print("column {0} was updated".format(col.Name))
				col.SortMode = DataGridViewColumnSortMode.Programmatic
				col.DisplayIndex = 3
				col.ReadOnly = True
			elif col.Name == self.columnNames[2]:
				print("column {0} was updated".format(col.Name))
				col.SortMode = DataGridViewColumnSortMode.Programmatic
				col.DisplayIndex = 4
				col.ReadOnly = True
			elif col.Name == self.columnNames[3]:
				print("column {0} was updated".format(col.Name))
				col.SortMode = DataGridViewColumnSortMode.Programmatic
				col.DisplayIndex = 5
				col.ReadOnly = True
			elif col.Name == self.columnNames[4]:
				print("column {0} was updated".format(col.Name))
				col.SortMode = DataGridViewColumnSortMode.Programmatic
				col.DisplayIndex = 1
				col.ReadOnly = True
			elif col.Name == self.columnNames[5]:
				print("column {0} was updated".format(col.Name))
				col.SortMode = DataGridViewColumnSortMode.Programmatic
				col.DisplayIndex = 2
				col.ReadOnly = True
			

	def getRowIndiciesFromStrIds(self, inStrIds):
		returnIndicies = []
		for row in self.dgv.Rows:
			#print("row.Cells[self.dgv.Columns[self.columnNames[0]].Index].FormattedValue {}".format(row.Cells[self.dgv.Columns[self.columnNames[0]].Index].FormattedValue))
			if row.Cells[self.idColumnIndex].FormattedValue in inStrIds:
				returnIndicies.append(row.Index)
		return returnIndicies

	def markSelected(self):
		for i, row in enumerate(self.dgv.Rows):
			currentId = row.Cells[self.idColumnIndex].FormattedValue
			if currentId in MainForm.selectedRowStrIds:
				self.dgv.Rows[i].Selected = True
			else:
				self.dgv.Rows[i].Selected = False

	def setSelectedRows(self):
		#print("TabForm.selectedRowIndices {}".format(TabForm.selectedRowIndices))
		""" for i, r in enumerate(self.dgv.Rows):
			# print("ElId {0}".format(self.dgv.Rows[i].Cells[1].FormattedValue))
			if self.dgv.Rows[i].Cells[self.idColumnIndex].FormattedValue in viewSelectionIdStrings:	
				TabForm.selectedRowIndices.append(i) """
		#print("TabForm.selectedRowIndices {}".format(TabForm.selectedRowIndices))
		#print("TabForm.userSelectedStrIds {}".format(TabForm.userSelectedStrIds))
		print("setSelectedRows - TabForm.userSelectedRowIndices {}".format(TabForm.userSelectedRowIndices))
		print("setSelectedRows - TabForm.selectedRowIndicies {}".format(TabForm.selectedRowIndices))
		
		
		self.markSelected()
		
		#self.dgv.ClearSelection()
		print("Rows Count {}".format(self.dgv.Rows.Count))
		""" brightRow = self.dgv.DefaultCellStyle.Clone()
		brightRow.BackColor = Color.White
		darkRow = self.dgv.DefaultCellStyle.Clone()
		darkRow.BackColor = Color.AliceBlue """
		selectedRow = self.dgv.DefaultCellStyle.Clone()
		selectedRow.BackColor = Color.Orange
		
		for i in TabForm.userSelectedRowIndices:
			self.dgv.Rows[i].DefaultCellStyle = selectedRow
		
		if self.parameter.IsReadOnly or self.parameter.StorageType == StorageType.ElementId:
			self.setParameterButton.Enabled = False
			self.setParameterTextBox.Enabled = False
			self.dgv.Columns[self.columnNames[3]].ReadOnly = True
		else:
			self.setParameterButton.Enabled = True
			self.setParameterTextBox.Enabled = True

	def setParameterSubmit(self, sender, event):
		#print("key was pressed in {0}, dir(event): {1}".format(sender.Name, dir(event)))
		print("key was pressed in {0}, dir(event): {1}".format(sender.Name, event.KeyValue))
		if event.KeyValue == 13:
			self.setParametersOfSelected(self.setParameterTextBox, event)

	def cellClick(self, sender, e):
		if e.RowIndex >=0:
			print("{0} Row, {1} Column button clicked".format(e.RowIndex +1, e.ColumnIndex +1))
			for x in self.elements:
				if x.Id.ToString() == "{0}".format(self.dgv.Rows[e.RowIndex].Cells[self.idColumnIndex].FormattedValue):
					elId = [x.Id]
				else:
					elId = []
			elementsCol = Clist[ElementId](elId)
			#uidoc.Selection.SetElementIds(elementsCol)

	def isolateSelectedElements(self, sender, event):
		if sender.Text == "Isolate selected elements":
			iDs = []
			for row in self.dgv.SelectedRows:
				for x in self.elements:
					if x.Id.ToString() == "{0}".format(self.dgv.Rows[row.Index].Cells[self.idColumnIndex].FormattedValue):
						iDs.append(x.Id)
				print("Isolated element on row {0} Id {1}".format(row.Index, self.dgv.Rows[row.Index].Cells[self.idColumnIndex].Value))
			elementIdsCol = Clist[ElementId](iDs)
			t = Transaction(doc, "Temporary Isolate Selected Elements")
			#transaction Start
			t.Start()
			uidoc.ActiveView.IsolateElementsTemporary(elementIdsCol)
			#uidoc.ShowElements(elementIdsCol)
			uidoc.Selection.SetElementIds(elementIdsCol)
			sender.Text = "Restore Isolation"
			#transaction commit
			t.Commit()
		else:
			t = Transaction(doc, "End Isolation Mode Elements")
			t.Start()
			uidoc.ActiveView.TemporaryViewModes.DeactivateAllModes()
			#uidoc.Selection.Clear()
			sender.Text = "Isolate selected elements"
			t.Commit()
		myDialogWindow.Close()

	def updateDGV(self):		
		#print("len(self.dgv.SelectedRows) {}".format(len(self.dgv.SelectedRows)))
		self.values = getValuesByParameterName(self.elements, self.parameterName, doc)
		idValueDic = {}
		for i, el in enumerate(self.elements):
			idValueDic[el.Id.ToString()] = self.values[i]
		#print("idValueDic {}".format(idValueDic))
		""" for i, row in enumerate(self.dgv.Rows):
			row.Cells[self.parameterColumnIndex].Value = self.values[i] if i < len(self.dgv.Rows)-1 else row.Cells[self.parameterColumnIndex].Value
		self.dgv.Refresh() """
		for i, row in enumerate(self.dgv.Rows):
			row.Cells[self.parameterColumnIndex].Value = idValueDic[row.Cells[self.idColumnIndex].FormattedValue]
		self.dgv.Refresh()
		

	def setParametersOfSelected(self, sender, event):
		elementsToSet = []
		for i,row in enumerate(self.dgv.SelectedRows):
			#print("elId {}".format(self.dgv.Rows[row.Index].Cells[3].FormattedValue))
			elId = viewElementsIdsDict[row.Cells[self.idColumnIndex].FormattedValue]			
			el = doc.GetElement(elId)
			elementsToSet.append(el)
			#elParams = el.GetOrderedParameters()
			#for elParam in elParams:
			#	if elParam.Definition.Name == self.parameterName:
		valuesToSet = [self.setParameterTextBox.Text for x in elementsToSet]

		t = Transaction(doc, "Set Parameters for selected elements")
		t.Start()
		parameterNameValuesSet = setValuesByParameterName(elementsToSet, valuesToSet, self.parameterName)	
		t.Commit()
		self.updateDGV()
		print("\nVýsledek: \n")
		for i, x in enumerate(parameterNameValuesSet):
			print("{}\n".format(x))
		""" try:
			t = Transaction(doc, "Set Parameters for selected elements")
			t.Start()
			parameterNameValuesSet = setValuesByParameterName(elementsToSet, valuesToSet, self.parameterName)	
			t.Commit()
			
			print("\nVýsledek: \n")
			for i, x in enumerate(parameterNameValuesSet):
				print("{}\n".format(x))
		except:
			t.RollBack()
			import traceback
			errorReport = traceback.format_exc()
			raise RuntimeError("Parameter name {0} not set !!! {1}".format(self.parameterName, errorReport)) """
		
	""" def buttonPanelOnResize(self, sender, event):
		self.setParameterButton.Width = self.buttonPanel.Width
		self.setParameterTextBox.Width = self.buttonPanel.Width """
		
	def selectionChanged(self, sender, event):
		self.idColumnIndex = self.dgv.Columns[self.columnNames[0]].Index
		self.categoryColumnIndex = self.dgv.Columns[self.columnNames[1]].Index
		self.elementNameColumnIndex = self.dgv.Columns[self.columnNames[2]].Index
		self.parameterColumnIndex = self.dgv.Columns[self.columnNames[3]].Index
		self.markColumnIndex = self.dgv.Columns[self.columnNames[4]].Index
		self.typeMarkColumnIndex = self.dgv.Columns[self.columnNames[5]].Index
		elNames = []
		selectedElements = []
		selectedElementsId = []
		elParamValues = []
		TabForm.selectedRowIndices = []
		TabForm.selectedRowIds = []
		TabForm.selectedRowStrIds = []
		for i,row in enumerate(self.dgv.SelectedRows):
			elementName = self.dgv.Rows[row.Index].Cells[self.elementNameColumnIndex].FormattedValue
			#print("X SelectionChanged Rows[row.Index].Cells[2].FormattedValue - {}".format(elementName))
			if elementName not in elNames:
				elNames.append(elementName)
			elId = viewElementsIdsDict[self.dgv.Rows[row.Index].Cells[self.idColumnIndex].FormattedValue]
			#print("SelectionChanged viewElementsIdsDict[self.dgv.Rows[row.Index].Cells[1].FormattedValue] - {}".format(elId))
			selectedElements.append(doc.GetElement(elId))
			selectedElementsId.append(elId)
			TabForm.selectedRowIndices.append(row.Index)
			TabForm.selectedRowStrIds.append(self.dgv.Rows[row.Index].Cells[self.idColumnIndex].FormattedValue)
		#print("selectionChanged() TabForm.selectedRowStrIds {}".format(TabForm.selectedRowStrIds))

		#for el in selectedElements:
		elemParamValues = getValuesByParameterName(selectedElements, self.parameterName, doc)
		uniqueValues = []
		for value in elemParamValues:
			if value not in uniqueValues and value !="":
				uniqueValues.append(value)
		#print("SelectionChanged selectedElementsId - {}".format(selectedElementsId))
		elementIdsCol = Clist[ElementId](selectedElementsId)
		uidoc.Selection.SetElementIds(elementIdsCol)
		if len(uniqueValues) == 1:
			self.setParameterTextBox.Text = "{}".format(uniqueValues[0])
			self.setParameterTextBox.ForeColor = Color.Black
		elif len(uniqueValues) == 0:
			self.setParameterTextBox.Text = ""
			self.setParameterTextBox.ForeColor = Color.Black
		else:
			self.setParameterTextBox.Text = "**multiple values selected** - {0}".format(elemParamValues)
			self.setParameterTextBox.ForeColor = Color.Gray
		self.setParameterTextBox.Refresh()
		#print("rows selected: {0}, unique element names: {1}, uniqueValues {2}".format(len(self.dgv.SelectedRows), len(elNames), len(uniqueValues)))

	def ColumnAdded(self, sender, *args):
		self.cCount += 1
		#print(sender.Text)
		print("{0} - {1}".format(self.cCount, args[0].Column.Name))
		if self.dgv.Columns.Count == len(self.columnNames):
			if args[0].Column.Name == self.columnNames[0]:
				print("column {0} added".format(args[0].Column.Name))
				args[0].Column.DisplayIndex = 0
				args[0].Column.ReadOnly = True
			if args[0].Column.Name == self.columnNames[1]:
				print("column {0} added".format(args[0].Column.Name))
				args[0].Column.DisplayIndex = 1
				args[0].Column.ReadOnly = True
			if args[0].Column.Name == self.columnNames[2]:
				print("column {0} added".format(args[0].Column.Name))
				args[0].Column.DisplayIndex = 2
				args[0].Column.ReadOnly = True
			if args[0].Column.Name == self.columnNames[3]:
				print("column {0} added".format(args[0].Column.Name))
				args[0].Column.DisplayIndex = 3
				args[0].Column.ReadOnly = True
			if args[0].Column.Name == self.columnNames[4]:
				print("column {0} added".format(args[0].Column.Name))
				args[0].Column.DisplayIndex = 4
				args[0].Column.ReadOnly = True
			if args[0].Column.Name == self.columnNames[5]:
				print("column {0} added".format(args[0].Column.Name))
				args[0].Column.DisplayIndex = 5
				args[0].Column.ReadOnly = True



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
		self.scriptDir = "\\".join(__file__.split("\\")[:-1]) 
		print("script directory: {}".format(self.scriptDir))
		iconFilename = os.path.join(self.scriptDir, 'spaceific_64x64_sat_X9M_icon.ico')
		icon = Icon(iconFilename)
		self.Icon = icon	

		self.tableData = tableData
		self.elements = elements
		self.viewSelectionIdStrings = inViewSelectionIdStrings
		self.inSelectedParameters = {k : True if k in selectedParams else False for k, v in uniqueParams.items()}
		self.InitializeComponent()

	def InitializeComponent(self):
		self.Text = "List of elements by selected parameter name"
		self.Width = 500
		self.Height = 200
		self.StartPosition = FormStartPosition.CenterScreen
		self.TopMost = True

		# self.paramaterValueTB = TextBox()
		# self.paramaterValueTB.Text = "Enter value"
		# #self.paramaterValueTB.Location = Point(5, 55)
		# self.paramaterValueTB.Width = 150
		# self.paramaterValueTB.Parent = self
		# self.paramaterValueTB.Anchor = AnchorStyles.Top
		# self.paramaterValueTB.Dock = DockStyle.Top		

		self.parameterCB = ComboBox()
		self.parameterCB.Width = 150
		self.parameterCB.Parent = self
		self.parameterCB.Anchor = AnchorStyles.Top
		self.parameterCB.Dock = DockStyle.Top
		self.parameterCB.Items.AddRange(tuple([k for k in sorted(uniqueParams.keys())]))
		self.parameterCB.SelectionChangeCommitted += self.OnChanged
		self.parameterCB.Text = "--SELECT--"
		self.parameterCB.DrawMode = DrawMode.OwnerDrawVariable
		self.parameterCB.DropDownStyle = ComboBoxStyle.DropDown
		self.parameterCB.DrawItem += self.comboBoxDrawItem

		# for item in self.parameterCB.Controls:
		# 	print("self.parameterCB.item {}".format(item.Text.BackColor))
		
		self.parameterCBLabel = Label()
		self.parameterCBLabel.Text = "Select parameter"
		self.parameterCBLabel.Width = 250
		self.parameterCBLabel.Parent = self
		self.parameterCBLabel.Anchor = AnchorStyles.Top
		self.parameterCBLabel.Dock = DockStyle.Top
		
		self.label = Label()
		self.label.Text = "Select parameter from list to create table of all elements with this parameter"
		self.label.Width = 250
		self.label.Parent = self
		self.label.Anchor = AnchorStyles.Top
		self.label.Dock = DockStyle.Top

		# self.paramaterNameTB = TextBox()
		# self.paramaterNameTB.Text = "Enter parameter Name"
		# #self.paramaterNameTB.Location = Point(5, 30)
		# self.paramaterNameTB.Width = 150
		# self.paramaterNameTB.Dock = DockStyle.Top

		self.submitButton = Button()
		self.submitButton.Text = 'OK'
		self.submitButton.Location = Point(25, 125)
		self.submitButton.Click += self.update
		self.submitButton.Parent = self
		self.submitButton.Anchor = AnchorStyles.Bottom
		self.submitButton.Dock = DockStyle.Bottom

		self.closeButton = Button()
		self.closeButton.Text = 'Close'
		self.closeButton.Click += self.close
		self.closeButton.Parent = self
		self.closeButton.Anchor = AnchorStyles.Bottom
		self.closeButton.Dock = DockStyle.Bottom

		self.AcceptButton = self.submitButton
		self.CancelButton = self.closeButton

		# self.Controls.Add(self.label)
		# self.Controls.Add(self.parameterCBLabel)
		# self.Controls.Add(self.paramaterNameTB)
		# self.Controls.Add(self.paramaterValueTB)
		# self.Controls.Add(self.submitButton)

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
		
		myParameterName = self.parameterCB.SelectedItem
		self.filteredElements = self.filterElementsByParameterName(self.elements, myParameterName)
		#myParameterValue = self.paramaterValueTB.Text
		print("\nYou selected: {0}".format(myParameterName))
		print("Number of Elements: {0}\n".format(len(self.filteredElements)))
		# for el in self.filteredElements:
		# 	print("{0} - \n".format(el.Id.ToString()))
		self.values = getValuesByParameterName(self.filteredElements, myParameterName, doc)
		
		self.elementTab = TabForm(self.tableData, self.filteredElements, myParameterName, self.viewSelectionIdStrings)
		self.elementTab.ShowDialog()
		
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

	def filterElementsByParameterName(self, inElements, inParameterName):
		filteredElements = []
		for el in inElements:
			if el.GetTypeId().IntegerValue > -1:
				typeElement = doc.GetElement(el.GetTypeId()) 
				if el.LookupParameter(inParameterName):
					filteredElements.append(el)
				elif typeElement.LookupParameter(inParameterName):
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
			if elParam.Definition.Name not in uniqueParams:
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

allElements = getAllElements(doc, inActiveView = False)
viewElementsIds = filterElementsByActiveViewIds(doc, allElements, disablePhases = False, onlyInActiveView = False)
viewElementsIdsDict = {"{}".format(x.IntegerValue) : x for x in viewElementsIds}
allViewElements = filterElementsByActiveViewIds(doc, allElements, toElement = True, disablePhases = True, onlyInActiveView = True)
viewElementsCol = Clist[ElementId](viewElementsIds)
nameToParamDic = {}
#uidoc.Selection.SetElementIds(viewElementsCol)
""" # get ids of elements not manualy selected in view
selectionDifference = []
mySelectedElIds = [x.Id.ToString() for x in mySelection]
viewSelectedIds = [x.ToString() for x in viewElementsIds]
for viewSelectedId in viewSelectedIds:
	if viewSelectedId not in mySelectedElIds:
		selectionDifference.append(viewSelectedId)
print("Difference in selected and acquired elements: {0}".format(selectionDifference)) """

print("Number of elements in view: {0}".format(len(viewElementsIds)))
#parameterName = "Objem"
colectionOfAllElementsIds = Clist[ElementId]([x.Id for x in allElements])

uniqueParams = getMembers(allViewElements)
viewSelection = uidoc.Selection
viewSelectionIds = list(viewSelection.GetElementIds())
viewSelectionIdStrings = [x.ToString() for x in viewSelectionIds]
viewSelectionElements = []
print("Selected Elements {}".format(len(viewSelectionIds)))
for i, elId in enumerate(viewSelectionIds):
	print("{0} - {1} - {2}".format(i, elId.IntegerValue, doc.GetElement(elId).Name))
	viewSelectionElements.append(doc.GetElement(elId))
selectedParams = getMembers(viewSelectionElements)
selectedParamsIds = {v.Id.ToString():v for k,v in selectedParams.items()}

#run input form
viewSelection = uidoc.Selection
Application.EnableVisualStyles()
myDialogWindow = MainForm(uniqueParams, allViewElements, viewSelectionIdStrings)

Application.Run(myDialogWindow)





