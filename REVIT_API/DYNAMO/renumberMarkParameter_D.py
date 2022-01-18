# -*- coding: utf-8 -*-
# Copyright(c) 2022, Daniel Gercak
#Script for selecting and grouping elements by levels and other parameters for dynamo 
#resource_path: H:\_WORK\PYTHON\REVIT_API\Group_geometry_node.py

import sys
import re
from itertools import groupby
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
from RevitServices.Transactions import TransactionManager
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

def getBuiltInParameterInstance(inBuiltInParamName):
	#print("RevitSelection.getBuiltInParameterInstance inBuiltInParamName {}".format(inBuiltInParamName))
	#builtInParams = Enum.GetValues(DB.BuiltInParameter)
	#bipNames = Enum.GetNames(DB.BuiltInParameter)
	returnVar = None
	''' for bip in builtInParams:
		#print("bip.ToString() {0} inBuiltInParamName {1}".format(bip.ToString(), inBuiltInParamName))
		if bip.ToString() in inBuiltInParamName:
			#print("bip.ToString() {0}".format(bip.ToString()))
			param_ID = DB.ElementId(bip)
			returnVar = bip
			break '''
	try:
		value = Enum.Parse(DB.BuiltInParameter, inBuiltInParamName, False)
		if Enum.IsDefined(DB.BuiltInParameter, value):
			returnVar = value
		else:
			returnVar = None
	except Exception as ex:
		#Errors.catch("Nevhodná (neexistujici) hodnota stringu pro funkci Enum.Parse", ex)
		returnVar = None
	return returnVar

''' def getValuesByParameterName(inElements, inName, doc, *args, **kwargs):
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
		return returnValues '''

def getValueByParameterName(el, inName, doc, *args, **kwargs):
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
	try:
		bip = getBuiltInParameterInstance(inName)
	except Exception as ex:
		bip = None
	if bip:
		pass
		#print("this is BIP param {0}".format(inName))
	else:
		if inBip:
			bip = inBip
		else:
			bip = None
	#raise TypeError("bip {0} inName {1}".format(bip, inName))
	#returnValues = []
	returnValue = None
	returnValueAsString = ""
	allParametersNames = []
	firstTime = True
	
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
			returnValue = DB.UnitUtils.ConvertFromInternalUnits(parameterVP.GetDoubleValue(el), DB.DisplayUnitType.DUT_MILLIMETERS)
		elif parameterVP.IsIntegerValueSupported(el):
			returnValue = parameterVP.GetIntegerValue(el)
		elif parameterVP.IsStringValueSupported(el):
			returnValue = parameterVP.GetStringValue(el) if parameterVP.GetStringValue(el) != None else ""
		elif parameterVP.IsElementIdValueSupported(el):
			returnValue = parameterVP.GetElementIdValue(el).IntegerValue
		else:
			returnValue = ""
	
	else:
		if not typeElement:
			parameter = el.LookupParameter(inName)
			if parameter:					
				if parameter.StorageType == DB.StorageType.Double:
					returnValueAsString = "{0}, {4}, {1}, {2}, {3:.4f}".format(el.Name if hasattr(el, "Name") else el.FamilyName, el.Id, parameter.Definition.Name, DB.UnitUtils.ConvertFromInternalUnits(parameter.AsDouble(), DB.DisplayUnitType.DUT_MILLIMETERS), el.Id)
					returnValue = DB.UnitUtils.ConvertFromInternalUnits(parameter.AsDouble(), DB.DisplayUnitType.DUT_MILLIMETERS)
				if parameter.StorageType == DB.StorageType.Integer:
					returnValueAsString = "{0}, {4}, {1}, {2}, {3}".format(el.Name if hasattr(el, "Name") else el.FamilyName, el.Id, parameter.Definition.Name, parameter.AsInteger(), el.Id)
					returnValue = parameter.AsInteger()
				if parameter.StorageType == DB.StorageType.String:
					returnValueAsString = "{0}, {4}, {1}, {2}, {3}".format(el.Name if hasattr(el, "Name") else el.FamilyName, el.Id, parameter.Definition.Name, parameter.AsString(), el.Id)
					returnValue = parameter.AsString() if parameter.AsString() != None else ""
				if parameter.StorageType == DB.StorageType.ElementId:
					returnValueAsString = "{0}, {4}, {1}, {2}, {3}".format(el.Name if hasattr(el, "Name") else el.FamilyName, el.Id, parameter.Definition.Name, parameter.AsElementId().IntegerValue, el.Id)
					returnValue = parameter.AsElementId()
				parameterFound = True
			else:
				raise RuntimeError("parameter {0} not in {1}".format(inName, el.Id.IntegerValue))
		else:
			parameter = typeElement.LookupParameter(inName)
			if parameter:					
				if parameter.StorageType == DB.StorageType.Double:
					returnValueAsString = "{0}, {4}, {1}, {2}, {3:.4f}".format(el.Name if hasattr(el, "Name") else el.FamilyName, el.Id, parameter.Definition.Name, DB.UnitUtils.ConvertFromInternalUnits(parameter.AsDouble(), DB.DisplayUnitType.DUT_MILLIMETERS), el.Id)
					returnValue = DB.UnitUtils.ConvertFromInternalUnits(parameter.AsDouble(), DB.DisplayUnitType.DUT_MILLIMETERS)
				if parameter.StorageType == DB.StorageType.Integer:
					returnValueAsString = "{0}, {4}, {1}, {2}, {3}".format(el.Name if hasattr(el, "Name") else el.FamilyName, el.Id, parameter.Definition.Name, parameter.AsInteger(), el.Id)
					returnValue = parameter.AsInteger()
				if parameter.StorageType == DB.StorageType.String:
					returnValueAsString = "{0}, {4}, {1}, {2}, {3}".format(el.Name if hasattr(el, "Name") else el.FamilyName, el.Id, parameter.Definition.Name, parameter.AsString(), el.Id)
					returnValue = parameter.AsString() if parameter.AsString() != None else ""
				if parameter.StorageType == DB.StorageType.ElementId:
					returnValueAsString = "{0}, {4}, {1}, {2}, {3}".format(el.Name if hasattr(el, "Name") else el.FamilyName, el.Id, parameter.Definition.Name, parameter.AsElementId().IntegerValue, el.Id)
					returnValue = parameter.AsElementId()
			else:
				raise RuntimeError("parameter {0} not in {1}".format(typeElement.Name, el.Id.IntegerValue))
	if info:
		return returnValueAsString
	elif allParametersInfo:
		return allParametersNames
	else:
		return returnValue

def setValueByParameterName(el, inValue, inName, doc, *args, **kwargs):
	"""
		set parameter value from element by parameter name
		must be in Transaction block

		args:
		inElement type: list(DB.Element,...)
		inValues type: list(DB.Element or str, or int, or float...)
		inName: type: string

	"""
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

	#returnValues = []
	returnValue = None
	#firstTime = True
	try:
		#TransactionManager.Instance.EnsureInTransaction(doc)
		#trans = SubTransaction(doc)
		#trans.Start()
		parameterFound = False
		if bip:
			parameterFound = True
			param_ID = DB.ElementId(bip)
			parameterVP = DB.ParameterValueProvider(param_ID)
			if parameterVP.IsDoubleValueSupported(el):
				if type(inValue) == float:
					returnValue = "parameter {0} as DoubleValue of element {1} has been set to {2}".format(inName, el.Id.IntegerValue, inValue)
					myParam = el.Parameter[bip].Set(inValue)
				else: 
					raise TypeError("Wrong format of input value {0} of type {1}. It must be of type int or float".format(inValue, type(inValue)))
			if parameterVP.IsIntegerValueSupported(el):
				if type(inValue) == int:
					myParam = el.Parameter[bip].Set(inValue)
					turnValue = "parameter {0} as IntegerValue of element {1} has been set to {2}".format(inName, el.Id.IntegerValue, inValue)
				else: 
					raise TypeError("Wrong format of input value {0} of type {1}. It must be of type int".format(inValue, type(inValue)))
			if parameterVP.IsStringValueSupported(el):
				if type(inValue) == str:
					#paramElementId = parameterVP.Parameter
					#paramElement = doc.GetElement(paramElementId)
					if el.Parameter[bip] != None:
						myParam = el.Parameter[bip].Set(inValue)
						returnValue = "parameter {0} as StringValue of element {1} has been set to {2}".format(inName, el.Id.IntegerValue, inValue)
					else:
						returnValue = "el is None!!"
				else: 
					raise TypeError("Wrong format of input value {0} of type {1}. It must be of type str".format(inValue, type(inValue)))
			if parameterVP.IsElementIdValueSupported(el):
				if type(inValue) == DB.ElementId:
					myParam = el.Parameter[bip].Set(inValue)
					returnValue = "parameter {0} as ElementIdValue of element {1} has been set to {2}".format(inName, el.Id.IntegerValue, inValue)
				else: 
					raise TypeError("Wrong format of input value {0} of type {1}. It must be of type ElementId".format(inValue, type(inValue)))
		
		else:
			if el.GetTypeId().IntegerValue > -1:
				typeElement = doc.GetElement(el.GetTypeId())
				parameter = typeElement.LookupParameter(inName)
				if parameter:
					if parameter.StorageType == DB.StorageType.Double:
						returnValue = setParameterAsDouble(el, parameter, inValue)
					if parameter.StorageType == DB.StorageType.Integer:
						returnValue = setParameterAsInteger(el, parameter, inValue)
					if parameter.StorageType == DB.StorageType.String:
						returnValue = setParameterAsString(el, parameter, inValue)
					if parameter.StorageType == DB.StorageType.ElementId:
						returnValue = setParamAsElementId(el, parameter, inValue)
					parameterFound = True
				
				else:
					elparameter = el.LookupParameter(inName)
					if elparameter:
					# parameters = el.GetOrderedParameters()
					# for parameter in parameters:
						# if parameter.Definition.Name == inName:
						if elparameter.StorageType == DB.StorageType.Double:
							returnValue = setParameterAsDouble(el, elparameter, inValue)
						if elparameter.StorageType == DB.StorageType.Integer:
							returnValue = setParameterAsInteger(el, elparameter, inValue)
						if elparameter.StorageType == DB.StorageType.String:
							returnValue = setParameterAsString(el, elparameter, inValue)
						if elparameter.StorageType == DB.StorageType.ElementId:
							returnValue= setParamAsElementId(el, elparameter, inValue)
						parameterFound = True
							# if not firstTime:
							# 	break					
		#TransactionManager.Instance.TransactionTaskDone()
		if not parameterFound:
			raise NameError("Parameter name {0} not found in element {1}".format(inName, el.Id.IntegerValue))
		#firstTime = False
		else:
			return returnValue
		
	except:
		
		import traceback
		errorReport = traceback.format_exc()
		#trans.RollBack()
		#TransactionManager.Instance.TransactionTaskDone()
		raise RuntimeError("Parameter name {0} not set !!! {1}".format(inName, errorReport))
		
def setParameterAsDouble(inElement, inParameter, inValue):
	if inParameter.StorageType == DB.StorageType.Double:
		try:
			strToFloat = float(inValue)
		except:
			strToFloat = False
		if type(inValue) == float:
			convertedValue = DB.UnitUtils.ConvertToInternalUnits(inValue, DB.DisplayUnitType.DUT_MILLIMETERS)
			inParameter.Set(convertedValue)
			return "parameter {0} as DoubleValue of element {1} has been set to {2}".format(inParameter.Definition.Name, inElement.Id.IntegerValue, convertedValue)
		elif strToFloat != False:
			convertedValue = DB.UnitUtils.ConvertToInternalUnits(strToFloat, DB.DisplayUnitType.DUT_MILLIMETERS)
			inParameter.Set(convertedValue)
			return "parameter {0} as strToFloat DoubleValue of element {1} has been set to {2}".format(inParameter.Definition.Name, inElement.Id.IntegerValue, convertedValue)
		else: 
			raise TypeError("Wrong format of input value {0} of type {1}. It must be of type float, int or str and conversion from str or from int by float() must throw no exception".format(inValue, type(inValue)))
	else:
		raise TypeError("input parameter.StorageType is not of type StorageType.Double in RevitSelection.py setDouble()")

def setParameterAsInteger(inElement, inParameter, inValue):
	if inParameter.StorageType == DB.StorageType.Integer:
		try:
			strToInt = int(inValue)
		except:
			strToInt = False
		if type(inValue) == int:
			inParameter.Set(inValue)
			return "parameter {0} as IntegerValue of element {1} has been set to {2}".format(inParameter.Definition.Name, inElement.Id.IntegerValue, inValue)
		elif strToInt != False:
			inParameter.Set(strToInt)
			return "parameter {0} as strToInt IntegerValue of element {1} has been set to {2}".format(inParameter.Definition.Name, inElement.Id.IntegerValue, strToInt)
		else: 
			raise TypeError("Wrong format of input value {0} of type {1}. It must be of type int or str and conversion from str to int by int() must throw no exception".format(inValues[i], type(inValues[i])))
	else:
		raise TypeError("input parameter.StorageType is not of type StorageType.Integer in RevitSelection.py setInteger()")

def setParameterAsString(inElement, inParameter, inValue):
	if inParameter.StorageType == DB.StorageType.String:
		try:
			valToStr = str(inValue)
		except:
			valToStr = False
		if type(inValue) == str:
			inParameter.Set(inValue)
			#Errors.catchVar("Element {0} has been set to {1}".format(inElement.Id, inValue))
			return "parameter {0} as StringValue of element {1} has been set to {2}".format(inParameter.Definition.Name, inElement.Id.IntegerValue, inValue)
		elif valToStr != False:
			inParameter.Set(valToStr)
			returnValue = "parameter {0} as valToStr StringValue of element {1} has been set to {2}".format(inParameter.Definition.Name, inElement.Id.IntegerValue, valToStr)
			return returnValue
		else: 
			raise TypeError("Wrong format of input value {0} of type {1}. It must be of type str or conversion from other format by str() must throw no exception".format(inValue, type(inValue)))
	else:
		raise TypeError("input parameter.StorageType is not of type StorageType.String in RevitSelection.py setString()")

def setParamAsElementId(inElement, inParameter, inValue):
	if inParameter.StorageType == DB.StorageType.ElementId:
		if type(inValue) == DB.ElementId:
			inParameter.Set(inValue)
			return "parameter {0} as StringValue of element {1} has been set to {2}".format(inParameter.Definition.Name, inElement.Id.IntegerValue, inValue)
		else: 
			raise TypeError("Wrong format of input value {0} of type {1}. It must be of type ElementId".format(inValue, type(inValue)))

def getElementsMatchingRegEx(inElementsIds, inBip, inRegExp):
	pvp = DB.ParameterValueProvider(DB.ElementId(int(inBip)))
	#regExp = r"^[A-Z][A-Z]\."
	regExp = r"" + inRegExp
	validRexExp = re.compile(regExp)
	#evaluator = DB.FilterStringRuleEvaluator()
	paramElId = DB.ElementId(int(inBip))
	elementsCol = DB.FilteredElementCollector(doc, inElementsIds).WhereElementIsNotElementType().ToElements()
	values = []
	returnElements = []
	try:
		for el in list(elementsCol):
			if pvp.IsStringValueSupported(el):
				#values.append(pvp.GetStringValue(el) if pvp.GetStringValue(el) != None else "")
				value = pvp.GetStringValue(el) if pvp.GetStringValue(el) != None else ""
				#matches = validRexExp.match(pvp.GetStringValue(el) if pvp.GetStringValue(el) != None else "")
				matches = validRexExp.match(pvp.GetStringValue(el))
				if matches:
					values.append("{0} matches regExp {1} : {2}".format(value, regExp, matches))
					returnElements.append(el)
				else:
					values.append("{0} doesn't match regExp {1} : {2}".format(value, regExp, matches))
			else:
				pass
				#values.append("Not StringValuesSupported")
		return (returnElements ,values)
	except Exception as ex:
		Errors.catch('Error ', ex)
		return None

def copyParameterValues(inElements, inFromParamName, inToParamName, doc, *args, **kwargs):
	inBipTo = kwargs["bipTo"] if 'bipTo' in kwargs else None
	inBipFrom = kwargs["bipFrom"] if 'bipFrom' in kwargs else None
	#print("this is BIP param {0}".format(inName))
	bipTo = getBuiltInParameterInstance(inToParamName)
	bipFrom = getBuiltInParameterInstance(inFromParamName)
	if bipTo:
		pass
		#print("this is BIP param {0}".format(inName))
	else:
		if inBipTo:
			bipTo = inBipTo
		else:
			bipTo = None
	
	if bipFrom:
		pass
		#print("this is BIP param {0}".format(inName))
	else:
		if inBipFrom:
			bipFrom = inBipFrom
		else:
			bipFrom = None

	results = []
	for el in inElements:
		fromParamValue = getValueByParameterName(el, inFromParamName, doc, bip = bipFrom)
		# set to inToParamterName
		if fromParamValue != None:
			setValue = setValueByParameterName(el, fromParamValue, inToParamName, doc, bip = bipTo)
			results.append(setValue)
		else:
			pass
	return results

def getMembers(inElements):
	uniqueParams = {}
	uniqueTypeIds = []
	uniqueFamilies = {}
	nameToParamDic = {}
	for el in inElements:
		if el.GetTypeId().IntegerValue > -1:
			if el.GetTypeId() not in uniqueTypeIds:
				uniqueTypeIds.append(el.GetTypeId())
			familyName = doc.GetElement(el.GetTypeId()).FamilyName
			if familyName not in uniqueFamilies:
				uniqueFamilies[familyName] = el.GetTypeId()
		elParams = el.GetOrderedParameters()
		for elParam in elParams:
			if elParam != None:
				if elParam.Definition.Name not in uniqueParams:
					uniqueParams[elParam.Definition.Name] = elParam
					nameToParamDic[elParam.Definition.Name] = elParam

	for k, elId in uniqueFamilies.items():
		el = doc.GetElement(elId)
		elParams = el.GetOrderedParameters()
		for elParam in elParams:
			if elParam.Definition.Name not in uniqueParams:
				uniqueParams[elParam.Definition.Name] = UnwrapElement(elParam)
				nameToParamDic[elParam.Definition.Name] = UnwrapElement(elParam)
	
	return (uniqueParams, nameToParamDic)

def parameterNameTest(inElements, inParamName):
	isElement = False
	isParameter = False
	if isinstance(inElements, list):
		if len(inElements) > 0:
			if isinstance(inElements[0], DB.Element):
				isElement = True
				isParameter = doTest(inElements[0], inParamName)
	elif isinstance(inElements, DB.Element):
		isElement = True
		isParameter = doTest(inElements[0], inParamName)

	return isParameter
		

def doTest(inElement, inParamName):
	isParameter = False
	try:
		param = inElement.LookupParameter(inParamName)
		if param:
			isParameter = True
	except Exception as ex:
		pass
	if not isParameter:
		try:
			param = getBuiltInParameterInstance(inParamName)
			if param:
				isParameter = True
		except Exception as ex:
			pass
	return isParameter

#MAIN INSTRUCTIONS

inElements = IN[0]
markBipName = "ALL_MODEL_MARK"
writeParamName = IN[1]
#writeParamName = "Komentář 2"
#writeParamName = "ALL_MODEL_MARK"
assemblyCodeBipName = "UNIFORMAT_CODE"

unWrapped = processList(UnwrapElement, inElements)

#INPUT PARAMETER TEST
paramTest = parameterNameTest(unWrapped, writeParamName)
if not paramTest:
	raise TypeError("Input Prameter Name isn't right name for Parameter, or Input elements has no such parameter Name")

elementsIds = [x.Id for x in unWrapped]

elementsIdsCol = Clist[DB.ElementId](elementsIds)
elementsCol = Clist[DB.Element](unWrapped)

#allElements = processList(UnwrapElement, allElements)


markBip = getBuiltInParameterInstance(markBipName)
assemblyCodeBip = getBuiltInParameterInstance(assemblyCodeBipName)
#copyToBip = getBuiltInParameterInstance(copyToBipName)
writeParamVals = processList(getValueByParameterName, unWrapped, writeParamName, doc)


markParamVals = processList(getValueByParameterName, unWrapped, markBipName, doc, bip = markBip)

assemblyCodeParamVals = processList(getValueByParameterName, unWrapped, assemblyCodeBipName, doc, bip = assemblyCodeBip)
#composite for grouping tuple(markParamVals, assemblyCodeParamVals, elementsCol)
grComp = zip(assemblyCodeParamVals, markParamVals, list(elementsCol))
grComp = sorted(grComp, key = lambda x: x[0])
key_func = lambda x: x[0]
#groupedACPVobj = groupby(assemblyCodeParamVals, lambda x: x[0])
groups = {}
for key, group in groupby(grComp, key_func):
	groups[key] = list(group)

#BEGIN TRANSACTION
TransactionManager.Instance.EnsureInTransaction(doc)
trans = DB.SubTransaction(doc)
trans.Start()
results = []
for k,group in groups.items():
	for i, item in enumerate(group):
		writeStr = "{0:0>3}".format(i+1)
		results.append(setValueByParameterName(item[2], writeStr, writeParamName, doc))
trans.Commit()
TransactionManager.Instance.TransactionTaskDone()
#END TRANSACTION

myOutput = results

if Errors.hasError():
 	OUT = Errors.report
elif Errors.hasContent():
	OUT = Errors.getConntainerContent()
else:
	OUT = myOutput