# -*- coding: utf-8 -*-
# Copyright(c) 2019, Daniel Gercak
#Script for selecting and grouping elements by levels and other parameters for dynamo 
#resource_path: C:\_WORK\PYTHON\REVIT_API\Group_geometry_node.py

import sys
#import traceback
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
lib_path = r'C:\_WORK\PYTHON\REVIT_API\LIB'
sys.path.append(pyt_path)
sys.path.append(lib_path)

from itertools import chain, groupby
from RevitSelection import *
import RevitSelection as RevitSelection
from ListUtils import *
import ListUtils as ListUtils
from Errors import *

import clr
# Import Element wrapper extension methods
clr.AddReference("RevitNodes")
import Revit
clr.ImportExtensions(Revit.Elements)
# Import geometry conversion extension methods
clr.ImportExtensions(Revit.GeometryConversion)

# Import DocumentManager and TransactionManager
clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
doc = DocumentManager.Instance.CurrentDBDocument

clr.AddReference("System")
from System.Collections.Generic import List as Clist

# Import RevitAPI
clr.AddReference("RevitAPI")
import Autodesk
import Autodesk.Revit.DB
#import Autodesk.Revit.DB as DB

clr.AddReference('RevitAPIUI')
from Autodesk.Revit.UI.Selection import *

#clr.AddReference('DSCoreNodes')
#from DSCore import List, Solid

clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *

#Revit to dynamo model
class RTD_model(object):
	"""
		Revit To Dynamo geometry
		acquire dynamo geometry as Solid from Revit.DB.Element objects
		include methods for selecting elements according to class name or BuiltInCategory
		
		inDoc:	CurrentDBDocument type: DocumentManager.Instance.CurrentDBDocument
		*args[0]: excludeElements type: list[Revit.DB.Element, ...] elements supposed to be excluded from selection
		*kwargs: inc_invis type: bool - sets the option property "IncludeNonVisibleObjects" 
										used in Autodesk.Revit.DB.Element.Geometry[Autodesk.Revit.DB.Options().IncludeNonVisibleObjects]
				 incopenings type: bool
				 incshadows type: bool
				 incwalls type: bool
				 incshared type: bool sets the option property for
				 					Autodesk.Revit.DB.Element.FindInserts(incopenings,incshadows,incwalls,incshared)
		Returns: 
	"""
	# roof class names
	roofCNs = [Autodesk.Revit.DB.ExtrusionRoof, Autodesk.Revit.DB.FootPrintRoof]
	# floor class names
	floorCNs = [Autodesk.Revit.DB.Floor, Autodesk.Revit.DB.HostedSweep]
	# wall class names
	wallCNs = [Autodesk.Revit.DB.Wall, Autodesk.Revit.DB.CurtainSystem]
	# column categories 
	columnCgs = [Autodesk.Revit.DB.BuiltInCategory.OST_Columns, Autodesk.Revit.DB.BuiltInCategory.OST_StructuralColumns]
	# structural frame categories 
	structFrameCgs = [Autodesk.Revit.DB.BuiltInCategory.OST_StructuralFraming]
	# curtain system categories 
	curtainSystemCgs = [Autodesk.Revit.DB.BuiltInCategory.OST_Curtain_Systems]

	def __init__(self, inDoc, *args, **kwargs):
		self.setup(inDoc, *args, **kwargs)

	def setup(self, inDoc, *args, **kwargs):
		"""
			instance parameter setup
		"""

		self.doc = inDoc
		if "inc_invis" in kwargs:
			self.inc_invis = kwargs["inc_invis"]
		else:
			self.inc_invis = False #default True
		if "incopenings" in kwargs:
			self.incopenings = kwargs["incopenings"]
		else:
			self.incopenings = True #default True
		if "incshadows" in kwargs:
			self.incshadows = kwargs["incshadows"]
		else:
			self.incshadows = False #default True
		if "incwalls" in kwargs:
			self.incwalls = kwargs["incwalls"]
		else:
			self.incwalls = True #default True
		if "incshared" in kwargs:
			self.incshared = kwargs["incshared"]
		else:
			self.incshared = True #default True
		if args > 0:
			if isinstance(args[0], list):
				#excludeElements = processList(Unwrap, IN[0])
				self.excludeElements = args[0]
			else:
				#excludeElements = [Unwrap(IN[0])]
				self.excludeElements = [args[0]]
		else:
			self.excludeElements = []
		myElementIds = []
		if self.excludeElements != None or self.excludeElements != []:
			#excludeElementIds = []			
			for x in self.excludeElements:
				myId = x.Id
				#when elements not unwrapped
				myElementId = Autodesk.Revit.DB.ElementId(myId)
				myElementIds.append(myElementId)

			self.exclude_element_collection = Clist[Autodesk.Revit.DB.ElementId](myElementIds)
		else:
			self.exclude_element_collection = Clist([])	

		"""
			levelIds setup
		"""

		self.allLevels = getLevels()
		self.levelIds = getLevelIds(self.allLevels)

	def getUnwrappedElements(self):
		try:
			self.elements = [RevitSelection.getElementByClassName(RTD_model.roofCNs, self.exclude_element_collection), \
					RevitSelection.getElementByClassName(RTD_model.floorCNs, self.exclude_element_collection), \
					RevitSelection.getElementByClassName(RTD_model.wallCNs, self.exclude_element_collection), \
					RevitSelection.getElementByCategory(RTD_model.columnCgs, self.exclude_element_collection), \
					RevitSelection.getElementByCategory(RTD_model.structFrameCgs, self.exclude_element_collection), \
					RevitSelection.getElementByCategory(RTD_model.curtainSystemCgs, self.exclude_element_collection)]
			return ListUtils.processList(Unwrap, self.elements)

		except Exception as ex:
			# if error accurs anywhere in the process catch it
			Errors.catch(ex, "Selecting self.elements in RTD_model.getUnwrappedElements() failed")
			return []

	def getModelOfOneSolidByUnion(self, removeInserts):
		"""
		get dynamo model of united solids from current Revit document

		arg: removeInserts type: bool - if True, it removes inserts from revit geometry in order to acquire clean geometry without holes
		
		Returns: Autodesk.DesignScript.Geometry.Solid
		"""
		model = self.getModel(removeInserts)
		flattenModel = ListUtils.flatList(model)
		try:
			unitedSolid = Autodesk.DesignScript.Geometry.Solid.ByUnion(flattenModel)
		except Exception as ex:
			Errors.catch(ex, "Solid.ByUnion in RTD_model.getModelOfOneSolidByUnion() failed")
			unitedSolid = []
		return unitedSolid
	
	def getOpeningsGeometry(self):
		"""
		get dynamo geometry of raw openings without filling from current Revit document

		no args
		
		Returns: Autodesk.DesignScript.Geometry.Solid
		"""
		modelWithOpenings = self.getModel(False)
		modelWithOpeningsOneSolid = Autodesk.DesignScript.Geometry.Solid.ByUnion(ListUtils.flatList(modelWithOpenings))		
		modelWithoutOpenings = self.getModel(True)
		modelWithoutOpeningsOneSolid = Autodesk.DesignScript.Geometry.Solid.ByUnion(ListUtils.flatList(modelWithoutOpenings))		
		try:
			differenceGeometry = modelWithoutOpeningsOneSolid.Difference(modelWithOpeningsOneSolid)
		except Exception as ex:
			Errors.catch(ex, "Solid.Difference in RTD_model.getOpeningsGeometry() failed")
			differenceGeometry = []
		return differenceGeometry
	
	def getModel(self, removeInserts):
		"""
		get dynamo solids from current Revit document

		arg: removeInserts type: bool - if True, it removes inserts from revit geometry in order to acquire clean geometry without holes
		
		Returns: List[Autodesk.DesignScript.Geometry.Solid]
		"""
		self.unwrappedElements = self.getUnwrappedElements()
		try:
			inserts = ListUtils.flatList(ListUtils.processList(RevitSelection.getInserts, self.unwrappedElements))			
		except Exception as ex:
			# if error accurs anywhere in the process catch it
			Errors.catch(ex, "Getting inserts RTD_model.getModel() failed.")
			inserts = []		
		# try:
		# 	uniqueInserts = self.getUniqueElements(inserts)
		# except Exception as ex:
		# 	# if error accurs anywhere in the process catch it
		# 	Errors.catch(ex, "Getting unique inserts in RTD_model.getModel() failed.")
		# 	uniqueInserts = []

		#uIs = [x.Id for x in uniqueInserts]
		uIs = [x.Id for x in inserts]
		#colectionOfUniqueInsertIds = Clist[Autodesk.Revit.DB.ElementId](uIs)
		colectionOfInsertIds = Clist[Autodesk.Revit.DB.ElementId](uIs)
		# Get ActiveView phase ID
		paramId = Autodesk.Revit.DB.ElementId(Autodesk.Revit.DB.BuiltInParameter.VIEW_PHASE)
		param_provider = Autodesk.Revit.DB.ParameterValueProvider(paramId)
		activeViewPhaseId = param_provider.GetElementIdValue(self.doc.ActiveView)
		docPhases =  Autodesk.Revit.DB.FilteredElementCollector(self.doc) \
									.OfCategory(Autodesk.Revit.DB.BuiltInCategory.OST_Phases) \
									.WhereElementIsNotElementType() \
									.ToElements()
		# docPhaseNames = [x.Name for x in docPhases]

		#Filter inserts visible only in active view and of Existing phase status - (ignore demolished elements in previous phases) 
		myElementPhaseStatusFilter1 = Autodesk.Revit.DB.ElementPhaseStatusFilter(activeViewPhaseId, Autodesk.Revit.DB.ElementOnPhaseStatus.Existing, False)
		myElementPhaseStatusFilter2 = Autodesk.Revit.DB.ElementPhaseStatusFilter(activeViewPhaseId, Autodesk.Revit.DB.ElementOnPhaseStatus.New,False)
		includeCategories = [Autodesk.Revit.DB.BuiltInCategory.OST_Doors, Autodesk.Revit.DB.BuiltInCategory.OST_Windows]
		includeClasses = [DB.Opening]

		includeCategoryFilters = [Autodesk.Revit.DB.ElementCategoryFilter(x) for x in includeCategories]
		includeClassesFilters = [Autodesk.Revit.DB.ElementClassFilter(x) for x in includeClasses]
		categoryAndClassFilters = includeCategoryFilters + includeClassesFilters

		#if len(colectionOfUniqueInsertIds) > 0:
		if len(colectionOfInsertIds) > 0:
			filteredInsertsByActiveViewIds = Autodesk.Revit.DB.FilteredElementCollector(self.doc, colectionOfInsertIds) \
																		.WherePasses(Autodesk.Revit.DB.LogicalOrFilter(categoryAndClassFilters)) \
																		.WherePasses(SelectableInViewFilter(self.doc, self.doc.ActiveView.Id)) \
																		.WherePasses(Autodesk.Revit.DB.LogicalOrFilter(myElementPhaseStatusFilter1 \
																									,myElementPhaseStatusFilter2)) \
																		.ToElementIds()
		else:
			filteredInsertsByActiveViewIds = []
		
		try:
			pass
			self.mySolids = self.getDynamoSolids(self.unwrappedElements, filteredInsertsByActiveViewIds, removeInserts)
			#myTestSolids = getDynamoSolids(unWrapedTestElements, filteredInsertsByActiveViewIds, True)
		except Exception as ex:
			Errors.catch(ex, "getDynamoSolids in RTD_model.getModel() failed")
			self.mySolids = []
		return self.mySolids

	# def getUniqueElements(self, items):
	# 	"""
	# 	acquire only unique elements filtered by Element.Id

	# 	arg: List[Autodesk.Revit.DB.Element]
		
	# 	Returns: List[Autodesk.Revit.DB.Element]
	# 	"""
	# 	try:
	# 		#make list of unique elements by filtering inserts list 
	# 		# first 3 * flatten 
	# 		flattenInserts = ListUtils.flatList(items)
	# 		if len(flattenInserts) > 0:
	# 			#sort by ID
	# 			myIds = zip(map(lambda x: x.Id, flattenInserts), flattenInserts)
	# 			myIds.sort(key = lambda a: a[0])
	# 			#make groups of same ids
	# 			myGroupedIds = []
	# 			for k, g in groupby(myIds, lambda a: a[0]):
	# 				myGroupedIds.append(list(g))
	# 			#map grupped items by notMoreThanOne function - if item is list of more than one element with same Id, get only first element 
	# 			uniqueInsertIds = map(lambda x: x[0] if ListUtils.notMoreThanOne(x) else x[0], myGroupedIds)
	# 			#unzip tuple
	# 			stringIds, returnInserts = zip(*uniqueInsertIds)
	# 			return returnInserts
	# 		return flattenInserts
	# 		else:
	# 			return []
	# 	except Exception as ex:
	# 		Errors.catch(ex, "Creating unique element list in RTD_model.getUniqueElements() failed.")
	# 		return []

	def getDynamoSolids(self, unWrappedElements, *args):
		"""
			acquire dynamo geometry as structured List 
			Element must be unwrapped - use Unwrap() function to each item before input as List
			Optional argument is list of inserts to exclude from final geometry (e.g. windows, doors... )

			arg: unWrappedElements type: List[Autodesk.Revit.DB.Element]
			
			args[0]: element Ids of filtered inserts by active view and phase filter - type: List[Autodesk.Revit.DB.ElementId]
			args[1]: remove_inserts - type: boolean

			Returns: Structured list of Autodesk.DesignScript.Geometry.Solid. See getDynamoSolid()
		"""
		detail_lvl = Autodesk.Revit.DB.ViewDetailLevel.Coarse
		#include invisible objects
		inc_invis = False
		view = self.doc.ActiveView
		if len(args) > 1:
			remove_inserts = args[1]
		else:
			remove_inserts = False
		if len(args) > 0:
			uniqueInsertIds = args[0]
		else:
			uniqueInsertIds = []
		TransactionManager.Instance.EnsureInTransaction(self.doc)
		trans = Autodesk.Revit.DB.SubTransaction(self.doc)
		trans.Start()
		myIsValidObject = []  
		if remove_inserts == True and len(uniqueInsertIds) > 0:								
			try:				
				self.doc.Delete(uniqueInsertIds)
				#t.Commit()
				self.doc.Regenerate()
			except Exception as ex:
				trans.RollBack()
				#myIsValidObject.append((insert.IsValidObject, insert.Id))
				# if error accurs anywhere in the process catch it
				Errors.catch(ex, "Deleting inserts in RTD_model.getModel().getDynamoSolid() failed.")
			
			geo_options = Autodesk.Revit.DB.Options()
			if view == None: geo_options.DetailLevel = detail_lvl
			geo_options.IncludeNonVisibleObjects = inc_invis
			if view != None: geo_options.View = view
			try:	
				returnSolids = ListUtils.processList(self.getDynamoSolid,unWrappedElements, geo_options)
			except Exception as ex:
				Errors.catch(ex, "Exception in RTD_model.getDynamoSolids() - \
					returnSolids = ListUtils.processList(self.getDynamoSolid,unWrappedElements, geo_options) failed.")
				return []

			trans.RollBack()
			TransactionManager.Instance.TransactionTaskDone()
			return returnSolids
		else:
			geo_options = Autodesk.Revit.DB.Options()
			if view == None: geo_options.DetailLevel = detail_lvl
			geo_options.IncludeNonVisibleObjects = inc_invis
			if view != None: geo_options.View = view
			try:	
				returnSolids = ListUtils.processList(self.getDynamoSolid,unWrappedElements, geo_options)
				return returnSolids
			except Exception as ex:
				Errors.catch(ex, "Exception in else block of (if remove_inserts == True and len(uniqueInsertIds) \
								in ListUtils.processList(getDynamoSolid,unWrappedElements, geo_options) in RTD_model.getDynamoSolids() failed.")
				return []
	
	def getDynamoSolid(self, item, *args):
		"""
			acquire dynamo geometry as Solid from Revit.DB.Element object
			Element must be unwrapped - use Unwrap() function before input as item

			arg: item type: Autodesk.Revit.DB.Element object
			
			*args[0]: Geometry options type: Autodesk.Revit.DB.Options

			Returns: dynamoGeometry type: Autodesk.DesignScript.Geometry.Solid

		"""

		if type(item) !=list:
			revitGeo = item.Geometry[args[0]]
			try:		
				revit_geos = convertGeometryInstance(revitGeo, list())
			except Exception as ex:
				Errors.catch(ex, "convertGeometryInstance in RTD_model.getDynamoSolid() failed.")

		#errorReport.append("length of revit_geos list: {}".format(len(revit_geos)))
		try:
			if len(revit_geos) != 0:
				revit_geo = revit_geos[0]
			else:		
				revit_geo = None
				raise TypeError("Variable revit_geos is unassigned or is list. For next process is variable of type GeometryElement necessary.")
		except Exception as ex:
			Errors.catch(ex)

		dynamoGeometry = revit_geo.ToProtoType()
	# 	try:
	# 		if isinstance(revit_geo.ToProtoType(),Solid):
	# #				surfaces = PolySurface.Surfaces(PolySurface.BySolid(dynamoGeometry))
	# 			dyn_geos = dynamoGeometry
	# 	except Exception as ex:
	# 		Errors.catch(ex, "Creating surfaces in getDynamoSolid() failed.")

		return dynamoGeometry

class EnAnalyse(object):
	def __init__(self, inDoc, *args):
		self.model = RTD_model(inDoc, *args)		
		self.setup()
	
	def setup(self):
		self.dynamoSolids = self.model.getModel(True)
		flattenedSolids = ListUtils.flatList(self.dynamoSolids)
		#drop out unassigned items
		filteredFlattenedSolids = filter(lambda x: x!=None, flattenedSolids)
		#make solid union of all solids representing element geometry and extract inner and outer shells from this union
		unitedSolid = Autodesk.DesignScript.Geometry.Solid.ByUnion(filteredFlattenedSolids)
		polySurfaces = Autodesk.DesignScript.Geometry.PolySurface.BySolid(unitedSolid)
		extractedSolids = list(Autodesk.DesignScript.Geometry.PolySurface.ExtractSolids(polySurfaces))

		groupedSolids = self.groupSolids(extractedSolids)
		outerShells = self.getOuterShells(groupedSolids)
		self.outerShellIntersectingElements = self.getOuterShellIntersectingElements(outerShells, self.dynamoSolids, self.model.unwrappedElements)
	
	def groupSolids(self, inList, inLevel = 0):
		"""
			Groups dynamo solids with enclosed geometry to objects with outer solid and inner solids
			representing the building outer shell and room volumes

			arg: inList type: List[Autodesk.DesignScript.Geometry.Solid]
				inLevel type Int : default = 0 (Recursive increment counter) 

			Returns: List[List[Autodesk.DesignScript.Geometry.Solid, ...], ...]
				Grouped list of solids. First item of solid group is outer solid representing
				the building outer shell surface, next elements are inner solids representing the surfaces of
				rooms
		"""
		nextLevelItems = []
		returnItems = []
		if len(inList) > 0:
			if inLevel == 0:
				inList.sort(key = lambda c : c.Volume, reverse=True)
			outerVolume = inList[0]
			otherVolumes = inList[1:]
			trueItems = filter(lambda x: outerVolume.DoesIntersect(x), otherVolumes)
			trueItems.insert(0, outerVolume)
			falseItems = filter(lambda x: not outerVolume.DoesIntersect(x), otherVolumes)
			if len(trueItems) > 0:
				returnItems = [trueItems]
				nextLevelItems = self.groupSolids(falseItems, inLevel + 1)
				#print("level {1} - nextLevelItems {0}\n".format(nextLevelItems,inLevel))    
		if returnItems != [] or nextLevelItems != None:
			#if len(nextLevelItems) == 0 and inLevel == 1:
			#	nextLevelItems.pop()
			return returnItems + nextLevelItems

	def getOuterShells(self, inGroupedSolids):
		"""
			returns 1D list of solids representing outer shell of building object.

			args:
				inGroupedSolids: list of grouped solid acquired by using function groupSolids()
				outer shells are placed at first positions in sublists of inGroupedSolids

			return: list of outer shell solids 
		"""
		returnItems = []
		for i in inGroupedSolids:
			returnItems.append(i[0])
		return returnItems
	
	def doesIntersect(self, item, *args):
		inPolysurface = args[0]
		inRemovedSurface = args[1]
		if type(item) == Autodesk.DesignScript.Geometry.Solid:
			if item.DoesIntersect(inPolysurface):
				return True
			elif item.DoesIntersect(inRemovedSurface):
				return True
			else:
				return []
		else:
			return []

	def getOuterShellIntersectingElements(self, inOuterShells, inSolids, inUnWrappedElements):
		returnList = []
		flattenedList = []
		for outerShell in inOuterShells:
			outerShellpolySurface = Autodesk.DesignScript.Geometry.PolySurface.BySolid(outerShell)
			outerShellSurfaces = list(outerShellpolySurface.Surfaces())
			outerShellSurfaces.sort(key = lambda c : c.Area, reverse=False)
			removedSurface = outerShellSurfaces[0]
			del outerShellSurfaces[0]	
			openedOuterShellPolysurface = Autodesk.DesignScript.Geometry.PolySurface.ByJoinedSurfaces(outerShellSurfaces)
			#filterMask = openedOuterShellPolysurface.DoesIntersect(inSolids)
			intersectedElements = processList(self.doesIntersect, inSolids, openedOuterShellPolysurface, removedSurface)
			returnCategories = []
			for c, category in enumerate(inSolids):
				returnItems = []
				for i, item in enumerate(category):
					myType = type(item)
					if  myType == Autodesk.DesignScript.Geometry.Solid and intersectedElements[c][i] == True:
						returnItems.append((item.Intersect(openedOuterShellPolysurface), inUnWrappedElements[c][i]))
						#flattenedList.append(item.Intersect(openedOuterShellPolysurface))
						#myflattenedList = ListUtils.flatList(flattenedList, maxLevel = 0)
					else:
						returnItems.append([])
				returnCategories.append(returnItems)
			returnList.append(returnCategories)
		return returnList


def Unwrap(item, *args):
	return UnwrapElement(item)

# def getDynamoSolid(item, *args):
# 	"""
# 		acquire dynamo geometry as Solid from Revit.DB.Element object
# 		Element must be unwrapped - use Unwrap() function before input as item

# 		arg: item type: Autodesk.Revit.DB.Element object
		
# 		*args[0]: Geometry options type: Autodesk.Revit.DB.Options

# 		Returns: dynamoGeometry type: Autodesk.DesignScript.Geometry.Solid

# 	"""

# 	if type(item) !=list:
# 		revitGeo = item.Geometry[args[0]]
# 		try:		
# 			revit_geos = convertGeometryInstance(revitGeo, list())
# 		except Exception as ex:
# 			Errors.catch(ex, "convertGeometryInstance in getDynamoSolid() failed.")

# 	#errorReport.append("length of revit_geos list: {}".format(len(revit_geos)))
# 	try:
# 		if len(revit_geos) != 0:
# 			revit_geo = revit_geos[0]
# 		else:		
# 			revit_geo = None
# 			raise TypeError("Variable revit_geos is unassigned or is list. For next process is variable of type GeometryElement necessary.")
# 	except Exception as ex:
# 		Errors.catch(ex)

# 	dynamoGeometry = revit_geo.ToProtoType()
# # 	try:
# # 		if isinstance(revit_geo.ToProtoType(),Solid):
# # #				surfaces = PolySurface.Surfaces(PolySurface.BySolid(dynamoGeometry))
# # 			dyn_geos = dynamoGeometry
# # 	except Exception as ex:
# # 		Errors.catch(ex, "Creating surfaces in getDynamoSolid() failed.")

# 	return dynamoGeometry


# def getDynamoSolids(unWrappedElements, *args):
# 	"""
# 		acquire dynamo geometry as structured List 
# 		Element must be unwrapped - use Unwrap() function to each item before input as List
# 		Optional argument is list of inserts to exclude from final geometry (e.g. windows, doors... )

# 		arg: unWrappedElements type: List[Autodesk.Revit.DB.Element]
		
# 		args[0]: element Ids of filtered inserts by active view and phase filter - type: List[Autodesk.Revit.DB.ElementId]
# 		args[1]: remove_inserts - type: boolean

# 		Returns: Structured list of tuples. See getDynamoSolid()
# 	"""
# 	detail_lvl = Autodesk.Revit.DB.ViewDetailLevel.Coarse
# 	#include invisible objects
# 	inc_invis = False
# 	view = doc.ActiveView
# 	if len(args) > 1:
# 		remove_inserts = args[1]
# 	else:
# 		remove_inserts = False
# 	if len(args) > 0:
# 		uniqueInsertIds = args[0]
# 	else:
# 		uniqueInsertIds = []
# 	TransactionManager.Instance.EnsureInTransaction(doc)
# 	trans = Autodesk.Revit.DB.SubTransaction(doc)
# 	trans.Start()
# 	myIsValidObject = []  
# 	if remove_inserts == True and len(uniqueInsertIds) > 0:								
# 		try:				
# 			doc.Delete(uniqueInsertIds)
# 			#t.Commit()
# 			doc.Regenerate()
# 		except Exception as ex:
# 			trans.RollBack()
# 			#myIsValidObject.append((insert.IsValidObject, insert.Id))
# 			# if error accurs anywhere in the process catch it
# 			Errors.catch(ex, "Deleting inserts in getDynamoSolid()failed.")
		
# 		geo_options = Autodesk.Revit.DB.Options()
# 		if view == None: geo_options.DetailLevel = detail_lvl
# 		geo_options.IncludeNonVisibleObjects = inc_invis
# 		if view != None: geo_options.View = view
# 		try:	
# 			returnSolids = processList(getDynamoSolid,unWrappedElements, geo_options)
# 		except Exception as ex:
# 			Errors.catch(ex, "Exception in remove_inserts == True and len(uniqueInsertIds) \
# 							  processList(getDynamoSolid,unWrappedElements, geo_options) in getDynamoSolids() failed.")
# 			return []

# 		trans.RollBack()
# 		TransactionManager.Instance.TransactionTaskDone()
# 		return returnSolids
# 	else:
# 		geo_options = Autodesk.Revit.DB.Options()
# 		if view == None: geo_options.DetailLevel = detail_lvl
# 		geo_options.IncludeNonVisibleObjects = inc_invis
# 		if view != None: geo_options.View = view
# 		try:	
# 			returnSolids = processList(getDynamoSolid,unWrappedElements, geo_options)
# 			return returnSolids
# 		except Exception as ex:
# 			Errors.catch(ex, "Exception in else block of (if remove_inserts == True and len(uniqueInsertIds) \
# 							  in processList(getDynamoSolid,unWrappedElements, geo_options) in getDynamoSolids() failed.")
# 			return []
	
# def groupSolids(inList, inLevel = 0):
# 	"""
# 		Groups dynamo solids with enclosed geometry to objects with outer solid and inner solids
# 		representing the building outer shell and room volumes

# 		arg: inList type: List[Autodesk.DesignScript.Geometry.Solid]
# 			 inLevel type Int : default = 0 (Recursive increment counter) 

# 		Returns: List[List[Autodesk.DesignScript.Geometry.Solid, ...], ...]
# 			Grouped list of solids. First item of solid group is outer solid representing
# 			the building outer shell surface, next elements are inner solids representing the surfaces of
# 			rooms
# 	"""
# 	nextLevelItems = []
# 	returnItems = []
# 	if len(inList) > 0:
# 		if inLevel == 0:
# 			inList.sort(key = lambda c : c.Volume, reverse=True)
# 		outerVolume = inList[0]
# 		otherVolumes = inList[1:]
# 		trueItems = filter(lambda x: outerVolume.DoesIntersect(x), otherVolumes)
# 		trueItems.insert(0, outerVolume)
# 		falseItems = filter(lambda x: not outerVolume.DoesIntersect(x), otherVolumes)
# 		if len(trueItems) > 0:
# 			returnItems = [trueItems]
# 			nextLevelItems = groupSolids(falseItems, inLevel + 1)
# 			#print("level {1} - nextLevelItems {0}\n".format(nextLevelItems,inLevel))    
# 	if returnItems != [] or nextLevelItems != None:
# 		#if len(nextLevelItems) == 0 and inLevel == 1:
# 		#	nextLevelItems.pop()
# 		return returnItems + nextLevelItems	

# def getUniqueElements(items):
# 	"""
# 		acquire only unique elements filtered by Element.Id

# 		arg: List[Autodesk.Revit.DB.Element]
		
# 		Returns: List[Autodesk.Revit.DB.Element]
# 	"""
# 	try:
# 		#make list of unique elements by filtering inserts list 
# 		# first 3 * flatten 
# 		flattenInserts = ListUtils.flatList(inserts)
# 		if len(flattenInserts) > 0:
# 			#sort by ID
# 			myIds = zip(map(lambda x: x.Id, flattenInserts), flattenInserts)
# 			myIds.sort(key = lambda a: a[0])
# 			#make groups of same ids
# 			myGroupedIds = []
# 			for k, g in groupby(myIds, lambda a: a[0]):
# 				myGroupedIds.append(list(g))
# 			#map grupped items by notMoreThanOne function - if item is list of more than one element with same Id, get only first element 
# 			uniqueInsertIds = map(lambda x: x[0] if notMoreThanOne(x) else x[0], myGroupedIds)
# 			#unzip tuple
# 			stringIds, returnInserts = zip(*uniqueInsertIds)
# 			return returnInserts
# 		else:
# 			return []
# 	except Exception as ex:
# 		Errors.catch(ex, "Creating unique element list in getUniqueElements() failed.")
# 		return []

# # def flattenList(inList, *args, **kwargs):
# #     """returns 1D list of items. flattens only list objects Tuple not List
# # 		flattens from up to deep - flattenList([1,2,[3,[4,5]]], maxLevel = 1) >>  [1, 2, 3, [4, 5]]
       
# #        args:
# #             arg_0: list of lists
# #             *args[0]: type: int - optional current level of recursion 
# #             **kwargs: maxLevel type: int -  maximum level of required flatten recursion. 
# #                                 If not set, function returns only not list items
# #                                 value 0 returns unflattened list
            
# #        return: flattened list according to maxLevel argument
# #     """
# #     levelItems = []
# #     returnItems = []
# #     myLevels = []
# #     if len(args) != 0:
# #         inLevel = args[0]
# #     else:
# #         inLevel = 0
# #     if "maxLevel" in kwargs:
# #         mLevel = kwargs["maxLevel"]-1
# #     else:
# #         mLevel = inLevel +200
# #     if type(inList) == list:
# #      for item in inList:
# #       if type(item) == list:
# #        if inLevel <= mLevel:
# #         returnItem = flattenList(item, inLevel + 1, maxLevel = mLevel)
# #        else:
# #         returnItem = [item]
# #       else:
# #        returnItem = [item]
# #       returnItems = returnItems + returnItem
# #     else:
# #      returnItems = [inList]
# #     return returnItems

# def pairIntersectingSurfacesWithSolid(inItem, *args):
# 	intersectedSurfaces = []
# 	returnSurface = []
# 	inSurfaces = args[0]
# 	if inItem != None:
# 		for surface in inSurfaces:
# 			if inItem.DoesIntersect(surface):
# 				itemPolySurface = Autodesk.DesignScript.Geometry.PolySurface.BySolid(inItem)
# 				itemSurfaces = itemPolySurface.Surfaces()
# 				for itemSurface in itemSurfaces:
# 					itemSurfPoint = itemSurface.PointAtParameter(0.0, 0.0)
# 					itemSurfNormal = itemSurface.NormalAtPoint(itemSurfPoint)
# 					surfacePoint = surface.PointAtParameter(0.0, 0.0)
# 					surfaceNormal = itemSurface.NormalAtPoint(surfacePoint)
# #					if itemSurfPoint.X == surfacePoint.X and itemSurfPoint.Y == surfacePoint.Y and itemSurfPoint.Z == surfacePoint.Z:
# #						intersectedSurfaces.append((surface, surfacePoint.X, itemSurfPoint.X, surfacePoint.Y, itemSurfPoint.Y, surfacePoint.Z, itemSurfPoint.Z))
# 					if itemSurfNormal.IsAlmostEqualTo(surfaceNormal) and itemSurface.DoesIntersect(surface):
# 						intersectedSurfaces.append((surface, surface.Area, itemSurface, itemSurface.Area, surfaceNormal, itemSurfNormal))
# 						returnSurface.append(surface)
# 					else:
# 						pass
# 						#intersectedSurfaces.append((surfacePoint.X, itemSurfPoint.X, surfacePoint.Y, itemSurfPoint.Y, surfacePoint.Z, itemSurfPoint.Z))
# 		return (returnSurface, intersectedSurfaces)
# 	else:
# 		return None

# def getOuterShells(inGroupedSolids):
# 	"""returns 1D list of solids representing outer shell of building object.

# 		args:
# 			inGroupedSolids: list of grouped solid acquired by using function groupSolids()
# 			outer shells are placed at first positions in sublists of inGroupedSolids

# 		return: list of outer shell solids 
# 	"""
# 	returnItems = []
# 	for i in inGroupedSolids:
# 		returnItems.append(i[0])
# 	return returnItems

# def doesIntersect(item, *args):
# 	inPolysurface = args[0]
# 	inRemovedSurface = args[1]
# 	if type(item) == Autodesk.DesignScript.Geometry.Solid:
# 		if item.DoesIntersect(inPolysurface):
# 			return True
# 		elif item.DoesIntersect(inRemovedSurface):
# 			return True
# 		else:
# 			return []
# 	else:
# 		return []

# def getOuterShellIntersectingElements(inOuterShells, inSolids, inUnWrappedElements):
# 	returnList = []
# 	flattenedList = []
# 	for outerShell in inOuterShells:
# 		outerShellpolySurface = Autodesk.DesignScript.Geometry.PolySurface.BySolid(outerShell)
# 		outerShellSurfaces = list(outerShellpolySurface.Surfaces())
# 		outerShellSurfaces.sort(key = lambda c : c.Area, reverse=False)
# 		removedSurface = outerShellSurfaces[0]
# 		del outerShellSurfaces[0]	
# 		openedOuterShellPolysurface = Autodesk.DesignScript.Geometry.PolySurface.ByJoinedSurfaces(outerShellSurfaces)
# 		#filterMask = openedOuterShellPolysurface.DoesIntersect(inSolids)
# 		intersectedElements = processList(doesIntersect, inSolids, openedOuterShellPolysurface, removedSurface)
# 		returnCategories = []
# 		for c, category in enumerate(inSolids):
# 			returnItems = []
# 			for i, item in enumerate(category):
# 				myType = type(item)
# 				if  myType == Autodesk.DesignScript.Geometry.Solid and intersectedElements[c][i] == True:
# 					returnItems.append((item.Intersect(openedOuterShellPolysurface), inUnWrappedElements[c][i], outerShell))
# 					#flattenedList.append(item.Intersect(openedOuterShellPolysurface))
# 					#myflattenedList = ListUtils.flatList(flattenedList, maxLevel = 0)
# 				else:
# 					returnItems.append([])
# 			returnCategories.append(returnItems)
# 		returnList.append(returnCategories)

# 	return returnList

# # exclude elements (we don't want them in selection)
# errorReport = []
if IN[0] != None:
	if isinstance(IN[0], list):
		#excludeElements = processList(Unwrap, IN[0])
		excludeElements = IN[0]
	else:
		#excludeElements = [Unwrap(IN[0])]
		excludeElements = [IN[0]]
else:
	excludeElements = []

# if IN[1] != None:
# 	if isinstance(IN[1], list):
# 		#excludeElements = processList(Unwrap, IN[0])
# 		testElements = IN[1]
# 	else:
# 		#excludeElements = [Unwrap(IN[0])]
# 		testElements = [IN[1]]
# else:
# 	testElements = []


# # creating ICollection of exxcluded elements used in FilteredElmentCollector
# #elementSet = Autodesk.Revit.DB.ElementSet()
# myElementIds = []
# if excludeElements != None or excludeElements != []:
# 	#excludeElementIds = []
	
# 	for x in excludeElements:
# 		myId = x.Id
# 		#when elements not unwrapped
# 		myElementId = Autodesk.Revit.DB.ElementId(myId)
# 		myElementIds.append(myElementId)
# 		#when elements unwrapped
# 		#myElementIds.append(myId)

# #		myElement = doc.GetElement(myId)		
# #		elementSet.Insert(myId)
# 	exclude_element_collection = Clist[Autodesk.Revit.DB.ElementId](myElementIds)

# else:
# 	exclude_element_collection = Clist([])

# incopenings = True
# incshadows = False
# incwalls = True
# incshared = True

# # roof class names
# roofCNs = [Autodesk.Revit.DB.ExtrusionRoof, Autodesk.Revit.DB.FootPrintRoof]
# # floor class names
# floorCNs = [Autodesk.Revit.DB.Floor, Autodesk.Revit.DB.HostedSweep]
# # wall class names
# wallCNs = [Autodesk.Revit.DB.Wall, Autodesk.Revit.DB.CurtainSystem]
# # column categories 
# columnCgs = [Autodesk.Revit.DB.BuiltInCategory.OST_Columns, Autodesk.Revit.DB.BuiltInCategory.OST_StructuralColumns]
# # structural frame categories 
# structFrameCgs = [Autodesk.Revit.DB.BuiltInCategory.OST_StructuralFraming]
# # curtain system categories 
# curtainSystemCgs = [Autodesk.Revit.DB.BuiltInCategory.OST_Curtain_Systems]

# #get level Ids
# allLevels = getLevels()
# levelIds = getLevelIds(allLevels)

# try:
# 	myElements = [RevitSelection.getElementByClassName(roofCNs, exclude_element_collection), \
# 			  RevitSelection.getElementByClassName(floorCNs, exclude_element_collection), \
# 			  RevitSelection.getElementByClassName(wallCNs, exclude_element_collection), \
# 			  RevitSelection.getElementByCategory(columnCgs, exclude_element_collection), \
# 			  RevitSelection.getElementByCategory(structFrameCgs, exclude_element_collection), \
# 			  RevitSelection.getElementByCategory(curtainSystemCgs, exclude_element_collection)]
# 	unWrappedElements = processList(Unwrap, myElements)
# 	unWrapedTestElements = processList(Unwrap, testElements)



# except Exception as ex:
# 	# if error accurs anywhere in the process catch it
# 	Errors.catch(ex, "Selecting myElements failed")
# 	unWrappedElements = []
# try:
# 	inserts = processList(getInserts, unWrappedElements)
	
# except Exception as ex:
# 	# if error accurs anywhere in the process catch it
# 	Errors.catch(ex, "Getting inserts failed.")
# 	inserts = []

# try:
# 	uniqueInserts = getUniqueElements(inserts)
# except Exception as ex:
# 	# if error accurs anywhere in the process catch it
# 	Errors.catch(ex, "Getting unique inserts failed.")
# 	uniqueInserts = []

# uIs = [x.Id for x in uniqueInserts]
# colectionOfUniqueInsertIds = Clist[Autodesk.Revit.DB.ElementId](uIs)
# # Get ActiveView phase ID
# paramId = Autodesk.Revit.DB.ElementId(Autodesk.Revit.DB.BuiltInParameter.VIEW_PHASE)
# param_provider = Autodesk.Revit.DB.ParameterValueProvider(paramId)
# activeViewPhaseId = param_provider.GetElementIdValue(doc.ActiveView)
# docPhases =  Autodesk.Revit.DB.FilteredElementCollector(doc) \
#  							   .OfCategory(Autodesk.Revit.DB.BuiltInCategory.OST_Phases) \
#  							   .WhereElementIsNotElementType() \
#  							   .ToElements()
# docPhaseNames = [x.Name for x in docPhases]

# #Filter inserts visible only in active view and of Existing phase status - (ignore demolished elements in previous phases) 
# myElementPhaseStatusFilter1 = Autodesk.Revit.DB.ElementPhaseStatusFilter(activeViewPhaseId, Autodesk.Revit.DB.ElementOnPhaseStatus.Existing, False)
# myElementPhaseStatusFilter2 = Autodesk.Revit.DB.ElementPhaseStatusFilter(activeViewPhaseId, Autodesk.Revit.DB.ElementOnPhaseStatus.New,False)
# includeCategories = [Autodesk.Revit.DB.BuiltInCategory.OST_Doors, Autodesk.Revit.DB.BuiltInCategory.OST_Windows]
# includeClasses = [DB.Opening]

# includeCategoryFilters = [Autodesk.Revit.DB.ElementCategoryFilter(x) for x in includeCategories]
# includeClassesFilters = [Autodesk.Revit.DB.ElementClassFilter(x) for x in includeClasses]
# categoryAndClassFilters = includeCategoryFilters + includeClassesFilters

# if len(colectionOfUniqueInsertIds) > 0:
# 	filteredInsertsByActiveViewIds = Autodesk.Revit.DB.FilteredElementCollector(doc, colectionOfUniqueInsertIds) \
# 																.WherePasses(Autodesk.Revit.DB.LogicalOrFilter(categoryAndClassFilters)) \
# 																.WherePasses(SelectableInViewFilter(doc, doc.ActiveView.Id)) \
# 																.WherePasses(Autodesk.Revit.DB.LogicalOrFilter(myElementPhaseStatusFilter1 \
# 																							,myElementPhaseStatusFilter2)) \
# 																.ToElementIds()
# else:
# 	filteredInsertsByActiveViewIds = []

# try:
# 	pass
# 	mySolids = getDynamoSolids(unWrappedElements, filteredInsertsByActiveViewIds, True)
# 	#myTestSolids = getDynamoSolids(unWrapedTestElements, filteredInsertsByActiveViewIds, True)
# except Exception as ex:
# 	# if error accurs anywhere in the process catch it
# 	mySolids = []
# 	#myTestSolids = []

# flattenedSolids = ListUtils.flatList(mySolids)
# #drop out unassigned items
# filteredFlattenedSolids = filter(lambda x: x!=None, flattenedSolids)
# #make solid union of all solids representing element geometry and extract inner and outer shells from this union
# unitedSolid = Solid.ByUnion(filteredFlattenedSolids)
# polySurfaces = PolySurface.BySolid(unitedSolid)
# extractedSolids = list(PolySurface.ExtractSolids(polySurfaces))

# groupedSolids = groupSolids(extractedSolids)
# outerShells = getOuterShells(groupedSolids)
# outerShellIntersectingElements = getOuterShellIntersectingElements(outerShells, mySolids, unWrappedElements)
myModel = RTD_model(doc, IN[0])
energyAnalyseObject = EnAnalyse(doc, IN[0])
myText = ""
# for k,v in myModel.__dict__:
# 	myText += "{0} - {1}; ".format(k,v)
myOutput = (IN[0], energyAnalyseObject.outerShellIntersectingElements)
#myOutput = myTestSolids
#Assign your output to the OUT variable
if Errors.hasError():
	OUT = Errors.report
else:
	OUT = myOutput