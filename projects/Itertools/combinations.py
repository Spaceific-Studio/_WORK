
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
print("kdTree: {0}".format(kdTree.tree))
inspPoint(1,1,1)
nearest = kdTree.get_nearest(kdTree.tree, inspPoint, 3, KD_Tree.dist_sq)
print("nearest point to {0} is {1}".format(inspPoint, nearest))
myList = []
for n in range(0,10):
    myList.append(n)
cmbns = [x for x in itertools.combinations(myList, 2)]
print("myList {0}".format(myList))
print("cmbns {0} len {1}".format(cmbns, len(cmbns)))