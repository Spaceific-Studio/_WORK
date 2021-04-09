# -*- coding: utf-8 -*-
# Copyright(c) 2021, Daniel Gercak
#Revit Python Shell script for multiple unjoining elements according to txt converted from html warnings report file
#resource_path: https://github.com/Spaceific-Studio/_WORK/REVIT_API/unJoinElementsByListFile.py
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
	    #import System
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
	    from System.Collections.Generic import List as Clist
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

class ProgressBarDialog(Form):
	def __init__(self, inMax):
		self.scriptDir = "\\".join(__file__.split("\\")[:-1])
		print(self.scriptDir)
		iconFilename = os.path.join(self.scriptDir, 'LIB\\spaceific_64x64_sat_X9M_icon.ico')
		icon = Icon(iconFilename)
		self.Icon = icon	

		self.Text = 'Unjoin Elements by file of list - Script by Spaceific-Studio'
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
	
	def close(self, sender, event):
		scriptCancelled = True
		openedForms = list(Application.OpenForms)
		infotext = ""
		rpsOpenedForms = []
		for i, oForm in enumerate(openedForms):
			print(str(i))
			print(oForm)
			infotext += "; {}".format(oForm)
			if "RevitPythonShell" in str(oForm):
				print("Totot je oForm {0}".format(oForm))
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

def createMultiCategoryFilter():
	listOfCategories = list()
	listOfCategories.append(DB.BuiltInCategory.OST_Floors)
	listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_Columns)
	listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_StructuralColumns)
	listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_StructuralFraming)
	listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_StructuralFoundation)
	listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_Walls)
	listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_Floors)
	listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_Roofs)
	listOfCategories.append(Autodesk.Revit.DB.BuiltInCategory.OST_Ceilings)
	colOfBIC = Clist[DB.BuiltInCategory](listOfCategories)
	multiCategoryFilter = DB.ElementMulticategoryFilter(colOfBIC)
	return multiCategoryFilter

# part of unjoining acording to file list of IDs gathered from warnings
pathToIDs = r"h:/2020_12_07-UV_ZELIVKA-F1/RVT/zaloha/2021_03_31/"
idsFileName = "PI18018_DSP_SO_03-02_ASR_R20_detached_CZDAGE_Error_20Report.txt"
#idsFileName = "PI18018_chyby2_ID.txt"
idsPath = os.path.join(pathToIDs, idsFileName)
idsFile = open(idsPath)
strIds = idsFile.readlines()
filteredStrIds =[]
idsFile.close()
pairs = []

for i, line in enumerate(strIds):
	strippedLine = line.strip()
	if "Highlighted elements are joined but do not intersect." in strippedLine:
		line2 = strIds[i+1] if i < (len(strIds) - 1) else []
		stripedLine2 = line2.strip()
		splitedLine2 = stripedLine2.split(" ")
		splitedLine = strippedLine.split(" ")
		id1Index = splitedLine.index("id")
		id2Index = splitedLine2.index("id")
		id1str = splitedLine[id1Index+1]
		id2str = splitedLine2[id2Index+1]
		filteredStrIds.append([id1str, id2str])
		#print("id1 {0} id2 {1}".format(id1str, id2str))
	#print(strippedLine)

multiCatFilter = createMultiCategoryFilter()

openedForms = list(Application.OpenForms)
for i, oForm in enumerate(openedForms):
	print(str(i))
	print(oForm)
	if "RevitPythonShell" in str(oForm):
		#print("Totot je oForm {0}".format(oForm))
		rpsOutput = oForm
	else:
		rpsOutput = None
print("__main__.OpenForms {}".format(list(Application.OpenForms)))
#rpsOutput = list(Application.OpenForms)[0]

if rpsOutput:
	rpsOutput.Hide()
else:
	pass

pBar = ProgressBarDialog(len(filteredStrIds))
fThread = Thread(ThreadStart(pBar))
pBar.Show()

t = DB.Transaction(doc, "Join selected elements")
t.Start()
for i,pair in enumerate(filteredStrIds):
	#splitedLine = line.strip().split(",")
	#strId0 = splitedLine[0] if len(splitedLine) > 0 else None
	#strId1 = splitedLine[1] if len(splitedLine) > 1 else None
	try:
		intId0 = int(pair[0])
	except:
		intId0 = None
	try:
		intId1 = int(pair[1])
	except:
		intId1 = None
	id0 = DB.ElementId(intId0) if intId0 else None
	id1 = DB.ElementId(intId1) if intId1 else None
	el0 = doc.GetElement(id0) if id0 else None
	el1 = doc.GetElement(id1) if id1 else None

	pairCol = Clist[DB.ElementId]([id0, id1])
	filteredElements = list(DB.FilteredElementCollector(doc, pairCol).WherePasses(multiCatFilter).ToElements())
	if len(filteredElements) == 2:
		pairs.append([el0, el1])
	else:
		pairs.append([])
	count = 0
	if len(pairs[i]) > 1:
		if pairs[i][0] and pairs[i][1]:
			areJoined = DB.JoinGeometryUtils.AreElementsJoined(doc, pairs[i][0], pairs[i][1])
			print("{0} - {1} <> {2} - {3}".format(pairs[i][0].Id.IntegerValue, \
											pairs[i][0].Category.Name, \
											pairs[i][1].Id.IntegerValue, \
											pairs[i][1].Category.Name, \
											areJoined))
			if areJoined:
				DB.JoinGeometryUtils.UnjoinGeometry(doc, pairs[i][0], pairs[i][1])
			finalJoin = DB.JoinGeometryUtils.AreElementsJoined(doc, pairs[i][0], pairs[i][1])
			#print("finalJoin................ {0}".format(finalJoin if finalJoin else None))
			pass
		else:
			print("This is not valid pair")
		if count > 1000:
			break
		count += 1
	if pBar and len(pairs[i]) == 2:
		pBar.updateProgressLabel("processing {0} of {1} - {2}-{3} with {4}-{5}".format(i, \
																				len(filteredStrIds), \
																				pairs[i][0].Id, \
																				pairs[i][0].Category.Name, \
																				pairs[i][1].Id, \
																				pairs[i][1].Category.Name))
		pBar.UpdateProgress()
t.Commit()
if pBar:
	pBar.Close()
rpsOutput.Show()
rpsOutput.TopMost = True
print("Script Finished")


