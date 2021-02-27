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

from itertools import combinations

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document


def pickobjects(inStatus):
    __window__.Hide()
    picked = uidoc.Selection.PickElementsByRectangle(inStatus)
    __window__.Show()
    #__window__.Topmost = True
    return picked

def pickobject(inStatus):
    from Autodesk.Revit.UI.Selection import ObjectType
    __window__.Hide()
    picked = uidoc.Selection.PickObject(ObjectType.Element, inStatus)
    __window__.Show()
    #__window__.Topmost = True
    return picked

priorityLookup = [	Autodesk.Revit.DB.BuiltInCategory.OST_Columns, \
					Autodesk.Revit.DB.BuiltInCategory.OST_StructuralFraming, \
					[Autodesk.Revit.DB.FootPrintRoof, Autodesk.Revit.DB.ExtrusionRoof], \
					Autodesk.Revit.DB.Wall, \
					[Autodesk.Revit.DB.Floor, Autodesk.Revit.DB.SlabEdge]]

def getPriorityCategoriesNames(inPriorityLookup):
	returnlist = []
	for item in inPriorityLookup:
		if not hasattr(item, "__iter__"):
			if str(item) == "OST_Columns":
				returnlist.append("Sloupy")
			elif str(item) == "OST_StructuralFraming":
				returnlist.append("Konstrukční rámová konstrukce")
			elif item == Autodesk.Revit.DB.Wall:
				returnlist.append("Stěny")
		elif Autodesk.Revit.DB.FootPrintRoof in item:
				returnlist.append("Střechy")
		elif Autodesk.Revit.DB.Floor in item:
				returnlist.append("Podlahy")
		else:
			returnlist.append(str(item))
	print("categoryNames {0}".format(returnlist))
	return returnlist
		

bic = System.Enum.GetValues(DB.BuiltInCategory)
#print(bic)
cats = {}
for i in bic:
	#print(type(i))
	try:
		cat = DB.Category.GetCategory(doc, i)
		#print(cat.Name if cat else i.ToString())
		cats[cat.Name] = i
	except:
		cat = None
#for k, v in cats.items():	
#	print("{0} - {1}".format(k,v))

class MainForm(Form):
	def __init__(self, inPriorityLookup):
		self.scriptDir = "\\".join(__file__.split("\\")[:-1])
		print(self.scriptDir)
		iconFilename = os.path.join(self.scriptDir, 'LIB\\spaceific_64x64_sat_X9M_icon.ico')
		icon = Icon(iconFilename)
		self.Icon = icon	

		self.priorityLookup = inPriorityLookup
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
		#self.dgv.SelectionChanged += self.selectionChanged
		#self.dgv.DataBindingComplete += self.setSelectedRowsEvent		

		self.columnNames = ("Priority", "Category", "Builtin Category or Class")

		tableDicList, tableObjectList = self.getDataSources(self.priorityLookup)
		#self.createDGVbyRows(tableDicList)
		self.createDGVbyDataSource(tableObjectList)
		print("self.dgv.DataSource {0}".format(self.dgv.DataSource))
		
		self.Controls.Add(self.buttonPanel)

		self.infoLabel = Label()
		self.infoLabel.Width = self.panelWidth
		self.infoLabel.Height = 30
		self.infoLabel.TextAlign = ContentAlignment.MiddleLeft
		self.infoLabel.Text = "wewe"
		self.infoLabel.Location = (Point(0,0))
		self.buttonPanel.Controls.Add(self.infoLabel)

		self.confirmButton = Button()
		self.confirmButton.Text = "Confirm"
		self.confirmButton.Height = 30
		self.confirmButton.Width = self.buttonPanel.Width
		self.confirmButton.Click += self.close
		self.confirmButton.Location = Point(0,60)
		#self.confirmButton.AutoSize = True
		#self.confirmButton.Dock = DockStyle.Top
		#self.confirmButton.Anchor = (AnchorStyles.Top | AnchorStyles.Left)
		self.buttonPanel.Controls.Add(self.confirmButton)

		self.upButton = Button()
		self.upButton.Text = "UP"
		self.upButton.Height = 30
		self.upButton.Click += self.itemUp
		self.upButton.Width = self.buttonPanel.Width/2
		self.upButton.Location = Point(0,30)
		#self.upButton.AutoSize = True
		#self.upButton.Dock = DockStyle.Left
		#self.upButton.Anchor = (AnchorStyles.Bottom| AnchorStyles.Right)
		self.buttonPanel.Controls.Add(self.upButton)

		self.downButton = Button()
		self.downButton.Text = "DOWN"
		self.downButton.Height = 30
		self.downButton.Click += self.itemUp
		self.downButton.Width = self.buttonPanel.Width/2
		self.downButton.Location = Point(self.buttonPanel.Width/2,30)
		#self.downButton.AutoSize = True
		#self.downButton.Dock = DockStyle.Right
		#self.downButton.Anchor = (AnchorStyles.Bottom | AnchorStyles.Right)
		self.buttonPanel.Controls.Add(self.downButton)
		
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
		priorityCategoriesNames = getPriorityCategoriesNames(inTableData)
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
		return (tableDicList, tableObjectList)
	
	def ColumnAdded(self, sender, *args):
		if self.dgv.Columns.Count == len(self.columnNames):
			if self.dgv.Columns["_Num"]:
				print("column Priority added")
				self.dgv.Columns["Priority"].DisplayIndex = 0
				self.dgv.Columns["Priority"].ReadOnly = True
				self.dgv.Columns["Priority"].Width = 65
			if self.dgv.Columns["Category"]:
				print("column Category added")
				self.dgv.Columns["Category"].DisplayIndex = 1
				self.dgv.Columns["Category"].ReadOnly = True

	def cellClick(self, sender, e):

		if e.RowIndex >=0:
			print("{0} Row, {1} Column button clicked".format(e.RowIndex +1, e.ColumnIndex +1))

	def itemUp(self, sender, e):
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
		#print("sender dir {0}".format(dir(sender)))
	def updateInfoLabel(self, inText):
		self.infoLabel.Text = str(inText)

	def close(self, sender, event):
		#pass
		priorityLookup = self.priorityLookup
		print("self.OpenForms {}".format(list(Application.OpenForms)))
		self.rpsOutput = list(Application.OpenForms)[0]
		currentForm = list(Application.OpenForms)[-1]
		print("currentForm.__class__.__name__ {}".format(currentForm.__class__.__name__))
		#self.rpsOutput.Hide()
		self.confirmed = True
		self.Close()
		#self.rpsOutput.TopMost = True
		#Application.Exit()

class ProgressBarDialog(Form):
	def __init__(self, inMax):
		self.scriptDir = "\\".join(__file__.split("\\")[:-1])
		print(self.scriptDir)
		iconFilename = os.path.join(self.scriptDir, 'LIB\\spaceific_64x64_sat_X9M_icon.ico')
		icon = Icon(iconFilename)
		self.Icon = icon	

		self.Text = 'Join All Selected Elements by Priority - Script by Spaceific-Studio'
		self.TopMost = True
		screenSize = Screen.GetWorkingArea(self)
		self.Height = 150
		self.Width = 800
		self.StartPosition = FormStartPosition.CenterScreen
		self.panelHeight = self.ClientRectangle.Height * 0.75
		self.panelWidth = self.ClientRectangle.Width / 3
		self.bgColor = Color.CadetBlue
		self.textColor = Color.White

		self.pb = ProgressBar()
		self.pb.Minimum = 1
		#self.pb.IsIndeterminate = False
		self.pb.Maximum = inMax + 1
		self.pb.Step = 0
		self.pb.Value = 1
		self.pb.Width = self.Width
		self.pb.Height = 30
		self.pb.Location = (Point(0,30))
		self.Controls.Add(self.pb)

		self.progressLabel = Label()
		self.progressLabel.Width = self.pb.Width
		self.progressLabel.Height = 30
		self.progressLabel.Text = "0"
		self.progressLabel.TextAlign = ContentAlignment.MiddleCenter
		self.progressLabel.Location = (Point(0,60))
		self.Controls.Add(self.progressLabel)

		self.infoLabel = Label()
		self.infoLabel.Width = self.pb.Width
		self.infoLabel.Height = 30
		self.infoLabel.TextAlign = ContentAlignment.MiddleCenter
		self.infoLabel.Text = "Joining elements..."
		self.infoLabel.Location = (Point(0,0))
		self.Controls.Add(self.infoLabel)
	
	def start(self):
		for i in range(100):
			self.UpdateProgress()
			#System.Threading.Dispatcher.Run(UpdateProgress())
			#self.pb.Dispatcher.Invoke(ProgressBarDelegate(self.UpdateProgress), DispatcherPriority.Background)
			Thread.Sleep(15)
		""" def update():
			for i in range(100):
				print i
				def step():
					self.prog.Value = i + 1
				
				self.Invoke(CallTarget0(step))
				Thread.Sleep(15)
			self.Close() """
		#t = Thread(ThreadStart(update))
		#t.Start()
	def updateProgressLabel(self, inText):
		self.progressLabel.Text = str(inText)

	def UpdateProgress(self):
		self.pb.Value +=1

class Dic2obj(object):
	def __init__(self, dictionary):
		for key in dictionary:
			setattr(self, key, dictionary[key])

def getElementPriority(inElement):
	if isinstance(inElement, Autodesk.Revit.DB.FamilyInstance):
		cat = cats[inElement.Category.Name]
		#print("cat[el.Category.Name] {0} - class {1}".format(cat, cat.__class__))
		if cat in priorityLookup:
			#print("{0} is in priorityLookup {1}".format(cat, priorityLookup.index(cat)))
			return priorityLookup.index(cat)
		else:
			return len(priorityLookup)
	else:
		cName = inElement.__class__.__name__
		if cName == "ExtrusionRoof" or cName == "FootPrintRoof":
			cat = [Autodesk.Revit.DB.FootPrintRoof, Autodesk.Revit.DB.ExtrusionRoof]
		elif cName == "Floor" or cName == "SlabEdge":
			cat = [Autodesk.Revit.DB.Floor, Autodesk.Revit.DB.SlabEdge]
		else:
			#print("type(inElement {0})".format(type(inElement)))
			cat = type(inElement)
		if cat in priorityLookup:
			return priorityLookup.index(cat)
		else:
			return len(priorityLookup)

firstSelection = [doc.GetElement(elId) for elId in __revit__.ActiveUIDocument.Selection.GetElementIds()]


print("firstSelection len {0}".format(len(firstSelection)))
for i, el in enumerate(firstSelection):
	if isinstance(el, Autodesk.Revit.DB.FamilyInstance):
		categoryId = el.Symbol.Family.FamilyCategoryId
		cat = cats[el.Category.Name]
		#className = el.Category.CategoryType
		name = cat.ToString()
	else:
		name = el.__class__.__name__
	print("{0}-{1} {2} {3}".format(i, el.Id, el.Category.Name, name))
selComb = list(combinations(firstSelection, 2))
#while next(selComb):
#    print("selComb \n{0}".format(selComb))
#print("selComb \n{0}".format(selComb))
print("selComb len {0}".format(len(selComb)))

openedForms = list(Application.OpenForms)
for i, oForm in enumerate(openedForms):
	print(str(i))
	print(oForm)
	if "RevitPythonShell" in str(oForm):
		print("Totot je oForm {0}".format(oForm))
		rpsOutput = oForm
	else:
		rpsOutput = None
print("__main__.OpenForms {}".format(list(Application.OpenForms)))
#rpsOutput = list(Application.OpenForms)[0]

if rpsOutput:
	rpsOutput.Hide()
else:
	pass
myDialogWindow = MainForm(priorityLookup)
myDialogWindow.updateInfoLabel("Number of element pairs to process - {0}".format(len(selComb)))
Application.Run(myDialogWindow)


if myDialogWindow.confirmed:
	pBar = ProgressBarDialog(len(selComb))
	
	fThread = Thread(ThreadStart(pBar))
	pBar.Show()
	#myDialogWindow = MainForm(priorityLookup)
	#Application.Run(myDialogWindow)
	#mainFormThread = threading.Thread(target=Application.Run(myDialogWindow), args=(1,))
	#mainFormThread.start()

	#mainFormThread.join()


	t = DB.Transaction(doc, "Join all selected elements")
	t.Start()

	for i, pair in enumerate(selComb):
		pairCats = []
		for item in pair:
			if isinstance(item, Autodesk.Revit.DB.FamilyInstance):
				cat = cats[item.Category.Name]
				#className = el.Category.CategoryType
				name = cat.ToString()
			else:
				name = item.__class__.__name__
			pairCats.append(name)
		areJoined = DB.JoinGeometryUtils.AreElementsJoined(doc, pair[0], pair[1])
		try:
			DB.JoinGeometryUtils.JoinGeometry(doc, pair[0], pair[1])
			joining = True
		except:
			joining = False
		finalJoin = DB.JoinGeometryUtils.AreElementsJoined(doc, pair[0], pair[1])
		if finalJoin:
			isCuttingElement = DB.JoinGeometryUtils.IsCuttingElementInJoin(doc, pair[0], pair[1])
		else:
			isCuttingElement = False
		itemOnePriority = getElementPriority(pair[0])
		itemTwoPriority = getElementPriority(pair[1])
		if not isCuttingElement and (itemOnePriority < itemTwoPriority) and finalJoin:
			try:
				DB.JoinGeometryUtils.SwitchJoinOrder(doc, pair[0], pair[1])
				switched = True
			except:
				switched = False
		elif isCuttingElement and (itemOnePriority > itemTwoPriority) and finalJoin:
			try:
				DB.JoinGeometryUtils.SwitchJoinOrder(doc, pair[0], pair[1])
				switched = True
			except:
				switched = False
		else:
			switched = False
		pBar.updateProgressLabel("processing {0} of {1} - {2} with {3}".format(i, len(selComb), pair[0].Id, pair[1].Id))
		pBar.UpdateProgress()
		print("{0} - Element_0: {1}-{2} priority {3} <> Element_1 {4}-{5} priority {6} \nwas joined - {7} \njoining {8} \nfinal join {9} \n first is cutting {10} \nswitched {11}".format(i, \
																													pair[0].Id, \
																													pairCats[0], \
																													getElementPriority(pair[0]), \
																													pair[1].Id, \
																													pairCats[1], \
																													getElementPriority(pair[1]), \
																													areJoined, \
																													joining, \
																													finalJoin, \
																													isCuttingElement, \
																													switched))

	#emptyList = []
	#emptyCList = Clist[DB.ElementId](emptyList)
	#__revit__.ActiveUIDocument.Selection.SetElementIds(emptyCList)
	""" 	areJoined = DB.JoinGeometryUtils.AreElementsJoined(doc, pair[0], pair[1])
		if not areJoined:
			try:
				DB.JoinGeometryUtils.JoinGeometry(doc, pair[0], pair[1])
				print("element {0} is joined with element {1} - areJoined > {2}".format(pair[0].Id, pair[1].Id, areJoined))
			except Exception as ex:
				import traceback
				print("ELEMENT {0} WAS NOT JOINED WITH ELEMENT {1} - {2}".format(pair[0].Id, pair[1].Id, areJoined))
				print("Traceback content >> \n {0}".format(sys.exc_info()))
				#exc_info = sys.exc_info()
				#traceback.print_exception(*exc_info)
				#del exc_info """
	t.Commit()
	pBar.Close()
	print("Script succesfully finished")
else:
	print("Script was cancelled")
rpsOutput.Show()
rpsOutput.TopMost = True
