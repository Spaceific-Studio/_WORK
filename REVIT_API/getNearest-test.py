# Enable Python support and load DesignScript library
import sys
import time
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
lib_path = r'H:\_WORK\PYTHON\REVIT_API\LIB'
sys.path.append(pyt_path)
sys.path.append(lib_path)

import clr
#import heapq
from SpaceOrganize import *
clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *

# The inputs to this node will be stored as a list in the IN variables.
inPoints = IN[0] 
surveyPoint = IN[1]

sTime = time.time()
kdTree = KD_Tree(inPoints)
eTime = time.time()
myTime = eTime - sTime
treeCreationTime_time = "treeCreationTime_time - {}s".format(myTime)

sTime = time.time()
nearestPoint = kdTree.get_nearest(kdTree.tree, (surveyPoint.X, surveyPoint.Y, surveyPoint.Z), 3, kdTree.dist_sq_dim)
eTime = time.time()
myTime = eTime - sTime
nearestPoint_time = "nearestPoint_time - {}s".format(myTime)
sTime = time.time()
nearestDSPoint = kdTree.get_nearest(kdTree.DSPointsTree, surveyPoint, 3, kdTree.dist_sq_dim)
eTime = time.time()
myTime = eTime - sTime
nearestDSPoint_time = "nearestDSPoint_time - {}s".format(myTime)
sTime = time.time()
knnDSPoint = kdTree.get_knn(kdTree.DSPointsTree, surveyPoint, 10, 3, kdTree.dist_sq_dim)
eTime = time.time()
myTime = eTime - sTime
knnDSPoint_time = "knnDSPoint_time - {}s".format(myTime)
# Place your code below this line

#OUT = kdTree.DSPointsTree
OUT = (nearestPoint, nearestDSPoint, knnDSPoint,(treeCreationTime_time, nearestPoint_time, nearestDSPoint_time, knnDSPoint_time))