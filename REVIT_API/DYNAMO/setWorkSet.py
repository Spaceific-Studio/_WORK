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
myOut = ""
myOut += "module : {0} ; hasMainAttr = {1}".format(dir(__file__), hasMainAttr)
myOut += "module : {0} ; hasAutodesk = {1}".format(__file__, hasAutodesk)

if sys.platform.startswith('linux'):
	libPath = r"/storage/emulated/0/_WORK/REVIT_API/LIB"
elif sys.platform.startswith('win') or sys.platform.startswith('cli'):
	scriptDir = "\\".join(__file__.split("\\")[:-1])
	scriptDisk = __file__.split(":")[0]
	myOut += "__file__ {0}".format(__file__)
	if scriptDisk == "B" or scriptDisk == "b":
		libPath = r"B:/Podpora Revit/Rodiny/141/_STAVEBNI/_REVITPYTHONSHELL/LIB"
	elif scriptDisk == "H" or scriptDisk == "h":
		libPath = r"H:/_WORK/PYTHON/REVIT_API/LIB"
""" 
if sys.platform.startswith('linux'):
	pythLibPath = r"/storage/emulated/0/_WORK/LIB"
elif sys.platform.startswith('win') or sys.platform.startswith('cli'):
	pythLibPath = r"H:/_WORK/PYTHON/LIB" """

#sys.path.append(libPath)
#sys.path.append(pythLibPath)

inId = IN[0][0]
worksetName = IN[1]
inId = UnwrapElement(inId)
#element = doc.GetElement(DB.ElementId(inId))
myParam = inId.Symbol.Parameter[DB.BuiltInParameter.ELEM_PARTITION_PARAM]
#paramType = myParam.Definition.ParameterType
#elementParams = [x.Definition.ParameterType for x in list(element.Parameters)]
#myOut = inId.__class__.__name__
# Umístit kód pod tento řádek

# Přiřaďte výstup k proměnné OUT.
worksetId = DB.WorksetId(myParam.AsInteger())
worksetTable = doc.GetWorksetTable()
isUnique = worksetTable.IsWorksetNameUnique(doc, worksetName)
worksetKindFilter = DB.WorksetKindFilter(DB.WorksetKind.UserWorkset)
workSets = DB.FilteredWorksetCollector(doc).WherePasses(worksetKindFilter)
exception = []

if isUnique:
	TransactionManager.Instance.EnsureInTransaction(doc)
	trans = Autodesk.Revit.DB.SubTransaction(doc)
	trans.Start()
	try:
		DB.Workset.Create(doc, worksetName)
		trans.Commit()
	except:
		exception.append(sys.exc_info())
		trans.RollBack()
worksetnames = {}
for c in workSets:
	worksetnames[c.Name] = c.Id
if worksetName in worksetnames:
	TransactionManager.Instance.EnsureInTransaction(doc)
	trans = Autodesk.Revit.DB.SubTransaction(doc)
	trans.Start()
	try:
		myParam.Set(worksetnames[worksetName].IntegerValue)
		trans.Commit()
	except:
		exception.append(sys.exc_info())
		trans.RollBack()
#workset = worksetTable.GetWorkset(worksetId)
if len(exception) == 0:
	OUT = "Instance workset was set to {0}".format(worksetName)
else:
	OUT = exception

#OUT = worksetnames