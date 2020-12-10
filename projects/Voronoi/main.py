import random
import sys
import os
from scipy.spatial import Voronoi, voronoi_plot_2d
import numpy as np
import math
from PIL import Image, ImageColor, ImageDraw
import time
import matplotlib.pyplot as plt
import platform
import itertools
import heapq


if "Windows" in platform.uname():
    lib_path = r'C:/_WORK/PYTHON/LIB'
else:
    lib_path = r"/storage/18D4-6C41/PYTHON/LIB"
sys.path.append(lib_path)
import ListUtils
from NumpyUtils import *
from IO_Utils import *

class Divide():
    def __init__(self):
        self.setup()
    def setup(self):
        self.x = 1000
        self.y = 1777
        self.pointNum = 500
        if "Windows" in platform.uname():
            self.path =  r'C:/_WORK/PYTHON/projects/Voronoi/'
        else:
            self.path = r"/storage/emulated/0/qpython/projects/Voronoi/"
        self.subDir = "0005/"
        
        self.mx = np.ones((self.x, self.y), dtype=np.float64)
        self.rndPointsX = np.random.randint(0,self.x, (self.pointNum))
        self.rndPointsXDtype = np.dtype([('x', '<i4')])
        #self.rndPointsX = np.asarray(self.rndPointsX,dtype=self.rndPointsXDtype)  
        self.rndPointsX.resize((self.rndPointsX.shape[0],1))
        self.rndPointsY = np.random.randint(0,int(self.y-self.y*0), (self.pointNum))
        self.rndPointsYDtype = np.dtype([('y', '<i4')])
        #self.rndPointsY = np.asarray(self.rndPointsY,dtype=self.rndPointsYDtype)  
        self.rndPointsY.resize((self.rndPointsY.shape[0],1))
        self.rndPoints = np.append(self.rndPointsX, self.rndPointsY, axis = 1)
        self.rndPointsDtype = np.dtype('i4')
        self.rndPoints = np.array(self.rndPoints, dtype=self.rndPointsDtype)
        #self.rndPointsMean = np.mean(self.rndPoints, axis=1)
        #self.meanArgsortPointsIndxs = np.argsort(self.rndPointsMean, axis=0)
        #self.meanArgsortPoints = self.getMeanCoordSort(self.rndPoints)
        #self.meanSortPoints = np.sort(self.rndPointsMean)
        self.sTime = time.time()
        self.indices = np.indices((self.x, self.y))
        #self.xindices = self.indices[0]
        #self.yindices = self.indices[1]
        self.myPoints = np.asarray([[20,5],[5,10],[10,18],[6,10],[15,5],[20,10], [8,10], [17,6], [8,25]], dtype = self.rndPointsDtype)
        #self.myPoints = np.asarray([[20,5],[9,30],[10,18]], dtype = self.rndPointsDtype)
        self.dim = 2
        self.myKdTree = self.make_kd_tree(list(self.rndPoints), self.dim, i=0)
        self.p1 = self.rndPoints[6]
        self.p2 = self.get_nearest(self.myKdTree, self.p1, self.dim, self.dist_sq_dim)[1]
        #self.p1 = [30,20]
        #self.p2 = [80,30]
        #self.nearestAll = self.get_knn(self.myKdTree, self.p1,self.rndPoints.shape[0], self.dim, self.dist_sq_dim, return_distances=False)
        sTime = time.time()
        self.nearestAll = self.get_knn(self.myKdTree, self.p1,len(self.rndPoints)-1, self.dim, self.dist_sq_dim, return_distances=False)
        eTime = time.time()
        myTime = eTime - sTime
        print("self.nearestAll {0} len {1} time {2:d}m {3:.6f}s".format(self.nearestAll,len(self.nearestAll),int(myTime/60), myTime%60 ))
        self.myMidPoint = self.getMidPoint(self.p1, self.p2)
        self.myMidLine = self.getLine(self.myMidPoint, self.getPerpVec(self.vecFrom2Points(self.p1, self.p2)))
        #self.myMidLine = self.getLine(self.p2, self.vecFrom2Points(self.p1, self.p2))
        print("p1 {0} p2 {1} myMidPoint {2} myMidLine {3}".format(self.p1,self.p2,self.myMidPoint, self.myMidLine))
        self.vdistance = self.getDistance(self.rndPoints,self.indices)
        #self.vdistance.dtype = np.uint8
        self.eTime = time.time()
        self.myVTime = self.eTime - self.sTime
        
        
        self.sTime = time.time()
        self.distance = self.getDistCoordSort(self.rndPoints)
        
        #self.sortedDistance = np.sort(self.distance)
        #self.distanceArgsortPointsIndxs = np.argsort(self.rndPointsMean, axis=0)
        self.RGBmx = self.getRGBmx(self.distance[1], self.distance[0])
        self.eTime = time.time()
        self.myTime = self.eTime - self.sTime
        #self.distance = self.getDistCoordSort(self.rndPoints)
        #self.rndPoints = np.asarray([(1,2),(4,6),(6,8)], dtype=self.rndPointsDtype)
        #self.rndPoints = np.asarray(self.rndPoints, dtype=self.rndPointsDtype)
        #self.xySortPoints = np.sort(self.rndPoints.view('i4,i4'), order=['f0','f1'], axis=0).view(np.int)
        #self.xSortPoints = np.sort(self.rndPoints.view('i4,i4'), order=['f0'], axis=0).view(np.int)
        #self.ySortPoints = np.sort(self.rndPoints.view('i4,i4'), order=['f1'], axis=0).view(np.int)
        #self.xArgSortPoints = np.argsort(self.rndPoints, axis=0)
        #self.argSortRndPointsIndxs = np.argsort(self.rndPoints, order=('x','y'))
        #self.argSortRndPoints = self.rndPoints[self.argSortRndPointsIndxs]
        #print("vdistance in setup {0} shape {1} dtype{2}".format(self.vdistance, self.vdistance.shape, self.vdistance.dtype))
        #self.myKdTree = self.make_kd_tree(list(self.rndPoints), self.dim, i=0)
        self.saveMxAsImg(self.vdistance)
        self.vor = Voronoi(self.rndPoints)
        voronoi_plot_2d(self.vor)
        plt.show()
        self.sTime = time.time()
        
        self.eTime = time.time()
        self.myKdTreeTime = self.eTime - self.sTime
        
    def getMeanCoordSort(self, inCoords):
        rndPointsMean = np.mean(inCoords, axis=1)
        meanArgsortPointsIndxs = np.argsort(rndPointsMean, axis=0)
        meanArgsortPoints = inCoords[meanArgsortPointsIndxs]
        return meanArgsortPoints
    
    def getDistCoordSort(self, inCoords, inOriginPoint=np.array([20,23])):
        #originPoint = np.resize(inOriginPoint, (1, inOriginPoint.shape[0]))
        originPoints = np.broadcast_to(inOriginPoint, (inCoords.shape[0],inCoords.shape[1]))
        originPointsXCoords = originPoints[...,0]
        originPointsYCoords = originPoints[...,1]
        pointsXCoords = inCoords[...,0]
        pointsYCoords = inCoords[...,1]
     
        #print("originPoints {0} shape {1} dtype {2}".format(originPoints, originPoints.shape, originPoints.dtype))
        result = np.sqrt(np.square(pointsXCoords - originPointsXCoords) \
               + np.square(pointsYCoords - originPointsYCoords))
        distanceArgsortPointsIndxs = np.argsort(result, axis=0)
        distanceArgsortPoints = inCoords[distanceArgsortPointsIndxs]
        return (result[distanceArgsortPointsIndxs],distanceArgsortPoints)
        
    def getDistance(self, inPoints, inIndxs=np.array([[0,1,2,3], \
    	                                                  [0,1,2,3], \
    	                                                  [0,1,2,3]], dtype = np.uint8) \
    	                                                  ):
        print("inIndxs {0}, shape {1}".format(inIndxs,inIndxs.shape))
        xIndices = inIndxs[0]       
        xIndices = np.resize(xIndices, (xIndices.shape[0],xIndices.shape[1],1))       
        xIndices = np.broadcast_to(xIndices, (xIndices.shape[0],xIndices.shape[1],inPoints.shape[0]))
        print("xIndices {0}, shape {1}".format(xIndices,xIndices.shape))
        yIndices = inIndxs[1]
        yIndices = np.resize(yIndices, (yIndices.shape[0],yIndices.shape[1], 1))
        yIndices = np.broadcast_to(yIndices, (yIndices.shape[0],yIndices.shape[1], inPoints.shape[0]))
        print("yIndices {0}, shape {1}".format(yIndices,yIndices.shape))
        points = np.resize(inPoints.copy(),(1, 1,inPoints.shape[0], inPoints.shape[1]))
        points = np.broadcast_to(points, (xIndices.shape[0],xIndices.shape[1],inPoints.shape[0], inPoints.shape[1]))
        print("points {0}, shape {1}".format(points,points.shape))
        pointsX = points[...,0]
        pointsY = points[...,1]
        print("pointsX {0}, shape {1}".format(pointsX,pointsX.shape))
        print("pointsY {0}, shape {1}".format(pointsY,pointsY.shape))
     
        dist = (pointsX-xIndices)**2 + (pointsY-yIndices)**2
        return np.argmin(dist,axis = 2)
        #return dist
        
    def saveMxAsImg(self, inMx):
        if len(inMx.shape) < 3:
            #saveMx = np.resize(inMx,(inMx.shape[0], inMx.shape[1], 1))
            
            myMode = 'L'
        elif inMx.shape[2] == 3:
            myMode = 'RGB'
        myMode = 'L'
        print("inMx in saveMxAsImg {0} shape {1} dtype{2}".format(inMx, inMx.shape, inMx.dtype))
        print("np.min(inMx) in saveMxAsImg {0}".format(np.min(inMx)))
        print("np.max(inMx) in saveMxAsImg {0}".format(np.max(inMx)))
        saveMx = npRemap(inMx.copy(), np.min(inMx),np.max(inMx), 0, 255)
        #saveMx = inMx
        saveMx = np.asarray(saveMx, dtype = np.uint8)
        saveMx = np.transpose(saveMx, (1,0))
        saveRGBmx = np.resize(saveMx, (saveMx.shape[0], saveMx.shape[1],1))
        saveRGBmx = np.broadcast_to(saveRGBmx.copy(),(saveRGBmx.shape[0],saveRGBmx.shape[1],3))
        saveRGBmx.setflags(write=1)
        saveRGBmx[self.rndPoints[...,1],self.rndPoints[...,0]] = np.asarray([255,255,255], dtype=np.uint8)
        #saveRGBmx[0,0,0] = 180
        #saveRGBmx[0,0,1] = 90
        #saveRGBmx[0,0,2] = 255
        #saveRGBmx[int(self.myMidPoint[0]),int(self.myMidPoint[1])] = [255,50,80]
        #saveMx.dtype = np.uint8
        print("saveRGBmx in saveMxAsImg {0} shape {1} dtype{2} flags{3}".format(saveRGBmx, saveRGBmx.shape, saveRGBmx.dtype, saveRGBmx.flags))
        
        print("self.myMidPoint {}".format(self.myMidPoint))
        img = Image.fromarray(saveRGBmx, mode = "RGB")
        imgD = ImageDraw.Draw(img)
        offsetCol = 110
        step = (330-offsetCol)/float(len(self.nearestAll))
        #colRange = range(int(offsetCol + step),int(330 + step),step)
        colRange = self.frange(offsetCol + step, 330 + step,step)
        print("step{}".format(step))
        print("colRange{}".format(colRange))
        for i, point in enumerate(self.nearestAll):
            col = ImageColor.getrgb("hsl({},100%,50%)".format(int(colRange[i-1 if i > 0 else 0])))
            imgD.point([(int(point[0]),int(point[1]))], col)
        #col = ImageColor.getrgb("hsl({},80%,40%)".format(45))
        #imgD.line([self.myMidLine[0][1],self.myMidLine[0][0],self.myMidLine[1][1], self.myMidLine[1][0]],(255,0,0))
        imgD.line(self.myMidLine,(255,0,0))
        #imgD.line([tuple(self.myMidLine[0]),tuple(self.myMidLine[1])],(255,0,0))
        imgD.point([(self.myMidPoint[0], self.myMidPoint[1])], (0,180,250))
        #imgD.point([(self.p2[0], self.p2[1])], (30,180,130))
        col = ImageColor.getrgb("hsl({},100%,55%)".format(53))
        imgD.point([(self.p1[0], self.p1[1])], col)
        #col = ImageColor.getrgb("hsl({},80%,60%)".format(30))
        #imgD.point([(int(self.p2[1]),int(self.p2[0]))], col)
        #img.convert('RGB')
        #myImgData = np.asarray(img.getdata())
        #print("myImgData {0} shape {1} dtype {2}".format(myImgData, myImgData.shape,myImgData.dtype))
        #img.putpixel((int(self.myMidPoint[0]),int(self.myMidPoint[1])), 255)
        #if "Windows" in platform.uname():
        #    path =  r'C:/_WORK/PYTHON/projects/numpy/numpy_image/'
        #else:
        #    path = r"/storage/emulated/0/qpython/projects/numpy/numpy_image/"
        #subDir = "0004/"
        ensure_dir(self.path + self.subDir)
        filename = "BW2.png"
        img.save(self.path + self.subDir + filename)
        print("hsl rgb {}".format(ImageColor.getrgb("hsl(0,100%,50%)")))
        
    def getRGBmx(self, inCoords, inMeanDistance):
        RGBmx = np.resize(self.mx, (self.mx.shape[0],self.mx.shape[1],1))
        RGBmx = np.broadcast_to(RGBmx, (RGBmx.shape[0],RGBmx.shape[1],3))
        RGBmx = npRemap(RGBmx.copy(), 0, np.max(RGBmx), 0, 255)
        RGBmx = np.array(RGBmx, dtype = np.uint8)
        meanDistance = npRemap(inMeanDistance, 0, np.max(inMeanDistance), 0., 360.)
        step = 360. / inCoords.shape[0]
        for i, v in enumerate(inCoords):
            color = np.array(list(ImageColor.getrgb("hsl(" + str(int(meanDistance[i])) + ",100%,20%)")),dtype=np.uint8)
         
            RGBmx[v[0],v[1]] = color
        #RGBmx[inCoords[...,0],inCoords[...,1], 0] /= 255
        #RGBmx[inCoords[...,0],inCoords[...,1], 1] /= 255
        #RGBmx[inCoords[...,0],inCoords[...,1], 2] /= 255
        img = Image.fromarray(RGBmx, mode = 'RGB')
        #if "Windows" in platform.uname():
        #    path =  r'C:/_WORK/PYTHON/projects/numpy/numpy_image/'
        #else:
        #    path = r"/storage/emulated/0/qpython/projects/numpy/numpy_image/"
        #subDir = "0003/"
        ensure_dir(self.path + self.subDir)
        filename = "COLORED_POINTS.png"
        img.save(self.path + self.subDir + filename)
        print(" {}".format(ImageColor.getrgb("hsl(0,100%,50%)")))
       # RGBmx[inCoords[0],inCoords[1], 1] /= 255
        return RGBmx
        
    def getIndicesMx(self, inIndxs):
        index = np.resize(inIndxs, (1, inIndxs.shape[0],inIndxs.shape[1]))
        index = np.broadcast_to( index, (self.pointNum, index.shape[1],index.shape[2]))
        return index
        
    def vecFrom2Points(self,inP1, inP2):
        return (inP2[0] - inP1[0], inP2[1] - inP1[1])
    
    def getPerpVec(self, inVec):
        return (-inVec[1], inVec[0])
        
    def getLine(self, inPoint, inVec):
        
        dY = inVec[0] / float(inVec[1]) if inVec[1] != 0 else None
        dX = inVec[1] / float(inVec[0]) if inVec[0] != 0 else None
        #p1Y = inPoint[1] - inVec[1]/inVec[0] * inPoint[0]
        #p1X = inPoint[0] - inVec[0]/inVec[1] * inPoint[1]
        yX0 = inPoint[1] - inPoint[0]*dX if dX else inPoint[0]
        xY0 = inPoint[0] - inPoint[1]*dY if dY else inPoint[1]
        yXw = inPoint[1] + (self.x - inPoint[0])*dX if dX else inPoint[0]
        xYh = inPoint[0] + (self.y - inPoint[1])*dY if dY else inPoint[1]
        
        #constrain x coordinate to fit to screen
        if self.isIncVec(inVec):
            p1 = [0,0]
            p2 = [self.x-1, self.y-1]
            if xY0 > 0:
                p1[0] = xY0
            if yX0 > 0:
                p1[1] = yX0
            if xYh < self.x:
                p2[0] = xYh
            if yXw < self.y:
                p2[1] = yXw
        else:
            p1 = [self.x-1,0]
            p2 = [0, self.y-1]
            if xY0 < self.x:
                p1[0] = xY0
            if yXw > 0:
                p1[1] = yXw
            if xYh > 0:
                p2[0] = xYh
            if yX0 < self.y:
                p2[1] = yX0
            if inVec[1] == 0:
                p1 = [0,yX0]
                p2 = [self.x, yXw]
            elif inVec[0] == 0:
                p1 = [xY0, 0]
                p2 = [xYh, self.y]
        print("getLine \n xY0 {0} \n yX0 {1} \n p1 {7}\n p2 {8}\n isIncVec {9}\n xYh {5} yXw {6}\n inVec {2}\n dX {3}\n dY {4}\n".format(xY0, yX0, inVec, dX, dY, xYh, yXw, p1, p2, self.isIncVec(inVec)))
        return [(p1[0], p1[1]), (p2[0], p2[1])]
    
    def frange(self, inStart, inEnd, inStep=1):
        inc = inStart
        myRange = int((inEnd - inStart)/inStep)
        returnRange = []
        for x in range(0, myRange):
            inc += inStep
            returnRange.append(inc)
        return returnRange
        
    def isIncVec(self, inVec):
        if inVec[0] > 0 and inVec[1] > 0:
            return True
        elif inVec[0] < 0 and inVec[1] < 0:
            return True
        else:
            return False
        
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
            
    def get_knn(self, kd_node, point, k, dim, dist_func, return_distances=True, i=0, heap=None): 
        import heapq 
        is_root = not heap 
        if is_root: 
            heap = []
        
        if kd_node: 
            dist = dist_func(point, kd_node[2]) 
            dx = kd_node[2][i] - point[i] 
            if len(heap) < k: 
                #print("len(heap) < k {0} -dist {1} kd_node[2] {2}".format(len(heap), -dist, kd_node[2]))
                heapq.heappush(heap, (-dist, list(kd_node[2]))) 
            elif dist < -heap[0][0]: 
                #print("len(heap) < k {0} -dist {1} kd_node[2] {2} -heap[0][0] {3}".format(len(heap), -dist, kd_node[2],-heap[0][0]))
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
            dx = kd_node[2][i] - point[i] 
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

    def dist_sq(self,a, b, dim): 
        return sum((a[i] - b[i]) ** 2 for i in range(dim)) 

    def dist_sq_dim(self,a, b): 
        return self.dist_sq(a, b, self.dim) 
    
    def getListShape(self, inList, level=0, maxLevel = 0):
        for x in inList:
            if ((type(x) == list or type(x)== tuple) and len(x) > 0):
            #if level < 2:
                nextLevel = self.getListShape(x, level+1, level+1)
                if nextLevel > maxLevel:
                    maxLevel = nextLevel
        return maxLevel
    
    def getMaxLen(self, inList, level=0, maxLevel = 0, maxLen = 0):
        for x in inList:
            if ((type(x) == list or type(x)== tuple) and len(x) > 0):
            #if level < 2:
                myLen = len(x)
                maxLen = myLen if myLen > maxLen else maxLen
                nextLevel = self.getMaxLen(x, level+1, level+1, maxLen)
                maxLen = nextLevel if nextLevel > maxLen else maxLen
            elif type(x) == str:
                myLen = len(x)
                maxLen = myLen if myLen > maxLen else maxLen
        return maxLen
    
    def printKdList(self, inList, maxLevel, level=0, ):
        text = ""
        for i, x in enumerate(inList):
            #if ((type(x) == list or type(x)== tuple) and len(x) > 0 and i<2):
            #    pass
            #if level < 2:
            #    nextLevel = self.getListShape(x, level+1, level+1)
            #    values.append(nextLevel)
            #    if nextLevel > maxLevel:
            #        maxLevel = nextLevel
            if i==2 and level <= maxLevel:
                right = ""
                left = ""
                if type(inList[0]) == list or type(inList[0]) == tuple or inList[0] != None:
                    left = "\nL-{1}-{0}".format(self.printKdList(inList[0], maxLevel, level+1), level+1)
                else:
                    left = "\nL-{0}-[_none_]".format(level+1)
                if type(inList[1]) == list or type(inList[1]) == tuple or inList[1] != None:        
                    right = "\nR-{1}-{0}".format(self.printKdList(inList[1], maxLevel, level+1), level+1)
                else:
                    right = "\nR-{0}-[_none_]".format(level+1)
                text = "{0}".format(x) + left + right
                
            else:
                text = "This is the end"
        if level == 0:
            tList = text.split("\n")
            first = tList[0]
            tList = [item.split("-") for item in tList[1:]]
            returnList = [[] for i in range(maxLevel+2)]
            returnList[0].append(first)
            returnText = ["" for t in range(maxLevel+2)]
            returnText[0] += first
            for i, v in enumerate(tList):
                ind = int(v[1])
                #myLen = len(returnList[ind])
                #if myLen % 2 == 0:
                returnList[ind].append(v[2])
                returnText[ind] += v[2]
                #else:
                #    poped = returnList[ind].pop()
                #    returnList[ind].append(v[2])
                #    returnList[ind].append(poped)
            maxChars = int(self.getMaxLen(returnText) * 1.8)
            #formatedText = "\n".join(["{:_^180}".format(x) for x in returnList])            
            formatedText = ""
            for l in returnList:
                formatedText += self.fillFullWidth(l, maxChars, " ") + "\n" 
            return (text,"\n".join(returnText), formatedText)
        else:
            return text
            
    def fillFullWidth(self, inListString, inMaxWidth, inChar = "_"):
        totalStrLength = 0
        listLen = len(inListString)
        fieldWidth = inMaxWidth / listLen
        returnStr = ""
        for s in inListString:
            sLen = len(s)
            if fieldWidth > sLen:
                fillLen = fieldWidth - sLen
            else:
                fillLen = 0
            fill = [inChar for c in range(fillLen)]
            half = len(fill) >> 1
            rFill = "".join(fill[half + 1:])
            lFill = "".join(fill[:half])
            returnStr += lFill + s + rFill
        return returnStr
    
    def getMidPoint(self, a, b):
        midX = a[0] +((b[0] - a[0])/2.)
        midY = a[1] +((b[1] - a[1])/2.)
        return [midX, midY]
    
    def generate_voronoi_diagram(self,width, height, num_cells):
        image = Image.new("RGB", (width, height))
        putpixel = image.putpixel
        imgx, imgy = image.size
        nx = []
        ny = []
        nr = []
        ng = []
        nb = []
        for i in range(num_cells):
            nx.append(random.randrange(imgx))
            ny.append(random.randrange(imgy))
            nr.append(random.randrange(256))
            ng.append(random.randrange(256))
            nb.append(random.randrange(256))
        for y in range(imgy):
            for x in range(imgx):
                dmin = math.hypot(imgx-1, imgy-1)
                j = -1
                for i in range(num_cells):
            	       d = math.hypot(nx[i]-x, ny[i]-y)
            	       if d < dmin:
                	       dmin = d
                	       j = i
                putpixel((x, y), (nr[j], ng[j], nb[j]))
        image.save(self.path + self.subDir + "VoronoiDiagram.png", "PNG")
        image.show()
    
    def printValues(self):
        print("Divide.mx {}".format(self.mx))
        #print("Divide.rndPointsX {0} shape {1} dtype {2}".format(self.rndPointsX, self.rndPointsX.shape, self.rndPointsX.dtype))
        #print("Divide.rndPointsXDtype {0}".format(self.rndPointsXDtype.type))
        #print("Divide.rndPointsY {0} shape {1} dtype {2}".format(self.rndPointsY, self.rndPointsY.shape, self.rndPointsY.dtype))
        #print("Divide.rndPointsDtype {0}".format(self.rndPointsDtype.type))
        print("Divide.rndPoints {0} shape {1} dtype {2}".format(self.rndPoints, self.rndPoints.shape, self.rndPoints.dtype))
        #print("Divide.xySortPoints {0} shape {1} dtype {2}".format(self.xySortPoints, self.xySortPoints.shape, self.xySortPoints.dtype))
        #print("Divide.xSortPoints {0} shape {1} dtype {2}".format(self.xSortPoints, self.xSortPoints.shape, self.xSortPoints.dtype))
        #print("Divide.ySortPoints {0} shape {1} dtype {2}".format(self.ySortPoints, self.ySortPoints.shape, self.ySortPoints.dtype))
        #print("Divide.rndPointsMean {0} shape {1} dtype {2}".format(self.rndPointsMean, self.rndPointsMean.shape, self.rndPointsMean.dtype))
        #print("Divide.meanArgsortPointsIndxs {0} shape {1} dtype {2}".format(self.meanArgsortPointsIndxs, self.meanArgsortPointsIndxs.shape, self.meanArgsortPointsIndxs.dtype))
        #print("Divide.meanArgsortPoints {0} shape {1} dtype {2}".format(self.meanArgsortPoints, self.meanArgsortPoints.shape, self.meanArgsortPoints.dtype))
        #print("Divide.RGBmx {0} shape {1} dtype {2}".format(self.RGBmx, self.RGBmx.shape, self.RGBmx.dtype))
        #print("Divide.meanSortPoints {0} shape {1} dtype {2}".format(self.meanSortPoints, self.meanSortPoints.shape, self.meanSortPoints.dtype))
        # print("Divide.myTime = {0:d}m {1:.6f}s" \
 	    #             .format( \
        #          int(self.myTime/60), \
        #          self.myTime%60 \
        #         ) \
 	    #         )
        #print("Divide.vdistance {0} shape {1} dtype {4} Divide.myVTime = {2:d}m {3:.6f}s".format(self.vdistance, self.vdistance.shape, int(self.myVTime/60), self.myVTime%60,self.vdistance.dtype))
        #print("myKdTree {0} len {1} {2:d}m {3:.6f}s".format(self.myKdTree, len(self.myKdTree), int(self.myKdTreeTime/60), self.myTime%60))
        #sTime = time.time()
        myShape = self.getListShape(self.myKdTree)
        #eTime = time.time()
        #myTime = eTime - sTime
        #print("myKdTree shape {0} {1:d}m {2:.6f}s".format(myShape, int(myTime/60), myTime%60))
        #sTime = time.time()
        #myKdTreeValues = self.printKdList(self.myKdTree, myShape)
        #eTime = time.time()
        #myTime = eTime - sTime
        #writeFile(self.path + self.subDir, myKdTreeValues[2], "kd_tree.txt")
        #print("myKdTreeValues {0} \n {1:d}m {2:.6f}s \n list \n{3} \n formatedText \n{4}".format(myKdTreeValues[0], int(myTime/60), myTime%60,myKdTreeValues[1],myKdTreeValues[2]))
        print("[0]*self.dim {0}".format([0]*self.dim))
        print("[0]*self.rndPoints[0] {0}".format(self.rndPoints[0]))
        sTime = time.time()
        myNearest = self.get_nearest(self.myKdTree, np.asarray([0,10], dtype= np.uint8), self.dim, lambda a,b: self.dist_sq(a, b, self.dim))
        eTime = time.time()
        myTime = eTime - sTime
        print("self.get_nearest {0} {1:d}m {2:.6f}s".format(myNearest, int(myTime/60), myTime%60))
        #print("self.get_knn(self.rndPoints[0]) {0}".format(self.get_knn(self.myKdTree, self.rndPoints[0], 3, self.dim, self.dist_sq_dim, return_distances=True, i=0, heap=None)))
        #sTime = time.time()
        #indices = np.indices((self.x, self.y))
        #xindices = indices[0]
        #yindices = indices[1]
        #myXIndxs = self.getIndicesMx(xindices)
        #myYIndxs = self.getIndicesMx(yindices)
        #mx = myIndxs(xindicies)
        #self.generate_voronoi_diagram(self.x, self.y, self.pointNum)
        #eTime = time.time()
        #myTime = eTime - sTime
        #print("self.generate_voronoi_diagram  shape myTime = {0:d}m {1:.6f}s".format(int(myTime/60), myTime%60))
        #print("myXIndxs {0} shape {1} Divide.myTime = {2:d}m {3:.6f}s".format(myXIndxs, myXIndxs.shape, int(myTime/60), myTime%60))
        #print("myYIndxs {0} shape {1} Divide.myTime = {2:d}m {3:.6f}s".format(myYIndxs, myYIndxs.shape, int(myTime/60), myTime%60))
        #print("Divide.distance {0} shape {1} dtype {2}".format(self.distance, self.distance.shape, self.distance.dtype))
        #print("Divide.xArgSortPoints {0} shape {1}".format(self.xArgSortPoints, self.xArgSortPoints.shape))
        #print("Divide.argSortRndPointsIndxs {0} shape {1}".format(self.argSortRndPointsIndxs, self.argSortRndPointsIndxs.shape))
        #print("Divide.argSortRndPoints {0} shape {1}".format(self.argSortRndPoints, self.argSortRndPoints.shape))
myMx = Divide()
myMx.printValues()
myArray = [1,2,3,4,5,6]
print("myArray {0}".format(myArray[3<=2]))




