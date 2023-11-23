# -*- coding: utf-8 -*-
# Copyright(c) 2020, Daniel Gercak
#Script for import SAT geometry into family (generic model)
#resource_path: H:\_WORK\PYTHON\REVIT_API\familyImportSAT.py
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB.Architecture import *
from Autodesk.Revit.DB.Analysis import *
from Autodesk.Revit.UI import *
import sys
#if "Windows" in platform.uname():
	#lib_path = r'H:/_WORK/PYTHON/LIB'

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
import clr
from RevitSelection import getFamilyInstancesByName, getValuesByParameterName, setValuesByParameterName

clr.AddReferenceByPartialName('PresentationCore')
clr.AddReferenceByPartialName('PresentationFramework')
clr.AddReferenceByPartialName('System.Windows.Forms')
import System.Windows
from System.Windows.Forms import *
from Autodesk.Revit.DB import ImportUnit as IU
uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
selection = [doc.GetElement(elId) for elId in __revit__.ActiveUIDocument.Selection.GetElementIds()]
#print(dir(__revit__))

if "rpsOutput" in dir():
	rpsOutput.Show()

openedForms = list(Application.OpenForms)
rpsOpenedForms = []
for i, oForm in enumerate(openedForms):
	if "RevitPythonShell" in str(oForm):
		rpsOpenedForms.append(oForm)

if len(rpsOpenedForms) > 0:
	lastForm = rpsOpenedForms[-1]
	lastForm.Show()

<<<<<<< HEAD
dirName = r"H:\2022_08_16-PCOV_KOLOVRATY-INTENZIFIKACE\RVT\import"
fileName = r"TEST_VOLUME.sat"
=======
dirName = r"H:\2022_03_28-AK_KOPANINA\RVT\import"
#fileName = r"ROSTLY_TEREN_TEST.sat"
#isVoid1 = False
#fileName = r"VYKOPY_TEST.sat"
fileName = r"H:\2022_03_28-AK_KOPANINA\RVT\import\STAVAJICI_OBJEKTY_TEST.sat"
isVoid1 = True
>>>>>>> f83599d64840aa9910eedcf455af15c8253dea67
filePath = os.path.join(dirName, fileName)

satOptions = SATImportOptions()
satOptions.Placement = ImportPlacement.Origin
satOptions.Unit = IU.Foot
#print("ImportUnit {0}".format(dir(ImportUnit)))
print("satOptions.Unit {0}",format(satOptions.Unit))
#scaleFactor = 3.280839895 * 10
#scaleFactor = 1
#satOptions.CustomScale = scaleFactor
SaveAsOpt = SaveAsOptions()
SaveAsOpt.OverwriteExistingFile = True
opt1 = Options()
opt1.ComputeReferences = True
isVoid1 = False
enableMat = True
mat1Name = "ROSTLÝ TERÉN"
cat = Category.GetCategory(doc, BuiltInCategory.OST_GenericModel)
print("Category name {0}".format(cat.Name))

t = Transaction(doc, "Import SAT")
t.Start()
satId = doc.Import(filePath, satOptions, doc.ActiveView)
#satId = famdoc.Import(sat1, satOpt, view1)
el1 = doc.GetElement(satId)

geom1 = el1.get_Geometry(opt1)
print("geom1 {0}".format(geom1))

enum = geom1.GetEnumerator()
enum.MoveNext()
geom2 = enum.Current.GetInstanceGeometry()
print("geom2 {0}".format(geom2))

enum2 = geom2.GetEnumerator()
enum2.MoveNext()
s1 = enum2.Current
print("s1 {0}".format(s1))

doc.Delete(satId)
#System.IO.File.Delete(sat_path)

#save_path = '%s%s.rfa' % (temp_path, name1)
try: #set the category
	fam_cat = doc.Settings.Categories.get_Item(cat.Name)
	doc.OwnerFamily.FamilyCategory = fam_cat
except: pass
print("category set to {0}".format(fam_cat.Name))
try:
	s2 = FreeFormElement.Create(doc,s1)
	print("s2 {0}".format(s2))
except Exception as ex:
	print("Exception in FreeFormElement.Create(doc,s1) {0}".format(sys.exc_info()))
if isVoid1:
	void_par = s2.get_Parameter(BuiltInParameter.ELEMENT_IS_CUTTING).Set(1)
	void_par2 = doc.OwnerFamily.get_Parameter(BuiltInParameter.FAMILY_ALLOW_CUT_WITH_VOIDS).Set(1)
else: #voids do not have a material values or a sub-cateogry
	pass
"""
if enableMat:
	try:
		mat_fec = FilteredElementCollector(doc).OfClass(Material)
		for m in mat_fec:
			if m.Name == mat1Name:
				fam_mat = m
				break
		mat_par = s2.get_Parameter(BuiltInParameter.MATERIAL_ID_PARAM).Set(fam_mat.Id)
	except: pass
"""
t.Commit()

