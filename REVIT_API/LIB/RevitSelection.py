# -*- coding: utf-8 -*-
# Copyright(c) 2020, Daniel Gercak
#Classes and functions for selecting and organizing elements from Revit. 
#There are also functions for geometry transform to Dynamo
#resource_path: H:\_WORK\PYTHON\REVIT_API\LIB\RevitSelection.py
import sys
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
lib_path = r'H:\_WORK\PYTHON\REVIT_API\LIB'
sys.path.append(lib_path)
sys.path.append(pyt_path)



import ListUtils as ListUtils
from Errors import *

try:
	sys.modules['__main__']
	hasMainAttr = True	
except:
	hasMainAttr = False


if hasMainAttr:

	#import clr
	from Autodesk.Revit.UI.Selection import *
	import Autodesk.Revit.DB as DB
	doc = __revit__.ActiveUIDocument.Document
	#clr.AddReference("RevitServices")
	#import RevitServices
	#from RevitServices.Transactions import TransactionManager

else:
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
from itertools import chain, groupby

def Unwrap(item, *args):
	return UnwrapElement(item)

def _UnwrapElement(listOrEle):
	if listOrEle is None: 
		return None

	if hasattr(listOrEle, '__iter__'):
		return [_UnwrapElement(x) for x in listOrEle]
	elif hasattr(listOrEle, 'InternalElement'):
		return listOrEle.InternalElement
	else:
		return listOrEle

def getLevelAbove(e):
	allLevels = DB.FilteredElementCollector(doc) \
				.OfCategory(BuiltInCategory.OST_Levels) \
				.WhereElementIsNotElementType() \
				.ToElements()

	elevations = [i.Elevation for i in allLevels]
	sortedLevels = [x for (y,x) in sorted(zip(elevations,allLevels))]
	sortedLevelNames = [i.Name for i in sortedLevels]
	index = sortedLevelNames.index(e.Name)
	if index + 1 >= len(sortedLevels):
		return None
	else:
		return sortedLevels[index+1]

def getLevels():
	"""returns 1D list of DB.Element of all levels in active document
       
       args:
            
       return: sorted list of DB.Element objects of levels according to elevation
    """
	allLevels = DB.FilteredElementCollector(doc) \
				.OfCategory(DB.BuiltInCategory.OST_Levels) \
				.WhereElementIsNotElementType() \
				.ToElements()

	elevations = [i.Elevation for i in allLevels]
	sortedLevels = [x for (y,x) in sorted(zip(elevations,allLevels))]
	return sortedLevels

def getLevelIds(inLevels):
	"""returns 1D list of int representation of ids of level elements in input
       
       args:
            inLevels: list of DB.Element of category DB.BuiltInCategory.OST_Levels
            
       return: list of level Ids - type: int
    """
	levelIds = []
	if type(inLevels) == list:
		for level in inLevels:
		#	levelIdNames.append(str(level.Name))
			levelIds.append(int(str(level.Id)))
		return levelIds
	else:
		return [int(str(level.Id))]

def getElementLevelIdIndex(item, inlevelIds):
	"""returns list index of document level Ids of DB.Element object
       
       args:
            item: type: DB.Element
            inlevelIds: list of level Ids - type: [int, ...]
            
       return: index of inlevelIds list of DB.Element - type: int
    """
	elemLevId = int(str(item.LevelId))
	categoryId = item.Category.Id
	builtincategory = Enum.ToObject(DB.BuiltInCategory, item.Category.Id.IntegerValue)
#	inCategory = doc.Settings.Categories.GetEnumerator()
#	inCategory.Current
	inCategory = None
	levIdIndex = 0  
	if elemLevId != -1:
		levIdIndex = inlevelIds.index(elemLevId)
	else:
		if "Column" in builtincategory.ToString():
			for colCg in columnCgs:
				if builtincategory.ToString() in colCg.ToString():
	#			levIdIndex = inlevelIds.index(inlevelIds[len(inlevelIds) - 1])
					levIdIndex = 10000
	return (levIdIndex)

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

def getElementByClassName(inClass, *args, **kwargs):
	"""returns 1D list of all Revit Elements in active view according to class name input
       
       args:
            inClass: list of Revit class names inherited from DB.Element Class (e.g. [DB.ExtrusionRoof, ...])
            args[0]: inExcludeElementCollection type: ICollection - optional list of elements intended to be excluded from final selection 
            
			kwargs["curtainWall"]: type: bool if True, returns only curtain walls or curtain system objects, else if not set or False returns Wall objects except curtain walls
       return: IList of DB.Element objects
    """
	curtainWall = kwargs["curtainWall"] if "curtainWall" in kwargs else False
	elements = []
	if len(args) > 0:
		inExcludeElementCollection = args[0]
	else:
		inExcludeElementCollection = []
	if isinstance(inClass, list):
		notFlattened = []
		for i in inClass:
			if len(inExcludeElementCollection) != 0:
				myElements = DB.FilteredElementCollector(doc, doc.ActiveView.Id) \
							.OfClass(i) \
							.WherePasses(DB.ExclusionFilter(inExcludeElementCollection)) \
							.ToElements()
			else:
				myElements = DB.FilteredElementCollector(doc, doc.ActiveView.Id) \
							.OfClass(i) \
							.ToElements()
			notFlattened.append(list(myElements))
		elements = Clist[DB.Element](list(chain.from_iterable(notFlattened)) if len(notFlattened) > 0 else [])

	else:
		if len(inExcludeElementCollection) != 0:
			elements = DB.FilteredElementCollector(doc, doc.ActiveView.Id) \
						.OfClass(inClass) \
						.WherePasses(DB.ExclusionFilter(inExcludeElementCollection)) \
						.ToElements()
		else:
			elements = DB.FilteredElementCollector(doc, doc.ActiveView.Id) \
						.OfClass(inClass) \
						.ToElements()

	#curtain wall iDs
	cwIds = []
	#other elements iDs
	otherIds = []
	for element in list(elements):
		if element.GetType().Name == "CurtainSystem" or (element.GetType().Name == "Wall" and element.CurtainGrid != None):
			cwIds.append(element.Id)
		else:
			otherIds.append(element.Id)
	cwIds_collection = Clist[DB.ElementId](cwIds)
	
	otherIds_collection = Clist[DB.ElementId](otherIds)
	#raise ValueError("cwIds_collection {0} - {1}; wIds_collection {2} - {3}".format(len(cwIds_collection), cwIds_collection, len(wIds_collection), wIds_collection))
	returnOther = Clist[DB.Element]([])
	returnCWs = Clist[DB.Element]([])
	for i in inClass:
		if curtainWall:	
			#elements = DB.FilteredElementCollector(doc, cwIds_collection).OfClass(i).ToElements() if len(list(cwIds_collection)) > 0 else Clist[DB.Element]([])
			''' if len(otherIds_collection) > 0:
				elements = DB.FilteredElementCollector(doc, doc.ActiveView.Id) \
							.OfClass(i) \
							.WherePasses(DB.ExclusionFilter(otherIds_collection)) \
							.ToElements()
			if i == DB.CurtainSystem:
				raise ValueError("CurtainSystem elements {0} - {1}".format(len(elements), elements))
			elif i == DB.Wall:
				pass
				#raise ValueError("CurtainWall elements {0} - {1}".format(len(elements), elements))
				#return elements
				#break
			else: 
				elements = DB.FilteredElementCollector(doc, doc.ActiveView.Id) \
							.OfClass(i) \
							.ToElements()
				#return elements
				#break
			for el in elements:
				returnCWs.Add(el) '''
			for elId in list(cwIds_collection):
				myElement = doc.GetElement(elId)
				returnCWs.Add(myElement)
			#raise ValueError("CurtainWall elements {0} - {1}".format(len(returnCWs), returnCWs))

		else:
			#elements = DB.FilteredElementCollector(doc, wIds_collection).OfClass(i).ToElements() if len(list(wIds_collection)) > 0 else Clist[DB.Element]([])
			#elements = doc.GetElement(wIds_collection)
			if len(cwIds_collection) > 0:
				elements = DB.FilteredElementCollector(doc, doc.ActiveView.Id) \
							.OfClass(i) \
							.WherePasses(DB.ExclusionFilter(cwIds_collection)) \
							.ToElements()
				#return elements
				#break
			else: 
				elements = DB.FilteredElementCollector(doc, doc.ActiveView.Id) \
							.OfClass(i) \
							.ToElements()
				#return elements
				#break
			for el in elements:
				returnOther.Add(el)
		#raise ValueError("returnWalls {0} - {1}".format(len(returnWalls), returnWalls))
		if curtainWall:
			return returnCWs
		else:
			return returnOther
	#elements = Clist[DB.Element](list(chain.from_iterable(notFlattened)) if len(notFlattened) > 0 else [])
	

def getElementByClassNameAtLevels(inClass, inLevelIds, *args):
	"""returns structured list of all Revit Elements in active view according to class name input
       
       args:
            inClass: list of Revit class names inherited from DB.Element Class (e.g. [DB.ExtrusionRoof, ...])
			inLevelIds: list of level Ids type: list[int, ...]
            args[0]: inExcludeElementCollection type: ICollection - optional list of elements intended to be excluded from final selection 
            
       return: list[level_1[DB.Element, ...], level_2[DB.Element, ...], ...]
    """
	elements = []
	allLevels = getLevels()
	if len(args) > 0:
		inExcludeElementCollection = args[0]
	else:
		inExcludeElementCollection = []
	if isinstance(inClass, list):
		notFlattened = []
		for i in inClass:
			if len(inExcludeElementCollection) != 0:
				myElements = DB.FilteredElementCollector(doc, doc.ActiveView.Id) \
							.OfClass(i) \
							.WherePasses(DB.ExclusionFilter(inExcludeElementCollection)) \
							.ToElements()
			else:
				myElements = DB.FilteredElementCollector(doc, doc.ActiveView.Id) \
							.OfClass(i) \
							.ToElements()
			notFlattened.append(myElements)
		elements = list(chain.from_iterable(notFlattened))
	else:
		if len(inExcludeElementCollection) != 0:
			elements = DB.FilteredElementCollector(doc, doc.ActiveView.Id) \
						.OfClass(inClass) \
						.WherePasses(DB.ExclusionFilter(inExcludeElementCollection)) \
						.ToElements()
		else:
			elements = DB.FilteredElementCollector(doc, doc.ActiveView.Id) \
						.OfClass(inClass) \
						.ToElements()
	elementsAtLevel = [[] for i in range(len(allLevels))] 
	for i, element in enumerate(elements):
		elemLevId = int(str(element.LevelId)) 
		levIdIndex = 0  
		if elemLevId != -1:
			levIdIndex = inLevelIds.index(elemLevId)
		else:
			if inClass in roofCNs:
				levIdIndex = inLevelIds.index(inLevelIds[len(allLevels) - 1])
		elementsAtLevel[levIdIndex].append(element)
	return elementsAtLevel

def getElementByCategory(inCategory, *args):
	"""returns 1D list of all Revit Elements in active view according to DB.BuiltInCategory member name
       
       args:
            inCategory: list of DB.BuiltInCategory member names (e.g. [DB.BuiltInCategory.OST_Walls, ...])
            args[0]: inExcludeElementCollection type: ICollection - optional list of elements intended to be excluded from final selection 
            
       return: IList of DB.Element objects
    """
	elements = []
	if len(args) > 0:
		inExcludeElementCollection = args[0]
	else:
		inExcludeElementCollection = []
	if isinstance(inCategory, list):
		notFlattened = []
		for i in inCategory:
			if len(inExcludeElementCollection) != 0:
				myElements = DB.FilteredElementCollector(doc, doc.ActiveView.Id) \
							   .OfCategory(i) \
							   .WherePasses(DB.ExclusionFilter(inExcludeElementCollection)) \
							   .WhereElementIsNotElementType() \
							   .ToElements()
			else:
				myElements = DB.FilteredElementCollector(doc, doc.ActiveView.Id) \
							   .OfCategory(i) \
							   .WhereElementIsNotElementType() \
							   .ToElements()
			notFlattened.append(myElements)
		elements = list(chain.from_iterable(notFlattened))
	else:
		if len(inExcludeElementCollection) != 0:
			elements = DB.FilteredElementCollector(doc, doc.ActiveView.Id) \
						 .OfCategory(inCategory) \
						 .WherePasses(DB.ExclusionFilter(inExcludeElementCollection)) \
						 .ToElements()
		else:
			elements = DB.FilteredElementCollector(doc, doc.ActiveView.Id) \
						 .OfCategory(inCategory) \
						 .ToElements()
	return elements

def getElementByCategoryAtLevels(inCategory, inLevelIds, *args):
	"""returns structured list of all Revit Elements in active view according to DB.BuiltInCategory member name
       
       args:
            inCategory: list of DB.BuiltInCategory member names (e.g. [DB.BuiltInCategory.OST_Walls, ...])
			inLevelIds: list of level Ids type: list[int, ...]
            args[0]: inExcludeElementCollection type: ICollection - optional list of elements intended to be excluded from final selection 
            
       return: list[level_1[DB.Element, ...], level_2[DB.Element, ...], ...]
    """
	elements = []
	allLevels = getLevels()
	if len(args) > 0:
		inExcludeElementCollection = args[0]
	else:
		inExcludeElementCollection = []
	if isinstance(inCategory, list):
		notFlattened = []
		for i in inCategory:
			if len(inExcludeElementCollection) != 0:
				myElements = DB.FilteredElementCollector(doc, doc.ActiveView.Id) \
							   .OfCategory(i) \
							   .WherePasses(DB.ExclusionFilter(inExcludeElementCollection)) \
							   .WhereElementIsNotElementType() \
							   .ToElements()
			else:
				myElements = DB.FilteredElementCollector(doc, doc.ActiveView.Id) \
							   .OfCategory(i) \
							   .WhereElementIsNotElementType() \
							   .ToElements()
			notFlattened.append(myElements)
		elements = list(chain.from_iterable(notFlattened))
	else:
		if len(inExcludeElementCollection) != 0:
			elements = DB.FilteredElementCollector(doc, doc.ActiveView.Id) \
						 .OfCategory(inCategory) \
						 .WherePasses(DB.ExclusionFilter(inExcludeElementCollection)) \
						 .ToElements()
		else:
			elements = DB.FilteredElementCollector(doc, doc.ActiveView.Id) \
						 .OfCategory(inCategory) \
						 .ToElements()
	elementsAtLevel = [[] for i in range(len(allLevels))] 
	for i, element in enumerate(elements):
		elemLevId = int(str(element.LevelId)) 
		levIdIndex = 0  
		if elemLevId != -1:
			levIdIndex = inLevelIds.index(elemLevId)
		else:
			if inCategory in columnCgs:
				levIdIndex = inLevelIds.index(inLevelIds[len(allLevels) - 1])
		elementsAtLevel[levIdIndex].append(element)
	return elementsAtLevel

def getInserts(item, *args, **kwargs):
	"""returns inserts of element (DB.Element) if exist

		args:
			item: DB.Element
			incopenings: option for included openings - default = True
			incshadows = option for included shadows - default = True
			incwalls = option for included walls - default = True
			incshared = option for included shared element - default = True

		return: list[DB.Element, ...]
		"""
	
	incopenings = kwargs["incopenings"] if "incopenings" in kwargs else True
	incshadows = kwargs["incshadows"] if "incshadows" in kwargs else True
	incwalls = kwargs["incwalls"] if "incwalls" in kwargs else True
	incshared = kwargs["incshared"] if "incshared" in kwargs else True
	# Regular host objects
	if hasattr(item, "FindInserts"):
		returnInserts = [item.Document.GetElement(x) for x in item.FindInserts(incopenings,incshadows,incwalls,incshared)]
		if len(returnInserts)>0:
			pass
		return returnInserts
	# Railings
	if hasattr(item, "GetAssociatedRailings"):
		return [item.Document.GetElement(x) for x in item.GetAssociatedRailings()]
	else: return []

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

def getOpeningsElements(inElements, **kwargs):
	"""
	get Revit Elements of raw openings without filling from current Revit document

	inElements [Autodesk.RevitDB.Element]
	kwargs["onlyFills"] type: bool - if True, returns only fills of openings, otherwise returns only openings as a Wall elements
	Returns: list[Autodesk.RevitDB.Element]
	"""
	onlyFills = kwargs["onlyFills"] if "onlyFills" in kwargs else False
	rawInserts = ListUtils.flatList(ListUtils.processList(getInserts, inElements, incopenings = True, incshadows = False, incwalls = False, incshared = True))
	#raise ValueError("rawInserts {0}".format(len(rawInserts)))
	rawInsertsIds = [x.Id for x in rawInserts]
	rawInsertsIdsCol = Clist[DB.ElementId](rawInsertsIds)
	paramId = DB.ElementId(DB.BuiltInParameter.VIEW_PHASE)
	param_provider = DB.ParameterValueProvider(paramId)
	activeViewPhaseId = param_provider.GetElementIdValue(doc.ActiveView)

	myElementPhaseStatusFilter1 = DB.ElementPhaseStatusFilter(activeViewPhaseId, DB.ElementOnPhaseStatus.Existing, False)
	myElementPhaseStatusFilter2 = DB.ElementPhaseStatusFilter(activeViewPhaseId, DB.ElementOnPhaseStatus.New,False)
	if len(rawInsertsIdsCol) > 0:
		insertOpenings = DB.FilteredElementCollector(doc, rawInsertsIdsCol) \
																			.WherePasses(DB.LogicalOrFilter(myElementPhaseStatusFilter1 \
																				,myElementPhaseStatusFilter2)) \
																			.WherePasses(DB.ElementCategoryFilter(DB.BuiltInCategory.OST_Walls, True)) \
																			.ToElements()
		#Errors.catchVar(insertOpenings, "insertOpenings")
		insertWalls = DB.FilteredElementCollector(doc, rawInsertsIdsCol) \
																		.WherePasses(DB.ElementCategoryFilter(DB.BuiltInCategory.OST_Walls, False)) \
																		.ToElementIds()
		#Errors.catchVar(insertWalls, "insertWalls")
	else:
		insertOpenings = Clist[DB.Element]([])
		insertWalls = Clist[DB.ElementId]([])	
	

	filteredWalls = []
	for elem in list(insertOpenings):
		#el = insertWalls[0].Id
		# Get the element from the selected element reference
		el_ID = doc.GetElement(elem.Id)
		# Get the Bounding Box of the selected element.
		el_bb = el_ID.get_BoundingBox(doc.ActiveView)
		# Get the min and max values of the elements bounding box.
		el_bb_max = el_bb.Max
		el_bb_min = el_bb.Min
		filteredWall = DB.FilteredElementCollector(doc, insertWalls) \
																		.WherePasses(DB.BoundingBoxIntersectsFilter(DB.Outline(el_bb_min, el_bb_max))) \
																		.ToElements()
		if len(list(filteredWall)) > 0:
			filteredWalls += filteredWall		
	if onlyFills:
		return insertOpenings
	else:
		return ListUtils.flattenList(filteredWalls)

def getRevitGeometry(inElement, *args, **kwargs):
	"""
		get revit geometry from revit element

		inElement: type: DB.Element
		kwargs['only3D'] type: bool - returns only solid objects if true, else returns also 2D geometry as tuple(geos, geosNot3D, geosOther), default = True
		kwargs['asDynamoGeometry'] - returns Autodesk.DesignScript.Geometry.Solid objects if True, default False
		Returns: list[DB.Solid, ...] if only3D == True, else returns 
					tuple(list[DB.Solid] - all 3D solids,
						  list[DB.Solid] - Solids with zero Volume, 
						  list[...], other geometry)
	"""
	only3D = kwargs['only3D'] if 'only3D' in kwargs else True
	asDynamoGeo = kwargs['asDynamoGeometry'] if 'asDynamoGeometry' in kwargs else False

	gopt = DB.Options()
	gopt.View = doc.ActiveView
	element = _UnwrapElement(inElement)		
	geo1 = element.get_Geometry(gopt)
	enum1 = geo1.GetEnumerator()
	geos = []
	geos2 = None
	geosNot3D = []
	geosOther = []
	unitedSolid = None
	first = True
	while enum1.MoveNext():
		geos2 = []
		if hasattr(enum1.Current, "GetInstanceGeometry"):
			geo2 = enum1.Current.GetInstanceGeometry()
		else:
			geo2 = enum1.Current
		geosNot3d2 = []
		geosOther2 = []
		if ListUtils.isIterable(geo2):
			for i, g in enumerate(geo2):
				if hasattr(g, "Volume"):
					if g.Volume > 0:
						#solid = g.Convert()
						#geos2.append(solid)
						if asDynamoGeo:
							geos2.append(g.ToProtoType())
						else:
							geos2.append(g)
					else:
						geosNot3d2.append(g)
				else:
					geosOther2.append(g.ToProtoType()) if hasattr(g, "ToProtoType") else geosOther2.append(g)
			geosNot3D.append(geosNot3d2)
			geosOther.append(geosOther2)
		else:
			if hasattr(geo2, "Volume"):
				if geo2.Volume > 0:
					if asDynamoGeo:
							geos2.append(geo2.ToProtoType())
					else:
						geos2.append(geo2)
				else:
					geosNot3d.append(geo2)
			else:
				geosOther.append(geo2.ToProtoType()) if hasattr(geo2, "ToProtoType") else geosOther2.append(geo2)

	#geos = geos2 if geos2 else geo1 
	geos = geos2[0] if len(geos2) == 1 else geos2

	if only3D:
		return geos
	else:
		return (geos, geosNot3D, geosOther)

def getDynamoGeometry(inElement, *args, **kwargs):
	"""
		get dynamo geometry from revit element

		inElement: type: DB.Element
		kwargs['only3D'] type: bool - returns only solid objects if true, else returns also 2D geometry as tuple(geos, geosNot3D, geosOther), default = True
		kwargs['united'] type: bool - returns united solid of all solids in element if True, else returns separated geometry, default = True
		Returns: list[Autodesk.DesignScript.Geometry.Solid, ...] if only3D == True, else returns 
					tuple(list[Autodesk.DesignScript.Geometry.Solid] - all 3D solids,
						  list[Autodesk.DesignScript.Geometry.Solid] - Solids with zero Volume, 
						  list[Autodesk.DesignScript.Geometry...], other geometry)
		"""
	only3D = kwargs['only3D'] if 'only3D' in kwargs else True
	united = kwargs['united'] if 'united' in kwargs else True
	gopt = DB.Options()	
	element = _UnwrapElement(inElement)		
	geo1 = element.get_Geometry(gopt)
	enum1 = geo1.GetEnumerator()
	geos = []
	geosNot3D = []
	geosOther = []
	unitedSolid = None
	first = True
	while enum1.MoveNext():
		geos2 = []
		if hasattr(enum1.Current, "GetInstanceGeometry"):
			geo2 = enum1.Current.GetInstanceGeometry()
		else:
			geo2 = enum1.Current
		geosNot3d2 = []
		geosOther2 = []
		if ListUtils.isIterable(geo2):
			for i, g in enumerate(geo2):
				if hasattr(g, "Volume"):
					if g.Volume > 0:
						solid = g.Convert()
						if united:
							if first:
								unitedSolid = solid
								first = False
							else:
								try:
									unitedSolid = DSGeometry.Solid.Union(unitedSolid, solid)
								except Exception as ex:
									pass
									#Errors.catch(ex, "Unable to make union of solids in element {0} of geometry object {1}".format(inElement.Id.IntegerValue, i))
						else:
							geos2.append(solid)
					else:
						geosNot3d2.append(g)
				else:
					geosOther2.append(g.ToProtoType()) if hasattr(g, "ToProtoType") else geosOther2.append(g)
		else:
			if hasattr(geo2, "Volume"):
				if geo2.Volume > 0:
					solid = geo2.Convert()
					if united:
						if first:
							unitedSolid = solid
							first = False
						else:
							try:
								unitedSolid = DSGeometry.Solid.Union(unitedSolid, solid)
							except Exception as ex:
								pass
								#Errors.catch(ex, "Unable to make union of solids in element {0} of geometry object {1}".format(inElement.Id.IntegerValue, i))
					else:
						geos2.append(solid)
				else:
					geosNot3d2.append(geo2)
			else:
				geosOther2.append(geo2.ToProtoType()) if hasattr(geo2, "ToProtoType") else geosOther2.append(geo2)
		geos = geos2[0] if len(geos2) == 1 else geos2
		#geos.append(geos2) if united == False else geos.append(unitedSolid)
		geosNot3D.append(geosNot3d2)
		geosOther.append(geosOther2)
	if only3D:
		return geos
	else:
		return (geos, geosNot3D, geosOther)

def get_BoundingBox():
	pass
def convertGeometryInstance(inRevitGeo, elementlist):
	"""returns converted geometry of DB.GeometryInstance

		args:
			inRevitGeo: DB.GeometryInstance
			elementList: empty list - type list

		return: list[DB.GeometryElement, ...]
		"""
	
	for g in inRevitGeo:
		if str(g.GetType()) == 'DB.GeometryInstance':
			elementlist = convertGeometryInstance(g.GetInstanceGeometry(), elementlist)
		else:
			try: 
				if g.Volume != 0:
					elementlist.append(g)
			except:
				pass
	return elementlist

def getElementAndCategory(inSelection):
	try:
		if isinstance(inSelection, list):
			returnCategories = []
			returnElements = []
			for el in inSelection:
				elementCategory = el.Category.Name
				if elementCategory not in returnCategories:
					returnCategories.append(elementCategory)
					returnElements.append(el)
			returnTuple = (tuple(returnElements), tuple(returnCategories))
		elif type(inSelection) == DB.Element:
			returnCategories = []
			returnElements = []
			for el in inSelection:
				elementCategory = el.Category.Name
				if elementCategory not in returnCategories:
					returnCategories.append(elementCategory)
					returnElements.append(el)
			returnTuple = (tuple(returnElements), tuple(returnCategories))
		else:
			raise ValueError("inSelection is not of type list[DB.Element] or DB.Element")
	except Exception as ex:
		Errors.catch(ex, "Error in RevitSelection.getElementAndCategory()")
		returnTuple = []
	return returnTuple

def getParametersByCategories(inTuple):
	returnParameters = []
	for el in inTuple[0]:
		param_set = el.GetOrderedParameters()
		for param in list(param_set):
			paramName = param.Definition.Name
			if paramName not in returnParameters:
				returnParameters.append(paramName)
	listSorted = sorted(returnParameters)
	return tuple(listSorted)

def getMaterialParameters(inItem):
	returnParameters = []
	try:
		if type(inItem) == DB.Material:
			param_set = inItem.GetOrderedParameters()
			elementProperty = dir(inItem.Parameter.PropertyType.Definition.PropertyType)
			for param in list(param_set):
				paramName = param.Definition.Name
				if paramName not in returnParameters:
					returnParameters.append("ParameterGroup: {0} Name: {1} \n ParameterType {2}".format(param.Definition.ParameterGroup, paramName, param.Definition.ParameterType))
			listSorted = sorted(returnParameters)
			return (returnParameters, elementProperty)
		else:
			raise ValueError("inItem is not of type DB.Material")
	except Exception as ex:
		Errors.catch(ex, "Error in RevitSelection.getMaterialParameters()")
		return []

def findPairsRecursive(inOpeningFills, inSolids):
	results = []
	if len(inOpeningFills) > 0:
		for i, o in enumerate(inOpeningFills):
			if o.__class__.__name__ == "Solid":
				for j, s in enumerate(inSolids):
					if o.DoesIntersect(s):
						#pairOpeningsIndex = pairOpenings.index(o)
						#results.append("pairOpeningIndex_{4}>({2}){0}~({3}){1}".format(o.name, s.name, i, j,  pairOpeningsIndex))
						iOpeningFill = inOpeningFills.pop(i)
						iSolid = inSolids.pop(j)
						returnPair = findPairsRecursive(inOpeningFills, inSolids)
						return [(iOpeningFill, iSolid)] + returnPair if returnPair != None else [(iOpeningFill, iSolid)]

def findPairs(inOpeningFills, inSolids):
	results = []
	for i, o in enumerate(inOpeningFills):
		for j, s in enumerate(inSolids):
			if doesIntersect(o, s):
				pairOpeningsIndex = pairOpenings.index(o)
				results.append("pairOpeningIndex_{4}>({2}){0}~({3}){1}".format(o.name, s.name, i, j,  pairOpeningsIndex))
				break
	return results

def getFamilyInstancesByName(doc, inName):
	#familySymbolFilter = DB.FamilySymbolFilter()
	familyClassFilter = DB.ElementClassFilter(DB.Family)
	allElements = DB.FilteredElementCollector(doc)
	allElements.WherePasses(DB.LogicalOrFilter(DB.ElementIsElementTypeFilter(False), DB.ElementIsElementTypeFilter(True)))
	allElements.WherePasses(familyClassFilter)
	allElements.WhereElementIsNotElementType()
	elementIds = None
	for i, el in enumerate(list(allElements)):
		if el.Name == inName:
			elementIds = el.GetFamilySymbolIds()
	returnElements = []
	for elId in elementIds:
		familyInstances = DB.FilteredElementCollector(doc) \
							.WherePasses(DB.FamilyInstanceFilter(doc, elId)) \
							.ToElements()
		el = doc.GetElement(elId)
		returnElements += (list(familyInstances))
	
	return returnElements

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
					#raise RuntimeError("parameter {0} not in {1}".format(inName, el.Id.IntegerValue))
					returnValues = None
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
					#raise RuntimeError("parameter {0} not in {1}".format(typeElement.Name, el.Id.IntegerValue))
					returnValues = None

			""" parameters = el.GetOrderedParameters()
			
			for parameter in parameters:
				#print(" parameter {0}".format(parameter.Definition.Name))
				if parameter.Definition.Name == inName:

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
					if not firstTime:
						break					
				if firstTime:
					if parameter.Definition.Name not in allParametersNames:
						allParametersNames.append("{}".format(parameter.Definition.Name))
			
		if not parameterFound:
			raise NameError("Parameter name {0} not found in element {1}".format(inName, el.Id.IntegerValue))
		firstTime = False """
	if info:
		return returnValuesAsString
	elif allParametersInfo:
		return allParametersNames
	else:
		return returnValues

def setValuesByParameterName(inElements, inValues, inName, *args, **kwargs):
	"""
		set parameter value from element by parameter name
		must be in Transaction block

		args:
		inElement type: list(DB.Element,...)
		inValues type: list(DB.Element or str, or int, or float...)
		inName: type: string

	"""
	bip = getBuiltInParameterInstance(inName)
	returnValues = []
	#firstTime = True
	try:
		# TransactionManager.Instance.EnsureInTransaction(doc)
		# trans = SubTransaction(doc)
		# trans.Start()
		for i, el in enumerate(inElements):
			parameterFound = False
			if bip:
				parameterFound = True
				param_ID = DB.ElementId(bip)
				parameterVP = DB.ParameterValueProvider(param_ID)
				if parameterVP.IsDoubleValueSupported(el):
					if type(inValues[i]) == float:
						returnValues.append("parameter {0} as DoubleValue of element {1} has been set to {2}".format(inName, el.Id.IntegerValue, inValues[i]))
						myParam = el.Parameter[bip].Set(inValues[i])
					else: 
						raise TypeError("Wrong format of input value {0} of type {1}. It must be of type int or float".format(inValues[i], type(inValues[i])))
				if parameterVP.IsIntegerValueSupported(el):
					if type(inValues[i]) == int:
						myParam = el.Parameter[bip].Set(inValues[i])
						turnValues.append("parameter {0} as IntegerValue of element {1} has been set to {2}".format(inName, el.Id.IntegerValue, inValues[i]))
					else: 
						raise TypeError("Wrong format of input value {0} of type {1}. It must be of type int".format(inValues[i], type(inValues[i])))
				if parameterVP.IsStringValueSupported(el):
					if type(inValues[i]) == str:
						#paramElementId = parameterVP.Parameter
						#paramElement = doc.GetElement(paramElementId)
						myParam = el.Parameter[bip].Set(inValues[i])
						returnValues.append("parameter {0} as StringValue of element {1} has been set to {2}".format(inName, el.Id.IntegerValue, inValues[i]))
					else: 
						raise TypeError("Wrong format of input value {0} of type {1}. It must be of type str".format(inValues[i], type(inValues[i])))
				if parameterVP.IsElementIdValueSupported(el):
					if type(inValues[i]) == DB.ElementId:
						myParam = el.Parameter[bip].Set(inValues[i])
						returnValues.append("parameter {0} as ElementIdValue of element {1} has been set to {2}".format(inName, el.Id.IntegerValue, inValues[i]))
					else: 
						raise TypeError("Wrong format of input value {0} of type {1}. It must be of type ElementId".format(inValues[i], type(inValues[i])))
			
			else:
				if el.GetTypeId().IntegerValue > -1:
					typeElement = doc.GetElement(el.GetTypeId())
					parameter = typeElement.LookupParameter(inName)
					if parameter:
						if parameter.StorageType == DB.StorageType.Double:
							returnValues.append(setParameterAsDouble(el, parameter, inValues[i]))
						if parameter.StorageType == DB.StorageType.Integer:
							returnValues.append(setParameterAsInteger(el, parameter, inValues[i]))
						if parameter.StorageType == DB.StorageType.String:
							returnValues.append(setParameterAsString(el, parameter, inValues[i]))
						if parameter.StorageType == DB.StorageType.ElementId:
							returnValues.append(setParamAsElementId(el, parameter, inValues[i]))
						parameterFound = True
					
					else:
						elparameter = el.LookupParameter(inName)
						if elparameter:
						# parameters = el.GetOrderedParameters()
						# for parameter in parameters:
							# if parameter.Definition.Name == inName:
							if elparameter.StorageType == DB.StorageType.Double:
								returnValues.append(setParameterAsDouble(el, elparameter, inValues[i]))
							if elparameter.StorageType == DB.StorageType.Integer:
								returnValues.append(setParameterAsInteger(el, elparameter, inValues[i]))
							if elparameter.StorageType == DB.StorageType.String:
								returnValues.append(setParameterAsString(el, elparameter, inValues[i]))
							if elparameter.StorageType == DB.StorageType.ElementId:
								returnValues.append(setParamAsElementId(el, elparameter, inValues[i]))
							parameterFound = True
								# if not firstTime:
								# 	break					

			if not parameterFound:
				raise NameError("Parameter name {0} not found in element {1}".format(inName, el.Id.IntegerValue))
			#firstTime = False
		else:
			return returnValues

	except:
		
		import traceback
		errorReport = traceback.format_exc()
		raise RuntimeError("Parameter name {0} not set !!! {1}".format(inName, errorReport))
		# trans.RollBack()
		# TransactionManager.Instance.TransactionTaskDone()

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

def getBuiltInParameterInstance(inBuiltInParamName):
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
	return returnVar

def filterElementsByActiveViewIds(doc, inElements, **kwargs):
	"""
		Filter elements by active view parameters (active view phase, category...)

		inElements> list[DB.Element]
		kwargs["rawOpening"] including wall elements of opening (raw openings geometry) type: bool
		kwargs["toElement"] type: bool
		kwargs["disablePhases"] type: bool select all elements independently on all phases, default = False
		kwargs["onlyInActiveView"] tyep bool, select all elements independently on activeView, default = False
		Returns: list[DB.ElementId] if kwargs["toElement"] == False or list[DB.Element] if kwargs["toElement"] == True 
	"""
	

	if "rawOpening" in kwargs and kwargs["rawOpening"] == True:
		includeCategories = [DB.BuiltInCategory.OST_Walls]
		includeClasses = []
	else:
		includeCategories = [DB.BuiltInCategory.OST_Doors, DB.BuiltInCategory.OST_Windows]
		includeClasses = [DB.Opening]

	toElement = kwargs["toElement"] if "toElement" in kwargs else False
	disablePhases = kwargs["disablePhases"] if "disablePhases" in kwargs else False
	onlyInActiveView = kwargs["onlyInActiveView"] if "onlyInActiveView" in kwargs else False
	

	ids = [x.Id for x in inElements]
	#colectionOfUniqueInsertIds = Clist[DB.ElementId](uIs)
	colectionOfElementsIds = Clist[DB.ElementId](ids)

	# Get ActiveView phase ID
	paramId = DB.ElementId(DB.BuiltInParameter.VIEW_PHASE)
	param_provider = DB.ParameterValueProvider(paramId)
	activeViewPhaseId = param_provider.GetElementIdValue(doc.ActiveView)
	docPhases =  DB.FilteredElementCollector(doc) \
								.OfCategory(DB.BuiltInCategory.OST_Phases) \
								.WhereElementIsNotElementType() \
								.ToElements()

	#Filter inserts visible only in active view and of Existing phase status - (ignore demolished elements in previous phases) 
	myElementPhaseStatusFilter1 = DB.ElementPhaseStatusFilter(activeViewPhaseId, DB.ElementOnPhaseStatus.Existing, False)
	myElementPhaseStatusFilter2 = DB.ElementPhaseStatusFilter(activeViewPhaseId, DB.ElementOnPhaseStatus.New,False)

	includeCategoryFilters = [DB.ElementCategoryFilter(x) for x in includeCategories]
	includeClassesFilters = [DB.ElementClassFilter(x) for x in includeClasses]
	categoryAndClassFilters = includeCategoryFilters + includeClassesFilters
	
	if not disablePhases:
		if len(colectionOfElementsIds) > 0:
			if toElement == True:
				if onlyInActiveView:
					filteredElementsByActiveViewIds = DB.FilteredElementCollector(doc, colectionOfElementsIds) \
																				.WherePasses(SelectableInViewFilter(doc, doc.ActiveView.Id)) \
																				.WherePasses(DB.LogicalOrFilter(myElementPhaseStatusFilter1 \
																											,myElementPhaseStatusFilter2)) \
																				.WhereElementIsNotElementType() \
																				.ToElements()
				else:
					filteredElementsByActiveViewIds = DB.FilteredElementCollector(doc, colectionOfElementsIds) \
																				.WherePasses(DB.LogicalOrFilter(myElementPhaseStatusFilter1 \
																											,myElementPhaseStatusFilter2)) \
																				.WhereElementIsNotElementType() \
																				.ToElements()
			else:
				if onlyInActiveView:
					filteredElementsByActiveViewIds = DB.FilteredElementCollector(doc, colectionOfElementsIds) \
																				.WherePasses(SelectableInViewFilter(doc, doc.ActiveView.Id)) \
																				.WherePasses(DB.LogicalOrFilter(myElementPhaseStatusFilter1 \
																											,myElementPhaseStatusFilter2)) \
																				.WhereElementIsNotElementType() \
																				.ToElementIds()
				else:
					filteredElementsByActiveViewIds = DB.FilteredElementCollector(doc, colectionOfElementsIds) \
																				.WherePasses(DB.LogicalOrFilter(myElementPhaseStatusFilter1 \
																											,myElementPhaseStatusFilter2)) \
																				.WhereElementIsNotElementType() \
																				.ToElementIds()
		else:
			filteredElementsByActiveViewIds = []
	else:
		if len(colectionOfElementsIds) > 0:
			if toElement == True:
				if onlyInActiveView:
					filteredElementsByActiveViewIds = DB.FilteredElementCollector(doc, colectionOfElementsIds) \
																				.WherePasses(SelectableInViewFilter(doc, doc.ActiveView.Id)) \
																				.WhereElementIsNotElementType() \
																				.ToElements()
				else:
					filteredElementsByActiveViewIds = DB.FilteredElementCollector(doc, colectionOfElementsIds) \
																				.WhereElementIsNotElementType() \
																				.ToElements()

			else:
				if onlyInActiveView:
					filteredElementsByActiveViewIds = DB.FilteredElementCollector(doc, colectionOfElementsIds) \
																				.WherePasses(SelectableInViewFilter(doc, doc.ActiveView.Id)) \
																				.WhereElementIsNotElementType() \
																				.ToElementIds()
				else:
					filteredElementsByActiveViewIds = DB.FilteredElementCollector(doc, colectionOfElementsIds) \
																				.WhereElementIsNotElementType() \
																				.ToElementIds()
		else:
			filteredElementsByActiveViewIds = []
	return filteredElementsByActiveViewIds
