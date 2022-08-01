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
from itertools import groupby
#import time
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)
pyt_path = r'C:\Program Files\IronPython 2.7\Lib'
sys.path.append(pyt_path)

import os
import time
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

from RevitSelection import getValueByParameterName, getValuesByParameterName, setValueByParameterName, getBuiltInParameterInstance
from ListUtils import processList

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

try:
	runFromCsharp = True if "__csharp__" in dir() else False
	#UI.TaskDialog.Show("Run from C#", "Script is running from C#")
except:
	runFromCsharp = False

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
mySelection = [doc.GetElement(elId) for elId in __revit__.ActiveUIDocument.Selection.GetElementIds()]

class Dic2obj(object):
	def __init__(self, dictionary):
		for key in dictionary:
			setattr(self, key, dictionary[key])

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
		rpsOutput.Show()
		#time.delay(5)
		time.sleep(5)
		#rpsOutput.Hide()
	else:
		pass
else:
	rpsOutput = None

nameToParamDic = {}
activeViewType = doc.ActiveView.ViewType


if activeViewType == ViewType.Schedule:
	#markBipName = "ALL_MODEL_MARK"
	markBipName = "DOOR_NUMBER"
	markTypeBipName = "ALL_MODEL_TYPE_MARK"
	assemblyCodeBipName = "UNIFORMAT_CODE"

	
	allElements = list(FilteredElementCollector(doc,doc.ActiveView.Id).WhereElementIsNotElementType().ToElements())
	if len(allElements) > 0:
		try:
			markParamName = allElements[0].Parameter[BuiltInParameter.DOOR_NUMBER].Definition.Name
			markParamId = allElements[0].Parameter[BuiltInParameter.DOOR_NUMBER].Id
			markParamValueProvider = ParameterValueProvider(markParamId)
			#markTypeParamName = allElements[0].Parameter[BuiltInParameter.ALL_MODEL_TYPE_MARK].Definition.Name
			"""
			markTypeParamId = allElements[0].Parameter[BuiltInParameter.ALL_MODEL_TYPE_MARK].Id
			markTypeParamValueProvider = ParameterValueProvider(markTypeParamId)
			print("markParamName = {0}, markParamID = {1}, markBipName = {2}".format(markParamName, markParamId, markBipName))
			print("markTypeParamName = {0}, markParamID = {1}, markTypeBipName = {2}".format(markTypeParamName, markTypeParamId, markTypeBipName))
			"""
			#print("markTypeParamName = {0}".format(markTypeParamName))
		except:
			print(sys.exc_info())
			markParamValueProvider = None
			markTypeParamValueProvider = None
	
	if markParamValueProvider != None:
		filteredScheduleElements_mark = list(FilteredElementCollector(doc,doc.ActiveView.Id).WherePasses(ElementParameterFilter(FilterStringRule(markParamValueProvider, FilterStringBeginsWith(), "001"))).ToElements())
		print("filteredScheduleElements_mark len() = {}".format(len(filteredScheduleElements_mark)))
		for el in allElements:
			print("markParamValue = {0} - {1}".format(markParamValueProvider.GetStringValue(el), el.Id))
	else:
		filteredScheduleElements_mark = None
	
	if markTypeParamValueProvider != None:
		filteredScheduleElements_markType = list(FilteredElementCollector(doc,doc.ActiveView.Id).WherePasses(ElementParameterFilter(FilterStringRule(markTypeParamValueProvider, FilterStringBeginsWith(), "1K"))).WhereElementIsNotElementType().ToElements())
		for el in allElements:
			print("markParamValue = {0} - {1}".format(markTypeParamValueProvider.GetStringValue(el), el.Id))
	else:
		filteredScheduleElements_markType = None

	uniqueParams = getMembers(allElements)
	viewSelection = uidoc.Selection
	viewSelectionIds = list(viewSelection.GetElementIds())
	viewSelectionIdStrings = [x.ToString() for x in viewSelectionIds]

	viewSelectionElements = []
	print("Selected Elements {}".format(len(allElements )))
	#for i, elId in enumerate(viewSelectionIds):
		#print("{0} - {1} - {2}".format(i, elId.IntegerValue, doc.GetElement(elId).Name))
		#viewSelectionElements.append(doc.GetElement(elId))
	#selectedParams = getMembers(viewSelectionElements)
	#selectedParamsIds = {v.Id.ToString():v for k,v in selectedParams.items()}

	print("filteredScheduleElements_mark len: {0}".format(len(filteredScheduleElements_mark) if filteredScheduleElements_mark else None ))
	print("filteredScheduleElements_markType len: {0}".format(len(filteredScheduleElements_markType) if filteredScheduleElements_markType else None ))
	#for el in allElements:
	#	print("el.Id: {0}, category: {1}".format(el.Id, el.Category.Name))










