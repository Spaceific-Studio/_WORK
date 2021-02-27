# -*- coding: utf-8 -*-
# Copyright(c) 2020, Daniel Gercak
#Script for parameters update of family "Prostup (SWECO)"
#resource_path: H:\_WORK\PYTHON\REVIT_API\vyska_prostupu.py
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB.Architecture import *
from Autodesk.Revit.DB.Analysis import *
from Autodesk.Revit.UI import *
from Autodesk.Revit.UI.Selection import *

import sys
#if "Windows" in platform.uname():
	#lib_path = r'H:/_WORK/PYTHON/LIB'
lib_path = r'H:/_WORK/PYTHON/REVIT_API/LIB'
sys.path.append(lib_path)

from RevitSelection import getFamilyInstancesByName, getValuesByParameterName, setValuesByParameterName, filterElementsByActiveViewIds, getAllElements

import clr
clr.AddReference("System")
from System.Collections.Generic import List as Clist

clr.AddReferenceByPartialName('PresentationCore')
clr.AddReferenceByPartialName('PresentationFramework')
clr.AddReferenceByPartialName('System.Windows.Forms')
import System.Windows
import System.Drawing
from System.Reflection import BindingFlags
from System.Drawing import *
from System.Windows.Forms import *
from System.ComponentModel import BindingList


uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
mySelection = [doc.GetElement(elId) for elId in __revit__.ActiveUIDocument.Selection.GetElementIds()]

class Dic2obj(object):
	def __init__(self, dictionary):
		for key in dictionary:
			setattr(self, key, dictionary[key])

class TabForm(Form):
	selectedRowIndices = []

	def __init__(self, tableData, elements, parameterName):
		self.tableData = tableData
		self.elements = elements
		self.elementsNumber = len(self.elements)
		self.parameterName = parameterName
		self.parameter = nameToParamDic[self.parameterName]
		self.ControlAdded += self.control_Added
		self.InitializeComponent()
		

		
		

	def InitializeComponent(self):
		self.Text = "Table of elements with selected parameter: " + self.parameterName
		self.Width = 800
		self.Height = 500
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

		self.buttonPanel = Panel()
		self.buttonPanel.Dock = DockStyle.Bottom
		self.buttonPanel.AutoSize = True
		self.buttonPanel.Name = "Button Panel"
		self.buttonPanel.Height = 150
		self.buttonPanel.AutoSizeMode = AutoSizeMode.GrowAndShrink
		self.buttonPanel.AutoScroll = True
		self.buttonPanel.BackColor = Color.White
		self.buttonPanel.ControlAdded += self.control_Added
		
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

		self.dgv.RowsDefaultCellStyle.BackColor = Color.White;
		self.dgv.AlternatingRowsDefaultCellStyle.BackColor = Color.AliceBlue
		self.dgv.ColumnHeadersDefaultCellStyle = headerCellStyle
		self.dgv.CellClick += self.cellClick
		self.dgv.SelectionChanged += self.selectionChanged
		#self.dgv.DataBindingComplete += self.setSelectedRowsEvent		

		self.columnNames = ("Element Id", "Category", "Element Name", "parameter_{}".format(self.parameterName))
		self.values = getValuesByParameterName(self.elements, self.parameterName, doc)
		tableObjectList = []
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
			tableObjectList.append(rowObj)
		
		#self.dgv.DataSource = Clist[object](tableObjectList)
		
		#print("tableDicList - {}".format(tableDicList))
		
		self.dgv.AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.Fill
		self.dgv.Dock = DockStyle.Fill
		self.dgv.AutoResizeColumns()

		self.isolateButton = Button()
		self.isolateButton.Text = "Isolate selected elements"
		self.isolateButton.Height = 30
		self.isolateButton.Click += self.isolateSelectedElements
		self.isolateButton.Location = Point(0,120)
		self.isolateButton.AutoSize = True
		self.buttonPanel.Controls.Add(self.isolateButton)

		self.setParameterButton = Button()
		self.setParameterButton.Text = "Set Value For Selected"
		self.setParameterButton.Height = 30
		self.setParameterButton.Location = Point(0,60)
		self.setParameterButton.Click += self.setParametersOfSelected
		self.buttonPanel.Controls.Add(self.setParameterButton)

		self.setParameterTextBox = TextBox()
		#self.setParameterTextBox.FontHeight = 20
		self.setParameterTextBox.Text = "Text"
		self.setParameterTextBox.Name = "setParameterTextBox"
		self.setParameterTextBox.Height = 60
		self.setParameterTextBox.Location = Point(0,0)
		self.setParameterTextBox.Multiline = True
		self.setParameterTextBox.KeyDown += self.setParameterSubmit

		self.buttonPanel.Controls.Add(self.setParameterTextBox)		
		self.dgvPanel.Controls.Add(self.dgv)

		self.Controls.Add(self.dgvPanel)
		self.Controls.Add(self.buttonPanel)
		
		#self.isolateButton.Width = self.buttonPanel.Width
		self.setParameterButton.Width = self.buttonPanel.Width
		self.setParameterTextBox.Width = self.buttonPanel.Width
		self.isolateButton.Width = self.buttonPanel.Width
		self.setParameterTextBox.Height = 60
		self.setParameterTextBox.Location = Point(0,0)

		#self.createDGVbyDataSource(tableObjectList)
		self.createDGVbyRows(tableDicList)

		self.testButton = Button()
		self.testButton.Text = "Test"
		self.testButton.Height = 30
		self.testButton.Location = Point(0,90)
		self.testButton.Click += self.backColorChanged
		self.testButton.Width = self.buttonPanel.Width
		self.buttonPanel.Controls.Add(self.testButton)	
		#self.setParameterButton.Enabled = False
		#self.setParameterButton.Enabled = True
		


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
					# elId = v.Id.ToString()
					# elCategory = "{}".format(v.Category.Name)
					# parameterValue = "{}".format(self.values[i])
					# elName = "{}".format(v.Name if hasattr(v, "Name") else v.FamilyName)
					# rowObj = Dic2obj({self.columnNames[0] : elId, \
					# 								self.columnNames[1] : elCategory, \
					# 								self.columnNames[2] : elName, \
					# 								self.columnNames[3] : parameterValue})
					#row = [elId, elCategory, elName, parameterValue]
					#rowCol = Clist[str](row)
					#cRows = Clist[DataGridViewRow]
					#dgvRow = DataGridViewRow()
					#cRows.Add(DataGridViewRow())
					
					#rowValues = dic.values()
					rowValues = (dic[self.columnNames[0]], dic[self.columnNames[1]], dic[self.columnNames[2]], dic[self.columnNames[3]])
					#cRows.Item[cRows.Count - 1].CreateCells(self.dgv,Clist[dict](dic))

					self.dgv.Rows.Add(*rowValues)
					
				# self.dgv.NotifyCurrentCellDirty(True)
				# self.dgv.EndEdit()
				# self.dgv.NotifyCurrentCellDirty(False)
				# self.dgv.CommitEdit(DataGridViewDataErrorContexts.Commit)
				""" self.dgv.NotifyCurrentCellDirty(True)
				if self.dgv.IsCurrentCellDirty or self.dgv.IsCurrentRowDirty:
					print("self.dgv.DataSource {0} self.dgv.DataMember {1}".format(self.dgv.DataSource, self.dgv.DataMember))
					#self.dgv.CurrentRow.DataGridView.EndEdit()
					self.dgv.EndEdit()
					cm = self.dgv.BindingContext[self.dgv.DataSource, self.dgv.DataMember]
					cm.EndCurrentEdit()
				print("self.dgv.IsCurrentCellDirty NOT") """
				
				rowToDelete = self.dgv.Rows.GetLastRow(DataGridViewElementStates.None)
				print("self.dgv.Rows.GetLastRow().RowIndex - {}".format(self.dgv.Rows.GetLastRow(DataGridViewElementStates.None)))
				# if rowToDelete > -1:
				# 	self.dgv.Rows.RemoveAt(rowToDelete)
				
					#self.dgv.Rows.AddRange(cRows.ToArray())
				#self.columnNames = ("Element Id", "Category", "Element Name", self.parameterName)
				#self.setSelectedRows()
			else:
				raise IndexError("inDicList is empty list")
		else:
			raise TypeError("input argument inDicList not of type list")
	def control_Added(self, sender, e):
		print("The control named " + e.Control.Text + " has been added to the form.")
		if e.Control.Name == "Button Panel":
			self.setSelectedRows()

	def backColorChanged(self, sender, event):
		print("BackColorChanged")
		self.dgv.ClearSelection()
		for i in TabForm.selectedRowIndices:
			print("row to select {0}".format(self.dgv.Rows[i].Index))
			self.dgv.Rows[i].Selected = True

	def setSelectedRowsEvent(self, sender, event):
		print("setSelectedRowsEvent {0} {1} {2}".format(self.setSelectedRowsEvent, sender, event))
		self.setSelectedRows()
		
	def setSelRows(self):
		self.dgv.ClearSelection()
		for i in TabForm.selectedRowIndices:
			print("row to selecttt {0}".format(self.dgv.Rows[i].Index))
			self.dgv.Rows[i].Selected = True

	def setSelectedRows(self):
		for i, r in enumerate(self.dgv.Rows):
			# print("ElId {0}".format(self.dgv.Rows[i].Cells[1].FormattedValue))
			if self.dgv.Rows[i].Cells[0].FormattedValue in viewSelectionIdStrings:	
				TabForm.selectedRowIndices.append(i)

		#self.dgv.ClearSelection()
		for i in TabForm.selectedRowIndices:
			print("row to selecttt {0}".format(self.dgv.Rows[i].Index))
			self.dgv.Rows[i].Selected = True
		
		#self.dgv.ClearSelection()
		print("Rows Count {}".format(self.dgv.Rows.Count))
		brightRow = self.dgv.DefaultCellStyle.Clone()
		brightRow.BackColor = Color.White
		darkRow = self.dgv.DefaultCellStyle.Clone()
		darkRow.BackColor = Color.AliceBlue
		selectedRow = self.dgv.DefaultCellStyle.Clone()
		selectedRow.BackColor = Color.Orange
		
		for i,r in enumerate(self.dgv.Rows):
			if i in TabForm.selectedRowIndices:
				r.DefaultCellStyle = selectedRow
				r.Selected = True
				self.dgv.Rows[i].Selected = True
		
		if self.parameter.IsReadOnly:
			self.setParameterButton.Enabled = False
			self.setParameterTextBox.Enabled = False
			self.dgv.Columns[3].ReadOnly = True
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
				if x.Id.ToString() == "{0}".format(self.dgv.Rows[e.RowIndex].Cells[0].FormattedValue):
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
					if x.Id.ToString() == "{0}".format(self.dgv.Rows[row.Index].Cells[0].FormattedValue):
						iDs.append(x.Id)
				print("Isolated element on row {0} Id {1}".format(row.Index, self.dgv.Rows[row.Index].Cells[0].Value))
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

	def updateDGV(self):		
		print("len(self.dgv.SelectedRows) {}".format(len(self.dgv.SelectedRows)))
		values = getValuesByParameterName(self.elements, self.parameterName, doc)
		for i, row in enumerate(self.dgv.Rows):
			row.Cells[3].Value = values[i] if i < len(self.dgv.Rows)-1 else row.Cells[3].Value
		self.dgv.Refresh()
		

	def setParametersOfSelected(self, sender, event):
		elementsToSet = []
		for i,row in enumerate(self.dgv.SelectedRows):
			elId = viewElementsIdsDict[self.dgv.Rows[row.Index].Cells[0].FormattedValue]
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
		
	def buttonPanelOnResize(self, sender, event):
		self.setParameterButton.Width = self.buttonPanel.Width
		self.setParameterTextBox.Width = self.buttonPanel.Width
		
	def selectionChanged(self, sender, event):
		elNames = []
		selectedElements = []
		selectedElementsId = []
		elParamValues = []
		for i,row in enumerate(self.dgv.SelectedRows):
			elementName = self.dgv.Rows[row.Index].Cells[2].FormattedValue
			#print("X SelectionChanged Rows[row.Index].Cells[2].FormattedValue - {}".format(elementName))
			if elementName not in elNames:
				elNames.append(elementName)
				elId = viewElementsIdsDict[self.dgv.Rows[row.Index].Cells[0].FormattedValue]
				#print("SelectionChanged viewElementsIdsDict[self.dgv.Rows[row.Index].Cells[1].FormattedValue] - {}".format(elId))
			selectedElements.append(doc.GetElement(elId))
			selectedElementsId.append(elId)
			#print("{0} - Selected element Id: {1} with value {2}".format(i, self.dgv.Rows[row.Index].Cells[0].FormattedValue, self.dgv.Rows[row.Index].Cells[3].FormattedValue))

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
			self.setParameterTextBox.Text = "**multiple values selected** - {0}, elemParamValues {1}".format(len(uniqueValues), elemParamValues)
			self.setParameterTextBox.ForeColor = Color.Gray
		self.setParameterTextBox.Refresh()
		#print("rows selected: {0}, unique element names: {1}, uniqueValues {2}".format(len(self.dgv.SelectedRows), len(elNames), len(uniqueValues)))

	def ColumnAdded(self, sender, *args):
		if self.dgv.Columns.Count == len(self.columnNames):
			if self.dgv.Columns["Element Id"]:
				print("column Element Id added")
				self.dgv.Columns["Element Id"].DisplayIndex = 0
				self.dgv.Columns["Element Id"].ReadOnly = True
			if self.dgv.Columns["Category"]:
				print("column Category added")
				self.dgv.Columns["Category"].DisplayIndex = 1
				self.dgv.Columns["Category"].ReadOnly = True
			if self.dgv.Columns["Element Name"]:
				print("column Element Name added")
				self.dgv.Columns["Element Name"].DisplayIndex = 2
				self.dgv.Columns["Element Name"].ReadOnly = True
			if self.dgv.Columns["parameter_{}".format(self.parameterName)]:
				print("column parameter_{} added".format(self.parameterName))
				self.dgv.Columns["parameter_{}".format(self.parameterName)].DisplayIndex = 3
				self.dgv.Columns["parameter_{}".format(self.parameterName)].ReadOnly = True

	def setupTable(self):
		self.panel = Panel()
		self.panel.Dock = DockStyle.Fill
		self.panel.AutoScroll = True
		self.panel.AutoSize = False

		self.table = TableLayoutPanel()
		absoluteHeaderRowHeight = 20
		absoluteRowHeight = 20
		#self.table.Width = self.panel.Width
		#self.table.Height = self.panel.Height
		self.table.GrowStyle = TableLayoutPanelGrowStyle.AddRows
		self.table.Dock = DockStyle.Top
		self.table.AutoSize = True
		self.table.AutoSizeMode = AutoSizeMode.GrowAndShrink
		#self.table.MaximumSize = Size(self.table.Width, self.table.Height)
		#self.table.AutoScroll = True
		#self.table.ColumnCount = 4	
		#self.table.ControlAdded += self.OnControlAdded
		self.table.CellBorderStyle = TableLayoutPanelCellBorderStyle.None
		#self.filteredElements = self.filterElementsByParameterName(self.elements, self.parameterName)
		self.values = getValuesByParameterName(self.elements, self.parameterName, doc)
		self.tableItems = [(v.Id.ToString(), "{}".format(v.Category.Name), "{}".format(v.Name if hasattr(v, "Name") else v.FamilyName), "{}".format(self.values[i])) for i,v in enumerate(self.elements)]
		header = ("Element Id", "Category", "Element Name", self.parameterName)
		#self.tableItems = header + self.tableItems
		rStyle = RowStyle(SizeType.Absolute, absoluteHeaderRowHeight)
		self.table.RowStyles.Add(rStyle)
		for j, value in enumerate(header):
			self.table.Controls.Add(self.setupHeaderLabel(value), j, 0)
		for i, row in enumerate(self.tableItems):
			rStyle = RowStyle(SizeType.Absolute, absoluteRowHeight)
			self.table.RowStyles.Add(rStyle)
			for j, value in enumerate(row):
				cStyle = ColumnStyle(SizeType.Percent, 10 if j == 0 else 30)
				self.table.ColumnStyles.Add(cStyle)
				#print("{0}_{1} - {2}".format(i,j,value))
				self.table.Controls.Add(self.setupBodyTextBox(value, i) if j !=0 else self.setupBodyButton(value, i), j, i+1)

		self.Controls.Add(self.panel)
		self.panel.Height = self.table.Height
		self.panel.Controls.Add(self.table)		

		self.filteredNumLabel = Label()
		self.filteredNumLabel.Text = "Elements Count: {}".format(self.elementsNumber)
		self.filteredNumLabel.Width = self.Width
		self.filteredNumLabel.Parent = self
		self.filteredNumLabel.Anchor = AnchorStyles.Top
		self.filteredNumLabel.Dock = DockStyle.Top

		self.SelectAllButton = Button()
		self.SelectAllButton.Text = 'Select All'
		##self.SelectAllButton.Click += self.select
		self.SelectAllButton.Parent = self
		self.SelectAllButton.Anchor = AnchorStyles.Bottom
		self.SelectAllButton.Dock = DockStyle.Bottom

		self.closeButton = Button()
		self.closeButton.Text = 'Close'
		##self.closeButton.Click += self.close
		self.closeButton.Parent = self
		self.closeButton.Anchor = AnchorStyles.Bottom
		self.closeButton.Dock = DockStyle.Bottom

	def setupHeaderLabel(self, inText):
		label = Label()
		label.Text = "{}".format(inText)
		label.Margin = Padding(0)
		label.Dock = DockStyle.Fill
		label.Font = Font(label.Font, FontStyle.Bold)
		#label.TextAlign = ContentAlignment.MiddleCenter
		label.TextAlign = ContentAlignment.MiddleLeft
		label.Width = self.table.Width #* (1/float(len(self.tableData)))
		label.BackColor = Color.LightSkyBlue
		return label

	def setupBodyTextBox(self, inText, inRowPosition):
		tbPanel = Panel()
		tbPanel.Dock = DockStyle.Fill
		tbPanel.Margin = Padding(0)
		tbPanel.BackColor = Color.AliceBlue if inRowPosition % 2 == 0 else Color.White
		#tbPanel.AutoSize = True
		#tbPanel.AutoSizeMode = AutoSizeMode.GrowAndShrink
		textBox = TextBox()		
		textBox.Text = "{}".format(inText)
		textBox.Dock = DockStyle.Fill
		textBox.TextAlign = HorizontalAlignment.Left
		textBox.Width = self.table.Width #* (1/float(len(self.tableData)))
		textBox.BorderStyle = BorderStyle.None #FixedSingle
		#textBox.BorderColor = Color.AliceBlue if inRowPosition % 2 == 0 else Color.White
		textBox.Margin = Padding(0)
		#textBox.AutoSize = True
		textBox.BackColor = Color.AliceBlue if- inRowPosition % 2 == 0 else Color.White
		tbPanel.Controls.Add(textBox)
		return tbPanel

	def setupBodyButton(self, inText, inRowPosition):
		button = Button()
		button.Text = "{}".format(inText)
		button.Click += self.selectItem
		button.Dock = DockStyle.Fill
		button.Name = "{0}".format(inRowPosition)
		button.Margin = Padding(0)
		button.FlatStyle = FlatStyle.Flat
		button.FlatAppearance.BorderSize = 0
		button.TextAlign = ContentAlignment.MiddleLeft
		#button.Width = self.table.Width * 0.4
		button.AutoSizeMode = AutoSizeMode.GrowAndShrink
		button.BackColor = Color.AliceBlue if inRowPosition % 2 == 0 else Color.White
		return button

	def select(self, sender, event):
		elIds = [x.Id for x in self.elements]
		elementsCol = Clist[ElementId](elIds)
		uidoc.Selection.SetElementIds(elementsCol)
		self.Close()

	def selectItem(self, sender, event):
		print("{0}".format(sender.Text))
		for x in self.elements:
			if x.Id.ToString() == sender.Text:
				elId = [x.Id]
		elementsCol = Clist[ElementId](elId)
		uidoc.Selection.SetElementIds(elementsCol)
		self.Close()
	
	def info(self, sender, event):
		print("{0}".format(sender.Margin))
		sender.Margin = Padding(0)
		print("margin was set to {0}".format(sender.Margin))
		#for s in list(self.table.RowStyles):
		#	s.Height = 120

		#elIds = [x.Id for x in self.elements]
	def close(self, sender, event):
		self.Close()

	# def OnControlAdded(self, sender, event):
	# 	if event.Control != None:
	# 		row = self.table.GetPositionFromControl(event.Control).Row
	# 		print("Row {} to self.table was added".format(row))
	# 		#print("Sender Row {} to self.table was added".format(dir(sender)))

	def onRowClickSelect(self, sender, event):
		elIds = [x.Id for x in self.elements]
		elementsCol = Clist[ElementId](elIds)
		uidoc.Selection.SetElementIds(elementsCol)
		self.Close()

			#typeParameters = typeElement.GetOrderedParameters()
			#for parameter in typeParameters:



class MainForm(Form):
	def __init__(self, tableData, elements):
		self.tableData = tableData
		self.elements = elements
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
		
		self.elementTab = TabForm(self.tableData, self.filteredElements, myParameterName)
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
myDialogWindow = MainForm(uniqueParams, allViewElements)

Application.Run(myDialogWindow)





