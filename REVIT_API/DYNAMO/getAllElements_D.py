# -*- coding: utf-8 -*-
# Copyright(c) 2019, Daniel Gercak
#Script for selecting and grouping elements by levels and other parameters for dynamo 
#resource_path: H:\_WORK\PYTHON\REVIT_API\Group_geometry_node.py

import sys
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
lib_path = r'H:\_WORK\PYTHON\REVIT_API\LIB'
sys.path.append(pyt_path)
sys.path.append(lib_path)


# from itertools import chain, groupby
# from RevitSelection import *
# import RevitSelection as RevitSelection
# from ListUtils import *
# import ListUtils as ListUtils

import clr
clr.AddReference("RevitAPI")
#import Autodesk
import Autodesk.Revit.DB as DB

clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
#from RevitServices.Transactions import TransactionManager
doc = DocumentManager.Instance.CurrentDBDocument

clr.AddReference('ProtoGeometry')
import Autodesk.DesignScript.Geometry as DSGeometry

# Import Element wrapper extension methods
clr.AddReference("RevitNodes")
import Revit
clr.ImportExtensions(Revit.Elements)
clr.ImportExtensions(Revit.GeometryConversion)
clr.AddReference('RevitAPIUI')
from Autodesk.Revit.UI.Selection import *


clr.AddReference("System")

from System.Collections.Generic import List as Clist
from System import Enum 

doc = DocumentManager.Instance.CurrentDBDocument

""" clr.AddReference("System.Windows.Forms")
clr.AddReference("System.Drawing")

import System.Drawing
import System.Windows.Forms
from System.Drawing import *
from System.Windows.Forms import Application, Button, Form, ComboBox, Label, TextBox, DockStyle, AnchorStyles, FormBorderStyle """

class Errors(object):
	report = []
	variables = []
	varNames = []
	def __init__(self):
		pass

	@classmethod
	def hasError(cls):
		if len(cls.report) > 0:
			return True
		else:
			return False
	
	@classmethod
	def hasContent(cls):
		if len(cls.variables) > 0:
			return True
		else:
			return False
			
	@classmethod
	def catch(cls, inEx, *args):
		"""
		catches the error in Exception block as a class parameter report 

		arg: inEx: an Exception catched in Exception block
		*args[0]: inText: short description of the error. Where it ocured (function or block of commands) type: string

		Returns: None
		"""
		if len(args) > 0:
			inText = args[0]
		else:
			inText = ""
		error_type, error_instance, traceback = sys.exc_info()
		cls.report.append("{0} \
							Exception: {1} error_type: {2}, error_instance {3}, traceback -{4}" \
							.format(inText \
									,inEx \
									,error_type \
									,error_instance \
									,traceback))
	
	@classmethod
	def catchVar(cls, inVar, inName, *args, **kwargs):
		"""
		catches the variable and stores it in variables for direct acces during tuning of code 

		input:
		inVar: content of variable to store
		inName: name of variable type: string 

		Returns: None
		"""
		front = kwargs['front'] if 'front' in kwargs else False
		if front:
			cls.variables.insert(0, inVar)
			cls.varNames.insert(0, inName)
		else:
			cls.variables.append(inVar)
			cls.varNames.append(inName)

	@classmethod
	def getConntainerContent(cls, *args, **kwargs):
		withName = kwargs["withName"] if "withName" in kwargs else True
		if withName == True:			
			return zip(cls.varNames, cls.variables)
		else:
			return cls.variables

def processList(_func, _list, *args, **kwargs):
	"""Iterates trough input list and aplies a function to each item of the list

		args:
			_func: name of the func type: callable
			_list: input list - type: list 
			*args: arguments for input function

		return: list of the same structure as input list - type: list
	"""
	return map( lambda x: processList(_func, x, *args, **kwargs) if type(x)==list else _func(x, *args, **kwargs), _list )

def getAllElements(doc, *args, **kwargs):
	"""
		acquire all Elements from active view

		kwargs["toId"] type boolean: returns collection of DB.ElementId if True, else return DB.Element
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

""" def getBuiltInParameterInstance(inBuiltInParamName):
	#print("RevitSelection.getBuiltInParameterInstance inBuiltInParamName {}".format(inBuiltInParamName))
	builtInParams = Enum.GetValues(DB.BuiltInParameter)
	returnVar = None
	for bip in builtInParams:
		#print("bip.ToString() {0} inBuiltInParamName {1}".format(bip.ToString(), inBuiltInParamName))
		if bip.ToString() in inBuiltInParamName:
			#print("bip.ToString() {0}".format(bip.ToString()))
			param_ID = DB.ElementId(bip)
			returnVar = bip
			break
	return returnVar """

def getValuesByParameterName(inElements, inName, doc, *args, **kwargs):
	"""
		get parameter value from element by parameter name

		args:
		inElement type: list(DB.Element,...)
		inName: type: string
		kwargs['info'] type: bool returns parameter info as string (element name, element Id, parameter name, parameter value as string) if True, default False
		kwargs['allParametersInfo'] type: bool returns list of all parameters names of instance as a list default False
	"""
	info = kwargs['info'] if 'info' in kwargs else False
	allParametersInfo = kwargs['allParametersInfo'] if 'allParametersInfo' in kwargs else False
	inBip = kwargs["bip"] if 'bip' in kwargs else None
	#print("this is BIP param {0}".format(inName))
	bip = getBuiltInParameterInstance(inName)
	if bip:
		pass
		#print("this is BIP param {0}".format(inName))
	else:
		if inBip:
			bip = inBip
		else:
			bip = None
	#raise TypeError("bip {0} inName {1}".format(bip, inName))
	returnValues = []
	returnValuesAsString = []
	allParametersNames = []
	firstTime = True
	
	for el in inElements:
		if not el.LookupParameter(inName) and not bip:
			typeElement = doc.GetElement(el.GetTypeId())
			#print("{0} {1} is typeParameter of type {2}".format(el.Id, inName, typeElement.FamilyName))
			#el = typeElement
		#elif not el.LookupParameter(inName) and bip:
		else:
			typeElement = None
		parameterFound = False
		if bip:
			parameterFound = True
			param_ID = DB.ElementId(bip)
			parameterVP = DB.ParameterValueProvider(param_ID)
			if parameterVP.IsDoubleValueSupported(el):
				returnValues.append(DB.UnitUtils.ConvertFromInternalUnits(parameterVP.GetDoubleValue(el), DB.DisplayUnitType.DUT_MILLIMETERS))
			elif parameterVP.IsIntegerValueSupported(el):
				returnValues.append(parameterVP.GetIntegerValue(el))
			elif parameterVP.IsStringValueSupported(el):
				returnValues.append(parameterVP.GetStringValue(el) if parameterVP.GetStringValue(el) != None else "")
			elif parameterVP.IsElementIdValueSupported(el):
				returnValues.append(parameterVP.GetElementIdValue(el).IntegerValue)
			else:
				returnValues.append("")
		
		else:
			if not typeElement:
				parameter = el.LookupParameter(inName)
				if parameter:					
					if parameter.StorageType == DB.StorageType.Double:
						returnValuesAsString.append("{0}, {4}, {1}, {2}, {3:.4f}".format(el.Name if hasattr(el, "Name") else el.FamilyName, el.Id, parameter.Definition.Name, DB.UnitUtils.ConvertFromInternalUnits(parameter.AsDouble(), DB.DisplayUnitType.DUT_MILLIMETERS), el.Id))
						returnValues.append(DB.UnitUtils.ConvertFromInternalUnits(parameter.AsDouble(), DB.DisplayUnitType.DUT_MILLIMETERS))
					if parameter.StorageType == DB.StorageType.Integer:
						returnValuesAsString.append("{0}, {4}, {1}, {2}, {3}".format(el.Name if hasattr(el, "Name") else el.FamilyName, el.Id, parameter.Definition.Name, parameter.AsInteger(), el.Id))
						returnValues.append(parameter.AsInteger())
					if parameter.StorageType == DB.StorageType.String:
						returnValuesAsString.append("{0}, {4}, {1}, {2}, {3}".format(el.Name if hasattr(el, "Name") else el.FamilyName, el.Id, parameter.Definition.Name, parameter.AsString(), el.Id))
						returnValues.append(parameter.AsString() if parameter.AsString() != None else "")
					if parameter.StorageType == DB.StorageType.ElementId:
						returnValuesAsString.append("{0}, {4}, {1}, {2}, {3}".format(el.Name if hasattr(el, "Name") else el.FamilyName, el.Id, parameter.Definition.Name, parameter.AsElementId().IntegerValue, el.Id))
						returnValues.append(parameter.AsElementId())
					parameterFound = True
				else:
					raise RuntimeError("parameter {0} not in {1}".format(inName, el.Id.IntegerValue))
			else:
				parameter = typeElement.LookupParameter(inName)
				if parameter:					
					if parameter.StorageType == DB.StorageType.Double:
						returnValuesAsString.append("{0}, {4}, {1}, {2}, {3:.4f}".format(el.Name if hasattr(el, "Name") else el.FamilyName, el.Id, parameter.Definition.Name, DB.UnitUtils.ConvertFromInternalUnits(parameter.AsDouble(), DB.DisplayUnitType.DUT_MILLIMETERS), el.Id))
						returnValues.append(DB.UnitUtils.ConvertFromInternalUnits(parameter.AsDouble(), DB.DisplayUnitType.DUT_MILLIMETERS))
					if parameter.StorageType == DB.StorageType.Integer:
						returnValuesAsString.append("{0}, {4}, {1}, {2}, {3}".format(el.Name if hasattr(el, "Name") else el.FamilyName, el.Id, parameter.Definition.Name, parameter.AsInteger(), el.Id))
						returnValues.append(parameter.AsInteger())
					if parameter.StorageType == DB.StorageType.String:
						returnValuesAsString.append("{0}, {4}, {1}, {2}, {3}".format(el.Name if hasattr(el, "Name") else el.FamilyName, el.Id, parameter.Definition.Name, parameter.AsString(), el.Id))
						returnValues.append(parameter.AsString() if parameter.AsString() != None else "")
					if parameter.StorageType == DB.StorageType.ElementId:
						returnValuesAsString.append("{0}, {4}, {1}, {2}, {3}".format(el.Name if hasattr(el, "Name") else el.FamilyName, el.Id, parameter.Definition.Name, parameter.AsElementId().IntegerValue, el.Id))
						returnValues.append(parameter.AsElementId())
				else:
					raise RuntimeError("parameter {0} not in {1}".format(typeElement.Name, el.Id.IntegerValue))
	if info:
		return returnValuesAsString
	elif allParametersInfo:
		return allParametersNames
	else:
		return returnValues

""" def getMembers(inElements):
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
	
	return uniqueParams """

def getElementsWithParameter(inElements, inBip):
	pvp = DB.ParameterValueProvider(DB.ElementId(int(inBip)))
	#evaluator = DB.FilterStringRuleEvaluator()
	paramElId = DB.ElementId(int(inBip))

	#FilterStringRuleEvaluator
	evaluatorGrater = DB.FilterStringGreater()
	evaluatorEquals = DB.FilterStringEquals()

	#Parameter filter rule
	ruleValStr = ""
	paramFilterRuleGreater = DB.FilterStringRule(pvp, evaluatorGrater, ruleValStr, False)
	paramFilterRuleEquals = DB.FilterStringRule(pvp, evaluatorEquals, ruleValStr, False)

	#element parameter filter
	epfGreater = DB.ElementParameterFilter(paramFilterRuleGreater)
	epfEquals = DB.ElementParameterFilter(paramFilterRuleEquals)
	col = DB.FilteredElementCollector(doc, inElements).WherePasses(DB.LogicalOrFilter(epfGreater, epfEquals))
	
	return col

	for el in inElements:
		try:
			if DB.ParameterFilterUtilities.IsParameterApplicable(el, paramElId):
				returnElements.append(el)
		except Exception as ex:
			Errors.catch('Error DB.ParameterFilterUtilities.IsParameterApplicable', ex)

	return returnElements



# <Run the form window
""" Application.EnableVisualStyles()
appWindow = MainForm(energyAnalyseObject)
appWindow.FormBorderStyle = FormBorderStyle.FixedSingle
appWindow.TopMost = True
appWindow.BackColor = Color.White


Application.Run(appWindow) """
# Run the form window>


allElementsIdsCol = getAllElements(doc, toId=True)
#allElements = processList(UnwrapElement, allElements)
markBip = DB.BuiltInParameter.ALL_MODEL_MARK

filteredElementsByParam = getElementsWithParameter(allElementsIdsCol, markBip)



#markValues = getValuesByParameterName(allElements, "ALL_MODEL_MARK", doc)

myOutput = filteredElementsByParam

if Errors.hasError():
 	OUT = Errors.report
elif Errors.hasContent():
	OUT = Errors.getConntainerContent()
else:
	OUT = myOutput