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
from System import Array
from System.ComponentModel import IListSource


clr.AddReferenceByPartialName('PresentationCore')
clr.AddReferenceByPartialName('PresentationFramework')
clr.AddReferenceByPartialName('System.Windows.Forms')
import System.Windows
import System.Drawing

#from System.Drawing import *
from System.Drawing import *
from System.Windows.Forms import *
# from System.Windows.Forms import Application, Button, Form, Panel, ComboBox, Label, \
# 									TextBox, DockStyle, AnchorStyles, Screen, TreeView, \
# 									TreeNode, ScrollBars, TabControl, TabPage, \
# 									TableLayoutPanel, TableLayoutPanelCellBorderStyle, \
# 									TableLayoutPanelGrowStyle, SizeType, ButtonBorderStyle, \
# 									RowStyle, ColumnStyle, FormStartPosition, AutoSizeMode, Padding, \
# 									HorizontalAlignment, BorderStyle, FlatStyle, ControlEventHandler \


class Dic2obj(object):
	def __init__(self, dictionary):
		for key in dictionary:
			setattr(self, key, dictionary[key])

class TabForm(Form):
	def __init__(self):
		self.tableData = (Person("Peter", "Uchal", 33), \
						  Person("Hedviga", "Serengetiova", 20), \
						  Person("Medved", "Sob", 14), \
						  Person("eeee", "lll", 14), \
						  Person("ds", "d", 143), \
						  Person("defe", "mefe", 8), \
						  Person("Medved", "Sob", 14), \
						  Person("eeee", "lll", 14), \
						  Person("ds", "d", 143), \
						  Person("defe", "mefe", 8), \
						  Person("Medved", "Sob", 14), \
						  Person("eeee", "lll", 14), \
						  Person("ds", "d", 143), \
						  Person("defe", "mefe", 8), \
						  Person("Medved", "Sob", 14), \
						  Person("eeee", "lll", 14), \
						  Person("ds", "d", 143), \
						  Person("defe", "mefe", 8), \
						  Person("Medved", "Sob", 14), \
						  Person("eeee", "lll", 14), \
						  Person("ds", "d", 143), \
						  Person("defe", "mefe", 8), \
						  Person("Medved", "Sob", 14), \
						  Person("eeee", "lll", 14), \
						  Person("ds", "d", 143), \
						  Person("defe", "mefe", 8), \
						  Person("Fele", "Bele", 14))
		self.personNumber = len(self.tableData)
		self.InitializeComponent()

	def InitializeComponent(self):
		self.Text = "Table of persons"
		self.Width = 800
		self.Height = 500
		self.StartPosition = FormStartPosition.CenterScreen
		self.TopMost = True
		#DefaultBorderColor = Color.AliceBlue
		#Control.DefaultMargin = Padding(0)
		#self.setupTable()
		#self.setupRowTable()
		self.setupDataGridView()

	def setupDataGridView(self):
		self.dgvPanel = Panel()
		self.dgvPanel.Dock = DockStyle.Fill
		self.dgvPanel.AutoSize = False
		self.dgvPanel.AutoSizeMode = AutoSizeMode.GrowAndShrink
		self.dgvPanel.AutoScroll = True
		self.dgv = DataGridView()
		self.dgv.ColumnHeadersDefaultCellStyle.Font = Font(self.dgv.ColumnHeadersDefaultCellStyle.Font, FontStyle.Bold)
		
		
		#self.dgv.ColumnCount = len(self.tableData[0].person.keys())
		self.dgv.SelectionMode = DataGridViewSelectionMode.FullRowSelect
		self.dgv.AutoGenerateColumns = True
		self.dgv.ColumnAdded += self.ColumnAdded

		#self.dgv.AutoSize = True
		#self.dgv.AutoSizeMode = AutoSizeMode.GrowAndShrink
		self.dgv.AutoSizeRowsMode = DataGridViewAutoSizeRowsMode.DisplayedCellsExceptHeaders
		self.dgv.RowHeadersVisible = False
		self.dgv.AutoSizeRowsMode = DataGridViewAutoSizeRowsMode.DisplayedCellsExceptHeaders
		self.dgv.BorderStyle = BorderStyle.Fixed3D
		self.dgv.EditMode = DataGridViewEditMode.EditOnEnter
		self.dgv.Anchor = (AnchorStyles.Bottom | AnchorStyles.Left | AnchorStyles.Right)
		objVars = vars(self.tableData[0])
		print(objVars.keys())
		j = 0
		for key in objVars.keys():
			print("{0} - {1}".format(key, objVars[key]))
			#self.dgv.Columns[j].Name = key
			j += 1
		values = []
		for i, row in enumerate(self.tableData):
			#myArray = Clist(Person)
			#myArray.Add(row)
			objVars = vars(row)
			myObj = Dic2obj(objVars)
			print("objVars {}".format(objVars))
			objVarsObj = type('MyClass', (), objVars)
			print("objVarsObj.Name {}".format(objVarsObj.name))
			values.append(myObj)
		print("vlaues {}".format(values))
		#valuesObj = type('MyClass', (), values)
		#print("valuesObj - {}".format(valuesObj.name))
		self.dgv.DataSource = Clist[object](values)
		#self.dgvPanel.Controls.Add(self.dgv)
		#self.dgvPanel.Height = self.dgv.Height
		#self.dgv.Width = self.dgvPanel.Width
		
		
		self.dgv.AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.Fill
		self.dgv.Dock = DockStyle.Fill
		#self.dgv.Size = Size(self.width, self.Height)
		self.dgv.AutoResizeColumns()
		self.dgv.DataBindingComplete += self.setSelectedRows
		self.dgvPanel.Controls.Add(self.dgv)
		self.Controls.Add(self.dgvPanel)
		#row = self.dgv.Rows[3]
		#row.Selected = True
		#self.dgv.Height = self.Height

	def setSelectedRows(self, sender, value):
		print("pocet riadkov {}".format(len(self.dgv.Rows)))
		self.dgv.ClearSelection()
		self.dgv.Rows[3].Selected = True

	def ColumnAdded(self, sender, *args):
		print(self, sender, args)
 		#for x in self.dgv.Columns: print(x)
		if self.dgv.Columns["name"]:
			print("column name added")
			self.dgv.Columns["name"].DisplayIndex = 0

	def setupTable(self):
		self.panel = Panel()
		self.panel.Dock = DockStyle.Fill
		#self.panel.BackColor = Color.Red
		#self.panel.Width = self.Width
		#self.panel.Height = self.tableHeight
		self.panel.AutoScroll = True
		self.panel.AutoSize = True
		self.panel.AutoSizeMode = AutoSizeMode.GrowAndShrink

		self.table = TableLayoutPanel()
		absoluteHeaderRowHeight = 20
		absoluteRowHeight = 20
		#self.table.Width = self.panel.Width
		#self.table.BackColor = Color.Green
		self.table.Dock = DockStyle.Top
		self.table.GrowStyle = TableLayoutPanelGrowStyle.AddRows
		#self.table.ColumnCount = 3
		self.table.CellBorderStyle = TableLayoutPanelCellBorderStyle.Single
		self.table.AutoSize = True
		self.table.AutoSizeMode = AutoSizeMode.GrowAndShrink
		#headerRowControls = []
		rStyle = RowStyle(SizeType.Absolute, absoluteHeaderRowHeight)
		self.table.RowStyles.Add(rStyle)
		for j, key in enumerate(self.tableData[0].person.keys()):

			self.table.Controls.Add(self.setupHeaderLabel(key), j, 0)
		#	headerRowControls.append(self.setupHeaderLabel(key))
		#self.table.Controls.AddRange(Array[Control](headerRowControls))
		#i = 0		
		for i, row in enumerate(self.tableData):
			bodyRowControls = []
			print("{}".format(i))
			rStyle = RowStyle(SizeType.Absolute, absoluteRowHeight)
			print("self.table.Height {0}".format(self.table.Height))
			self.table.RowStyles.Add(rStyle)
			
			for j, value in enumerate(row.person.values()):
				cStyle = ColumnStyle(SizeType.Percent, 20)
				self.table.ColumnStyles.Add(cStyle)
				print("{0}_{1} - {2}".format(i,j,value))
				self.table.Controls.Add(self.setupBodyTextBox(value, i) if j !=0 else self.setupBodyButton(value, i), j, i+1)
				#bodyRowControls.append(self.setupBodyTextBox(value, i))
			#self.table.Controls.AddRange(Array[Control](bodyRowControls))
			#i += 1
		
		#self.table.Height = len(self.tableData) * absoluteRowHeight + absoluteHeaderRowHeight + 5
		self.panel.Height = self.table.Height
		self.panel.Controls.Add(self.table)
		
		self.Controls.Add(self.panel)

	def setupRowTable(self):
		self.panel = Panel()
		self.panel.Dock = DockStyle.Fill
		#self.panel.BackColor = Color.Red
		#self.panel.Width = self.Width
		#self.panel.Height = self.tableHeight
		self.panel.AutoScroll = True
		self.panel.AutoSize = True
		self.panel.AutoSizeMode = AutoSizeMode.GrowAndShrink

		self.table = TableLayoutPanel()
		self.table.Name = "RowTable"
		absoluteHeaderRowHeight = 20
		absoluteRowHeight = 20
		#self.table.Width = self.panel.Width
		#self.table.BackColor = Color.Green
		self.table.Dock = DockStyle.Top
		self.table.GrowStyle = TableLayoutPanelGrowStyle.AddRows
		#self.table.ColumnCount = 3
		self.table.CellBorderStyle = TableLayoutPanelCellBorderStyle.Single
		self.table.AutoSize = True
		self.table.AutoSizeMode = AutoSizeMode.GrowAndShrink
		#headerRowControls = []
		rStyle = RowStyle(SizeType.Absolute, absoluteHeaderRowHeight)
		self.table.RowStyles.Add(rStyle)
		#add Header
		#for j, key in enumerate(self.tableData[0].person.keys()):

		self.table.Controls.Add(self.setupBodyRowButton(self.tableData[0].person.keys(), 0), 0, 0)
		#	headerRowControls.append(self.setupHeaderLabel(key))
		#self.table.Controls.AddRange(Array[Control](headerRowControls))
		#i = 0		
		for i, row in enumerate(self.tableData):
			rStyle = RowStyle(SizeType.Absolute, absoluteRowHeight)
			self.table.RowStyles.Add(rStyle)
			self.table.Controls.Add(self.setupBodyRowButton(row.person.values(), i), 0, i+1)
			# for j, value in enumerate(row.person.values()):
			# 	cStyle = ColumnStyle(SizeType.Percent, 20)
			# 	self.table.ColumnStyles.Add(cStyle)
			# 	print("{0}_{1} - {2}".format(i,j,value))
			# 	self.table.Controls.Add(self.setupBodyTextBox(value, i) if j !=0 else self.setupBodyButton(value, i), j, i+1)
				#bodyRowControls.append(self.setupBodyTextBox(value, i))
			#self.table.Controls.AddRange(Array[Control](bodyRowControls))
			#i += 1
		
		#self.table.Height = len(self.tableData) * absoluteRowHeight + absoluteHeaderRowHeight + 5
		self.panel.Height = self.table.Height
		self.panel.Controls.Add(self.table)
		
		self.Controls.Add(self.panel)

	def setupHeaderLabel(self, inText):
		label = Label()
		label.Text = "{}".format(inText)
		label.Margin = Padding(0)
		label.Dock = DockStyle.Fill
		label.Font = Font(label.Font, FontStyle.Bold)
		label.TextAlign = ContentAlignment.MiddleCenter
		#label.TextAlign = ContentAlignment.MiddleLeft
		label.Width = self.table.Width #* (1/float(len(self.tableData)))
		label.BackColor = Color.LightSkyBlue
		return label
	
	def setupBodyTextBox(self, inText, inRowPosition):
		tbPanel = Panel()
		tbPanel.Name = "tbPanel_{0}".format(inRowPosition)
		tbPanel.Dock = DockStyle.Fill
		tbPanel.Margin = Padding(0)
		tbPanel.BackColor = Color.AliceBlue if inRowPosition % 2 == 0 else Color.White
		#tbPanel.AutoSize = True
		#tbPanel.AutoSizeMode = AutoSizeMode.GrowAndShrink
		textBox = TextBox()		
		textBox.Name = "textBox_{0}".format(inRowPosition)
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
		elIdBT = Button()
		elIdBT.Text = "{}".format(inText)
		#elIdBT.Click += self.info
		elIdBT.Dock = DockStyle.Fill
		elIdBT.Name = "button_{0}".format(inRowPosition)
		elIdBT.Margin = Padding(0)
		elIdBT.FlatStyle = FlatStyle.Flat
		elIdBT.FlatAppearance.BorderSize = 0
		elIdBT.TextAlign = ContentAlignment.MiddleLeft
		#elIdBT.Width = self.table.Width * 0.4
		elIdBT.AutoSizeMode = AutoSizeMode.GrowAndShrink
		elIdBT.BackColor = Color.AliceBlue if inRowPosition % 2 == 0 else Color.White
		return elIdBT

	''' def setupBodyRowButton(self, inItems, inRowPosition):
		panel = Panel()
		panel.Dock = DockStyle.Fill
		panel.Margin = Padding(0)
		panel.BackColor = Color.AliceBlue if inRowPosition % 2 == 0 else Color.White		
		panel.Name = "panel_{0}".format(inRowPosition)
		panel.MouseEnter += self.backColorChange
		panel.Leave += self.backColorChange
		table = TableLayoutPanel()
		table.Dock = DockStyle.Fill
		table.GrowStyle = TableLayoutPanelGrowStyle.AddColumns
		#.table.ColumnCount = 3
		table.CellBorderStyle = TableLayoutPanelCellBorderStyle.Single
		table.AutoSize = True
		table.AutoSizeMode = AutoSizeMode.GrowAndShrink
		for j, value in enumerate(inItems):
			cStyle = ColumnStyle(SizeType.Percent, 10 if j == 0 else 30)
			table.ColumnStyles.Add(cStyle)
			#print("{0}_{1} - {2}".format(i,j,value))
			table.Controls.Add(self.setupBodyTextBox(value, inRowPosition) if j !=0 else self.setupBodyButton(value, inRowPosition), j, 0)
		
		panel.Margin = Padding(0)
		panel.Controls.Add(table)
		upperPanel = Panel()
		upperPanel.Name = "upperPanel_{0}".format(inRowPosition)
		upperPanel.Dock = DockStyle.Fill
		upperPanel.Margin = Padding(0)
		upperPanel.Controls.Add(panel)
		return panel 

	 def backColorChange(self, sender, event):
		print("ROW - {}".format(sender.Parent.Parent.Parent.Parent.GetRow(sender.Parent.Parent.Parent)))
		if sender.BackColor == Color.Black:
			senderBackColor = Color.AliceBlue if sender.Parent.Parent.Parent.Parent.GetRow(sender.Parent.Parent.Parent) % 2 == 0 else Color.White
		else:
			sender.BackColor = Color.Black
		print("panel {0}".format(sender.Name)) '''


class Person():
	def __init__(self, name, surname, age):
		self.person = {"Name":name, "Surname":surname, "Age": age}
		self.name = name
		self.surname = surname
		self.age = age
	
	@property
	def Name(self): return self.name

	@property
	def Surname(self): return self.surname

	@property
	def Age(self): return self.age



Application.EnableVisualStyles()
myDialogWindow = TabForm()
Application.Run(myDialogWindow)