#import random
import sys
import os
import numpy as np
import itertools
#import math
from PIL import Image
#import time
#import matplotlib.pyplot as plt
import platform
#import itertools

if "Windows" in platform.uname():
    lib_path = r'C:/_WORK/PYTHON/LIB'
else:
    lib_path = r"/storage/18D4-6C41/PYTHON/LIB"
sys.path.append(lib_path)
import ListUtils
import NumpyUtils as npUtils
import IO_Utils

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

def genVecsCombinations(inVectors):
	vectorsIndx = range(0,len(inVectors))
	# indexes of combinations of RGB channels 
	rgbCombIndxs = list(itertools.combinations([x for x in inVectors], 3))
	for comb in rgbCombIndxs:
		yield comb

class CombinationGeneratorRGB_():

	def __init__(self, *args, **kwargs):
		"""
			inVectors: list of 1D vectors representing axis to measure angle of RGB vectors of image
			inData: numpy.ndarray of shape(image_width, image_height, RGBvector = shape(3))
		"""
		
		if "Windows" in platform.uname():
			self.imgPath =  r'C:/_WORK/PYTHON/projects/numpy/numpy_image/water-sculpture-2res.png'
		else:
			self.imgPath = r"/storage/emulated/0/qpython/projects/numpy/numpy_image/obr5.jpg"
		self.img = Image.open(imgPath)
		#img = img.resize((int(img.size[0]/23), int(img.size[1]/23)), Image.LANCZOS)
		self.data = np.asarray(img)
		print("imgData {0} \n shape {1} \n dtype {2} \n ndim {3} \n" \
			.format( \
				imgData, \
				imgData.shape, \
				imgData.dtype, \
				imgData.ndim \
				) \
			)
		self.origVectors = args[0] if len(args) > 0 else self.getRndValuesForVectors(7)
		self.rgbCombIndxs = self.createCombinations(self.origVectors)

		if "Windows" in platform.uname():
			self.path =  r'C:/_WORK/PYTHON/projects/numpy/numpy_image/'
		else:
			self.path = r"/storage/emulated/0/qpython/projects/numpy/numpy_image/"
		self.subDir = kwargs["sub_dir"] if "sub_dir" in kwargs else "013/"

	def run(self):
		self.saveRGB(self.genRGBmxs(self.getAngles, self.genVectors()))

	def getRndValuesForVectors(self, inCount):
		values = np.random.uniform(0,1,(inCount,3))
		myValues = [x for x in values]
		return myValues

	def createCombinations(self, origVectors):
		vectorsIndx = range(0,len(origVectors))
		rgbCombIndxs = list(itertools.combinations([x for x in vectorsIndx], 3))
		return rgbCombIndxs

	def genVectors(self):
		for x in self.rgbCombIndxs:
			yieldVectors = np.empty((0,self.data.shape[0], self.data.shape[1],3), dtype=np.float64)
			for y in x:
				npVec = np.array(y,dtype=np.float64)
				npVec = np.broadcast_to(npVec, (self.data.shape[0], self.data.shape[1], len(x)))
				npVecc = npVec.copy()
				npVecc.resize((1,self.data.shape[0], self.data.shape[1], self.data.shape[2]), refcheck=False)
				yieldVectors = np.append(yieldVectors, npVecc,axis=0)
			yield yieldVectors

	#generate 2D matrixes for RGB channels
	def genRGBmxs(self, inFunc, inVecs):
		data = np.asarray(self.data.copy(), dtype= np.float64)
		data /= 255
		for vecs in inVecs:
			for channel in vecs:
				rgbMxs = np.empty((0,data.shape[0], data.shape[1]), dtype = np.float64)
				print("vecs {0} - channel {1}".format(vecs, channel))
				mXs = inFunc(channel, data)
				mXs = np.asarray(npUtils.npRemap(mXs, np.nanmin(mXs), np.nanmax(mXs), 0, 255), dtype=np.uint8)
				mXs.resize((1,mXs.shape[0], mXs.shape[1]), refcheck=False)
				rgbMxs = np.append(rgbMxs, mXs, axis = 0)
			print("rgbChannels {0} shape {1}".format(rgbChannels, rgbChannels.shape))
			rgbChannels = np.transpose(rgbMxs, (1,2,0))
			print("rgbChannels transposed {0} shape {1}".format(rgbChannels, rgbChannels.shape))
			yield rgbChannels

	def saveRGB(self,inRGBchannels):
		#print("inRGBchannels {0}".format(inRGBchannels))
		myIter = iter(inRGBchannels)
		print("myIter {}".format(next(myIter)))
		print("myIter {}".format(next(myIter)))
		print("myIter {}".format(next(myIter)))
		for i, rgbChannels in enumerate(inRGBchannels):
			
			img = Image.fromarray(inRGBchannels, mode = 'RGB')
			filename = "rgbComb-" + "_".join(["{:.2f}".format(x) for x in self.origVectors[i][0]]) + "-" + "_".join(["{:.2f}".format(x) for x in self.origVectors[i][1]]) + "-" + "_".join(["{:.2f}".format(x) for x in self.origVectors[i][2]]) + ".png"
			img.save(self.path + self.subDir + filename)
			#mXs.resize((1,mXs.shape[0], mXs.shape[1]), refcheck=False)
			#returnMXs = np.append(returnMXs, mXs, axis = 0)

	def setSavePath(self, inPath):
		self.path = inPath

	def setSaveSubDir(self, inPath):
		self.subDir = inPath

	def getAngles(self, mx1, mx2):
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

if "Windows" in platform.uname():
    imgPath =  r'C:/_WORK/PYTHON/projects/numpy/numpy_image/water-sculpture-2res.png'
else:
    imgPath = r"/storage/emulated/0/qpython/projects/numpy/numpy_image/obr5.jpg"
img = Image.open(imgPath)
#img = img.resize((int(img.size[0]/23), int(img.size[1]/23)), Image.LANCZOS)
imgData = np.asarray(img)
print("imgData {0} \n shape {1} \n dtype {2} \n ndim {3} \n" \
    .format( \
            imgData, \
            imgData.shape, \
            imgData.dtype, \
            imgData.ndim \
           ) \
    )


myAxis = [[1,0,0],[0,1,0],[0,0,1],[1,1,0],[1,0,1],[0,1,1],[1,1,1]]
values = np.random.uniform(0,1,(7,3))
myValues = [x for x in values]
myRange = np.linspace(0.05, 0.95, 4, endpoint=True)
myRange = np.broadcast_to(myRange, (3, myRange.shape[0]))
combinations = list(np.array(np.meshgrid(myRange[0], myRange[1], myRange[2])).T.reshape(-1,3))

myGenerator = CombinationGeneratorRGB_()
myGenerator.run()

for i, vec in enumerate(myGenerator.genVectors()):
	print("vecs {0} >>> {1}".format(i, vec))

vectors = iter(myGenerator.genVectors())
end = False
while end == False:
	myInput = input("Stlacenim lubovolnej klavesy generuj dalsi prvok sekvencie kombinacie")
	if myInput == "":
		print("vectors {}".format(next(vectors)))
	else:
		end = True


matrix1 = np.array([[[1,2,3,4,], \
	                     [5,6,7,8], \
	                     [9,10,11,12]], \
	                     
	                    [[13,14,15,16], \
	                     [17,18,19,20], \
	                     [21,22,23,24]], \
	                    [[25,26,27,28], \
	                     [29,30,31,32], \
	                     [33,34,35,36]],
	                    [[37,38,39,40], \
	                     [41,42,43,44], \
	                     [45,46,47,48]]], dtype = np.uint8)

matrix1 = np.transpose(matrix1)
#print("matrix1 >>> {0} \n shape: {1} \n".format(matrix1, matrix1.shape))

matrix2 = np.array([[[101,11,11,11,11,11,11,11,1001], \
	                 [102,12,12,12,12,12,12,12,1002], \
	                 [103,13,13,13,13,13,13,13,1003], \
					 [104,14,14,14,14,14,14,14,1004]], \
	                [[201,21,21,21,21,21,21,21,2001], \
	                 [202,22,22,22,22,22,22,22,2002], \
	                 [203,23,23,23,23,23,23,23,2003], \
					 [204,24,24,24,24,24,24,24,2004]], \
	                [[301,31,31,31,31,31,31,31,3001], \
	                 [302,32,32,32,32,32,32,32,3002], \
					 [303,33,33,33,33,33,33,33,3003], \
	                 [304,34,34,34,34,34,34,34,3004]]], dtype = np.uint64)
#print("matrix2 >>> {0} \n shape: {1} \n".format(matrix2, matrix2.shape))
matrix2 = np.transpose(matrix2, (1,2,0))
#print("matrix2_T >>> {0} \n shape: {1} \n".format(matrix2, matrix2.shape))
matrix2A0 = matrix2[0,...]
matrix2A1 = matrix2[1,...]
matrix2A2 = matrix2[2,...]
#print("matrix2A0 >>> {0} \n shape: {1} \n".format(matrix2A0, matrix2A0.shape))
#print("matrix2A1 >>> {0} \n shape: {1} \n".format(matrix2A1, matrix2A1.shape))
#print("matrix2A2 >>> {0} \n shape: {1} \n".format(matrix2A2, matrix2A2.shape))
path = r"/storage/emulated/0/qpython/projects/numpy/numpy_image/"
subDir = "002/"

#matrix = np.array([[[1,2,3,4], \
#	                     [5,6,7,8], \
#	                     [9,10,11,12]], \
#	                    [[13,14,15,16], \
#	                     [17,18,19,20], \
#	                     [21,22,23,24]], \
#	                    [[25,26,27,28], \
#	                     [29,30,31,32], \
#	                     [33,34,35,36]], \
#	                    [[37,38,39,40], \
#	                     [41,42,43,44], \
#	                     [45,46,47,48], \
#	                    [[49,50,51,52], \
#	                     [53,54,55,56], \
#	                     [57,58,59,60]]], dtype = np.uint8)
#print("matrix >>> {0} \n shape: {1} \n".format(matrix, matrix.shape))
#matrix = np.transpose(matrix)
#print("matrix.T >>> {0} \n shape: {1} \n".format(matrix, matrix.shape))
