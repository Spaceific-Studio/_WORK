    
import itertools
import platform
import sys
import random
#print(dir(sys))
print("platform.sys {0}".format(platform.sys))
print("platform.platform() {0}".format(platform.platform()))
print("platform.os {0}".format(platform.os))
print("platform.system {0}".format(platform.system()))
print("sys.prefix {0}".format(sys.prefix))
print("sys.version {0}".format(sys.version))


if platform.system() == "Linux":
    libPath = r"/storage/emulated/0/_WORK/REVIT_API/LIB"
elif platform.system() == "Windows":
    libPath = r"H:/_WORK/PYTHON/REVIT_API/LIB"

sys.path.append(libPath)

from SpaceOrganize import KD_Tree

points = [(random.randint(0,10), random.randint(0,10), random.randint(0,10)) for x in range(0,10)]
print("points {0}".format(points))

kdTree = KD_Tree(points)
print("kdTree: {0} dim {1}".format(kdTree.tree, kdTree.dim))
inspPoint = (7,3,4)
#get nearest point
nearest = kdTree.get_nearest(kdTree.tree, inspPoint, kdTree.dim, kdTree.dist_sq_dim)
#get k nearest points
k = 10
kNearest = kdTree.get_knn(kdTree.tree, inspPoint, k, kdTree.dim, kdTree.dist_sq_dim)

print("nearest point to {0} is {1}".format(inspPoint, nearest))
print("kNearest points to {0} is {1} len {2}".format(inspPoint, kNearest, len(kNearest)))

myList = []
for n in range(0,10):
    myList.append(n)
cmbns = [x for x in itertools.combinations(kNearest, 2)]
print("myList {0}".format(myList))
print("cmbns {0} len {1}".format(cmbns, len(cmbns)))