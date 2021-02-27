# -*- coding: utf-8 -*-
# Copyright(c) 2021, Daniel Gercak
#Revit Python Shell script for multiple joining elements
#joins all selected elements by brute force applying join command to all pair combinations, determine according to
#priority table which element cuts another
#resource_path: https://github.com/Spaceific-Studio/_WORK/REVIT_API/joinAllElements.py
import sys
if "IronPython" in sys.prefix:
	pytPath = r'C:\Program Files (x86)\IronPython 2.7\Lib'
	sys.path.append(pytPath)
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
	    import Autodesk
	    import System
	    import threading
	    from System.Collections.Generic import List as Clist
	    #import System.Drawing
	    import clr
	    clr.AddReferenceByPartialName('System.Windows.Forms')
	    clr.AddReference("System.Drawing")
	    clr.AddReference('System')
	    #import System.Windows.Forms
	    from System.Threading import ThreadStart, Thread
	    from System.Windows.Forms import *
	    from System.Drawing import *
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

try:
	import Autodesk
	sys.modules['Autodesk']
	hasAutodesk = True	
except:
	hasAutodesk = False

print("module : {0} ; hasMainAttr = {1}".format(__file__, hasMainAttr))
print("module : {0} ; hasAutodesk = {1}".format(__file__, hasAutodesk))

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
    print("PythonLibPath was imported")

sys.path.append(libPath)
sys.path.append(pythLibPath)



""" Errors.catchVar(sys.platform, "sys.platform")
Errors.catchVar(sys.prefix, "sys.prefix")
Errors.catchVar(os.name, "os.name")
Errors.catchVar(platform.sys, "platform.sys")
Errors.catchVar(platform.os, "platform.os")
Errors.catchVar(platform.platform(), "platform.platform()") """

#import SpaceOrganize
#import RevitSelection as RS
from ListUtils import *
#from ListUtils import Dic2obj
from IO_Utils import *
print(ensure_dir)
#print("ProcesList {0}".format(processList(ensure_dir, sys.path)))

from itertools import combinations

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document

class Dic2obj(object):
	def __init__(self, dictionary):
		for key in dictionary:
			setattr(self, key, dictionary[key])

class MainForm(Form):
	def __init__(self, inIds):
		self.scriptDir = "\\".join(__file__.split("\\")[:-1])
		print(self.scriptDir)
		iconFilename = os.path.join(self.scriptDir, 'LIB\\spaceific_64x64_sat_X9M_icon.ico')
		icon = Icon(iconFilename)
		self.Icon = icon	

		self.ids = inIds
		self.confirmed = False
		
		self.InitializeComponent()

	def InitializeComponent(self):
		self.Text = "Setup of join priority for categories by Spaceific-Studio"
		self.Width = 500
		self.Height = 200
		self.StartPosition = FormStartPosition.CenterScreen
		self.TopMost = True
		screenSize = Screen.GetWorkingArea(self)
		self.Height = screenSize.Height / 5
		self.Width = screenSize.Width / 3
		self.panelHeight = self.ClientRectangle.Height * 0.75
		self.panelWidth = self.ClientRectangle.Width / 3
		self.bgColor = Color.CadetBlue
		self.textColor = Color.White

		self.setupDataGridView()
	
	def setupDataGridView(self):
		self.dgvPanel = Panel()
		self.dgvPanel.Dock = DockStyle.Fill
		self.dgvPanel.AutoSize = False
		self.dgvPanel.AutoSizeMode = AutoSizeMode.GrowAndShrink
		self.dgvPanel.AutoScroll = True
		self.dgvPanel.BackColor = Color.Blue
		
		self.buttonPanel = Panel()
		self.buttonPanel.Dock = DockStyle.Bottom
		self.buttonPanel.AutoSize = True
		self.buttonPanel.Name = "Button Panel"
		self.buttonPanel.Height = 60
		self.buttonPanel.AutoSizeMode = AutoSizeMode.GrowAndShrink
		self.buttonPanel.AutoScroll = True
		self.buttonPanel.BackColor = Color.White
		#self.buttonPanel.Anchor = (AnchorStyles.Bottom | AnchorStyles.Left | AnchorStyles.Right)
		#self.buttonPanel.ControlAdded += self.control_Added 
		
		
		self.dgv = DataGridView()
		self.dgv.SelectionMode = DataGridViewSelectionMode.FullRowSelect
		#self.dgv.AutoGenerateColumns = True
		self.dgv.BackColor = Color.Yellow
		self.dgv.ColumnAdded += self.ColumnAdded

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
		self.dgv.CellClick += self.cellClick
		self.dgv.SelectionChanged += self.selectionChanged
		#self.dgv.DataBindingComplete += self.setSelectedRowsEvent		

		self.columnNames = ("Num", "Id", "Category")

		tableDicList, tableObjectList = self.getDataSources(self.ids)
		#self.createDGVbyRows(tableDicList)
		self.createDGVbyDataSource(tableObjectList)
		print("self.dgv.DataSource {0}".format(self.dgv.DataSource))
		
		self.Controls.Add(self.buttonPanel)

		self.infoLabel = Label()
		self.infoLabel.Width = self.panelWidth
		self.infoLabel.Height = 30
		self.infoLabel.TextAlign = ContentAlignment.MiddleLeft
		self.infoLabel.Text = ""
		self.infoLabel.Location = Point(0,0)
		self.buttonPanel.Controls.Add(self.infoLabel)

		self.inputTextBox = TextBox()
		self.inputTextBox.Name = "inputTextBox"
		self.inputTextBox.Width = self.panelWidth
		self.inputTextBox.Height = 30
		self.inputTextBox.TextAlign = HorizontalAlignment.Left
		self.inputTextBox.Text = ""
		self.inputTextBox.Location = Point(0,30)
		self.inputTextBox.KeyDown += self.close
		self.buttonPanel.Controls.Add(self.inputTextBox)

		self.confirmButton = Button()
		self.confirmButton.Text = "Show Element"
		self.confirmButton.Name = "confirmButton"
		self.confirmButton.Height = 30
		self.confirmButton.Width = self.buttonPanel.Width
		self.confirmButton.Click += self.close
		self.confirmButton.Location = Point(0,60)
		#self.confirmButton.AutoSize = True
		#self.confirmButton.Dock = DockStyle.Top
		#self.confirmButton.Anchor = (AnchorStyles.Top | AnchorStyles.Left)
		self.buttonPanel.Controls.Add(self.confirmButton)

		""" self.upButton = Button()
		self.upButton.Text = "Select"
		self.upButton.Height = 30
		self.upButton.Click += self.itemUp
		self.upButton.Width = self.buttonPanel.Width/2
		self.upButton.Location = Point(0,30)
		#self.upButton.AutoSize = True
		#self.upButton.Dock = DockStyle.Left
		#self.upButton.Anchor = (AnchorStyles.Bottom| AnchorStyles.Right)
		self.buttonPanel.Controls.Add(self.upButton) """

		self.selectButton = Button()
		self.selectButton.Name = "selectButton"
		self.selectButton.Text = "Select"
		self.selectButton.Height = 30
		self.selectButton.Click += self.selectSelected
		self.selectButton.Width = self.buttonPanel.Width/2
		self.selectButton.Location = Point(self.buttonPanel.Width/2,30)
		#self.downButton.AutoSize = True
		#self.downButton.Dock = DockStyle.Right
		#self.downButton.Anchor = (AnchorStyles.Bottom | AnchorStyles.Right)
		self.buttonPanel.Controls.Add(self.selectButton)
		
		self.Controls.Add(self.dgvPanel)
		
		self.dgvPanel.Controls.Add(self.dgv)		

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
					rowValues = (dic[self.columnNames[0]], dic[self.columnNames[1]])
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
	
	def getDataSources(self, inTableData):
		tableObjectList = []
		tableDicList = []
		#priorityCategoriesNames = getPriorityCategoriesNames(inTableData)
		for i,elId in enumerate(inTableData):

			""" if not hasattr(v, "__iter__"):
				#print("toString {}".format(dir(v)))
				builtInPriorityCategory = str(v)
			else:
				builtInPriorityCategory = ", ".join([str(x) for x in v])
			priorityCategory = priorityCategoriesNames[i]
			dic = {self.columnNames[0] : i, \
					self.columnNames[1] : priorityCategory, \
					self.columnNames[2] : builtInPriorityCategory} """
			element = doc.GetElement(elId)
			elCategory = element.Category.Name if element else None
			#elementId = element.Id.IntegerValue
			dic = {self.columnNames[0] : i, \
					self.columnNames[1] : elId.IntegerValue, \
					self.columnNames[2] : elCategory}
			rowObj = Dic2obj(dic)
			tableDicList.append(dic)
			tableObjectList.append(rowObj)
		return (tableDicList, tableObjectList)
	
	def ColumnAdded(self, sender, *args):
		if self.dgv.Columns.Count == len(self.columnNames):
			if self.dgv.Columns["Num"]:
				print("column Num added")
				self.dgv.Columns["Num"].DisplayIndex = 0
				self.dgv.Columns["Num"].ReadOnly = True
				self.dgv.Columns["Num"].Width = 65
			if self.dgv.Columns["Category"]:
				print("column Category added")
				self.dgv.Columns["Category"].DisplayIndex = 2
				self.dgv.Columns["Category"].ReadOnly = True
				self.dgv.Columns["Category"].ReadOnly = True
			if self.dgv.Columns["Id"]:
				print("column Id added")
				self.dgv.Columns["Id"].DisplayIndex = 1
				self.dgv.Columns["Id"].ReadOnly = True
				self.dgv.Columns["Id"].ReadOnly = True

	def selectionChanged(self, sender, e):
		#self.infoLabel.Text = "Id {0} at row {1}".format(self.dgv.Columns["Id"][0], self.dgv.Rows[e.RowIndex])
		self.selectedIds = []
		for i,row in enumerate(self.dgv.SelectedRows):
			elementId = self.dgv.Rows[row.Index].Cells[1].FormattedValue
			self.selectedIds.append(DB.ElementId(int(elementId)))
		strIds = [x.ToString() for x in self.selectedIds]
		self.inputTextBox.Text = ",".join(strIds)
		self.infoLabel.Text = "selected Ids {0}".format(strIds)
		#print("sender - {0}".format(dir(sender)))

	def cellClick(self, sender, e):
		if e.RowIndex >=0:
			print("{0} Row, {1} Column button clicked".format(e.RowIndex +1, e.ColumnIndex +1))
			#self.infoLabel.Text = "Id {0} at row {1}".format(self.dgv.Columns["Id"][0], self.dgv.Rows[e.RowIndex])
			#print("sender - {0}".format(dir(sender)))

	def itemUp(self, sender, e):
		pass
		""" 
		print("sender.Name {0}, e {1}".format(sender.Text, e))
		if sender.Text == "UP":
			up = True
		else:
			up = False
		movementDone = False
		selectedRow = self.dgv.SelectedRows
		print("selectedRow.Index {0}".format(selectedRow[0].Index if len(selectedRow)>0 else None))
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
		#print("sender dir {0}".format(dir(sender))) """

	def updateInfoLabel(self, inText):
		self.infoLabel.Text = str(inText)

	def selectSelected(self, sender, event):
		if sender.Name == "selectButton":
			strIds = [x.strip() for x in self.inputTextBox.Text.split(",")]
			self.selectedIds = [DB.ElementId(int(x)) for x in strIds]
			print("strIds {}".format(strIds))
			selectedIdsCol = Clist[DB.ElementId](self.selectedIds)
			uidoc.Selection.SetElementIds(selectedIdsCol)
			uidoc.ShowElements(selectedIdsCol)


	def close(self, sender, event):
		
		self.confirmed = True
		if sender.Name == "inputTextBox":
			if event.KeyValue == 13:			
				inputId = DB.ElementId(int(sender.Text))
				print("inputTextBox {0}".format(inputId))
		elif sender.Name =="confirmButton":
			#pass
			#priorityLookup = self.priorityLookup
			print("self.OpenForms {}".format(list(Application.OpenForms)))
			self.rpsOutput = list(Application.OpenForms)[0]
			currentForm = list(Application.OpenForms)[-1]
			print("currentForm.__class__.__name__ {}".format(currentForm.__class__.__name__))
			#self.rpsOutput.Hide()
			selectedIdsCol = Clist[DB.ElementId](self.selectedIds)
			uidoc.Selection.SetElementIds(selectedIdsCol)
			uidoc.ShowElements(selectedIdsCol)
			self.Close()
			#self.rpsOutput.TopMost = True
			#Application.Exit()

openedForms = list(Application.OpenForms)
rpsOutputs = []
for i, oForm in enumerate(openedForms):
	print(str(i))
	print(oForm)
	if "RevitPythonShell" in str(oForm):
		print("Totot je oForm {0}".format(oForm))
		rpsOutputs.append(oForm)
	else:
		rpsOutput = None

print(doc)

elIds = [DB.ElementId(1064911), \
		DB.ElementId(1356699), \
		DB.ElementId(1268613)]

viewSelection = list(uidoc.Selection.GetElementIds())

if len(viewSelection) > 0:
	elIds = viewSelection

for i, elId in enumerate(elIds):
	myElement = doc.GetElement(elId)
	print("{0} - {1}".format(i, myElement))

#uidoc.ShowElements(ElementId)

myDialogWindow = MainForm(elIds)
#myDialogWindow.updateInfoLabel("Number of element pairs to process - {0}".format(len(selComb)))
Application.Run(myDialogWindow)

if len(rpsOutputs) > 0:
	try:
		for rpsOutput in rpsOutputs:
			rpsOutput.Show()
			rpsOutput.TopMost = True
	except:
		pass
