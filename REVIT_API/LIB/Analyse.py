# -*- coding: utf-8 -*-
# Copyright(c) 2019, Daniel Gercak
#Classes for bulding a simplyfied Dynamo geometry from Revit model and classes for making further
#analyses e.g. energy analyses...
#resource_path: H:\_WORK\PYTHON\REVIT_API\LIB\Analyse.py

import sys
import time
#import traceback
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
lib_path = r'H:\_WORK\PYTHON\REVIT_API\LIB'
sys.path.append(pyt_path)
sys.path.append(lib_path)

from itertools import chain, groupby
from RevitSelection import *
import RevitSelection as RevitSelection
from ListUtils import *
import ListUtils as ListUtils
from Errors import *
from SpaceOrganize import *

import clr
# Import Element wrapper extension methods
clr.AddReference("RevitNodes")
import Revit
clr.ImportExtensions(Revit.Elements)
# Import geometry conversion extension methods
clr.ImportExtensions(Revit.GeometryConversion)

#import windows forms
clr.AddReference("System.Windows.Forms")
clr.AddReference("System.Drawing")
import System.Drawing
import System.Windows.Forms as WF
from System.Drawing import *
from System.Windows.Forms import Application, Button, Form, ComboBox, Label, TextBox, DockStyle, AnchorStyles

# Import DocumentManager and TransactionManager
clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
doc = DocumentManager.Instance.CurrentDBDocument

clr.AddReference("System")
from System.Collections.Generic import List as Clist
from System.Collections.Generic import IEnumerable as iEnum

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
	#curtainSystemCgs = [Autodesk.Revit.DB.BuiltInCategory.OST_Curtain_Systems]
	# windows categories
	windowsCgs = [Autodesk.Revit.DB.BuiltInCategory.OST_Windows]
	doorsCgs = [Autodesk.Revit.DB.BuiltInCategory.OST_Doors]

	# openings category
	openingsCNs = [Autodesk.Revit.DB.Opening]


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
			self.inc_invis = False #default False
		if "incopenings" in kwargs:
			self.incopenings = kwargs["incopenings"]
		else:
			self.incopenings = True #default True
		if "incshadows" in kwargs:
			self.incshadows = kwargs["incshadows"]
		else:
			self.incshadows = False #default False
		if "incwalls" in kwargs:
			self.incwalls = kwargs["incwalls"]
		else:
			self.incwalls = True #default True
		if "incshared" in kwargs:
			self.incshared = kwargs["incshared"]
		else:
			self.incshared = True #default True
		if len(args) > 0:
			if isinstance(args[0], list):
				#excludeElements = processList(Unwrap, IN[0])
				self.excludeElements = args[0]
			else:
				#excludeElements = [Unwrap(IN[0])]
				self.excludeElements = [args[0]]
		else:
			self.excludeElements = []
		#raise ValueError("self.excludeElements {0} - {1}".format(len(self.excludeElements), self.excludeElements))
		myElementIds = []
		if len(self.excludeElements) > 0:
			#excludeElementIds = []			
			for x in self.excludeElements:
				if hasattr(x, "Id"):
					myId = x.Id
					#when elements not unwrapped
					myElementId = Autodesk.Revit.DB.ElementId(myId)
					myElementIds.append(myElementId)

			self.exclude_element_collection = Clist[Autodesk.Revit.DB.ElementId](myElementIds)
		else:
			self.exclude_element_collection =  Clist[Autodesk.Revit.DB.ElementId]([])
		#raise ValueError("self.exclude_element_collection {0}".format(len(self.exclude_element_collection)))
		self.detail_lvl = Autodesk.Revit.DB.ViewDetailLevel.Coarse
		#include invisible objects
		self.inc_invis = False
		self.view = self.doc.ActiveView
		self.geo_options = Autodesk.Revit.DB.Options()
		if self.view == None: geo_options.DetailLevel = self.detail_lvl
		self.geo_options.IncludeNonVisibleObjects = self.inc_invis
		if self.view != None: self.geo_options.View = self.view

		self.allLevels = getLevels()
		self.levelIds = getLevelIds(self.allLevels)

		sTime = time.time()
		self.structuredElements = self.getStructuredElements()		
			
		# Dynamo solids must be created before appending opening elements to self.unwrappedElements because of 
		# throwing exception while trying to get geometry from elements in mode wihout openings, which 
		# must be done in transaction where openings are deleted and then deletion is undone 
		self.dynamoSolids = self.getDynamoModel(True)
		eTime = time.time()
		myTime = eTime - sTime
		Errors.catchVar(self.structuredElements,"self.structuredElements + time dynamoSolids - {0:.5f} s".format(myTime))
		Errors.catchVar(self.dynamoSolids,"self.dynamoSolids + time dynamoSolids - {0:.5f} s".format(myTime))
		 
		#Errors.catchVar(self.dynamoSolids, "self.dynamoSolids")
		#raise ValueError("self.dynamoSolids {0}".format(len(self.dynamoSolids), self.dynamoSolids))
		#self.dynamoSolids.append(self.dynamoOpeningSolids)
		self.dynamoSolidsWithOpenings = self.getDynamoModel(False, incCW = True)
		Errors.catchVar(self.dynamoSolidsWithOpenings,"self.dynamoSolidsWithOpenings".format())
		
		flattenedSolids = ListUtils.flatList(self.dynamoSolids)
		flattenedSolidsWithOpenings = ListUtils.flatList(self.dynamoSolidsWithOpenings)		
		#drop out unassigned items
		filteredFlattenedSolids = filter(lambda x: x!=None, flattenedSolids)
		Errors.catchVar(filteredFlattenedSolids, "filteredFlattenedSolids")
		
		filteredFlattenedSolidsWithOpenings = filter(lambda x: x!=None, flattenedSolidsWithOpenings)
		Errors.catchVar(filteredFlattenedSolidsWithOpenings, "filteredFlattenedSolidsWithOpenings")
		
		#make solid union of all solids representing element geometry 
		sTime = time.time()
		
		try:
			self.unitedSolid = Autodesk.DesignScript.Geometry.Solid.ByUnion(filteredFlattenedSolids)
			Errors.catchVar(self.unitedSolid, "self.unitedSolid")

			#get openings by subtracting united solid without openings and with united solid with openings
			self.unitedSolidWithOpenings = Autodesk.DesignScript.Geometry.Solid.ByUnion(filteredFlattenedSolidsWithOpenings)
			self.subtractedOpenings = Autodesk.DesignScript.Geometry.Solid.DifferenceAll(self.unitedSolid, Clist[Autodesk.DesignScript.Geometry.Solid]([self.unitedSolidWithOpenings]))
			self.subtractedOpenings = Autodesk.DesignScript.Geometry.PolySurface.BySolid(self.subtractedOpenings)
			self.subtractedOpenings = Autodesk.DesignScript.Geometry.PolySurface.ExtractSolids(self.subtractedOpenings)
			if len(self.subtractedOpenings) != len(self.openingFills):
				ModelConsistency.catch("Err_05", "Model Consistency Error in RTD_model.setup()")
			eTime = time.time()
			myTime = eTime - sTime
			Errors.catchVar(self.subtractedOpenings, "self.subtractedOpenings + time self.unitedSolids{0:.5f} s".format(myTime))

			#extract inner and outer shells from the unitedSolid
			polySurfaces = Autodesk.DesignScript.Geometry.PolySurface.BySolid(self.unitedSolid)
			extractedSolids = list(Autodesk.DesignScript.Geometry.PolySurface.ExtractSolids(polySurfaces))

			
			#group all extracted solids by outer shells and assigning inner shells to them
			self.groupedSolids = self.groupSolids(extractedSolids)
			Errors.catchVar(self.groupedSolids, "self.groupedSolids")

			# strFrameSolids = ListUtils.flattenList(ListUtils.processList(RevitSelection.getDynamoGeometry, self.structuredElements[4]))
			# Errors.catchVar(strFrameSolids, "strFrameSolids",front = True)
			
			#model consistency test for outer and inner solids (outer solid is at index 0 inner solids are at indices > 0)
			for i, obj in enumerate(self.groupedSolids):
				if len(obj) < 2:
					ModelConsistency.catch("Err_01", "OBJ-{0}".format(i))

			self.outerShells = self.getOuterShells(self.groupedSolids) 
			self.innerShells = self.getOuterShells(self.groupedSolids, innerShell=True) 
			Errors.catchVar(self.outerShells, "self.outerShells")
			Errors.catchVar(self.innerShells, "self.innerShells")
			''' 
			#Errors.catchVar(self.outerShells, "self.outerShells")
			self.outerShellPolysurfaces = []
			self.rawOuterShellAreas = []
			for outerShell in self.outerShells:
				pSurface = Autodesk.DesignScript.Geometry.PolySurface.BySolid(outerShell)
				self.outerShellPolysurfaces.append(pSurface)
				self.rawOuterShellAreas.append(pSurface.Area * 0.000001) '''

			#collection of all door and window elements gathered by RevitSelection.getInserts method in RTD_Model.getDynamoModel()
			sTime = time.time()
			openingFillsIds = [x.Id for x in self.openingFills]
			openingFillsCol = Clist[Autodesk.Revit.DB.ElementId](openingFillsIds)
			self.doors = list(DB.FilteredElementCollector(doc, openingFillsCol).OfCategory(Autodesk.Revit.DB.BuiltInCategory.OST_Doors))
			self.windows = list(DB.FilteredElementCollector(doc, openingFillsCol).OfCategory(Autodesk.Revit.DB.BuiltInCategory.OST_Windows))
			#Errors.catchVar(self.windows, "self.doors")
			#creating SolidPoints containig center point of opening solids and subtracted solid 
			solidPoints = []
			for solid in self.subtractedOpenings:
				solidPoints.append(SolidPoint(solid))

			#Errors.catchVar(solidPoints, "solidPoints")
			#raise TypeError("solidPoints of type {0}".format(solidPoints[0].__class__.__name__))
			#kdTree for nearest solid search for all door and window elements
			kdTree = KD_Tree(solidPoints)
			#Errors.catchVar(kdTree.DSPointsTree, "doorsKdTree")
			self.doorSolids = self.getNearestSolids(self.doors, kdTree)
			self.windowSolids = self.getNearestSolids(self.windows, kdTree)

			#Errors.catchVar(zip(self.doorSolids, self.doors), "self.doorSolids",front = True)
			#append doors and windows to self.structuredElements and dynamoSolids
			self.structuredElements.append(self.doors)		
			self.structuredElements.append(self.windows)
			self.dynamoSolidsWithOpenings.append(self.doorSolids)
			self.dynamoSolidsWithOpenings.append(self.windowSolids)

			eTime = time.time()
			myTime = eTime - sTime
			Errors.catchVar((self.doorSolids, self.windowSolids), "(self.doorSolids, self.windowSolids) {0:.5f} s".format(myTime))
			#get outerShell surfaces by intersecting all self.dynamoSolids with self.outerShells
			sTime = time.time()
			try:
				self.outerShellIntersectingSurfaces = self.getOuterShellIntersectingSurfaces(self.outerShells, self.dynamoSolidsWithOpenings, self.structuredElements)
			except Exception as ex:
				Errors.catch(ex, "Creating outerShellIntersectingSurfaces in RTD_model.setup() failed {0} - {1}".format(self.outerShells, self.dynamoSolids))
			eTime = time.time()
			myTime = eTime - sTime
			Errors.catchVar(self.outerShellIntersectingSurfaces, "self.outerShellIntersectingSurfaces {0:.5f} s".format(myTime))
		except Exception as ex:
			Errors.catch(ex, "3D model in setup in RTD_model.setup() failed")
		
		"""
		try:
			self.outerShellIntersectingSurfacesAreaSums = ListUtils.processListSum(self.getAreasWithSum, self.outerShellIntersectingSurfaces)
		except Exception as ex:
			Errors.catch(ex, "Creating area sums from outerShellIntersectingSurfaces in RTD_model.setup() failed {0} - {1}".format(self.outerShells, self.dynamoSolids))
			self.outerShellIntersectingSurfacesAreaSums = []
		
		#replace opening items represented by wall element with openingFill element	
		try:
			for o, obj in enumerate(self.outerShellIntersectingSurfaces):
				replaceItems = []
				try:
					for i, item in enumerate(obj[6]):
						if (type(item) == tuple) and len(item) > 0:
							replaceItems.append((item[0], self.openingFills[i]))
					self.outerShellIntersectingSurfaces[o][6] = replaceItems
				except Exception as ex:
					Errors.catch(ex, "eee {0} - {1}".format(o, obj))
		except Exception as ex:
			Errors.catch(ex, "fuckOff") 
		"""
	def getNearestSolids(self, inElements, inKd_tree):
		solids = []
		for el in inElements:
			dynGeo = RevitSelection.getDynamoGeometry(el)
			boundingBox = Autodesk.DesignScript.Geometry.BoundingBox.ByGeometry(dynGeo)
			cuboid = Autodesk.DesignScript.Geometry.BoundingBox.ToCuboid(boundingBox)
			centroid = Autodesk.DesignScript.Geometry.Solid.Centroid(cuboid)
			nearestSolidPoint = inKd_tree.get_nearest(inKd_tree.DSPointsTree, centroid, 3, inKd_tree.dist_sq_dim, return_distances=False)
			try:
				if nearestSolidPoint.solid.DoesIntersect(cuboid):
					solids.append(nearestSolidPoint.solid)
				else:
					raise ValueError("Element: {0} does not intersect with nearest solid represented by center point X: {1} Y: {2} Z: {3}".format(el.Id, nearestSolidPoint.point.X, nearestSolidPoint.point.Y,nearestSolidPoint.point.Z))
			except Exception as ex:
				Errors.catch(ex, "Unable to pair all elements with solids in RTD_Model.getNearestSolids()")
		return solids

	def getAreasWithSum(self, item, *args, **kwargs):
		"""
			function for use in processListSum() to get area values 
			and their sum from Surface objects
			
			item: type tuple(tuple(Surface, ...), element name type: string, ...)
			
			returns tuple(tuple(Surface.area,...), sum of areas type: float or int)
		"""
		
		#item must be not empty tuple with not empty tuple of Surface objects
		if item.__class__.__name__ == "tuple":
			#item must be not empty tuple with not empty tuple of Surface objects
			if len(item) > 0 and len(item[0]) > 0 and item[0][0].__class__.__name__ == "Surface":
				areas = [e.Area/1000000 for e in item[0]]
				return (tuple(areas), sum(areas))
			else:
				return (None, 0)

	def getCategoryId(self, item):
		return (item.__class__.__name__, item.Category.Name, item.Category.Id)
	
	def getCategoryName(self, item):
		return item.Category.Name

	def getStructuredElements(self):
		allElementsIds = RevitSelection.getAllElements(doc, toId = True)
		#allElementsIdsCol = Clist[Autodesk.Revit.DB.ElementId](allElementsIds)
		if len(self.exclude_element_collection) > 0:
			roofs = list(DB.FilteredElementCollector(doc, allElementsIds) \
									.WherePasses(Autodesk.Revit.DB.ElementCategoryFilter(Autodesk.Revit.DB.BuiltInCategory.OST_Roofs, False)) \
									.WherePasses(DB.ExclusionFilter(self.exclude_element_collection)) \
									.WhereElementIsNotElementType() \
									.ToElements() )
			floors = list(DB.FilteredElementCollector(doc, allElementsIds) \
									.WherePasses(Autodesk.Revit.DB.ElementCategoryFilter(Autodesk.Revit.DB.BuiltInCategory.OST_Floors, False)) \
									.WherePasses(DB.ExclusionFilter(self.exclude_element_collection)) \
									.WhereElementIsNotElementType() \
									.ToElements() )
			walls = list(DB.FilteredElementCollector(doc, allElementsIds) \
									.WherePasses(Autodesk.Revit.DB.ElementCategoryFilter(Autodesk.Revit.DB.BuiltInCategory.OST_Walls, False)) \
									.WherePasses(DB.ExclusionFilter(self.exclude_element_collection)) \
									.WhereElementIsNotElementType() \
									.ToElements() )
			structuralFrames = list(DB.FilteredElementCollector(doc, allElementsIds) \
									.WherePasses(Autodesk.Revit.DB.ElementCategoryFilter(Autodesk.Revit.DB.BuiltInCategory.OST_StructuralFraming, False)) \
									.WherePasses(DB.ExclusionFilter(self.exclude_element_collection)) \
									.WhereElementIsNotElementType() \
									.ToElements() )
			# structuralColumns = list(DB.FilteredElementCollector(doc, allElementsIds) \
			# 						.WherePasses(Autodesk.Revit.DB.ElementCategoryFilter(Autodesk.Revit.DB.BuiltInCategory.OST_StructuralColumns, False)) \
			# 						.WherePasses(DB.ExclusionFilter(self.exclude_element_collection)) \
			#						.WhereElementIsNotElementType() \
			# 						.ToElements() )
			structuralColumns = list(DB.FilteredElementCollector(doc) \
									.OfCategory(Autodesk.Revit.DB.BuiltInCategory.OST_StructuralColumns) \
									.OfClass(Autodesk.Revit.DB.FamilyInstance) \
									.WherePasses(DB.ExclusionFilter(self.exclude_element_collection)) \
									.WhereElementIsNotElementType()
			 						.ToElements() )
			columns = list(DB.FilteredElementCollector(doc) \
									.OfCategory(Autodesk.Revit.DB.BuiltInCategory.OST_Columns) \
									.OfClass(Autodesk.Revit.DB.FamilyInstance) \
									.WhereElementIsNotElementType()
									.WherePasses(DB.ExclusionFilter(self.exclude_element_collection)) \
			 						.ToElements() )
			structuralColumns += columns
			structuralFoundation = list(DB.FilteredElementCollector(doc, allElementsIds) \
									.WherePasses(Autodesk.Revit.DB.ElementCategoryFilter(Autodesk.Revit.DB.BuiltInCategory.OST_StructuralFoundation, False)) \
									.WherePasses(DB.ExclusionFilter(self.exclude_element_collection)) \
									.WhereElementIsNotElementType() \
									.ToElements() )
			# curtainWalls = curtainSystem = list(DB.FilteredElementCollector(doc, allElementsIds) \
			# 						.WherePasses(Autodesk.Revit.DB.ElementCategoryFilter(Autodesk.Revit.DB.BuiltInCategory.OST_Curtain_Systems, False)) \
			# 						.ToElements() )
			#curtainSystems = list(DB.FilteredElementCollector(doc, allElementsIds) \
			#						.WherePasses(Autodesk.Revit.DB.ElementCategoryFilter(Autodesk.Revit.DB.BuiltInCategory.OST_Curtain_Systems, False)) \
			#						.WherePasses(DB.ExclusionFilter(self.exclude_element_collection)) \
			#						.ToElements() )
			curtainWalls = list(RevitSelection.getElementByClassName(RTD_model.wallCNs, self.exclude_element_collection, curtainWall = True))
			doors = list(DB.FilteredElementCollector(doc, allElementsIds) \
									.WherePasses(Autodesk.Revit.DB.ElementCategoryFilter(Autodesk.Revit.DB.BuiltInCategory.OST_Doors, False)) \
									.WherePasses(DB.ExclusionFilter(self.exclude_element_collection)) \
									.WhereElementIsNotElementType() \
									.ToElements() ) 
			windows = list(DB.FilteredElementCollector(doc, allElementsIds) \
									.WherePasses(Autodesk.Revit.DB.ElementCategoryFilter(Autodesk.Revit.DB.BuiltInCategory.OST_Windows, False)) \
									.WherePasses(DB.ExclusionFilter(self.exclude_element_collection)) \
									.WhereElementIsNotElementType() \
									.ToElements() )
		else:
			roofs = list(DB.FilteredElementCollector(doc, allElementsIds) \
								.WherePasses(Autodesk.Revit.DB.ElementCategoryFilter(Autodesk.Revit.DB.BuiltInCategory.OST_Roofs, False)) \
								.WhereElementIsNotElementType() \
								.ToElements() )
			floors = list(DB.FilteredElementCollector(doc, allElementsIds) \
									.WherePasses(Autodesk.Revit.DB.ElementCategoryFilter(Autodesk.Revit.DB.BuiltInCategory.OST_Floors, False)) \
									.WhereElementIsNotElementType() \
									.ToElements() )
			walls = list(DB.FilteredElementCollector(doc, allElementsIds) \
									.WherePasses(Autodesk.Revit.DB.ElementCategoryFilter(Autodesk.Revit.DB.BuiltInCategory.OST_Walls, False)) \
									.WhereElementIsNotElementType() \
									.ToElements() )
			structuralFrames = list(DB.FilteredElementCollector(doc, allElementsIds) \
									.WherePasses(Autodesk.Revit.DB.ElementCategoryFilter(Autodesk.Revit.DB.BuiltInCategory.OST_StructuralFraming, False)) \
									.WhereElementIsNotElementType() \
									.ToElements() )
			# structuralColumns = list(DB.FilteredElementCollector(doc, allElementsIds) \
			# 						.WherePasses(Autodesk.Revit.DB.ElementCategoryFilter(Autodesk.Revit.DB.BuiltInCategory.OST_StructuralColumns, False)) \
			#						.WhereElementIsNotElementType() \
			# 						.ToElements() )
			structuralColumns = list(DB.FilteredElementCollector(doc, allElementsIds) \
									.OfCategory(Autodesk.Revit.DB.BuiltInCategory.OST_StructuralColumns) \
									.OfClass(Autodesk.Revit.DB.FamilyInstance) \
									.WhereElementIsNotElementType()
			 						.ToElements() )
			columns = list(DB.FilteredElementCollector(doc, allElementsIds) \
									.OfCategory(Autodesk.Revit.DB.BuiltInCategory.OST_Columns) \
									.OfClass(Autodesk.Revit.DB.FamilyInstance) \
									.WhereElementIsNotElementType()
			 						.ToElements() )
			structuralColumns += columns
			structuralFoundation = list(DB.FilteredElementCollector(doc, allElementsIds) \
									.WherePasses(Autodesk.Revit.DB.ElementCategoryFilter(Autodesk.Revit.DB.BuiltInCategory.OST_StructuralFoundation, False)) \
									.WhereElementIsNotElementType() \
									.ToElements() )
			# curtainWalls = curtainSystem = list(DB.FilteredElementCollector(doc, allElementsIds) \
			# 						.WherePasses(Autodesk.Revit.DB.ElementCategoryFilter(Autodesk.Revit.DB.BuiltInCategory.OST_Curtain_Systems, False)) \
			# 						.ToElements() )
			#curtainSystems = list(DB.FilteredElementCollector(doc, allElementsIds) \
			#						.WherePasses(Autodesk.Revit.DB.ElementCategoryFilter(Autodesk.Revit.DB.BuiltInCategory.OST_Curtain_Systems, False)) \
			#						.WherePasses(DB.ExclusionFilter(self.exclude_element_collection)) \
			#						.ToElements() )
			curtainWalls = list(RevitSelection.getElementByClassName(RTD_model.wallCNs, self.exclude_element_collection, curtainWall = True))
			doors = list(DB.FilteredElementCollector(doc, allElementsIds) \
									.WherePasses(Autodesk.Revit.DB.ElementCategoryFilter(Autodesk.Revit.DB.BuiltInCategory.OST_Doors, False)) \
									.WhereElementIsNotElementType() \
									.ToElements() )
			windows = list(DB.FilteredElementCollector(doc, allElementsIds) \
									.WherePasses(Autodesk.Revit.DB.ElementCategoryFilter(Autodesk.Revit.DB.BuiltInCategory.OST_Windows, False)) \
									.WhereElementIsNotElementType() \
									.ToElements() )
			self.doorsAndWindowsFills = doors + windows
		returnElements = [roofs, floors, walls, structuralFrames, structuralColumns, structuralFoundation, curtainWalls]
		return returnElements

	def getUnwrappedElements(self):
		"""
			get Unwrapped elements to facilitate manipulation with 
			NOTICE - In order to avoid Exception (error find global name UnwrapElement) while importing external library into main script
					I decided not to Unwrap elements. For now it is not necessary
		"""
		#try:
		returnElements = [ \
				list(RevitSelection.getElementByClassName(RTD_model.roofCNs, self.exclude_element_collection)), \
				list(RevitSelection.getElementByClassName(RTD_model.floorCNs, self.exclude_element_collection)), \
				list(RevitSelection.getElementByClassName(RTD_model.wallCNs, self.exclude_element_collection)), \
				list(RevitSelection.getElementByCategory(RTD_model.columnCgs, self.exclude_element_collection)), \
				list(RevitSelection.getElementByCategory(RTD_model.structFrameCgs, self.exclude_element_collection)), \
				list(RevitSelection.getElementByClassName(RTD_model.wallCNs, self.exclude_element_collection, curtainWall = True)), \
				# #RevitSelection.getOpeningsElements(RTD_model.windowsCgs, self.exclude_element_collection), \
				# #RevitSelection.getElementByClassName(RTD_model.openingsCNs, self.exclude_element_collection) \
				]
		#raise ValueError("returnElements {0} - {1}".format(len(returnElements[2]), returnElements))
		#return ListUtils.processList(UnwrapElement, returnElements)
		return returnElements

		#except Exception as ex:
		#	# if error accurs anywhere in the process catch it
		#	Errors.catch(ex, "Selecting returnElements in RTD_model.getUnwrappedElements() failed")
		#	return []

	# def getModelOfOneSolidByUnion(self, removeInserts):
	# 	"""
	# 	get dynamo model of united solids from current Revit document

	# 	arg: removeInserts type: bool - if True, it removes inserts from revit geometry in order to acquire clean geometry without holes
		
	# 	Returns: Autodesk.DesignScript.Geometry.Solid
	# 	"""
	# 	model = self.getDynamoModel(removeInserts)
	# 	flattenModel = ListUtils.flatList(model)
	# 	try:
	# 		unitedSolid = Autodesk.DesignScript.Geometry.Solid.ByUnion(flattenModel)
	# 	except Exception as ex:
	# 		Errors.catch(ex, "Solid.ByUnion in RTD_model.getModelOfOneSolidByUnion() failed")
	# 		unitedSolid = []
	# 	return unitedSolid
	
	# def getOpeningsElements(self, inElements):
	# 	"""
	# 	get Revit Elements of raw openings without filling from current Revit document

	# 	no args
		
	# 	Returns: list[Autodesk.RevitDB.Element]
	# 	"""
	# 	rawInserts = ListUtils.flatList(ListUtils.processList(RevitSelection.getInserts, inElements, incopenings = True, incshadows = False, incwalls = False, incshared = True))
		
	# 	rawInsertsIds = [x.Id for x in rawInserts]
	# 	rawInsertsIdsCol = Clist[Autodesk.Revit.DB.ElementId](rawInsertsIds)
	# 	paramId = Autodesk.Revit.DB.ElementId(Autodesk.Revit.DB.BuiltInParameter.VIEW_PHASE)
	# 	param_provider = Autodesk.Revit.DB.ParameterValueProvider(paramId)
	# 	activeViewPhaseId = param_provider.GetElementIdValue(self.doc.ActiveView)

	# 	myElementPhaseStatusFilter1 = Autodesk.Revit.DB.ElementPhaseStatusFilter(activeViewPhaseId, Autodesk.Revit.DB.ElementOnPhaseStatus.Existing, False)
	# 	myElementPhaseStatusFilter2 = Autodesk.Revit.DB.ElementPhaseStatusFilter(activeViewPhaseId, Autodesk.Revit.DB.ElementOnPhaseStatus.New,False)

	# 	insertOpenings = Autodesk.Revit.DB.FilteredElementCollector(self.doc, rawInsertsIdsCol) \
	# 																		.WherePasses(Autodesk.Revit.DB.LogicalOrFilter(myElementPhaseStatusFilter1 \
	# 																			,myElementPhaseStatusFilter2)) \
	# 																		.WherePasses(Autodesk.Revit.DB.ElementCategoryFilter(Autodesk.Revit.DB.BuiltInCategory.OST_Walls, True)) \
	# 																		.ToElements()
	# 	insertWalls = Autodesk.Revit.DB.FilteredElementCollector(self.doc, rawInsertsIdsCol) \
	# 																		.WherePasses(Autodesk.Revit.DB.ElementCategoryFilter(Autodesk.Revit.DB.BuiltInCategory.OST_Walls, False)) \
	# 																		.ToElementIds()

	# 	filteredWalls = []
	# 	for elem in list(insertOpenings):
	# 		#el = insertWalls[0].Id
	# 		# Get the element from the selected element reference
	# 		el_ID = self.doc.GetElement(elem.Id)
	# 		# Get the Bounding Box of the selected element.
	# 		el_bb = el_ID.get_BoundingBox(self.doc.ActiveView)
	# 		# Get the min and max values of the elements bounding box.
	# 		el_bb_max = el_bb.Max
	# 		el_bb_min = el_bb.Min
	# 		filteredWall = Autodesk.Revit.DB.FilteredElementCollector(self.doc, insertWalls) \
	# 																		.WherePasses(Autodesk.Revit.DB.BoundingBoxIntersectsFilter(Autodesk.Revit.DB.Outline(el_bb_min, el_bb_max))) \
	# 																		.ToElements()
	# 		if len(list(filteredWall)) > 0:
	# 			filteredWalls += filteredWall		

	# 	return ListUtils.flattenList(filteredWalls)
	
	def filterElementsByActiveViewIds(self, inElements, **kwargs):
		"""
			Filter elements by active view parameters (active view phase, category...)

			inElements> list[Autodesk.Revit.DB.Element]
			kwargs["rawOpening"] including wall elements of opening (raw openings geometry) type: bool
			kwargs["toElement"] type: bool
		
			Returns: list[Autodesk.Revit.DB.ElementId] if kwargs["toElement"] == False or list[Autodesk.Revit.DB.Element] if kwargs["toElement"] == True 
		"""
		

		if "rawOpening" in kwargs and kwargs["rawOpening"] == True:
			includeCategories = [Autodesk.Revit.DB.BuiltInCategory.OST_Walls]
			includeClasses = []
		else:
			includeCategories = [Autodesk.Revit.DB.BuiltInCategory.OST_Doors, Autodesk.Revit.DB.BuiltInCategory.OST_Windows]
			includeClasses = [DB.Opening]

		toElement = True if "toElement" in kwargs and kwargs["toElement"] == True else False
		
		

		ids = [x.Id for x in inElements]
		#colectionOfUniqueInsertIds = Clist[Autodesk.Revit.DB.ElementId](uIs)
		colectionOfElementsIds = Clist[Autodesk.Revit.DB.ElementId](ids)

		# Get ActiveView phase ID
		paramId = Autodesk.Revit.DB.ElementId(Autodesk.Revit.DB.BuiltInParameter.VIEW_PHASE)
		param_provider = Autodesk.Revit.DB.ParameterValueProvider(paramId)
		activeViewPhaseId = param_provider.GetElementIdValue(self.doc.ActiveView)
		docPhases =  Autodesk.Revit.DB.FilteredElementCollector(self.doc) \
									.OfCategory(Autodesk.Revit.DB.BuiltInCategory.OST_Phases) \
									.WhereElementIsNotElementType() \
									.ToElements()

		#Filter inserts visible only in active view and of Existing phase status - (ignore demolished elements in previous phases) 
		myElementPhaseStatusFilter1 = Autodesk.Revit.DB.ElementPhaseStatusFilter(activeViewPhaseId, Autodesk.Revit.DB.ElementOnPhaseStatus.Existing, False)
		myElementPhaseStatusFilter2 = Autodesk.Revit.DB.ElementPhaseStatusFilter(activeViewPhaseId, Autodesk.Revit.DB.ElementOnPhaseStatus.New,False)

		includeCategoryFilters = [Autodesk.Revit.DB.ElementCategoryFilter(x) for x in includeCategories]
		includeClassesFilters = [Autodesk.Revit.DB.ElementClassFilter(x) for x in includeClasses]
		categoryAndClassFilters = includeCategoryFilters + includeClassesFilters
			
		# if len(colectionOfElementsIds) > 0:
		# 	if toElement == True:
		# 		filteredElementsByActiveViewIds = Autodesk.Revit.DB.FilteredElementCollector(self.doc, colectionOfElementsIds) \
		# 																	.WherePasses(Autodesk.Revit.DB.LogicalOrFilter(categoryAndClassFilters)) \
		# 																	.WherePasses(SelectableInViewFilter(self.doc, self.doc.ActiveView.Id)) \
		# 																	.WherePasses(Autodesk.Revit.DB.LogicalOrFilter(myElementPhaseStatusFilter1 \
		# 																								,myElementPhaseStatusFilter2)) \
		# 																	.WherePasses(Autodesk.Revit.DB.ElementCategoryFilter(Autodesk.Revit.DB.BuiltInCategory.OST_Walls, True)) \
		# 																	.ToElements()
		# 	else:
		# 		filteredElementsByActiveViewIds = Autodesk.Revit.DB.FilteredElementCollector(self.doc, colectionOfElementsIds) \
		# 																	.WherePasses(Autodesk.Revit.DB.LogicalOrFilter(categoryAndClassFilters)) \
		# 																	.WherePasses(SelectableInViewFilter(self.doc, self.doc.ActiveView.Id)) \
		# 																	.WherePasses(Autodesk.Revit.DB.LogicalOrFilter(myElementPhaseStatusFilter1 \
		# 																								,myElementPhaseStatusFilter2)) \
		# 																	.WherePasses(Autodesk.Revit.DB.ElementCategoryFilter(Autodesk.Revit.DB.BuiltInCategory.OST_Walls, True)) \
		# 																	.ToElementIds()
		# else:
		# 	filteredElementsByActiveViewIds = []

		if len(colectionOfElementsIds) > 0:
			if toElement == True:
				filteredElementsByActiveViewIds = Autodesk.Revit.DB.FilteredElementCollector(self.doc, colectionOfElementsIds) \
																			.WherePasses(SelectableInViewFilter(self.doc, self.doc.ActiveView.Id)) \
																			.WherePasses(Autodesk.Revit.DB.LogicalOrFilter(myElementPhaseStatusFilter1 \
																										,myElementPhaseStatusFilter2)) \
																			.WherePasses(Autodesk.Revit.DB.ElementCategoryFilter(Autodesk.Revit.DB.BuiltInCategory.OST_Walls, True)) \
																			.ToElements()
			else:
				filteredElementsByActiveViewIds = Autodesk.Revit.DB.FilteredElementCollector(self.doc, colectionOfElementsIds) \
																			.WherePasses(SelectableInViewFilter(self.doc, self.doc.ActiveView.Id)) \
																			.WherePasses(Autodesk.Revit.DB.LogicalOrFilter(myElementPhaseStatusFilter1 \
																										,myElementPhaseStatusFilter2)) \
																			.WherePasses(Autodesk.Revit.DB.ElementCategoryFilter(Autodesk.Revit.DB.BuiltInCategory.OST_Walls, True)) \
																			.ToElementIds()
		else:
			filteredElementsByActiveViewIds = []

		return filteredElementsByActiveViewIds

	def getDynamoModel(self, removeInserts, **kwargs):
		"""
		get dynamo solids from current Revit document

		arg: removeInserts type: bool - if True, it removes inserts from revit geometry in order to acquire clean geometry without holes
		kwargs["incCW"] type: bool - including curtain walls if true, default = True
		Returns: List[Autodesk.DesignScript.Geometry.Solid]
		"""
		
		#self.unwrappedElements = self.getUnwrappedElements()
		try:
			self.inserts = ListUtils.flatList(ListUtils.processList(RevitSelection.getInserts, self.structuredElements))
			#self.openingWalls = filter(lambda x: x.Category.Name == "Walls", self.inserts)
			
		except Exception as ex:
			# if error accurs anywhere in the process catch it
			Errors.catch(ex, "Getting inserts RTD_model.getDynamoModel() failed.")
			self.inserts = []		
		
		# try:
		# 	uniqueInserts = self.getUniqueElements(inserts)
		# except Exception as ex:
		# 	# if error accurs anywhere in the process catch it
		# 	Errors.catch(ex, "Getting unique inserts in RTD_model.getDynamoModel() failed.")
		# 	uniqueInserts = []

		# #uIs = [x.Id for x in uniqueInserts]
		# uIs = [x.Id for x in self.inserts]
		# #colectionOfUniqueInsertIds = Clist[Autodesk.Revit.DB.ElementId](uIs)
		# colectionOfInsertIds = Clist[Autodesk.Revit.DB.ElementId](uIs)
		# # Get ActiveView phase ID
		# paramId = Autodesk.Revit.DB.ElementId(Autodesk.Revit.DB.BuiltInParameter.VIEW_PHASE)
		# param_provider = Autodesk.Revit.DB.ParameterValueProvider(paramId)
		# activeViewPhaseId = param_provider.GetElementIdValue(self.doc.ActiveView)
		# docPhases =  Autodesk.Revit.DB.FilteredElementCollector(self.doc) \
		# 							.OfCategory(Autodesk.Revit.DB.BuiltInCategory.OST_Phases) \
		# 							.WhereElementIsNotElementType() \
		# 							.ToElements()
		# # docPhaseNames = [x.Name for x in docPhases]

		# #Filter inserts visible only in active view and of Existing phase status - (ignore demolished elements in previous phases) 
		# myElementPhaseStatusFilter1 = Autodesk.Revit.DB.ElementPhaseStatusFilter(activeViewPhaseId, Autodesk.Revit.DB.ElementOnPhaseStatus.Existing, False)
		# myElementPhaseStatusFilter2 = Autodesk.Revit.DB.ElementPhaseStatusFilter(activeViewPhaseId, Autodesk.Revit.DB.ElementOnPhaseStatus.New,False)
		# includeCategories = [Autodesk.Revit.DB.BuiltInCategory.OST_Doors, Autodesk.Revit.DB.BuiltInCategory.OST_Windows]
		# includeClasses = [DB.Opening]

		# includeCategoryFilters = [Autodesk.Revit.DB.ElementCategoryFilter(x) for x in includeCategories]
		# includeClassesFilters = [Autodesk.Revit.DB.ElementClassFilter(x) for x in includeClasses]
		# categoryAndClassFilters = includeCategoryFilters + includeClassesFilters

		# #if len(colectionOfUniqueInsertIds) > 0:
		# if len(colectionOfInsertIds) > 0:
		# 	self.filteredInsertsByActiveViewIds = Autodesk.Revit.DB.FilteredElementCollector(self.doc, colectionOfInsertIds) \
		# 																.WherePasses(Autodesk.Revit.DB.LogicalOrFilter(categoryAndClassFilters)) \
		# 																.WherePasses(SelectableInViewFilter(self.doc, self.doc.ActiveView.Id)) \
		# 																.WherePasses(Autodesk.Revit.DB.LogicalOrFilter(myElementPhaseStatusFilter1 \
		# 																							,myElementPhaseStatusFilter2)) \
		# 																.ToElementIds()
		# else:
		self.filteredInsertsByActiveViewIds = self.filterElementsByActiveViewIds(self.inserts)
		#raise TypeError("len self.filteredInsertsByActiveViewIds {}".format(self.filteredInsertsByActiveViewIds))
		self.openingFills = filter(lambda x: x.Category.Name != "Walls", [doc.GetElement(x) for x in list(self.filteredInsertsByActiveViewIds)])
		try:
			if removeInserts:
				self.mySolids = self.getDynamoSolids(self.structuredElements , self.filteredInsertsByActiveViewIds, **kwargs)
				#raise TypeError("len self.mySolids {}".format(len(self.mySolids)))
			else:
				args = []
				self.mySolids = self.getDynamoSolids(self.structuredElements , *args, **kwargs)
			#myTestSolids = getDynamoSolids(unWrapedTestElements, filteredInsertsByActiveViewIds, True)
		except Exception as ex:
			Errors.catch(ex, "getDynamoSolids in RTD_model.getDynamoModel() failed")
			self.mySolids = []
		#Errors.catchVar("self.mySolids", self.mySolids)
		#raise ValueError("self.mySolids {0}".format(len(self.mySolids), self.mySolids))
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

	def getDynamoSolids(self, unWrappedElements, *args, **kwargs):
		"""
			acquire dynamo geometry as structured List 
			Element must be unwrapped - use Unwrap() function to each item before input as List
			Optional argument is list of inserts to exclude from final geometry (e.g. windows, doors... )

			arg: unWrappedElements type: List[Autodesk.Revit.DB.Element]
			
			args[0]: element Ids of filtered inserts by active view and phase filter - type: List[Autodesk.Revit.DB.ElementId]
			kwargs["incCW"] type: bool - including curtain walls if true, default = True
			Returns: Structured list of Autodesk.DesignScript.Geometry.Solid. See getDynamoSolid()
		"""
		detail_lvl = Autodesk.Revit.DB.ViewDetailLevel.Coarse
		#include invisible objects
		inc_invis = False
		view = self.doc.ActiveView
		if len(args) > 0:
			uniqueInsertIds = args[0]
			remove_inserts = True
		else:
			uniqueInsertIds = []
			remove_inserts = False
		#raise TypeError("len uniqueInsertIds {}".format(len(uniqueInsertIds)))
		TransactionManager.Instance.EnsureInTransaction(self.doc)
		trans = Autodesk.Revit.DB.SubTransaction(self.doc)
		
		myIsValidObject = [] 		
		if remove_inserts == True and len(uniqueInsertIds) > 0:		
			trans.Start()
			try:					
				try:				
					self.doc.Delete(uniqueInsertIds)
					#t.Commit()
					self.doc.Regenerate()
				except Exception as ex:
					trans.RollBack()
					#myIsValidObject.append((insert.IsValidObject, insert.Id))
					# if error accurs anywhere in the process catch it
					Errors.catch(ex, "Deleting inserts in RTD_model.getDynamoModel().getDynamoSolid() failed.")
				
				geo_options = Autodesk.Revit.DB.Options()
				if view == None: geo_options.DetailLevel = detail_lvl
				geo_options.IncludeNonVisibleObjects = inc_invis
				if view != None: geo_options.View = view
				#raise TypeError("len unWrappedElements {}".format(len(unWrappedElements)))
				#areValidObjects = ListUtils.processList(self.isValid, unWrappedElements)
				#raise TypeError("areValidObjects {}".format(areValidObjects))
				try:	
					returnSolids = ListUtils.processList(self.getDynamoSolid,unWrappedElements, geo_options, **kwargs)
					
				except Exception as ex:
					Errors.catch(ex, "Exception in RTD_model.getDynamoSolids() - \
						returnSolids = ListUtils.processList(self.getDynamoSolid,unWrappedElements, geo_options) failed.")
					return []

				trans.RollBack()
				TransactionManager.Instance.TransactionTaskDone()
				return returnSolids
			except Exception as ex:
				trans.RollBack()
				Errors.catch(ex, "Exception remove_inserts == True block in RTD_model.getDynamoSolids()")
		elif remove_inserts == False or len(uniqueInsertIds) == 0:
			geo_options = Autodesk.Revit.DB.Options()
			if view == None: geo_options.DetailLevel = detail_lvl
			geo_options.IncludeNonVisibleObjects = inc_invis
			if view != None: geo_options.View = view
			try:	
				returnSolids = ListUtils.processList(self.getDynamoSolid,unWrappedElements, geo_options, **kwargs)
				return returnSolids
			except Exception as ex:
				Errors.catch(ex, "Exception in elif block of (if remove_inserts == True and len(uniqueInsertIds) \
								in ListUtils.processList(getDynamoSolid,unWrappedElements, geo_options) in RTD_model.getDynamoSolids() failed.")
				return []
	def isValid(self, item):
		return False if item.IsValidObject == False else True
	def getDynamoSolid(self, item, *args, **kwargs):
		"""
			acquire dynamo geometry as Solid from Revit.DB.Element object
			Element must be unwrapped - use Unwrap() function before input as item

			arg: item type: Autodesk.Revit.DB.Element object
			
			args[0]: Geometry options type: Autodesk.Revit.DB.Options
			kwargs["incCW"] type: bool - including curtain walls if true, default = True

			Returns: dynamoGeometry type: Autodesk.DesignScript.Geometry.Solid

		"""
		# try:
		# 	if 'incCW' in kwargs:
		# 		raise NameError('incCW is set to {}'.format(kwargs['incCW']))
		# except Exception as es:
		# 	Errors.catch(ex, "incCW in RTD_model.getDynamoSolid")
		#Errors.catchVar(item,"RTD_Model.getDynamoSolid{0}".format(item.Id))
		geo_options = args[0] if len(args) > 0 else self.geo_options 
		incCW = kwargs['incCW'] if 'incCW' in kwargs else True
		#incCW = False
		if item.GetType().Name == "CurtainSystem" or (item.GetType().Name == "Wall" and item.CurtainGrid != None):
			try:
				if incCW == True:
					return self.getCurtainWallSimplyfiedGeometry(item, thickness=80)
				else:
					return None
			except Exception as ex:
				Errors.catch(ex, "getCurtainWallSimplyfiedGeometry in RTD_model.getDynamoSolid() failed.")
		elif self.isValid(item):
			if type(item) !=list:
				revitGeo = item.Geometry[geo_options]
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
			try:
				dynamoGeometry = revit_geo.ToProtoType()
			except Exception as ex:
				Errors.catch(ex, "error in converting geometry in RTD_model.getDynamoSolid() dynamoGeometry = revit_geo.ToProtoType() item ID = {}".format(item.Id.IntegerValue))
				dynamoGeometry = None
			return dynamoGeometry

	def getCurtainWallSimplyfiedGeometry(self, inElement, **kwargs):
		thickness = kwargs["thickness"] if "thickness" in kwargs else 25
		if inElement.GetType().Name == "CurtainSystem":
			curtainSystemGridsIterator = inElement.CurtainGrids.ForwardIterator()
			cells = []
			for curtainGrid in curtainSystemGridsIterator:
				curtainSystemSurfaces = []
				for cell in curtainGrid.GetCurtainCells():				
					curtainSystemSurfaces += [Autodesk.DesignScript.Geometry.Surface.ByPatch(Autodesk.DesignScript.Geometry.PolyCurve.ByJoinedCurves([y.ToProtoType() for y in x])) for x in cell.CurveLoops]
				cells += ListUtils.flatList(curtainSystemSurfaces)
			polySurface = Autodesk.DesignScript.Geometry.PolySurface.ByJoinedSurfaces(cells)
			solid = Autodesk.DesignScript.Geometry.Surface.Thicken(polySurface, thickness, True)
			return solid
		elif inElement.GetType().Name == "Wall":		
			curtainWallGridCells = inElement.CurtainGrid.GetCurtainCells()
			curtainSystemSurfaces = []
			for cell in curtainWallGridCells:				
				curtainSystemSurfaces += [Autodesk.DesignScript.Geometry.Surface.ByPatch(Autodesk.DesignScript.Geometry.PolyCurve.ByJoinedCurves([y.ToProtoType() for y in x])) for x in cell.CurveLoops]
			polySurface = Autodesk.DesignScript.Geometry.PolySurface.ByJoinedSurfaces(curtainSystemSurfaces)
			solid = Autodesk.DesignScript.Geometry.Surface.Thicken(polySurface, thickness, True)
			return solid
	
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

	def getOuterShells(self, inGroupedSolids, *args, **kwargs):
		"""
			returns 1D list of solids representing outer shell of building object.

			args:
				inGroupedSolids: list of grouped solid acquired by using function groupSolids()
				outer shells are placed at first positions in sublists of inGroupedSolids
			kwargs['innerShell'] type bool, if true function returns inner shells else returns outer shell, default is False 
			return: list of solids 
		"""
		innerShell = kwargs['innerShell'] if 'innerShell' in kwargs else False
		returnItems = []
		innerShells = []
		for i in inGroupedSolids:
			innerShells.append(i[1:])
			returnItems.append(i[0])
		if innerShell:
			return innerShells
		else:
			return returnItems
	
	def getOuterShellIntersectingSurfaces(self, inOuterShells, inSolids, inRevitElements, **kwargs):
		returnList = []
		flattenedList = []
		self.openedOuterShellPolysurfaces = []
		self.closedOuterShellPolysurfaces = []
		for outerShell in inOuterShells:
			outerShellpolySurface = Autodesk.DesignScript.Geometry.PolySurface.BySolid(outerShell)
			outerShellSurfaces = list(outerShellpolySurface.Surfaces())
			outerShellSurfaces.sort(key = lambda c : c.Area, reverse=False)
			removedSurface = outerShellSurfaces.pop(0)
			#del outerShellSurfaces[0]	
			openedOuterShellPolysurface = Autodesk.DesignScript.Geometry.PolySurface.ByJoinedSurfaces(outerShellSurfaces)
			closedOuterShellPolysurface = Autodesk.DesignScript.Geometry.Surface.Join(openedOuterShellPolysurface, removedSurface)
			#closedOuterShellPolysurface = Autodesk.DesignScript.Geometry.PolySurface.ByJoinedSurfaces(closedOuterShellSurfaces)
			#filterMask = openedOuterShellPolysurface.DoesIntersect(inSolids)
			intersectedElements = processList(self.doesIntersect, inSolids, closedOuterShellPolysurface, removedSurface)
			returnCategories = []
			# if "openings" in kwargs and kwargs["openings"] == True:
			# 	openingSolids = self.extractedOpenings
			# 	inSolids = inSolids + openingSolids
			# else:
			# 	pass
			for c, category in enumerate(inSolids):
				returnItems = []
				for i, item in enumerate(category):
					myType = type(item)
					if  myType == Autodesk.DesignScript.Geometry.Solid and intersectedElements[c][i] == True:
						intersection = item.Intersect(closedOuterShellPolysurface)
						if ListUtils.isIterable(intersection):
							filteredIntersection = filter(lambda x: x.__class__.__name__ == "Surface", intersection)
							if len(filteredIntersection) > 0:
								returnItems.append((filteredIntersection, inRevitElements[c][i]))
						else:
							if intersection.__class__.__name__ == "Surface":
								returnItems.append(([intersection], inRevitElements[c][i]))
						#flattenedList.append(item.Intersect(openedOuterShellPolysurface))
						#myflattenedList = ListUtils.flatList(flattenedList, maxLevel = 0)
					#else:
					#	returnItems.append([])
				returnCategories.append(returnItems)
			self.openedOuterShellPolysurfaces.append(openedOuterShellPolysurface)
			self.closedOuterShellPolysurfaces.append(closedOuterShellPolysurface)
			returnList.append(returnCategories)
		return returnList

	def doesIntersect(self, item, *args):
		inPolysurface = args[0]
		inRemovedSurface = args[1] if len(args) > 1 else None
		if type(item) == Autodesk.DesignScript.Geometry.Solid:
			if item.DoesIntersect(inPolysurface):
				return True
			elif item.DoesIntersect(inRemovedSurface):
				return True
			else:
				return []
		else:
			return []	

class EnAnalyse(object):
	"""

		inDoc:	CurrentDBDocument type: DocumentManager.Instance.CurrentDBDocument
		inRTD_model: revit to dynamo model type: RTD_model

	"""

	def __init__(self, inDoc, inRTD_model):
		self.model = inRTD_model	
		self.check = []	
		self.setup()
		
	
	def setup(self):
		"""
		flattenedSolids = ListUtils.flatList(self.model.dynamoSolids)
		flattenedSolidsWithOpenings = ListUtils.flatList(self.model.dynamoSolidsWithOpenings)		
		#drop out unassigned items
		filteredFlattenedSolids = filter(lambda x: x!=None, flattenedSolids)
		filteredFlattenedSolidsWithOpenings = filter(lambda x: x!=None, flattenedSolidsWithOpenings)
		#make solid union of all solids representing element geometry and extract inner and outer shells from this union
		self.unitedSolid = Autodesk.DesignScript.Geometry.Solid.ByUnion(filteredFlattenedSolids)
		self.unitedSolidWithOpenings = Autodesk.DesignScript.Geometry.Solid.ByUnion(filteredFlattenedSolidsWithOpenings)
		
		polySurfaces = Autodesk.DesignScript.Geometry.PolySurface.BySolid(self.unitedSolid)
		extractedSolids = list(Autodesk.DesignScript.Geometry.PolySurface.ExtractSolids(polySurfaces))

		self.groupedSolids = self.groupSolids(extractedSolids)
		#model consistency test for outer and inner solids (outer solid is at index 0 inner solids are at indices > 0)
		for i, obj in enumerate(self.groupedSolids):
			if len(obj) < 2:
				ModelConsistency.catch("Err_01", "OBJ-{0}".format(i))

		self.outerShells = self.getOuterShells(self.groupedSolids)
		
		self.outerShellPolysurfaces = []
		self.rawOuterShellAreas = []
		for outerShell in self.outerShells:
			pSurface = Autodesk.DesignScript.Geometry.PolySurface.BySolid(outerShell)
			self.outerShellPolysurfaces.append(pSurface)
			self.rawOuterShellAreas.append(pSurface.Area * 0.000001)
		
		"""
		#outerShellpolySurface = Autodesk.DesignScript.Geometry.PolySurface.BySolid(self.outerShells[0])
		
		"""
		self.facesArea = ListUtils.processList(self.getFacesArea, self.outerShellIntersectingSurfaces)

		#self.outerShellIntersectingOpenings = self.getOuterShellIntersectingSurfaces(self.outerShells, self.dynamoOpenings, self.openingElements)
		#self.outerShellIntersectingSurfacesWithOpenings = self.getOuterShellIntersectingSurfaces(self.outerShells, self.dynamoSolidsWithOpenings, self.revitElements)
		"""

		self.quantities = ListUtils.processList(self.getQuantities, self.model.outerShellIntersectingSurfaces)
		self.overalAreaOfEnvelope = [Autodesk.DesignScript.Geometry.PolySurface.BySolid(x).Area/1000000 for x in self.model.outerShells]
		self.overalAreaOfEnvelopeSurfaces = []
		self.openingsArea = []
		self.nonTransparentConstructionArea = []
		self.curtainWallsArea = []
		for obj in self.quantities:
			self.openingsArea.append(self.getQuantityAreas(obj[6]))
			self.curtainWallsArea.append(self.getQuantityAreas(obj[5]))
			self.overalAreaOfEnvelopeSurfaces.append(self.getQuantityAreas(obj))
			self.nonTransparentConstructionArea.append(self.getQuantityAreas(obj[:4]))	

		self.averageHeatTransferCoefficient = self.getAHTC(self.quantities)
		# # points = [Autodesk.DesignScript.Geometry.Point.ByCoordinates(0,0), \
		# # 		  Autodesk.DesignScript.Geometry.Point.ByCoordinates(10000,0), \
		# # 		  Autodesk.DesignScript.Geometry.Point.ByCoordinates(10000,10000), \
		# # 		  Autodesk.DesignScript.Geometry.Point.ByCoordinates(0,10000)
		# # 		]
		# #self.surfaceArea = Autodesk.DesignScript.Geometry.Surface.ByPerimeterPoints(points).Area
		self.facesArea = ListUtils.processList(self.getFacesArea, self.quantities)

		
	def getQuantityAreas(self, _list, *args, **kwargs):
		"""Iterates trough input list and aplies a function to each item of the list

			args:
				_func: name of the func type: callable
				_list: input list - type: list 
				*args: arguments for input function

			return: list of the same structure as input list - type: list
		"""
		#partialSum = kwargs["partialSum"] if "partialSum" in kwargs else None
		try:
			if type(_list)==tuple:
				self.check.append(_list[-1])
				return _list[-1]		
			elif type(_list) == list:
				partialAreas = []
				for item in _list:
					partialArea = self.getQuantityAreas(item, *args, **kwargs)
					partialAreas.append(partialArea)
				partialSum = sum(partialAreas) if len(partialAreas) > 0 else 0
				return partialSum
		except Exception as ex:
			Errors.catch(ex, "{}".format(self.check))

	def getAreaOfItem(self, *args, **kwargs):
		if type(x)==tuple:
			return ()

	def getAHTC(self, quantities):
		"""

			returns Average Heat Transfer Coefficient (AHTC) of outer shell:

			item:  Autodesk.Revit.DB.Element
			
			return: avgThCon type: float
		"""		
			
		objectAreas = []		
		for obj in quantities:
			objectArea = .0
			categoryAreas = []
			for category in obj:
				categoryArea = .0
				elAreas = []	
				for el in category:
					if type(el) == tuple:
						elArea = sum([a.Area for a in el[2]])
						categoryArea += elArea
						elAreas.append(elArea/1000000)
				categoryAreas.append((categoryArea/1000000, elAreas))
				objectArea += categoryArea/1000000
			objectAreas.append((objectArea, categoryAreas))
		return (objectAreas, [b.Area/1000000 for b in self.model.outerShells])

	def getArea(self, item):
		areas = []
		if type(item) == tuple:
			areas.append(item[0])
			for x in item[1]:
				areas.append(x.Area) if hasattr(x, "Area") else 0
			return areas
		else:
			return []
	
	def getFacesArea(self, inItem):
			return "{}".format(type(inItem))


	def getQuantities(self, item, *args, **kwargs):
		"""
			returns tuple of geometry and quantities associated with material parameters prepared for next evaluation:

			item:  Autodesk.Revit.DB.Element				  
			
			return: (
					 Autodesk.Revit.DB.Element,
					 elementCategory type: str, 
					 list[Autodesk.DesignScript.Geometry.surface, ...], 
					 list[list[Autodesk.Revit.DB.Material, Autodesk.Revit.DB.Material.Name, thermalConductivity type: float], Autodesk.Revit.DB.WallType.ThermalProperties.HeatTransferCoefficient type: float] 
					 	or list[Autodesk.Revit.DB.Material, Autodesk.Revit.DB.RoofType.ThermalProperties.HeatTransferCoefficient type: float]
					 structureWidth type: list[overalWidth type: int, list[layerWidth type: int, ..]]
					 area type: float
					 )
		"""
		onlyMaterial = kwargs['onlyMaterial'] if 'onlyMaterial' in kwargs else False
		self.modelMaterials = []
		structureMaterial = "Material Not Acquired Yet !!!"
		structureWidth = "Width Not Acquired Yet !!!"
		elementCategory = "Category Not Acquired Yet !!!"
		if type(item)== tuple:
			if isinstance(item[-1], Autodesk.Revit.DB.Element):
				if item[-1].__class__.__name__ == "CurtainSystem" or item[-1].__class__.__name__ == "Wall":
					if item[-1].GetType().Name == "CurtainSystem" or (item[-1].GetType().Name == "Wall" and item[-1].CurtainGrid != None):
						structureMaterial = "this is CurtainSystem with assigned heat transfer coeficient"
						structureWidth = "Curtain System width"
					else:
						structureMaterial = self.getItemMaterials(item)
						structureWidth = self.getCompoundStructureLayersWidth(item[-1].WallType)
				elif hasattr(item[-1], "RoofType"):
					structureMaterial = structureMaterial = self.getItemMaterials(item)
					structureWidth = self.getCompoundStructureLayersWidth(item[-1].RoofType)
				elif hasattr(item[-1], "FloorType"):
					structureMaterial = self.getItemMaterials(item)
					structureWidth = self.getCompoundStructureLayersWidth(item[-1].FloorType)
				elif self.model.getCategoryName(item[-1]) == "Windows":
					structureMaterial = "this is Window with assigned heat transfer coeficient"
					overalWidth = Autodesk.Revit.DB.UnitUtils.ConvertFromInternalUnits( \
						item[-1].Host.Width, Autodesk.Revit.DB.DisplayUnitType.DUT_MILLIMETERS)
					structureWidth = overalWidth
				elif self.model.getCategoryName(item[-1]) == "Doors":
					structureMaterial = "this is Door with assigned heat transfer coeficient"
					overalWidth = Autodesk.Revit.DB.UnitUtils.ConvertFromInternalUnits( \
						item[-1].Host.Width, Autodesk.Revit.DB.DisplayUnitType.DUT_MILLIMETERS)
					structureWidth = overalWidth
				else:
					myElementCategory = item[-1].Category.Name
					myElementCategoryId = item[-1].Category.Id
					myElementCategorySubcategories = item[-1].Category.SubCategories
					myElementCategoryType =  item[-1].Category.GetCategory(self.model.doc, item[-1].Category.Id).Name
					myElementCategoryMaterial = item[-1].GetMaterialIds(True)
					#myElementCategoryMaterialName = myElementCategoryMaterial.Category
					structureMaterial = myElementCategoryMaterial
				if type(structureMaterial) or type(structureMaterial) == list:
					for material in structureMaterial:
						if hasattr(material, "Id"):
							if material.Id.IntegerValue not in self.modelMaterials:
								self.modelMaterials.append(material.Id.IntegerValue)
				else:
					if hasattr(structureMaterial, "Id"):
						if structureMaterial.Id.IntegerValue not in self.modelMaterials:
							self.modelMaterials.append(structureMaterial.Id.IntegerValue)
				elementCategory = item[-1].Category.Name
				
				return (item[-1], item[-1].__class__.__name__ if item[-1].__class__.__name__ != "FamilyInstance" else item[-1].Category.Name, item[0], structureMaterial, structureWidth, sum([a.Area for a in item[0]])/1000000)
		else:
			return []

	def getThermalAssetProperties(self, inMaterial, **kwargs):
		if inMaterial.ThermalAssetId.IntegerValue < 0:
			return None			
		else:
			thermallAssetId = inMaterial.ThermalAssetId
			propertySetElement = self.model.doc.GetElement(thermallAssetId)
			thermalAss = propertySetElement.GetThermalAsset()
			return thermalAss

	def getItemMaterials(self, item):
		cStructure = None
		if hasattr(item[-1], "RoofType"):
			cStructure = item[-1].RoofType.GetCompoundStructure()
		elif hasattr(item[-1], "FloorType"):
			cStructure = item[-1].FloorType.GetCompoundStructure()
		elif hasattr(item[-1], "WallType"):
			cStructure = item[-1].WallType.GetCompoundStructure()		
		materials = None
		if cStructure != None:
			materials = self.getCompoundStructureMaterials(item)
		else:
			materials = self.getOneComponentStructureMaterial(item)
		return materials

	def getOneComponentStructureMaterial(self, item):
		if not hasattr(item[-1], "RoofType") or not hasattr(item[-1], "FloorType") or hasattr(item[-1], "WallType"):
			myElementCategory = item[-1].Category.Name
			myElementCategoryId = item[-1].Category.Id
			myElementCategorySubcategories = item[-1].Category.SubCategories
			myElementCategoryType =  item[-1].Category.GetCategory(self.model.doc, item[-1].Category.Id).Name
			myElementCategoryMaterials = item[-1].GetMaterialIds(True)
			for mat in list(myElementCategoryMaterials):
				if self.getThermalAssetProperties(mat) != None:
					try:
						assProperties = self.getThermalAssetProperties(mat)
					except Exception as ex:
						Errors.catch(ex, "Error in Analyse.EnAnalyse.getCompoundStructureMaterials() in else block of if cStructure != None: One component structure Material has no attribute ThermalAssetProperties.")
						assProperties = None
					if assProperties:
						tC = assProperties.ThermalConductivity
						thermalConductivity = Autodesk.Revit.DB.UnitUtils.ConvertFromInternalUnits( \
								tC, Autodesk.Revit.DB.DisplayUnitType.DUT_WATTS_PER_METER_KELVIN)
					else:
						thermalConductivity = None					#thermalConductivity = assProperties.ThermalConductivity
										
				else:
					thermalConductivity = None
					materialName = mat.Name
					materials.append((mat,materialName,thermalConductivity))
			return (materials)

	def getCompoundStructureMaterials(self, item):
		"""
			returns list of materials according to layers for objects that has GetCompoundStructure callable attribute:

			arg1: item type Autodesk.Revit.DB.Element > All classes inherited from Autodesk.Revit.DB.Element containing 
				  GetCompoundStructure() method -(e.g. Autodesk.Revit.DB.WallType, Autodesk.Revit.DB.RoofType, Autodesk.Revit.DB.FloorType)
			
			return: list[Autodesk.Revit.DB.Material, ...]
		"""
		cStructure = None
		if hasattr(item[-1], "RoofType"):
			cStructure = item[-1].RoofType.GetCompoundStructure()
			htc = item[-1].RoofType.ThermalProperties.HeatTransferCoefficient
		elif hasattr(item[-1], "FloorType"):
			cStructure = item[-1].FloorType.GetCompoundStructure()
			htc = item[-1].FloorType.ThermalProperties.HeatTransferCoefficient
		elif hasattr(item[-1], "WallType"):
			cStructure = item[-1].WallType.GetCompoundStructure()			
			htc = item[-1].WallType.ThermalProperties.HeatTransferCoefficient
			#heatTransferCoeficient = Autodesk.Revit.DB.UnitUtils.ConvertFromInternalUnits( \
			#				tC, Autodesk.Revit.DB.DisplayUnitType.DUT_WATTS_PER_METER_KELVIN)
		else:
			htc = None
		materials = []
		if cStructure != None:
			layers = cStructure.GetLayers()			
			for layer in layers:
				materialID = layer.MaterialId
				# If  materialID.IntegerValue < 0 --> element has no assigned material. Category Material will be used 
				if materialID.IntegerValue < 0:
					myId = item[-1].Id
					myCategory = item[-1].Category
					myCategoryMaterial = myCategory.Material
					
					if self.getThermalAssetProperties(myCategoryMaterial) != None:
						try:
							assProperties = self.getThermalAssetProperties(myCategoryMaterial)							
						except Exception as ex:
							Errors.catch(ex, "Error in Analyse.EnAnalyse.getCompoundStructureMaterials() - CompoundStructure Category Material has no attribute ThermalAssetProperties.")							
							assProperties = None
							#thermalConductivity = assProperties
						if assProperties:
							tC = assProperties.ThermalConductivity
							thermalConductivity = Autodesk.Revit.DB.UnitUtils.ConvertFromInternalUnits( \
								tC, Autodesk.Revit.DB.DisplayUnitType.DUT_WATTS_PER_METER_KELVIN)						
						else:
							thermalConductivity = None
							ModelConsistency.catch("Err_03", item[-1].Id)
					else:							
						thermalConductivity = None
						ModelConsistency.catch("Err_03", item[-1].Id.IntegerValue)				
					myCategoryMaterialName = myCategoryMaterial.Name
					materials.append((myCategoryMaterial, myCategoryMaterialName, thermalConductivity))
				else:
					material = self.model.doc.GetElement(materialID)
					if self.getThermalAssetProperties(material) != None:
						try:
							assProperties = self.getThermalAssetProperties(material)
						except Exception as ex:
							Errors.catch(ex, "Error in Analyse.EnAnalyse.getCompoundStructureMaterials() in else block of (if materialID.IntegerValue < 0:) - Compound Structure Assigned Material has no attribute ThermalAssetProperties.")
							assProperties = None
					else:
						assProperties = None
						
					if assProperties:
						#thermalConductivity = assProperties
						tC = assProperties.ThermalConductivity
						thermalConductivity = Autodesk.Revit.DB.UnitUtils.ConvertFromInternalUnits( \
							tC, Autodesk.Revit.DB.DisplayUnitType.DUT_WATTS_PER_METER_KELVIN)
					else:
						thermalConductivity = None					
					materialName = material.Name
					materials.append((material, material.Name, thermalConductivity))
			materials.append(htc)
			return (materials)
		else:
			return None	

		# layers = item.GetCompoundStructure().GetLayers()
		# layersIndxs = [i for i, x in enumerate(layers)]
		# layersCount = item.GetCompoundStructure().LayerCount
		# materialIds = [item.GetCompoundStructure().GetMaterialId(x) for x in layersIndxs]
		# materialElements = [self.model.doc.GetElement(x) for x in materialIds]
		#materialProperties = [x.Parameter for x in materialElements]


	def getCompoundStructureLayersWidth(self, item):
		"""
			returns Width parameter of Autodesk.Revit.DB.Element that has GetCompoundStructure callable attribute:

			arg1: item type Autodesk.Revit.DB.Element > All classes inherited from Autodesk.Revit.DB.Element containing 
				  GetCompoundStructure() method -(e.g. Autodesk.Revit.DB.WallType, Autodesk.Revit.DB.RoofType, Autodesk.Revit.DB.FloorType)
			
			return: list[Autodesk.Revit.DB.Material, ...]
		"""
		try:
			if hasattr(item, "GetCompoundStructure"):
				overalWidth = Autodesk.Revit.DB.UnitUtils.ConvertFromInternalUnits( \
						item.GetCompoundStructure().GetWidth(), Autodesk.Revit.DB.DisplayUnitType.DUT_MILLIMETERS)
				layers = item.GetCompoundStructure().GetLayers()
				widthsInMm = [Autodesk.Revit.DB.UnitUtils.ConvertFromInternalUnits( \
								x.Width, Autodesk.Revit.DB.DisplayUnitType.DUT_MILLIMETERS) \
								for x in layers]
				return (overalWidth, widthsInMm)
			else:
				raise AttributeError("Input object has no attribute GetCompoundStructure.")
		except Exception as ex:
			Errors.catch(ex, "Getting layers Width in Analyse.EnAnalyse.getCompoundStructureLayersWidth() failed")

	def doesIntersect(self, item, *args):
		inPolysurface = args[0]
		inRemovedSurface = args[1] if len(args) > 1 else None
		if type(item) == Autodesk.DesignScript.Geometry.Solid:
			if item.DoesIntersect(inPolysurface):
				return True
			elif item.DoesIntersect(inRemovedSurface):
				return True
			else:
				return []
		else:
			return []	

	def prepareOuterShellSolidForIntersection(self, inOuterShellSolid, **kwargs):
		pSurface = Autodesk.DesignScript.Geometry.PolySurface.BySolid(inOuterShellSolid)
		surfaces = Autodesk.DesignScript.Geometry.PolySurface.Surfaces(pSurface)
		surfaces.sort(key = lambda c : c.Area, reverse=False)
		smallestFace = surfaces[0]
		surfacesWithoutSmallest = surfaces[:-(len(surfaces)-1)]
		polySurface = Autodesk.DesignScript.Geometry.PolySurface.ByJoinedSurfaces(surfacesWithoutSmallest)
		joinedSurfaces = Autodesk.DesignScript.Geometry.Surface.Join(polySurface, smallestFace)

class MaterialMapper():
	def __init__(self):
		pass


# class MainForm(Form):
# 	def __init__(self):
# 		self.InitializeComponent()
	
# 	def InitializeComponent(self):
# 		self.Text = "SWECO INIT SCRIPTS"
# 		self.Width = 500
# 		self.Height = 200

# 		self.label = Label()
# 		self.label.Text = "Potvrď spuštění iniciačních skriptů pro update parametrů ve výkresu"
# 		self.label.Width = 250
# 		self.label.Parent = self
# 		self.label.Anchor = AnchorStyles.Top
# 		self.label.Dock = DockStyle.Top

# 		self.submitButton = Button()
# 		self.submitButton.Text = 'OK'
# 		self.submitButton.Click += self.update
# 		self.submitButton.Parent = self
# 		self.submitButton.Anchor = AnchorStyles.Bottom
# 		self.submitButton.Dock = DockStyle.Bottom

# 		self.cancelButton = Button()
# 		self.cancelButton.Text = 'Cancel'
# 		self.cancelButton.Click += self.close
# 		self.cancelButton.Parent = self
# 		self.cancelButton.Anchor = AnchorStyles.Bottom
# 		self.cancelButton.Dock = DockStyle.Bottom

# 	def runScripts(self):
# 		pass

# 	def update(self, sender, event):
# 		self.runScripts()
# 		#self.Close()

# 	def close(self, sender, event):
# 		self.Close()
# 	def OnChanged(self, sender, event):
# 		self.label.Text = sender.Text


# def Unwrap(item, *args):
# 	return UnwrapElement(item)
