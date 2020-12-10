import numpy as np
import time

xSize = 50
ySize = 50
myArray = np.indices((xSize,ySize))
xIndicies = myArray[0]
yIndicies = myArray[1]
pointNum = 200
print("myArray {0} shape {1} dtype {2} \n xIndicies {3} shape {4} dtype {5} \n yIndicies {6} shape {7} dtype {8}" \
		.format( \
			myArray, \
			myArray.shape, \
			myArray.dtype, \
			xIndicies, \
			xIndicies.shape, \
			xIndicies.dtype, \
			yIndicies, \
			yIndicies.shape, \
			yIndicies.dtype \
		)
	)
myPointsX = np.random.randint(0,xSize,(200), dtype = np.uint8)
myPointsY = np.random.randint(0,ySize,(200), dtype = np.uint8)
myPointsX = np.resize(myPointsX,(myPointsX.shape[0],1))
myPointsY = np.resize(myPointsY,(myPointsY.shape[0],1))
myPoints = np.append(myPointsX, myPointsY, axis = 1)
print("myPointsX {0} \n myPointsY {1} \n shape myPointsX {2} \n shape myPointsY {3}".format(myPointsX, myPointsY, myPointsX.shape, myPointsY.shape))
print("myPoints {0} \n shape myPoints {1}".format(myPoints, myPoints.shape))
def getDistance(inMx, inPoint):
	originX = inMx[0] - inPoint[0]
	originY = inMx[1] - inPoint[1]
	originDist = np.sqrt(originX**2 + originY**2)
	print("originX {0} shape {1} dtype {2} \n originY {3} shape {4} dtype {5} \n originDist {6} shape {7} dtype {8}" \
		.format( \
			originX, \
			originX.shape, \
			originX.dtype, \
			originY, \
			originY.shape, \
			originY.dtype, \
			originDist , \
			originDist.shape, \
			originDist.dtype \
		)
	)
	return np.argmin(originDist)
def getClosestPoint(inMxIndicies, inPoints):
	indiciesT = np.transpose(inMxIndicies,(1,2,0))
	indiciesT = np.resize(indiciesT, (1, indiciesT.shape[0], indiciesT.shape[1], indiciesT.shape[2]))
	indicies = np.broadcast_to(indiciesT,(inPoints.shape[0], indiciesT.shape[1], indiciesT.shape[2], indiciesT.shape[3]))
	points = np.resize(inPoints, (inPoints.shape[0], 1,1, inPoints.shape[1]))
	points = np.broadcast_to(points,(points.shape[0], xSize, ySize, inPoints.shape[1]))
	origin = indicies - points
	print("indicies {0} \n shape {1}".format(indicies, indicies.shape))
	print("points {0} \n shape {1}".format(points, points.shape))
	print("origin {0} \n shape {1}".format(origin, origin.shape))
sTime = time.time()
myPoint = getDistance(myArray, myPoints[0])
eTime = time.time()
myTime = eTime - sTime
print("myPoint {}".format(myPoint))
print("myTime {0:d}m {1:.6f}s".format(int(myTime/60), myTime%60))
sTime = time.time()
getClosestPoint(myArray, myPoints)
eTime = time.time()
myTime = eTime - sTime
print("getClosestPoint myTime {0:d}m {1:.6f}s".format(int(myTime/60), myTime%60))