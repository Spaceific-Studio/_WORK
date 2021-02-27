# -*- coding: utf-8 -*-
# Copyright(c) 2021, Daniel Gercak
#Revit Python Shell script for multiple unjoining elements
#resource_path: https://github.com/Spaceific-Studio/_WORK/REVIT_API/unJoinSelectedElements.py
import sys
if "IronPython" in sys.prefix:
	pytPath = r'C:\Program Files (x86)\IronPython 2.7\Lib'
	sys.path.append(pytPath)
import os
import platform
import time
from itertools import combinations

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
	    import System
	    import clr
	    #import threading
	    clr.AddReferenceByPartialName('System.Windows.Forms')
	    clr.AddReference('System')
	    clr.AddReference("System.Drawing")
	    #import System.Windows.Forms
	    from System.Windows.Forms import *
	    from System.Drawing import *
	    #from Windows import Threading
	    from System.Threading import ThreadStart, Thread
	    #Dispatcher, DispatcherPriority
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

class InfoDialog(Form):
	def __init__(self, inText):
		self.scriptDir = "\\".join(__file__.split("\\")[:-1])
		print(self.scriptDir)
		iconFilename = os.path.join(self.scriptDir, 'LIB\\spaceific_64x64_sat_X9M_icon.ico')
		icon = Icon(iconFilename)
		self.Icon = icon	

		self.InfoText = inText
		
		self.InitializeComponent()

	def InitializeComponent(self):
		self.Text = "Setup of join priority for categories by Spaceific-Studio"
		self.Width = 500
		self.Height = 200
		self.StartPosition = FormStartPosition.CenterScreen
		self.TopMost = True
		screenSize = Screen.GetWorkingArea(self)
		self.Height = screenSize.Height / 2
		self.Width = screenSize.Width / 3
		self.panelHeight = self.ClientRectangle.Height * 0.75
		self.panelWidth = self.ClientRectangle.Width / 3
		self.bgColor = Color.CadetBlue
		self.textColor = Color.White
		self.setup()
	
	def setup(self):
		self.label1 = Label()
		self.label1.Text = self.InfoText
		self.label1.Size = Size(200, 50)

		self.Controls.Add(self.label1)

class ProgressBarDialog(Form):
	def __init__(self, inMax):
		self.scriptDir = "\\".join(__file__.split("\\")[:-1])
		print(self.scriptDir)
		iconFilename = os.path.join(self.scriptDir, 'LIB\\spaceific_64x64_sat_X9M_icon.ico')
		icon = Icon(iconFilename)
		self.Icon = icon	

		self.Text = 'Unjoin All Selected Elements - Script by Spaceific-Studio'
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
		self.infoLabel.Text = "Unjoining elements..."
		self.infoLabel.Location = (Point(0,0))
		self.Controls.Add(self.infoLabel)
		#self.Shown += self.start
		#System.Threading.Dispatcher.Run(self.start())

	#def start(self, s, e):
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

firstSelection = [doc.GetElement(elId) for elId in __revit__.ActiveUIDocument.Selection.GetElementIds()]

#TransactionManager.Instance.EnsureInTransaction(doc)
#t = DB.SubTransaction(doc)

# Begin new transaction
#t.Start()
#t = DB.Transaction(doc, "Select element to join with")
#t.Start()
#secondSelection = doc.GetElement(pickobject("Select objects to join element with").ElementId)

#t.Commit()
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

for i, el in enumerate(firstSelection):
	if isinstance(el, Autodesk.Revit.DB.FamilyInstance):
		categoryId = el.Symbol.Family.FamilyCategoryId
		cat = cats[el.Category.Name]
		#className = el.Category.CategoryType
		name = cat.ToString()
	else:
		name = el.__class__.__name__
	print("{0}-{1} {2} {3}".format(i, el.Id, el.Category.Name, name))

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
""" 
if hasattr(secondSelection, "__iter__"):
	for i in secondSelection:
		print("You have selected {0} elements".format(len(secondSelection)))
else:
	print("You have selected 1 element {0}".format(secondSelection.Id)) """

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

""" #infoDialogWindow = InfoDialog("Unjoining...")
#mainFormThread = threading.Thread(target=Application.Run(infoDialogWindow), args=(1,))
#mainFormThread.start()
pBar = ProgressBar()
pBar.Minimum = 0
pBar.Maximum = len(selComb)
pBar.Value = 0
pBar.Step = 1
Application.Run(pBar)
"""

Application.EnableVisualStyles()
#Application.ProgressBarDialog
pBar = ProgressBarDialog(len(selComb))
fThread = Thread(ThreadStart(pBar))
pBar.Show()
#Windows.Threading.Dispatcher.Run(pBar.start())

t = DB.Transaction(doc, "Join selected elements")
t.Start()

fTime = 0.0
for i, pair in enumerate(selComb):
	pairCats = []
	sTime = time.time()
	for item in pair:
		if isinstance(item, Autodesk.Revit.DB.FamilyInstance):
			cat = cats[item.Category.Name]
			#className = el.Category.CategoryType
			name = cat.ToString()
		else:
			name = item.__class__.__name__
		pairCats.append(name)
	areJoined = DB.JoinGeometryUtils.AreElementsJoined(doc, pair[0], pair[1])
	if areJoined:
		try:
			DB.JoinGeometryUtils.UnjoinGeometry(doc, pair[0], pair[1])
			unjoining = True
		except:
			unjoining = False
	else:
		unjoining = False
	
	finalJoin = DB.JoinGeometryUtils.AreElementsJoined(doc, pair[0], pair[1])
	eTime = time.time()
	myTime = eTime - sTime
	fTime += myTime
	#pBar.PerformStep()
	pBar.updateProgressLabel("processing {0} of {1}".format(i, len(selComb)))
	pBar.UpdateProgress()
	
	print("{0} - Element_0: {1}-{2} <> Element_1 {3}-{4} \nwas joined - {5} \nunjoining {6} \nfinal join {7} proceed time {8:.5f}s\n".format(i, \
																												pair[0].Id, \
																												pairCats[0], \
																												pair[1].Id, \
																												pairCats[1], \
																												areJoined, \
																												unjoining, \
																												finalJoin, \
																												myTime))
	print("Final proceed time - {0:.5f}".format(fTime))
""" 
for i, el in enumerate(firstSelection):
	print(el.Id)
	areJoined = DB.JoinGeometryUtils.AreElementsJoined(doc, el, secondSelection)
	if not areJoined:
		try:
			DB.JoinGeometryUtils.JoinGeometry(doc, el, secondSelection)
			print("element {0} is joined with element {1} - areJoined > {2}".format(el.Id, secondSelection.Id, areJoined))
		except Exception as ex:
			import traceback
			print("ELEMENT {0} WAS NOT JOINED WITH ELEMENT {1} - {2}".format(el.Id, secondSelection.Id, areJoined))
			print("Traceback content >> \n {0}".format(sys.exc_info()))
			#exc_info = sys.exc_info()
			#traceback.print_exception(*exc_info)
			#del exc_info """
t.Commit()
print("Script succesfully finished")
#mainFormThread.join()
#infoDialogWindow.Close()
pBar.Close()
rpsOutput.Show()
rpsOutput.TopMost = True
