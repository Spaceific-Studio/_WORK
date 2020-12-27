# -*- coding: utf-8 -*-
# Copyright(c) 2020, Daniel Gercak
#Classes for organizing elements in space and for space analases
#e.g. kD_Trees...
#resource_path: H:\_WORK\PYTHON\REVIT_API\LIB\SpaceOrganize.py
import sys

try:
	sys.modules['__main__']
	hasMainAttr = True	
except:
	hasMainAttr = False
	
try:
	sys.modules['Autodesk']
	hasAutodesk = True	
except:
	hasAutodesk = False

print("module : {0} ; hasMainAttr = {1}".format(__file__, hasMainAttr))
print("module : {0} ; hasAutodesk = {1}".format(__file__, hasAutodesk))

	
if hasMainAttr:
	#import clr
	if "pydroid" in sys.prefix:
	    pass
	else:
	    from Autodesk.Revit.UI.Selection import *
	    import Autodesk.Revit.DB as DB
	    doc = __revit__.ActiveUIDocument.Document
	    #clr.AddReference("RevitServices")
	    #import RevitServices
	    #from RevitServices.Transactions import TransactionManager
	    pass

else:
	if "pydroid" in sys.prefix:
	    pass
	else:
	    import clr
	    clr.AddReference('ProtoGeometry')
	    from Autodesk.DesignScript.Geometry import *

# clr.AddReference("RevitAPI")
# import Autodesk
# import Autodesk.Revit.DB as DB

pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
lib_path = r'H:\_WORK\PYTHON\REVIT_API\LIB'
sys.path.append(lib_path)
sys.path.append(pyt_path)

#clr.AddReference('ProtoGeometry')
#from Autodesk.DesignScript.Geometry import *

import ListUtils as ListUtils
#from Errors import Errors

import heapq

# clr.AddReference("RevitServices")
# import RevitServices
# from RevitServices.Persistence import DocumentManager
# from RevitServices.Transactions import TransactionManager
# doc = DocumentManager.Instance.CurrentDBDocument

# clr.AddReference("System")
# from System.Collections.Generic import List as Clist
# from System import Enum

# # Import Element wrapper extension methods
# clr.AddReference("RevitNodes")
# import Revit
# clr.ImportExtensions(Revit.Elements)
# clr.ImportExtensions(Revit.GeometryConversion)

class SolidPoint():
	def __init__(self, inSolid):		
		self.solid = inSolid
		boundingBox = BoundingBox.ByGeometry(self.solid)
		cuboid = BoundingBox.ToCuboid(boundingBox)
		centroid = Solid.Centroid(cuboid)
		self.point = centroid

class KD_Tree():
	def __init__(self, inPoints):
		if isinstance(inPoints, list) or isinstance(inPoints, tuple):
			if hasAutodesk:
			    if len(inPoints) > 0 and (inPoints[0].__class__.__name__ == "SolidPoint" or isinstance(inPoints[0], Autodesk.DesignScrtipt.Geometry.Point)):
				    self.points = self.transformDSPoints(inPoints)
				    self.dsPoints = inPoints
				    self.dim = 3
			elif len(inPoints) > 0 and (isinstance(inPoints[0], tuple) or isinstance(inPoints[0], list)):
				self.points = inPoints
				self.dim = len(inPoints[0])
				if self.dim == 3 and hasAutodesk:
					self.dsPoints = [Point.ByCoordinates(x[0], x[1], x[2]) for x in inPoints]
				else:
					self.dsPoints = []
			else:
				raise TypeError("items in list are not of type Autodesk.DesignScrtipt.Geometry.Point or of type tuple e.g. (0.12, 0.10, 0.5) it's of type: {0}".format(type(inPoints[0])))
		else:
			raise TypeError("Argument in KD_Tree constructor must be of type list or tuple")
		self.setup()

	def setup(self):
		self.tree = self.make_kd_tree(self.points, self.dim)
		self.DSPointsTree = self.make_kd_DSPoints_tree(self.dsPoints, self.dim)
		
	def transformDSPoints(self, inPoints):
		return ListUtils.processList(self.returnDSPointAsTuple, inPoints)

	def returnDSPointAsTuple(self, inPoint):
		if inPoint.__class__.__name__ == "Point":
			return (inPoint.X, inPoint.Y, inPoint.Z)
		elif inPoint.__class__.__name__ == "SolidPoint":
			return (inPoint.point.X, inPoint.point.Y, inPoint.point.Z)

	def make_kd_tree(self, points, dim, i=0):
		if len(points) > 1: 
			points = sorted(points, key=lambda x: x[i]) 
			i = (i + 1) % dim 
			half = len(points) >> 1 
			return ( 
				self.make_kd_tree(points[: half], dim, i), 
				self.make_kd_tree(points[half + 1:], dim, i), 
				points[half]) 
		elif len(points) == 1: 
			return (None, None, points[0])
	
	def make_kd_DSPoints_tree(self, points, dim, i=0):
		if len(points) > 1: 
			indexes = [i for x in range(len(points))]
			points = sorted(zip(points, indexes), key= self.getDSPointAxis)
			points, indexes = zip(*points)
			i = (i + 1) % dim 
			half = len(points) >> 1 
			return ( 
				self.make_kd_DSPoints_tree(points[: half], dim, i), 
				self.make_kd_DSPoints_tree(points[half + 1:], dim, i), 
				points[half]) 
		elif len(points) == 1: 
			return (None, None, points[0]) 
	# def make_kd_SolidPoints_tree(self, points, dim, i=0):
	# 	if len(points) > 1: 
	# 		indexes = [i for x in range(len(points))]
	# 		points = sorted(zip(points, indexes), key= self.getDSPointAxis)
	# 		points, indexes = zip(*points)
	# 		i = (i + 1) % dim 
	# 		half = len(points) >> 1 
	# 		return ( 
	# 			self.make_kd_DSPoints_tree(points[: half], dim, i), 
	# 			self.make_kd_DSPoints_tree(points[half + 1:], dim, i), 
	# 			points[half]) 
	# 	elif len(points) == 1: 
	# 		return (None, None, points[0]) 

	def getDSPointAxis(self, inPointWithIndex):
		index = inPointWithIndex[1]
		point = inPointWithIndex[0]
		if index == 0:
			if isinstance(point, Point):
				return point.X
				raise TypeError("getDSPointAxis: {0}".format(point.X))
			elif point.__class__.__name__ == "SolidPoint":
				
				return point.point.X 
			else:
				raise TypeError("item not of type: Autodesk.DesignScript.Geometry.Point, or of type: SolidPoint")
		elif index == 1:
			if isinstance(point, Point):
				return point.Y
			elif point.__class__.__name__ == "SolidPoint":
				return point.point.Y 
			else:
				raise TypeError("item not of type: Autodesk.DesignScript.Geometry.Point, or of type: SolidPoint")
		elif index == 2:
			if isinstance(point, Point):
				return point.Z
			elif point.__class__.__name__ == "SolidPoint":
				return point.point.Z 
			else:
				raise TypeError("item not of type: Autodesk.DesignScript.Geometry.Point, or of type: SolidPoint")
		else:
			raise TypeError("index of point dimensions out of range for (X,Y,Z) index is max 2")

	def get_knn(self, kd_node, point, k, dim, dist_func, return_distances=True, i=0, heap=None): 
		import heapq 
		is_root = not heap 
		if is_root: 
			heap = []

		if kd_node: 
			dist = dist_func(point, kd_node[2])
			if hasAutodesk:
				if isinstance(kd_node[2], Point):
				    dx = self.getDSPointAxis((kd_node[2], i)) - self.getDSPointAxis((point, i))
				else:
				    dx = kd_node[2][i] - point[i]
			else:
			    dx = kd_node[2][i] - point[i]
			if len(heap) < k: 
				#print("len(heap) < k {0} -dist {1} kd_node[2] {2}".format(len(heap), -dist, kd_node[2]))
				if hasAutodesk:
				    if isinstance(kd_node[2], Point):
					    heapq.heappush(heap, (-dist, kd_node[2])) 
				    else:
					    heapq.heappush(heap, (-dist, list(kd_node[2])))
				else:
				    heapq.heappush(heap, (-dist, list(kd_node[2])))
			elif dist < -heap[0][0]: 
				#print("len(heap) < k {0} -dist {1} kd_node[2] {2} -heap[0][0] {3}".format(len(heap), -dist, kd_node[2],-heap[0][0]))
				if hasAutodesk:
				    if isinstance(kd_node[2], Point):
					    heapq.heappushpop(heap, (-dist, kd_node[2])) 
				    else:
					    heapq.heappushpop(heap, (-dist, list(kd_node[2]))) 
				else:
				    heapq.heappushpop(heap, (-dist, list(kd_node[2]))) 
			i = (i + 1) % dim 
			# Goes into the left branch, and then the right branch if needed 
			self.get_knn(kd_node[dx < 0], point, k, dim, dist_func, return_distances, i, heap) 
			if dx * dx < -heap[0][0]: # -heap[0][0] is the largest distance in the heap 
				self.get_knn(kd_node[dx >= 0], point, k, dim, dist_func, return_distances, i, heap) 
		if is_root: 
			#print("ROOT get_knn heap {0}".format(heap))
			myHeap = ((-h[0], h[1]) for h in heap)
			#myHeap1 = iter(((-h[0], h[1]) for h in heap))
			#for he in myHeap1:
			#    print("myHeap1 {0}".format(he))
			neighbors = sorted(myHeap) 
			return neighbors if return_distances else [n[1] for n in neighbors] 

	def get_nearest(self, kd_node, point, dim, dist_func, return_distances=True, i=0, best=None): 		
		if kd_node: 			
			dist = dist_func(point, kd_node[2])
			if hasAutodesk:
			    if isinstance(kd_node[2], Point) or kd_node[2].__class__.__name__ == "SolidPoint":
				    dx = self.getDSPointAxis((kd_node[2], i)) - self.getDSPointAxis((point, i))
			    else:
				    dx = kd_node[2][i] - point[i]
			else:
			    dx = kd_node[2][i] - point[i]
			#dx = self.getDSPointAxis((kd_node[2], i)) if isinstance(kd_node[2], Point) else kd_node[2][i] - self.getDSPointAxis((point, i)) if isinstance(point, Point) else point[i]
			if not best: 
				best = [dist, kd_node[2]] 
			elif dist < best[0] and dist != 0: 
				best[0], best[1] = dist, kd_node[2] 
			i = (i + 1) % dim 
			# Goes into the left branch, and then the right branch if needed 
			self.get_nearest(kd_node[dx < 0], point, dim, dist_func, return_distances, i, best) 
			if dx * dx < best[0]: 
				self.get_nearest(kd_node[dx >= 0], point, dim, dist_func, return_distances, i, best) 
		if return_distances:
			return best
		else:
			return best[1] 
	
	# def get_n(self, kd_node, point, dim, dist_func, return_distances=True, i=0, best=None): 
	# 	if kd_node: 
	# 		dist = dist_func(point, kd_node[2]) 
	# 		dx = kd_node[2][i] - point[i]
	# 		if not best: 
	# 			best = [dist, kd_node[2]] 
	# 		elif dist < best[0] and dist != 0: 
	# 			best[0], best[1] = dist, kd_node[2] 
	# 		i = (i + 1) % dim 
	# 		# Goes into the left branch, and then the right branch if needed 
	# 		self.get_n(kd_node[dx < 0], point, dim, dist_func, return_distances, i, best) 
	# 		if dx * dx < best[0]: 
	# 			self.get_n(kd_node[dx >= 0], point, dim, dist_func, return_distances, i, best) 
	# 	if return_distances:
	# 		return best
	# 	else:
	# 		return best[1] 

	def dist_sq(self,a, b, dim): 
		if (isinstance(a, tuple) and isinstance(b, tuple)) and ((isinstance(a[0], float) and isinstance(b[0], float)) or (isinstance(a[0], int) and isinstance(b[0], int))):
			return sum((a[i] - b[i]) ** 2 for i in range(dim))
		elif ((isinstance(a, Point) and b.__class__.__name__ == "SolidPoint") or (a.__class__.__name__ == "SolidPoint" and isinstance(b, Point)) or (isinstance(a, Point) and isinstance(b, Point)) or (a.__class__.__name__ == "SolidPoint" and b.__class__.__name__ == "SolidPoint")):
			#self.getDSPointAxis(inPointWithIndex):
			return sum((self.getDSPointAxis((a, i)) - self.getDSPointAxis((b, i))) ** 2 for i in range(dim))
		else:
			raise TypeError("dist_sq() in KD_Tree() arguments not of type tuple e.g (1.5, 0.2, 0.4) or (type: Point, index: type int)")

	def dist_sq_dim(self,a, b): 
		#if isinstance(a, tuple) and isinstance(b, tuple):
		return self.dist_sq(a, b, self.dim) 
		#elif isinstance(a, Point) and isinstance(b, Point) and isinstance(a[0], Point) and isinstance(b[0], Point):
		#	pass