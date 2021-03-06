# -*- coding: utf-8 -*-
# Copyright(c) 2020, Daniel Gercak
#Script for 
#resource_path: H:\_WORK\PYTHON\REVIT_API\getValueFromBuiltInParameter.py

import clr
import sys
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
lib_path = r'H:\_WORK\PYTHON\REVIT_API\LIB'
sys.path.append(pyt_path)
sys.path.append(lib_path)

clr.AddReference("RevitNodes")
import Revit
clr.ImportExtensions(Revit.Elements)

clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
doc = DocumentManager.Instance.CurrentDBDocument

clr.AddReference("RevitAPI")
import Autodesk
from Autodesk.Revit.DB import *
import System

clr.AddReference("System")
from System.Collections.Generic import List as Clist

builtInParamName = IN[0]
builtInCategoryName = IN[1]
#lookUpParameterName =IN[2]

# if not isinstance(IN[2], list):
# 	elements = [IN[2]]
# else:
# 	elements = IN[2]

#familyInstance = IN[3]

# if not isinstance(IN[2], list):
# 	paramValues = [IN[2]]
# else:
# 	paramValues = IN[2]


def getParameters(inBuiltInParamName, inBuiltinCategoryName):
	myBuiltInParameter = getBuitInParameterInstance(inBuiltInParamName)
	param_ID = ElementId(myBuiltInParameter) if myBuiltInParameter else None
	myBuiltInCategory = getBuiltInCategoryInstance(inBuiltinCategoryName)

	collector = FilteredElementCollector(doc)
	collector.OfCategory(myBuiltInCategory)
	collector.OfClass(FamilyInstance)
	famtypeitr = collector.GetElementIdIterator()
	famtypeitr.Reset()
	param_provider = ParameterValueProvider(param_ID) if param_ID else None

	#print (param_provider.GetDoubleValue(el))

	parameters = []
	instanceParamNames = []
	instanceBIPs = []
	instanceParamValues = []
	instances = []
	control = []
	categoriesNames = []
	for item in famtypeitr:
		famtypeID = item
		faminst = doc.GetElement(famtypeID)
		#famElement = faminst.InternalElement
		instanceParams = faminst.GetOrderedParameters()
		#instanceParamNames = [p.Definition.Name for p in instanceParams]
		instanceParamName = None
		categoriesNames.append(faminst.Category.Name)
		#instanceBIPs = ['{}'.format(p.Definition.BuiltInParameter) for p in instanceParams]
		paramIndx = None
		storageType = None
		displayUnitType = None
		#for i, BIP in enumerate(instanceBIPs):			
		#	if inBuiltInParamName == BIP:
		#		control.append((inBuiltInParamName, BIP, instanceParams[i].AsInteger() if paramIndx != None else None, i))
		#		paramIndx = i
		#instanceParamValues.append(UnitUtils.ConvertFromInternalUnits(param_provider.GetDoubleValue(famElement), DisplayUnitType.DUT_MILLIMETERS))
		if faminst.Parameter[myBuiltInParameter].StorageType == StorageType.Integer:
			storageType = StorageType.Integer
			displayUnitType = faminst.Parameter[myBuiltInParameter].DisplayUnitType
			instanceParamValues.append(faminst.Parameter[myBuiltInParameter].AsInteger())
			instanceParamName = faminst.Parameter[myBuiltInParameter].Definition.Name
		elif faminst.Parameter[myBuiltInParameter].StorageType == StorageType.Double:
			storageType = StorageType.Double
			displayUnitType = faminst.Parameter[myBuiltInParameter].DisplayUnitType
			instanceParamValues.append(UnitUtils.ConvertFromInternalUnits(faminst.Parameter[myBuiltInParameter].AsDouble(), DisplayUnitType.DUT_MILLIMETERS))
			instanceParamName = faminst.Parameter[myBuiltInParameter].Definition.Name
		elif faminst.Parameter[myBuiltInParameter].StorageType == StorageType.String:
			storageType = StorageType.String
			instanceParamValues.append(faminst.Parameter[myBuiltInParameter].AsString())
			instanceParamName = faminst.Parameter[myBuiltInParameter].Definition.Name
		elif faminst.Parameter[myBuiltInParameter].StorageType == StorageType.ElementId:
			storageType = StorageType.ElementId
			instanceParamValues.append(doc.GetElement(faminst.Parameter[myBuiltInParameter].AsElementId()))
			instanceParamName = faminst.Parameter[myBuiltInParameter].Definition.Name
		instances.append(faminst)
		#instanceParamValues.append((UnitUtils.ConvertFromInternalUnits(faminst.Parameter[myBuiltInParameter].AsDouble(), DisplayUnitType.DUT_MILLIMETERS), faminst.Parameter[myBuiltInParameter].Definition.Name, myBuiltInParameter))
		
		# instanceName.append(faminst.LookupParameter(inParamName).Definition.BuiltInParameter if faminst.LookupParameter(inParamName) != None else None)
		# if builtInParamName in instanceBIPs:
		# 	param = faminst.get_Parameter(BuiltInParameter.DOOR_WIDTH)
		# parameters.append(param.AsString())
		# fIcollection = Clist[Autodesk.Revit.DB.FamilyInstance](inElements)
		# height = param = faminst.get_Parameter('height')
	return (storageType, displayUnitType, categoriesNames, instances, instanceParamValues, instanceParamName, myBuiltInParameter)

def getBuitInParameterInstance(inBuiltInParamName):
	builtInParams = System.Enum.GetValues(BuiltInParameter)
	returnVar = None
	for bip in builtInParams:
		if bip.ToString() == inBuiltInParamName:
			param_ID = ElementId(bip)
			returnVar = bip
			break
	return returnVar

def getBuiltInCategoryInstance(inBuiltinCategoryName):
	builtInCategories = System.Enum.GetValues(BuiltInCategory)
	returnVar = None
	for bic in builtInCategories:
		if bic.ToString() == inBuiltinCategoryName:
			param_ID = ElementId(bic)
			returnVar = bic
			break
	#return zip(builtInCategories, [inBuiltinCategoryName for x in builtInCategories])
	return returnVar
""" 
def getBuiltinParam(inBuiltInParamName, inFamInst, inLookUpParameterName):
	#builtInParams = System.Enum.GetValues(BuiltInParameter)
	#builtInNames = System.Enum.GetType(BuiltInParameter)
	# for bip in builtInParams:
	# 	if bip.ToString() == inBuiltInParamName:
	myBuiltInParameter = getBuitInParameterInstance(inBuiltInParamName)
	param_ID = ElementId(myBuiltInParameter) if myBuiltInParameter else None
	param_provider = ParameterValueProvider(param_ID) if param_ID else None
	myElement = inFamInst.InternalElement
	elementValue = (UnitUtils.ConvertFromInternalUnits(param_provider.GetDoubleValue(myElement), DisplayUnitType.DUT_MILLIMETERS), myBuiltInParameter, param_provider.GetAssociatedGlobalParameterValue(myElement))
	
	#instanceParams = inFamInst.GetOrderedParameters()
	#famInst = doc.GetElement(inFamInst)
	# paramValue = inFamInst.GetParameterValueByName(inLookUpParameterName)
	# instanceParams = inFamInst.Parameters
	# instanceParamNames = [p.Name for p in instanceParams]
	# instanceParamValues = [p.Value for p in instanceParams]
	#instanceBIPs = ['{}'.format(p.Definition.BuiltInParameter) for p in instanceParams]
	#return zip(instanceParamNames, instanceParamValues)
	#return dir(inFamInst)
	#return inFamInst.InternalElement
	return elementValue
	#return zip(builtInNames, builtInParams)
	#return builtInNames """

try:
	errorReport = None
	#TransactionManager.Instance.EnsureInTransaction(doc)
	#paramValues = ListUtils.processList(getParameter, elements, builtInParamName, lookUpParameterName)
	
	#TransactionManager.Instance.TransactionTaskDone()
except:
	import traceback
	errorReport = traceback.format_exc()

if errorReport == None:
	#OUT = getBuiltInCategoryInstance(builtInCategoryName)
	OUT = getParameters(builtInParamName, builtInCategoryName)
	#OUT = getBuiltinParam(builtInParamName, familyInstance, lookUpParameterName)
else:
	OUT = errorReport