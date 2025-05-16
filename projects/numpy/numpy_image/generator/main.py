import random
import sys
import os
import numpy as np
import math
from PIL import Image
import time
import matplotlib.pyplot as plt
import platform
import itertools
import kivy

if "Windows" in platform.uname():
    lib_path = r'C:/_WORK/PYTHON/LIB'
else:
    lib_path = r"/storage/18D4-6C41/PYTHON/LIB"
sys.path.append(lib_path)
import ListUtils

#rndMatrix = np.random.uniform(0, 1, (20,20))
#vector = np.random.uniform(0,1,(20))
#result = vector.dot(rndMatrix)
#slicedRow = rndMatrix[0,...]
#slicedCol = rndMatrix[...,0]
#meanVector = vector.mean()
#stdVector = vector.std()
#zeros = np.zeros((9,6))
#zeros[5:,...] = 9
#insVector = np.asarray([[2,1],[2,2],[3,3],[4,4],[3,5]])
#insVector.T
#iResVector = np.resize(insVector, (2,9))
#iZeros = np.insert(zeros,3,iResVector, axis = 1)
#zerosMean = zeros.mean()
#zeros_mean = zeros - zeros.mean()
#stdZeros = zeros.std()
#zeroes_meanDivStd = zeros_mean / stdZeros
#ones = np.ones((6,6))
#ones[...,5] = 9
#onesMean = ones.mean()
#ones_mean = ones - ones.mean()
#stdOnes = ones.std()
#ones_meanDivStd = ones_mean / stdOnes
#x = results

def remap(value, minInput, maxInput, minOutput, maxOutput):
    if minInput < maxInput:
        value = maxInput if value > maxInput else value
        value = minInput if value < minInput else value
        inputSpan = maxInput - minInput
        outputSpan = maxOutput - minOutput
        scaledThrust = float(value - minInput) / float(inputSpan)
        return minOutput + (scaledThrust * outputSpan)
    else:
        return minOutput

#print("zerosMean {}".format(zerosMean))
#print("zeros {}".format(zeros))
#print("insVector shape {1} >>> {0}".format(insVector,insVector.shape))
#print("iResVector {}".format(iResVector))
#print("iZeros {}".format(iZeros))
#print("zeros_mean {}".format(zeros_mean))
#print("stdZeros {}".format(stdZeros))
#print("zeroes_meanDivStd {}".format(zeroes_meanDivStd))
#print("ones {}".format(ones))
#print("onesMean {}".format(onesMean))
#print("ones_mean {}".format(ones_mean))
#print("stdOnes {}".format(stdOnes))
#print("ones_meanDivStd {}".format(ones_meanDivStd))
#print("meanVector {}".format(meanVector))
#print("stdVector {}".format(stdVector))
#print("shape rndMatrix {0} - {1} - {2}".format(rndMatrix.shape, rndMatrix.dtype, rndMatrix))
#print("shape vector {0} - {1} - {2}".format(vector.shape, vector.dtype, vector))
#print("shape result {0} - {1} - {2}".format(result.shape, result.dtype, result))
#print("shape slicedRow {0} - {1} - {2}".format(slicedRow.shape, slicedRow.dtype, slicedRow))
#print("shape slicedCol {0} - {1} - {2}".format(slicedCol.shape, slicedCol.dtype, slicedCol))

#img2 = Image.open(imgPath)
#imgData = np.asarray(img)
#imgData = np.array(img2.getdata(), dtype=float)
#imgData2 = np.array(img.getdata())
#imgDataXSize = imgData.shape[0]
#imgDataYSize = imgData.shape[1]
#imgR = np.asarray(imgData[...,0], dtype=np.uint8)
#imgG = np.asarray(imgData[...,1], dtype=np.uint8)
#imgB = np.asarray(imgData[...,2], dtype=np.uint8)

#a1 = np.array([[1,2,3]])
#a1 = np.resize(a1, (a1.shape[0],a1.shape[1],1 ))
#a2 = np.array([[[0,0],[0,0],[0,0]]])
#b = np.concatenate((a1,a2), axis=2)
#print("a1>>> {0} \n a2>>> {1} \n concatenated>>> {2}".format(a1, a2, b))
#print("imgR>>> {0} \n imgG>>> {1} \n imgB>>> {2}".format(imgR, imgG, imgB))
#zeros = np.zeros((imgR.shape[0],imgR.shape[1],2), dtype= np.uint8)
#zeros1 = np.zeros((imgR.shape[1]), dtype= np.uint8)
#imgR.setflags(write=1)
#imgRC = imgR.copy()
#imgRC.resize(imgR.shape[0], imgR.shape[1], 1)
#imgGC = imgG.copy()
#imgGC.resize(imgG.shape[0], imgG.shape[1], 1)
#imgBC = imgB.copy()
#imgBC.resize(imgB.shape[0], imgB.shape[1], 1)
#print("imgR np.resizeded>>> {0}".format(imgR))
#imgRC = np.concatenate((imgRC,zeros),axis = 2)
#print("imgR np.concatenateed>>> {0}".format(imgR))
#imgGC = np.insert(imgGC,0,zeros1, axis=2)
#imgGC = np.insert(imgGC,2,zeros1, axis=2)
#print("imgGC np.inserted>>> {0} \n shape {1}".format(imgGC, imgGC.shape))
#imgBC = np.insert(imgBC,0,zeros1, axis=2)
#imgBC = np.insert(imgBC,0,zeros1, axis=2)
#print("imgBC np.inserted>>> {0} \n shape {1}".format(imgBC, imgBC.shape))
#imgData.resize((imgDataXSize*imgDataYSize,3))
#imgData.resize((imgDataXSize,imgDataYSize,3))


#imgData2.resize((img2.size[0], img2.size[1]))
#print(dir(imgData))
#print("imgData {}".format(imgData))
#sTime = time.time()
#for x in np.nditer(imgData2, op_flags = ['readwrite']):
#    x /= 255.0
#eTime = time.time()
#myTime = eTime - sTime
#print("imgData2 {0} \n shape {3} dtype {4}\n time = {1:d}m {2:.6f}s" \
#	    .format( \
#            imgData2, \
#            int(myTime/60), \
#	            myTime%60, \
#	            imgData2.shape, \
#	            imgData2.dtype \
#	           ) \
#	    )
	    

#sTime = time.time()
#imgData.setflags(write=1)
#imgData = imgData.astype('float64')
#imgData /= 255.0
#eTime = time.time()
#myTime = eTime - sTime
#print("imgData {0} \n shape {3} \n dtype {4} \n ndim {5} \n time = {1:d}m {2:.6f}s" \
#	    .format( \
#	            imgData, \
#	            int(myTime/60), \
#	            myTime%60, \
#	            imgData.shape, \
#	            imgData.dtype, \
#	            imgData.ndim \
#	           ) \
#	    )
#sTime = time.time()
#rndImg = vector = np.random.uniform(0.,.1,(imgData.shape[0], imgData.shape[1], imgData.shape[2]))
#rndImg = np.swapaxes(rndImg,0,1)
#eTime = time.time()
#myTime = eTime - sTime
#print("rndImage {0} \n shape {3} \n ndim {5} \n time = {1:d}m {2:.6f}s" \
#	    .format( \
#	            rndImg, \
#	            int(myTime/60), \
#	            myTime%60, \
#	            rndImg.shape, \
#	            rndImg.dtype, \
#	            rndImg.ndim \
#	           ) \
#	    )
#sTime = time.time()
#dotted = np.dot(imgData2,rndImg)
#dotted2 = dotted.copy()
#eTime = time.time()
#myTime = eTime - sTime
#print("dotted {0} \n shape {3} \n time = {1:d}m {2:.6f}s" \
#	    .format( \
#	            dotted, \
#	            int(myTime/60), \
#	            myTime%60, \
#            dotted.shape \
#	           ) \
#    )
#minValue = np.amin(dotted2)
#maxValue = np.amax(dotted2)
#print("dotted2 minValue {0} \n maxValue {1}" \
#    .format( \
#	            minValue, \
#	            maxValue \
#           ) \
#    )
#myRemap = np.vectorize(remap)
#sTime = time.time()
#remaped = myRemap(dotted, minValue, maxValue, 0, 255)
#eTime = time.time()
#myTime = eTime - sTime
#print("remaped {0} \n shape {3} \n time = {1:d}m {2:.6f}s" \
#	    .format( \
#	            remaped, \
#	            int(myTime/60), \
#	            myTime%60, \
#	            remaped.shape \
#	           ) \
#	    )

def npRemap(inNpArray, minInput, maxInput, minOutput, maxOutput):
    inputSpan = maxInput - minInput
    outputSpan = maxOutput - minOutput
    inNpArray -= minInput
    inNpArray /= inputSpan
    inNpArray *= outputSpan
    inNpArray += minOutput
    return inNpArray
	    
#sTime = time.time()
#dotted2 = npRemap(dotted2,minValue, maxValue, 0,1)
#inputSpan = maxValue - minValue
#outputSpan = 1 - 0
#scaledThrust = float(value - minInput) / float(inputSpan)
#dotted2 -= minValue
#dotted2 /= inputSpan
#dotted2 *= outputSpan
#dotted2 += 0
#eTime = time.time()
#myTime = eTime - sTime
#dotted = dotted.astype('int')
#dotted2 = dotted2.astype('float32')
#print("dotted2 {0} \n shape {3} dtype {4} \n time = {1:d}m {2:.6f}s" \
#	    .format( \
#            dotted2, \
#            int(myTime/60), \
#            myTime%60, \
#	            dotted2.shape, \
#            dotted2.dtype \
#           ) \
#	    )

def vecMag(inVec):
    return math.sqrt(sum(i**2 for i in inVec))
    
def vecAngle(inVec1, inVec2):
    dot = np.dot(inVec1,inVec2)
    vec1mag = vecMag(inVec1)
    vec2mag = vecMag(inVec2)
    
    cosFi = dot / (vec1mag*vec2mag)
    acosFi = math.acos(cosFi)
    #inner angle
    angle = math.degrees(acosFi)
#    print("inVec1 {0} \ninVec2 {1} \n dotVec12 {2} \n vec1mag {3} \n vec2mag {4} \n cosFi {5} \n acosFi {6} \n angle {7}"     	     
#	    .format( \
#            inVec1, \
#            inVec2, \
#            dot, \
#            vec1mag, \
#            vec2mag, \
#            cosFi, \
#            acosFi, \
#            angle \
#           ) \
#	    )
    
    
    #real angle
    return angle if dot>0 else 360 - angle

def getAngles(mx1, mx2):
    inMx1 = mx1.copy()
    #resize to 1D array
    inMx1.resize(mx1.shape[0]*mx1.shape[1], mx1.shape[2])
    inMx2 = mx2.copy()
    #resize to 1D array
    inMx2.resize(mx2.shape[0]*mx2.shape[1], mx2.shape[2])
    vectorsDot = np.sum(inMx1*inMx2, axis=1)
    #vectors magnitude
    mx1mags = np.sqrt(np.sum(inMx1*inMx1, axis=1))
    mx2mags = np.sqrt(np.sum(inMx2*inMx2, axis=1))
    cosFi = vectorsDot / (mx1mags * mx2mags)
#    npMax = np.nanmax(cosFi)
#    npMin = np.nanmin(cosFi)
#    print(" cosFi {0} \n cosFi-dtype {1} \n cosFi-shape {2} \n npMax={3} \n npMin={4}"     	     
#	    .format( \
#            cosFi, \
#            cosFi.dtype, \
#            cosFi.shape, \
#            npMax, \
#            npMin, \
#            mx1mags.shape, \
#            mx1mags.dtype \
#           ) \
#    )
    acosFi= np.arccos(cosFi.copy())
    #normalize dot product
    vectorsDotSign = (vectorsDot / np.abs(vectorsDot))
    #radians to degrees
    angles = np.degrees(acosFi)
    # treating convex and concave angles with positive or negative dot product
    angles = (360 + vectorsDotSign*angles) % 360
    #resize back to 2D matrix
    angles.resize((mx1.shape[0],mx1.shape[1]))
#    print("inMx1 {0} \ninMx2 {1} \n vectorsDot {2} \n vectorsDotSign {14} \n mx1mags {3} \n mx1mags-shape {12} \n mx1mags-dtype {13} \n mx2mags {4} \n cosFi {5} \n cosFi-dtype {6} \n cosFi-shape {7} \n acosFi {8} \n angles {9}  \n npMax={10} \n npMin={11}"     	     
#     .format( \
#            inMx1, \
#            inMx2, \
#            vectorsDot, \
#            mx1mags, \
#            mx2mags, \
#            cosFi, \
#            cosFi.dtype, \
#            cosFi.shape, \
#            acosFi, \
#            angles, \
#            npMax, \
#            npMin, \
#            mx1mags.shape, \
#            mx1mags.dtype, \
#            vectorsDotSign \
#           ) \
#    )
    return angles
    
def genAngles(mx1, mx2):
    inMx1 = mx1.copy()
    #resize to 1D array
    inMx1.resize(mx1.shape[0]*mx1.shape[1], mx1.shape[2])
    inMx2 = mx2.copy()
    #resize to 1D array
    inMx2.resize(mx2.shape[0]*mx2.shape[1], mx2.shape[2])
    vectorsDot = np.sum(inMx1*inMx2, axis=1)
    #vectors magnitude
    mx1mags = np.sqrt(np.sum(inMx1*inMx1, axis=1))
    mx2mags = np.sqrt(np.sum(inMx2*inMx2, axis=1))
    cosFi = vectorsDot / (mx1mags * mx2mags)
#    npMax = np.nanmax(cosFi)
#    npMin = np.nanmin(cosFi)
#    print(" cosFi {0} \n cosFi-dtype {1} \n cosFi-shape {2} \n npMax={3} \n npMin={4}"     	     
#	    .format( \
#            cosFi, \
#            cosFi.dtype, \
#            cosFi.shape, \
#            npMax, \
#            npMin, \
#            mx1mags.shape, \
#            mx1mags.dtype \
#           ) \
#    )
    acosFi= np.arccos(cosFi.copy())
    #normalize dot product
    vectorsDotSign = (vectorsDot / np.abs(vectorsDot))
    #radians to degrees
    angles = np.degrees(acosFi)
    # treating convex and concave angles with positive or negative dot product
    angles = (360 + vectorsDotSign*angles) % 360
    #resize back to 2D matrix
    angles.resize((mx1.shape[0],mx1.shape[1]))
#    print("inMx1 {0} \ninMx2 {1} \n vectorsDot {2} \n vectorsDotSign {14} \n mx1mags {3} \n mx1mags-shape {12} \n mx1mags-dtype {13} \n mx2mags {4} \n cosFi {5} \n cosFi-dtype {6} \n cosFi-shape {7} \n acosFi {8} \n angles {9}  \n npMax={10} \n npMin={11}"     	     
#     .format( \
#            inMx1, \
#            inMx2, \
#            vectorsDot, \
#            mx1mags, \
#            mx2mags, \
#            cosFi, \
#            cosFi.dtype, \
#            cosFi.shape, \
#            acosFi, \
#            angles, \
#            npMax, \
#            npMin, \
#            mx1mags.shape, \
#            mx1mags.dtype, \
#            vectorsDotSign \
#           ) \
#    )
    yield angles
    
vec1 = np.array([4,-5,9], dtype=np.float)
vec2 = np.array([0,0,9], dtype=np.float)
dotVec12 = np.dot(vec1,vec2)
angle = vecAngle(vec1, vec2)

print("dotVec12 {0} \n" \
	    .format( \
            dotVec12, \
           ) \
	    )
print("angle {0} \n" \
	    .format( \
            angle, \
           ) \
	    )
#print("dotted.dtype {}".format(dotted.dtype))
#imgData *= 255
#imgData = imgData.astype('uint8')
#print("imgData INT {0} \n shape {3} dtype {4} \n time = {1:d}m {2:.6f}s" \
#	    .format( \
#	            imgData, \
#	            int(myTime/60), \
#	            myTime%60, \
#	            imgData.shape, \
#	            imgData.dtype \
#	           ) \
#	    )
#sTime = time.time()


def ensure_dir(file_path):
    directory = os.path.dirname(file_path) 
    if not os.path.exists(directory):
        os.makedirs(directory)

def prepareVectors(inData, inVectors):
    vecs = np.empty((0,inData.shape[0], inData.shape[1],3), dtype=np.float64)
    #print("vecs >>> {0} \n shape: {1} \n dtype: {2} \n".format(vecs, vecs.shape, vecs.dtype))
    for vec in inVectors:
        npVec = np.array(vec,dtype=np.float64)
        npVec = np.broadcast_to(npVec, (inData.shape[0], inData.shape[1], len(vec)))
        npVecc = npVec.copy()
        npVecc.resize((1,inData.shape[0], inData.shape[1], inData.shape[2]), refcheck=False)
        #print("npVecc >>> {0} \n shape: {1} \n dtype: {2} \n".format(npVecc, npVecc.shape, npVecc.dtype))
        
        
        vecs = np.append(vecs, npVecc,axis=0)
    #print("vecs >>> {0} \n shape: {1} \n dtype: {2} \n".format(vecs, vecs.shape, vecs.dtype))
    return vecs
    
def genPreparedRGBCombOfVectors(inData, inVectors):
    vecs = np.empty((0,inData.shape[0], inData.shape[1],3), dtype=np.float64)
    #print("vecs >>> {0} \n shape: {1} \n dtype: {2} \n".format(vecs, vecs.shape, vecs.dtype))
    inVecIndxs = range(0,len(inVectors))
    rgbCombs = list(itertools.combinations([x for x in inVecs], 3))
    for vec in inVectors:
        npVec = np.array(vec,dtype=np.float64)
        npVec = np.broadcast_to(npVec, (inData.shape[0], inData.shape[1], len(vec)))
        npVecc = npVec.copy()
        npVecc.resize((1,inData.shape[0], inData.shape[1], inData.shape[2]), refcheck=False)
        #print("npVecc >>> {0} \n shape: {1} \n dtype: {2} \n".format(npVecc, npVecc.shape, npVecc.dtype))
        
        
        vecs = np.append(vecs, npVecc,axis=0)
    #print("vecs >>> {0} \n shape: {1} \n dtype: {2} \n".format(vecs, vecs.shape, vecs.dtype))
    return vecs
    
def doTheMxJob2(inFunc, inData, inVecs, inPath, inOriginalVectors):
    inData = np.asarray(inData.copy(), dtype= np.float64)
    inData /= 255
    rgbCombs = list(itertools.combinations([x for x in inVecs], 3))
    returnMXs = np.empty((0,inData.shape[0], inData.shape[1]), dtype = np.float64)
    for i, rgbComb in enumerate(npRgbCombs):
        mXs = inFunc(vec, inData)
        mXs = np.asarray(npRemap(mXs, np.nanmin(mXs), np.nanmax(mXs), 0, 255), dtype=np.uint8)
        img = Image.fromarray(mXs, mode = 'L')
        fileName = "vec-" + "_".join(["{:.2f}".format(x) for x in vec[0,0]]) + ".png"
        img.save(inPath + fileName)
        #mXs.resize((1,mXs.shape[0], mXs.shape[1]), refcheck=False)
        yield mXs
        returnMXs = np.append(returnMXs, mXs, axis = 0)
    #rgbCombs = list(itertools.combinations([x for x in returnMXs], 3))
    #print("origVecs >>> {0} \n shape: {1} \n".format(inOriginalVectors, len(inOriginalVectors)))
    origVecsCombs = list(itertools.combinations([x for x in inOriginalVectors], 3))
    #print("origVecsCombs >>> {0} \n shape: {1} \n".format(origVecsCombs, len(origVecsCombs)))
    npRgbCombs = np.asarray(rgbCombs, dtype = np.uint8)
    #print("npRgbCombs >>> {0} \n shape: {1} \n".format(npRgbCombs, npRgbCombs.shape))
    npRgbCombs = np.transpose(npRgbCombs, (0,2,3,1))
    #print("npRgbCombsT >>> {0} \n shape: {1} \n".format(npRgbCombs, npRgbCombs.shape))
    for i, rgbComb in enumerate(npRgbCombs):
        filename = "rgbComb-" + "_".join(["{:.2f}".format(x) for x in origVecsCombs[i][0]]) + "-" + "_".join(["{:.2f}".format(x) for x in origVecsCombs[i][1]]) + "-" + "_".join(["{:.2f}".format(x) for x in origVecsCombs[i][2]]) + ".png"
        img = Image.fromarray(rgbComb, mode = 'RGB')
        img.save(inPath + filename)
    
    
def doTheMxJob(inFunc, inData, inVecs, inPath, inOriginalVectors):
    inData = np.asarray(inData.copy(), dtype= np.float64)
    inData /= 255
    returnMXs = np.empty((0,inData.shape[0], inData.shape[1]), dtype = np.float64)
    for vec in inVecs:
        mXs = inFunc(vec, inData)
        mXs = np.asarray(npRemap(mXs, np.nanmin(mXs), np.nanmax(mXs), 0, 255), dtype=np.uint8)
        img = Image.fromarray(mXs, mode = 'L')
        fileName = "vec-" + "_".join(["{:.2f}".format(x) for x in vec[0,0]]) + ".png"
        img.save(inPath + fileName)
        mXs.resize((1,mXs.shape[0], mXs.shape[1]), refcheck=False)
        returnMXs = np.append(returnMXs, mXs, axis = 0)
    rgbCombs = list(itertools.combinations([x for x in returnMXs], 3))
    #print("origVecs >>> {0} \n shape: {1} \n".format(inOriginalVectors, len(inOriginalVectors)))
    origVecsCombs = list(itertools.combinations([x for x in inOriginalVectors], 3))
    #print("origVecsCombs >>> {0} \n shape: {1} \n".format(origVecsCombs, len(origVecsCombs)))
    npRgbCombs = np.asarray(rgbCombs, dtype = np.uint8)
    #print("npRgbCombs >>> {0} \n shape: {1} \n".format(npRgbCombs, npRgbCombs.shape))
    npRgbCombs = np.transpose(npRgbCombs, (0,2,3,1))
    #print("npRgbCombsT >>> {0} \n shape: {1} \n".format(npRgbCombs, npRgbCombs.shape))
    for i, rgbComb in enumerate(npRgbCombs):
        filename = "rgbComb-" + "_".join(["{:.2f}".format(x) for x in origVecsCombs[i][0]]) + "-" + "_".join(["{:.2f}".format(x) for x in origVecsCombs[i][1]]) + "-" + "_".join(["{:.2f}".format(x) for x in origVecsCombs[i][2]]) + ".png"
        img = Image.fromarray(rgbComb, mode = 'RGB')
        img.save(inPath + filename)
    return returnMXs

#print("myAngles >>> {0} \n shape: {1} \n dtype: {2} \n".format(myAngles, myAngles.shape, myAngles.dtype))
#eTime = time.time()
#myTime = eTime - sTime
#print("v1_0_0 \n shape = {1} \n ndim = {2} \n dtype = {3} \n time = {4:d}m {5:.6f}s" \
#	    .format( \
#            v1_0_0, \
#            v1_0_0.shape, \
#            v1_0_0.ndim, \
#            v1_0_0.dtype, \
#            int(myTime/60), \
#            myTime%60 \
#           ) \
#	    )
# vectors1 = np.array([[[0,2,3],[4,5,6]],[[-2,2,0],[4,-5,9]]])
# print("vectors1 {0} \n shape = {1} \n ndim = {2} \n dtype = {3} \n amax = {4}" \
# 	    .format( \
#             vectors1, \
#             vectors1.shape, \
#             vectors1.ndim, \
#             vectors1.dtype, \
#             np.amax(vectors1)\
#            ) \
# 	    )
# #vectors1 = np.array([[0,2,3], [3,2,2]])
# vectors2 = np.array([[[1,1,-3],[-4,2,-6]],[[1,2,-2],[0,0,9]]])
# print("vectors1 {0} \n \n shape = {1} \n ndim = {2} \n dtype = {3}" \
# 	    .format( \
#             vectors2, \
#             vectors2.shape, \
#             vectors2.ndim, \
#             vectors2.dtype\
#            ) \
# 	    )
# sTime = time.time()
# vecArray = []
# for i, x in enumerate(vectors1):
#     vecYArray = []
#     for j, y in enumerate(x):
#         vecYArray.append(vecAngle(y, vectors2[i,j]))
#     vecArray.append(vecYArray)
# eTime = time.time()
# myTime = eTime - sTime
# print("vecArray {0} \n time = {1:d}m {2:.6f}s" \
# 	    .format( \
#             vecArray, \
#             int(myTime/60), \
#             myTime%60 \
#            ) \
# 	    )
	    
# sTime = time.time()
# vectorsAngles = getAngles(vectors1, vectors2)
# print("vectorsAngles {0} \n shape {3} dtype {4} \n np.amax(vectorsAngles) {6} \np.amin(vectorsAngles) {5} \n  time = {1:d}m {2:.6f}s" \
# 	    .format( \
#             vectorsAngles, \
#             int(myTime/60), \
#             myTime%60, \
# 	           vectorsAngles.shape, \
#             vectorsAngles.dtype, \
#             np.amin(vectorsAngles), \
#             np.amax(vectorsAngles) \
#            ) \
# 	    )
# vectorsAnglesRmp = np.asarray(npRemap(vectorsAngles, np.nanmin(vectorsAngles), np.nanmax(vectorsAngles), 0, 255), dtype=np.uint8)
# eTime = time.time()
# myTime = eTime - sTime

# print("vectorsAnglesRmp {0} \n shape {3} dtype {4} \n time = {1:d}m {2:.6f}s" \
# 	    .format( \
#             vectorsAnglesRmp, \
#             int(myTime/60), \
#             myTime%60, \
# 	           vectorsAnglesRmp.shape, \
#             vectorsAnglesRmp.dtype \
#            ) \
# 	    )
#vectors1.resize(vectors1.shape[0]*vectors1.shape[1], vectors1.shape[2])
#vectors2.resize(vectors2.shape[0]*vectors2.shape[1], vectors2.shape[2])
#vectorsDot = np.sum(vectors1*vectors2, axis=1)
#vectorsProduct = np.inner(vectors1, vectors2)
#vectors1mag = np.sqrt(np.sum(vectors1*vectors1, axis=1))
#vectors2mag = np.sqrt(np.sum(vectors2*vectors2, axis=1))
#vectorsCosFi = vectorsDot / (vectors1mag * vectors2mag)
#vectorsAngle = np.degrees(np.arccos(vectorsCosFi))
#vectors = 


#print("vectorsDot {0} \n" \
#	    .format( \
#            vectorsDot, \
#           ) \
#      )
#print("vectorsProduct {0} \n" \
#	    .format( \
#            vectorsProduct, \
#           ) \
#      )
#print("vectors1mag {0} \n" \
#	    .format( \
#            vectors1mag, \
#           ) \
#     )
#print("vectorsCosFi {0} \n" \
#	    .format( \
#            vectorsCosFi, \
#           ) \
#     )
#print("vectorsAngle {0} \n" \
#	    .format( \
#            vectorsAngle, \
#           ) \
#     )
#print("vectorsAngles {0} \n" \
#	    .format( \
#            vectorsAngles, \
#           ) \
#     )
#vectors1mag = np.dot(vectors1,vectors2)

# matrix = np.asarray([[[1,2,3,4], \
# 	                     [5,6,7,8], \
# 	                     [9,10,11,12]], \
# 	                    [[13,14,15,16], \
# 	                     [17,18,19,20], \
# 	                     [21,22,23,24]], \
# 	                    [[25,26,27,28], \
# 	                     [29,30,31,32], \
# 	                     [33,34,35,36]]])
# matrix = np.transpose(matrix)
# print("matrix >>> {0} \n shape: {1} \n".format(matrix, matrix.shape))
# path = r"/storage/emulated/0/qpython/projects/numpy/numpy_image/"
if "Windows" in platform.uname():
    imgPath =  r'C:/_WORK/PYTHON/projects/numpy/numpy_image/obr5.jpg'
else:
    imgPath = r"/storage/emulated/0/qpython/projects/numpy/numpy_image/obr5.jpg"
img = Image.open(imgPath)
img = img.resize((int(img.size[0]/4), int(img.size[1]/4)), Image.LANCZOS)
imgData = np.asarray(img)
print("imgData {0} \n shape {1} \n dtype {2} \n ndim {3} \n" \
    .format( \
            imgData, \
            imgData.shape, \
            imgData.dtype, \
            imgData.ndim \
           ) \
    )

if "Windows" in platform.uname():
    path =  r'C:/_WORK/PYTHON/projects/numpy/numpy_image/'
else:
    path = r"/storage/emulated/0/qpython/projects/numpy/numpy_image/"
subDir = "004/"
ensure_dir(path + subDir)

myAxis = [[1,0,0],[0,1,0],[0,0,1],[1,1,0],[1,0,1],[0,1,1],[1,1,1]]
values = np.random.uniform(0,1,(7,3))
myValues = [x for x in values]
myRange = np.linspace(0.05, 0.95, 4, endpoint=True)
myRange = np.broadcast_to(myRange, (3, myRange.shape[0]))
combinations = list(np.array(np.meshgrid(myRange[0], myRange[1], myRange[2])).T.reshape(-1,3))

print("values >>> {0} \n shape: {1} \n dtype: {2} \n".format(values, values.shape, values.dtype))
print("myValues >>> {0} \n len: {1} \n".format(myValues, len(myValues)))
print("myRange >>> {0} \n shape: {1} \n dtype: {2} \n".format(myRange, myRange.shape, myRange.dtype))
print("combinations >>> {0} \n shape: {1} \n".format(combinations, len(combinations)))

preparedVecs = prepareVectors(imgData, myValues)
myAngles = doTheMxJob(genAngles, imgData, preparedVecs, path + subDir, myValues)

# print("matrix >>> {0} \n shape: {1} \n".format(matrix, matrix.shape))
# matrix = np.transpose(matrix)
# print("matrix.T >>> {0} \n shape: {1} \n".format(matrix, matrix.shape))
#img3 = Image.fromarray(vectorsAnglesRmp, mode = 'L')
#imgREDc = Image.fromarray(imgRC, mode = 'RGB')
#imgRED = Image.fromarray(imgR, mode = 'L')
#imgREDcFName = path + "obr5Rc.png"
#imgREDFName = path + "obr5R.png"
#imgREDc.save(imgREDcFName)
#imgRED.save(imgREDFName)
#imgGREENc = Image.fromarray(imgGC, mode = 'RGB')
#imgGREEN = Image.fromarray(imgG, mode = 'L')
#imgGREENcFName = path + "obr5Gc.png"
#imgGREENFName = path + "obr5G.png"
#imgGREENc.save(imgGREENcFName)
#imgGREEN.save(imgGREENFName)
#imgBLUEc = Image.fromarray(imgBC, mode = 'RGB')
#imgBLUE = Image.fromarray(imgB, mode = 'L')
#imgBLUEcFName = path + "obr5Bc.png"
#imgBLUEFName = path + "obr5B.png"
#imgBLUEc.save(imgBLUEcFName)
#imgBLUE.save(imgBLUEFName)
# Make a meshgrid
#xs, ys = np.meshgrid(points, points) 
#z = np.sqrt(xs ** 2 + ys ** 2) 
# Display the image on the axes 
#plt.imshow(x, cmap=plt.cm.gray) 
# Draw a color bar 
#plt.colorbar() 
# Show the plot 
#plt.show()
#k = [(k,v) for k, v in locals().items()]
#for x in k:
#    print("{0}>>>{1}".format(*x))
