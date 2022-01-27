# -*- coding: utf-8 -*-
# Copyright(c) 2021, Daniel Gercak
#Revit Python Shell script for multiple joining elements
#joins all selected elements applying join command to all neighbours using BoundingBoxIntersetctsFilter
#joining according to priority table 
#resource_path: https://github.com/Spaceific-Studio/_WORK/REVIT_API/joinAllElementsByPriority.py
import sys
if "IronPython" in sys.prefix:
	pytPath = r'C:\Program Files (x86)\IronPython 2.7\Lib'
	sys.path.append(pytPath)
import os
import platform
import time

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
		from Autodesk.Revit.DB import IFailuresPreprocessor, BuiltInFailures
		import System
		import threading
		from System.Collections.Generic import List as Clist
		from System import Type
		#from System.Collections.Generic import Ilist
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

try:
	runFromCsharp = True if "__csharp__" in dir() else False
	#UI.TaskDialog.Show("Run from C#", "Script is running from C#")
except:
	runFromCsharp = False


print("module : {0} ; hasMainAttr = {1}".format(__file__, hasMainAttr))
print("module : {0} ; hasAutodesk = {1}".format(__file__, hasAutodesk))

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

priorityLookup = [	[Autodesk.Revit.DB.BuiltInCategory.OST_Columns, Autodesk.Revit.DB.BuiltInCategory.OST_StructuralColumns], \
					Autodesk.Revit.DB.BuiltInCategory.OST_StructuralFraming, \
					[Autodesk.Revit.DB.FootPrintRoof, Autodesk.Revit.DB.ExtrusionRoof], \
					Autodesk.Revit.DB.Wall, \
					[Autodesk.Revit.DB.Floor, Autodesk.Revit.DB.SlabEdge], \
					Autodesk.Revit.DB.BuiltInCategory.OST_Ceilings]

def getAllElements(doc, *args, **kwargs):
	"""
		acquire all Elements from active view

		kwargs["toId"] type boolean: returns collection of Autodesk.Revit.DB.ElementId if True, else return Autodesk.Revit.DB.Element
		kwargs["inActiveView"] type bool: returns elements depending on active view if True, default = False
	"""
	toId = kwargs["toId"] if "toId" in kwargs else False
	inActiveView = kwargs["inActiveView"] if "inActiveView" in kwargs else False
	allElements = DB.FilteredElementCollector(doc)
	if inActiveView:
		paramId = DB.ElementId(DB.BuiltInParameter.VIEW_PHASE)
		param_provider = DB.ParameterValueProvider(paramId)
		activeViewPhaseId = param_provider.GetElementIdValue(doc.ActiveView)

		myElementPhaseStatusFilter1 = DB.ElementPhaseStatusFilter(activeViewPhaseId, DB.ElementOnPhaseStatus.Existing, False)
		myElementPhaseStatusFilter2 = DB.ElementPhaseStatusFilter(activeViewPhaseId, DB.ElementOnPhaseStatus.New,False)	
		
		if toId == False:
			returnElements = allElements.WherePasses(DB.LogicalOrFilter(DB.ElementIsElementTypeFilter(False), DB.ElementIsElementTypeFilter(True))) \
					.WherePasses(DB.LogicalOrFilter(myElementPhaseStatusFilter1 \
																	,myElementPhaseStatusFilter2)) \
					.ToElements()
		else:
			returnElements = allElements.WherePasses(DB.LogicalOrFilter(DB.ElementIsElementTypeFilter(False), DB.ElementIsElementTypeFilter(True))) \
				   .WherePasses(LogicalOrFilter(myElementPhaseStatusFilter1 \
																 ,myElementPhaseStatusFilter2)) \
				   .ToElementIds()
	else:
		if toId == False:
			returnElements = allElements.WherePasses(DB.LogicalOrFilter(DB.ElementIsElementTypeFilter(False), DB.ElementIsElementTypeFilter(True))).ToElements()
		else:
			returnElements = allElements.WherePasses(DB.LogicalOrFilter(DB.ElementIsElementTypeFilter(False), DB.ElementIsElementTypeFilter(True))).ToElementIds()

	return returnElements

def createMultiCategoryFilter():
	listOfCategories = list()
	#listOfCategories.append(DB.BuiltInCategory.OST_Floors)
	listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_Columns)
	listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_StructuralColumns)
	listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_StructuralFraming)
	listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_StructuralFoundation)
	#listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_Walls)
	#listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_Floors)
	#listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_Roofs)
	listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_Ceilings)
	colOfBIC = Clist[DB.BuiltInCategory](listOfCategories)
	multiCategoryFilter = DB.ElementMulticategoryFilter(colOfBIC)
	return multiCategoryFilter

def createExclusionMultiCategoryFilter():
	listOfCategories = list()
	#listOfCategories.append(DB.BuiltInCategory.OST_Floors)
	listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_IOSModelGroups)
	listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_MassOpening)
	listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_ArcWallRectOpening)
	listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_SWallRectOpening)
	listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_ShaftOpening)
	listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_StructuralFramingOpening)
	listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_ColumnOpening)
	listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_CeilingOpening)
	listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_FloorOpening)
	listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_RoofOpening)
	listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_IOSOpening)
	listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_WindowsOpeningCut)
	listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_DoorsOpeningCut)
	listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_CurtainGrids)
	listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_CurtainWallMullionsCut)
	listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_CurtainWallMullions)
	listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_CurtainWallPanels)
	listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_CurtainWallMullionsHiddenLines)
	listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_CurtainWallPanelsHiddenLines)
	colOfBIC = Clist[DB.BuiltInCategory](listOfCategories)
	multiCategoryFilter = DB.ElementMulticategoryFilter(colOfBIC)
	return multiCategoryFilter

def createMultiClassFilter():
	listOfClasses = list()
	listOfClasses.append(Autodesk.Revit.DB.FootPrintRoof)
	listOfClasses.append(Autodesk.Revit.DB.ExtrusionRoof)
	listOfClasses.append(Autodesk.Revit.DB.Wall)
	listOfClasses.append(Autodesk.Revit.DB.Floor)
	#due to an exception: Autodesk.Revit.Exceptions.ArgumentException: Input type(Autodesk.Revit.DB.SlabEdge)
	# is of an element type that exists in the API, but not in Revit's native object model. 
	# Try using Autodesk.Revit.DB.HostedSweep instead, and then postprocessing the results to find the elements of interest.
	#listOfClasses.append(Autodesk.Revit.DB.SlabEdge)
	listOfClasses.append(Autodesk.Revit.DB.HostedSweep)
	#colOfClasses = Clist[IronPython.Runtime.Types.PythonType](listOfClasses)
	typeList = Clist[System.Type]()
	for item in listOfClasses:
		typeList.Add(item)
	multiClassFilter = DB.ElementMulticlassFilter(typeList)
	return multiClassFilter

def getActiveViewPhaseStatusFilter():
	paramId = Autodesk.Revit.DB.ElementId(Autodesk.Revit.DB.BuiltInParameter.VIEW_PHASE)
	param_provider = Autodesk.Revit.DB.ParameterValueProvider(paramId)
	activeViewPhaseId = param_provider.GetElementIdValue(doc.ActiveView)
	docPhases =  Autodesk.Revit.DB.FilteredElementCollector(doc) \
								.OfCategory(Autodesk.Revit.DB.BuiltInCategory.OST_Phases) \
								.WhereElementIsNotElementType() \
								.ToElements()

	#Filter inserts visible only in active view and of Existing phase status - (ignore demolished elements in previous phases) 
	myElementPhaseStatusFilter1 = Autodesk.Revit.DB.ElementPhaseStatusFilter(activeViewPhaseId, Autodesk.Revit.DB.ElementOnPhaseStatus.Existing, False)
	myElementPhaseStatusFilter2 = Autodesk.Revit.DB.ElementPhaseStatusFilter(activeViewPhaseId, Autodesk.Revit.DB.ElementOnPhaseStatus.New,False)
	return DB.LogicalOrFilter(myElementPhaseStatusFilter1, myElementPhaseStatusFilter2)
	
def getAllModelElements(doc):
	multiCatFilter = createMultiCategoryFilter()
	allIdsOfModelElements = DB.FilteredElementCollector(doc).WherePasses(multiCatFilter).WhereElementIsNotElementType().ToElementIds()
	allElementsOfModel = map(lambda x: doc.GetElement(x), allIdsOfModelElements)
	return allElementsOfModel

def isElementInBBox(inElement, elementToSurvey, allElementsCol):
	inElementBBox = inElement.get_BoundingBox(doc.ActiveView)
	inElementOutline = DB.Outline(inElementBBox.Min, inElementBBox.Max)
	bboxIntersectingFilter = DB.BoundingBoxIntersectsFilter(inElementOutline)
	insideElementsIds = DB.FilteredElementCollector(doc).WherePasses(bboxIntersectingFilter).WhereElementIsNotElementType().ToElementIds()
	elIdsStr = [x.IntegerValue for x in insideElementsIds]
	for x in elIdsStr:
		print(x)
	if elementToSurvey.Id.IntegerValue in elIdsStr:
		print("Element {0} contains {1} inside BBox".format(inElement.Id, elementToSurvey.Id))
	return insideElementsIds

def convertFromInternal(inValue):
	displayUnitType = uidoc.Document.GetUnits().GetFormatOptions(DB.UnitType.UT_Length).DisplayUnits
	#print("displayUnitType {}".format(displayUnitType))
	return DB.UnitUtils.ConvertFromInternalUnits(inValue, displayUnitType)

def convertToInternal(inValue):
	displayUnitType = uidoc.Document.GetUnits().GetFormatOptions(DB.UnitType.UT_Length).DisplayUnits
	#print("displayUnitType {}".format(displayUnitType))
	return DB.UnitUtils.ConvertToInternalUnits(inValue, displayUnitType)

def getNeighbours(inElement, multiCatFilter, multiClassFilter, exclusionFilter, activeViewPhaseStatusFilter):
	inElementBBox = inElement.get_BoundingBox(doc.ActiveView)
	virtualBBoxOffset = 50
	newMin = DB.XYZ(convertToInternal(convertFromInternal(inElementBBox.Min.X)-virtualBBoxOffset), \
					convertToInternal(convertFromInternal(inElementBBox.Min.Y)-virtualBBoxOffset), \
					convertToInternal(convertFromInternal(inElementBBox.Min.Z)-virtualBBoxOffset))
	newMax = DB.XYZ(convertToInternal(convertFromInternal(inElementBBox.Max.X)+virtualBBoxOffset), \
					convertToInternal(convertFromInternal(inElementBBox.Max.Y)+virtualBBoxOffset), \
					convertToInternal(convertFromInternal(inElementBBox.Max.Z)+virtualBBoxOffset))
	#inElementOutline = DB.Outline(inElementBBox.Min, inElementBBox.Max)
	inElementOutline = DB.Outline(newMin, newMax)
	bboxIntersectingFilter = DB.BoundingBoxIntersectsFilter(inElementOutline)
	selfElementExclusionFilter = DB.ExclusionFilter(Clist[DB.ElementId]([inElement.Id]))
	
	insideElementsMulitCatIdsCol = DB.FilteredElementCollector(doc) \
									.WherePasses(multiCatFilter) \
									.WherePasses(exclusionFilter) \
									.WherePasses(bboxIntersectingFilter) \
									.WherePasses(selfElementExclusionFilter) \
									.WherePasses(activeViewPhaseStatusFilter) \
									.WhereElementIsNotElementType() \
									.ToElementIds()
	insideElementsMulitClassIdsCol = DB.FilteredElementCollector(doc) \
										.WherePasses(multiClassFilter) \
										.WherePasses(exclusionFilter) \
										.WherePasses(bboxIntersectingFilter) \
										.WherePasses(selfElementExclusionFilter) \
										.WherePasses(activeViewPhaseStatusFilter) \
										.WhereElementIsNotElementType() \
										.ToElementIds()

	insideElementsMulitCatIds = list(insideElementsMulitCatIdsCol)
	insideElementsMulitClassIds = list(insideElementsMulitClassIdsCol)

	return insideElementsMulitCatIds + insideElementsMulitClassIds

def getPriorityCategoriesNames(inPriorityLookup):
	returnlist = []
	for item in inPriorityLookup:
		if not hasattr(item, "__iter__"):
			if str(item) == "OST_StructuralFraming":
				returnlist.append("Konstrukční rámová konstrukce")
			elif str(item) == "OST_Ceilings":
				returnlist.append("Podhledy")
			elif item == Autodesk.Revit.DB.Wall:
				returnlist.append("Stěny")
		elif Autodesk.Revit.DB.BuiltInCategory.OST_Columns in item:
				returnlist.append("Sloupy")
		elif Autodesk.Revit.DB.FootPrintRoof in item:
				returnlist.append("Střechy")
		elif Autodesk.Revit.DB.Floor in item:
				returnlist.append("Podlahy")
		else:
			returnlist.append(str(item))
	#print("categoryNames {0}".format(returnlist))
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

		self.priorityLookup = inPriorityLookup
		self.confirmed = False
		
		self.InitializeComponent()

	def InitializeComponent(self):
		self.Text = "Setup of join priority for categories by Spaceific-Studio"
		self.Width = 500
		self.Height = 280
		self.StartPosition = FormStartPosition.CenterScreen
		self.TopMost = True
		screenSize = Screen.GetWorkingArea(self)
		#self.Height = screenSize.Height / 5
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
		#self.dgv.ColumnAdded += self.ColumnAdded
		self.dgv.DataBindingComplete += self.DataBindingComplete

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
		#print("self.dgv.DataSource {0}".format(self.dgv.DataSource))
		
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

	def DataBindingComplete(self, sender, event):
		self.arangeColumns()
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
				col.ReadOnly = True
			elif col.Name == self.columnNames[2]:
				#print("column {0} was updated".format(col.Name))
				col.SortMode = DataGridViewColumnSortMode.Programmatic
				col.DisplayIndex = 2
				col.ReadOnly = True

	def cellClick(self, sender, e):

		if e.RowIndex >=0:
			pass
			#print("{0} Row, {1} Column button clicked".format(e.RowIndex +1, e.ColumnIndex +1))

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
	def updateInfoLabel(self, inText):
		self.infoLabel.Text = str(inText)

	def close(self, sender, event):
		priorityLookup = self.priorityLookup
		self.confirmed = True
		self.Close()


class ProgressBarDialog(Form):
	def __init__(self, inMax):
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

		self.Text = 'Join All Selected Elements by Priority - Script by Spaceific-Studio'
		self.TopMost = True
		screenSize = Screen.GetWorkingArea(self)
		self.Height = 200
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

		""" self.infoLabel2 = Label()
		self.infoLabel2.Width = self.pb.Width
		self.infoLabel2.Height = 90
		self.infoLabel2.TextAlign = ContentAlignment.MiddleCenter
		self.infoLabel2.Text = "Joining elements..."
		self.infoLabel2.Location = (Point(0,90))
		self.Controls.Add(self.infoLabel2) """

		self.cancelButton = Button()
		self.cancelButton.Text =  "Cancel"
		self.cancelButton.Name = "Cancel"
		self.cancelButton.Location = (Point(self.Width/2 - self.cancelButton.Width/2, 120))
		self.cancelButton.Click += self.close
		self.Controls.Add(self.cancelButton)

	def updateProgressLabel(self, inText):
		pass
		self.progressLabel.Text = "{0}".format(inText)

	def UpdateProgress(self):
		self.pb.Value +=1
	
	def close(self, sender, event):
		scriptCancelled = True
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
				lastForm.Close()
		else:
			lastForm = None
			self.Close()
		
		
class WarningSwallower(IFailuresPreprocessor):
	def PreprocessFailures(self, failuresAccessor):
		#fail_list = CList[FailureMessageAccessor]()
		fail_acc_list = failuresAccessor.GetFailureMessages().GetEnumerator()
		print("WarningSwallower IS ACTIVE {}".format(failuresAccessor.IsActive()))
		for i, failure in enumerate(fail_acc_list):
			failure_id = failure.GetFailureDefinitionId()
			#failure_AdditionalElementIds = list(failure.GetAdditionalElementIds())
			#failure_ElementIds = list(failure.GetFailingElementIds())
			#failure_Type = failure.GetCurrentResolutionType()
			#failure_descriptionText = failure.GetDescriptionText()
			failure_has_resolutions = failure.HasResolutions()
			failure_elements_Ids = list(failure.GetFailingElementIds())
			#failure_default_resolution_caption = failure.GetDefaultResolutionCaption()
			#failure_has_resolutions = failure.HasResolutions()
			#failure_severity = failure.GetSeverity()
			joiningDisjoint_failure_type = DB.BuiltInFailures.JoinElementsFailures.JoiningDisjointWarn
			if failure_id == joiningDisjoint_failure_type:
				#print("{0} WITH ID: {1} DESCRIPTION: {2}: ID {3} - HAS RESOLUTION: {4}\n DEFAULT RESOLUTION CAPTION {5}".format( \
				#                                    failure_severity, \
				#                                    failure_id.Guid, \
				#                                    failure_descriptionText, \
				#                                    failure_id.ToString(), \
				#                                    failure_has_resolutions, \
				#                                    failure_default_resolution_caption))
				if failure_has_resolutions:                    
					#failuresAccessor.DeleteWarning(failure)
					failure.SetCurrentResolutionType(DB.FailureResolutionType.DetachElements)
					#print("FAILURE RESOLUTION TO DetachElements WAS SET")
					failuresAccessor.ResolveFailure(failure)
					print("{0} - FAILURE joiningDisjoint WAS RESOLVED - IDs {1}".format(i,[x.IntegerValue for x in failure_elements_Ids]))
					failuresAccessor.DeleteWarning(failure)
					print("  FAILURE WARNING WAS DELETED")
				else:
					failuresAccessor.DeleteWarning(failure)
			elif failure_id == BuiltInFailures.ColumnInsideWallFailures.ColumnInsideWall:
				if failure_has_resolutions:
					failure.SetCurrentResolutionType(DB.FailureResolutionType.DetachElements)
					failuresAccessor.ResolveFailure(failure)
					print("{0} - FAILURE ColumnInsideWall WAS RESOLVED - IDs {1}".format(i,[x.IntegerValue for x in failure_elements_Ids]))
					failuresAccessor.DeleteWarning(failure)
					print("  FAILURE WARNING WAS DELETED")
				else:
					failuresAccessor.DeleteWarning(failure)
			elif failure_id == BuiltInFailures.RegenFailures.GeomStepFailedError:
				print("{0} - FAILURE RegenFailures WAS RESOLVED - IDs {1}".format(i,[x.IntegerValue for x in failure_elements_Ids]))
				if failure_has_resolutions:
					#failure.SetCurrentResolutionType(DB.FailureResolutionType.DetachElements)
					#failuresAccessor.ResolveFailure(failure)
					print("  HAS RESOLUTION")
					failuresAccessor.DeleteWarning(failure)
					print("  FAILURE WARNING WAS DELETED")
				else:
					failuresAccessor.DeleteWarning(failure)
		return DB.FailureProcessingResult.Continue

class Dic2obj(object):
	def __init__(self, dictionary):
		for key in dictionary:
			setattr(self, key, dictionary[key])

def getElementPriority(inElement):
	try:
		if isinstance(inElement, Autodesk.Revit.DB.FamilyInstance):
			cat = cats[inElement.Category.Name]
			#print("cat[el.Category.Name] {0} - class {1}".format(cat, cat.__class__))
			if cat in priorityLookup:
				#print("{0} is in priorityLookup {1}".format(cat, priorityLookup.index(cat)))
				return priorityLookup.index(cat)
			elif cat == Autodesk.Revit.DB.BuiltInCategory.OST_Columns or cat == Autodesk.Revit.DB.BuiltInCategory.OST_StructuralColumns:
				return priorityLookup.index([Autodesk.Revit.DB.BuiltInCategory.OST_Columns, Autodesk.Revit.DB.BuiltInCategory.OST_StructuralColumns])
			else:
				return len(priorityLookup)
		else:
			cat = cats[inElement.Category.Name]
			#print("getElementPriority cat {}".format(cat))
			cName = inElement.__class__.__name__
			if cName == "ExtrusionRoof" or cName == "FootPrintRoof":
				cat = [Autodesk.Revit.DB.FootPrintRoof, Autodesk.Revit.DB.ExtrusionRoof]
			elif cName == "Floor" or cName == "SlabEdge":
				cat = [Autodesk.Revit.DB.Floor, Autodesk.Revit.DB.SlabEdge]
			elif cat in priorityLookup:
				#print("cat: {0} - priorityLookup {1}".format(cat, priorityLookup.index(cat) if cat in priorityLookup else "Not in priorityLookup"))
				try:
					priority = priorityLookup.index(cat)
				except:
					priority = len(priorityLookup)
				return priority
			else:
				#print("type(inElement {0})".format(type(inElement)))
				cat = type(inElement)
				#print("cat type(inElement): {0} - {1}".format(type(inElement), priorityLookup.index(cat) if cat in priorityLookup else "Not in priorityLookup"))
			if cat in priorityLookup:
				return priorityLookup.index(cat)
			else:
				return len(priorityLookup)
	except:
		return len(priorityLookup)

def getIntersectionWarnings():
	warningDescriptions = ["Highlighted elements are joined but do not intersect.", "Zvýrazněné prvky jsou připojeny, ale neprotínají se."]
	warnings = doc.GetWarnings()
	returnWarnings = []
	for j, warning in enumerate(warnings):
		descText = warning.GetDescriptionText()
		if descText in warningDescriptions:
			returnWarnings.append(warning)
	return returnWarnings

cvi = DB.ConnectionValidationInfo()
manyWarnings = cvi.ManyWarnings()
print("ManyWarnings() {0}".format(manyWarnings))
#input("waiting for enter press")

allElementsIds = getAllElements(doc, toId=True)
allElementsCol = Clist[DB.Element](getAllModelElements(doc))
print("allElementsIds length {}".format(len(allElementsIds)))
#input("waiting for enter...")

multiCatFilter = createMultiCategoryFilter()
multiClassFilter = createMultiClassFilter()
multiExclCategoryFilter = createExclusionMultiCategoryFilter()
allExcludedIds = list(DB.FilteredElementCollector(doc).WherePasses(multiExclCategoryFilter).ToElementIds())
allExcludedWallsIds = list(DB.FilteredElementCollector(doc).OfClass(Autodesk.Revit.DB.Wall))
wallIdsToExclude = []
for el in allExcludedWallsIds:
	#print("allExcludedWalls {}".format(dir(el)))
	if hasattr(el, "CurtainGrid"):
		if el.CurtainGrid:
			wallIdsToExclude.append(el.Id)
allExcludedIds += wallIdsToExclude

exclusionFilter = DB.ExclusionFilter(Clist[DB.ElementId](allExcludedIds))
activeViewPhaseStatusFilter = getActiveViewPhaseStatusFilter()

print("allExcludedIds length {}".format(len(allExcludedIds)))
#uidoc.Selection.SetElementIds(allExcludedIds)
#input("waiting for enter...")

firstSelectionMultiCatIdsCol = DB.FilteredElementCollector(doc, __revit__.ActiveUIDocument.Selection.GetElementIds()) \
									.WherePasses(multiCatFilter) \
									.WherePasses(exclusionFilter) \
									.WherePasses(activeViewPhaseStatusFilter) \
									.WhereElementIsNotElementType() \
									.ToElementIds()
firstSelectionMultiClassIdsCol = DB.FilteredElementCollector(doc, __revit__.ActiveUIDocument.Selection.GetElementIds()) \
									.WherePasses(multiClassFilter) \
									.WherePasses(exclusionFilter) \
									.WherePasses(activeViewPhaseStatusFilter) \
									.WhereElementIsNotElementType() \
									.ToElementIds()
firstSelectionMultiCat = [doc.GetElement(elId) for elId in firstSelectionMultiCatIdsCol]
firstSelectionMultiClass = [doc.GetElement(elId) for elId in firstSelectionMultiClassIdsCol]

firstSelection = firstSelectionMultiCat + firstSelectionMultiClass

firstSelectionMultiCatIds = list(firstSelectionMultiCatIdsCol)
firstSelectionMultiClassIds = list(firstSelectionMultiClassIdsCol)
firstSelectionIds = firstSelectionMultiCatIds + firstSelectionMultiClassIds
firstSelectionIdsCol = Clist[DB.ElementId](firstSelectionIds)
uidoc.Selection.SetElementIds(firstSelectionIdsCol)
firstSelection = [doc.GetElement(x) for x in firstSelectionIdsCol]
scriptCancelled = False

#print("firstSelection len {0}".format(len(firstSelection)))
for i, el in enumerate(firstSelection):
	if isinstance(el, Autodesk.Revit.DB.FamilyInstance):
		categoryId = el.Symbol.Family.FamilyCategoryId
		familyName = el.Symbol.Family.FamilyCategory.Name
		cat = cats[el.Category.Name]
		#className = el.Category.CategoryType
		name = cat.ToString()
	else:
		name = el.__class__.__name__
		familyName = None
	print("{0}-{1} {2} {3} familyName {4}".format(i, el.Id, el.Category.Name, name, familyName))

if runFromCsharp == False:
	openedForms = list(Application.OpenForms)
	for i, oForm in enumerate(openedForms):
		#print(str(i))
		#print(oForm)
		if "RevitPythonShell" in str(oForm):
			#print("Totot je oForm {0}".format(oForm))
			rpsOutput = oForm
		else:
			rpsOutput = None
	#print("__main__.OpenForms {}".format(list(Application.OpenForms)))
	#rpsOutput = list(Application.OpenForms)[0]


	if rpsOutput:
		pass
		rpsOutput.Hide()
	else:
		pass
else:
	rpsOutput = None

myDialogWindow = MainForm(priorityLookup)
myDialogWindow.updateInfoLabel("Number of elements to process - {0}".format(len(firstSelection)))
Application.Run(myDialogWindow)

if myDialogWindow.confirmed:
	pBar = ProgressBarDialog(len(firstSelection))
	
	fThread = Thread(ThreadStart(pBar))
	pBar.Show()
	#rpsOutput.Show()

	alreadyJoined = []
	t = DB.Transaction(doc, "AutoJoin elements")
	t.Start()
	options = t.GetFailureHandlingOptions()
	options.SetFailuresPreprocessor(WarningSwallower())
	t.SetFailureHandlingOptions(options)

	print("len firstSelection before joining {0}".format(len(firstSelection)))
	for j, el in enumerate(firstSelection):
		neighbours = [doc.GetElement(x) for x in getNeighbours(el, multiCatFilter, multiClassFilter, exclusionFilter, activeViewPhaseStatusFilter)]
		for i, neighbour in enumerate(neighbours):
			checkAlreadyJoinedStr = "{0}{1}".format(el.Id.IntegerValue, neighbour.Id.IntegerValue)
			if not checkAlreadyJoinedStr in alreadyJoined:
				pair = [el, neighbour]
				pairCats = []
				for item in pair:
					if isinstance(item, Autodesk.Revit.DB.FamilyInstance):
						cat = cats[item.Category.Name]
						#className = el.Category.CategoryType
						name = cat.ToString()
					else:
						name = item.__class__.__name__
					pairCats.append(name)
				#print(("figuring out join status {0} with {1}".format(pair[0].Id, pair[1].Id)))
				areJoined = DB.JoinGeometryUtils.AreElementsJoined(doc, pair[0], pair[1])
				#print("elements {0} and {1} are joined {2}".format(pair[0].Id, pair[1].Id, areJoined))
				#t = DB.Transaction(doc, "Join {0}-{1} with {2}-{3}".format(pair[0].Id, pair[0].Category.Name, pair[1].Id, pair[1].Category.Name))
				#t.Start()
				if not areJoined:
					try:
						DB.JoinGeometryUtils.JoinGeometry(doc, pair[0], pair[1])
						joining = True
						#t.Commit()
						#print("joining {0} with {1} - True".format(pair[0].Id, pair[1].Id))
					except:
						print("joining {0} with {1} - False {2}".format(pair[0].Id, pair[1].Id, sys.exc_info()))
						#t.RollBack()
						joining = False
				else:
					joining = False
				#print("JoinElementSwallower.hasMessage - {0}".format(JoinElementSwallower.hasMessage))
				finalJoin = DB.JoinGeometryUtils.AreElementsJoined(doc, pair[0], pair[1])
				#print("finalJoin {0} with {1} - {2}".format(pair[0].Id, pair[1].Id, finalJoin))
				if finalJoin:
					isCuttingElement = DB.JoinGeometryUtils.IsCuttingElementInJoin(doc, pair[0], pair[1])
				else:
					isCuttingElement = False
				itemOnePriority = getElementPriority(pair[0])
				itemTwoPriority = getElementPriority(pair[1])
				#t = DB.Transaction(doc, "Switch join Order {0}-{1} with {2}-{3}".format(pair[0].Id, pair[0].Category.Name, pair[1].Id, pair[1].Category.Name))
				#t.Start()
				if not isCuttingElement and (itemOnePriority < itemTwoPriority) and finalJoin:
					try:
						DB.JoinGeometryUtils.SwitchJoinOrder(doc, pair[0], pair[1])
						switched = True
					except:
						switched = False
					#t.Commit()
				elif isCuttingElement and (itemOnePriority > itemTwoPriority) and finalJoin:
					try:
						DB.JoinGeometryUtils.SwitchJoinOrder(doc, pair[0], pair[1])
						switched = True
					except:
						switched = False
					#t.Commit()
				else:
					switched = False
					#t.RollBack()
				if pBar:
					pBar.updateProgressLabel("processing {0} of {1} - {2}-{3} with {4}-{5}".format(j, len(firstSelection), pair[0].Id, pair[0].Category.Name, pair[1].Id, pair[1].Category.Name))
				alreadyJoined.append(checkAlreadyJoinedStr)
				checkAlreadyJoinedStr = "{1}{0}".format(el.Id.IntegerValue, neighbour.Id.IntegerValue)
				alreadyJoined.append(checkAlreadyJoinedStr)
				print("{0}:{12} - Element_0: {1}-{2} priority {3} <> Element_1 {4}-{5} priority {6} \nwas joined - {7} \njoining {8} \nfinal join {9} \n first is cutting {10} \nswitched {11}".format(j, \
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
																															switched, \
																															i))
			#else:
			#	print("ALREADY JOINED")
		if pBar:
			pBar.UpdateProgress()

		#emptyList = []
		#emptyCList = Clist[DB.ElementId](emptyList)
		#__revit__.ActiveUIDocument.Selection.SetElementIds(emptyCList)

	if pBar:
		pBar.Close()
	t.Commit()

	t = DB.Transaction(doc, "Unjoin failing connections from warnings")
	t.Start()
	intWarnings = getIntersectionWarnings()
	if len(intWarnings) > 0:
		for warning in intWarnings:
			failingElementsIds = warning.GetFailingElements()
			el1 = doc.GetElement(failingElementsIds[0])
			el2 = doc.GetElement(failingElementsIds[1])
			try:
				DB.JoinGeometryUtils.UnjoinGeometry(doc, el1, el2)
			except:
				print("Unable to unjoin elements in warnings list {0}-{1}: {2}".format(failingElementsIds[0].IntegerValue, failingElementsIds[1].IntegerValue, sys.exc_info()))
	t.Commit()

	print("Script succesfully finished")

else:
	pass
	print("Script was cancelled")

	if not scriptCancelled:
		openedForms = list(Application.OpenForms)
		rpsOpenedForms = []
		for i, oForm in enumerate(openedForms):
			if "RevitPythonShell" in str(oForm):
				rpsOpenedForms.append(oForm)

		if len(rpsOpenedForms) > 0:
			lastForm = rpsOpenedForms[-1]
			lastForm.Show()
			if len(rpsOpenedForms) > 1:
				rpsOFormsToClose = rpsOpenedForms[:-1]
				print("Script was cancelled")
				time.sleep(5)
				for oFormToClose in rpsOFormsToClose:
					oFormToClose.Close()
if runFromCsharp == False or "rpsOutput" in dir():
	if rpsOutput:
		rpsOutput.Show()