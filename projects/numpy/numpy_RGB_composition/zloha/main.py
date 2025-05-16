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
from IO_Utils import *

class CombinationGeneratorRGB_():
	
	def __init__(self, *args, **kwargs):
		"""
			inVectors: list of 1D vectors representing axis to measure angle of RGB vectors of image
			inData: numpy.ndarray of shape(image_width, image_height, RGBvector = shape(3))
		"""
		
		self.imgName = kwargs["image"] if "image" in kwargs else "Dan 1.jpg"
		if "Windows" in platform.uname():
			self.imgPath =  r"" + kwargs["load_dir"] + "/" if "load_dir" in kwargs else r"C:/_WORK/PYTHON/projects/numpy/numpy_RGB_composition/"
		else:
			self.imgPath =  r"" + kwargs["load_dir"] + "/" if "load_dir" in kwargs else r"/storage/emulated/0/qpython/projects/numpy/numpy_RGB_composition/"
		self.img = Image.open(self.imgPath + self.imgName)
		self.resizeRatio = kwargs["resize"] if "resize" in kwargs else 1
		self.img = self.img.resize((int(self.img.size[0] * self.resizeRatio), int(self.img.size[1]*self.resizeRatio)), Image.LANCZOS)
		self.data = np.asarray(self.img)
		print("CombinationGeneratorRGB_imgData {0} \n shape {1} \n dtype {2} \n ndim {3} \n" \
			.format( \
				self.data, \
				self.data.shape, \
				self.data.dtype, \
				self.data.ndim \
				) \
			)
		#self.origVectors = args[0] if len(args) > 0 else self.getRndValuesForVectors(10)
		myRange = np.linspace(0.05, 0.95, 4, endpoint=True)
		print("myRange {0}".format(myRange))
		myRange = np.sort(myRange)[::-1]
		print("myRange reversed {0}".format(myRange))
		myRange = np.broadcast_to(myRange, (3, myRange.shape[0]))
		self.origVectors = list(np.array(np.meshgrid(myRange[0], myRange[1], myRange[2])).T.reshape(-1,3))
		self.rgbCombIndxs = self.createCombinations(self.origVectors)
		self.rgbCombIndxsLen = len(self.rgbCombIndxs)

		if "Windows" in platform.uname():
			self.path = r"" + kwargs["save_path"] + "/" if "save_path" in kwargs else r"C:/_WORK/PYTHON/projects/numpy/numpy_RGB_composition/"
		else:
			self.path = r"" + kwargs["save_path"] + "/" if "save_path" in kwargs else r"/storage/emulated/0/qpython/projects/numpy/numpy_RGB_composition/"
		self.subDir = kwargs["sub_dir"] + "/" if "sub_dir" in kwargs else "015" + "/"
		ensure_dir(self.path + self.subDir)

	def run(self):
		#m = 0
		myGen = iter(self.genRGBmxs(self.getAngles, self.genVectors()))
		for m in range(0,self.rgbCombIndxsLen):
		#for m in range(0,20):
			print("Gen {0} out of {1}".format(m, self.rgbCombIndxsLen))
			self.saveRGB(next(myGen), m)

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
			print("rgbCombIndxs {0}".format(x))
			for y in x:
				npVec = np.array(self.origVectors[y],dtype=np.float64)
				npVec = np.broadcast_to(npVec, (self.data.shape[0], self.data.shape[1], len(x)))
				npVecc = npVec.copy()
				npVecc.resize((1,self.data.shape[0], self.data.shape[1], self.data.shape[2]), refcheck=False)
				yieldVectors = np.append(yieldVectors, npVecc,axis=0)
			yield yieldVectors

	def genRGBmxs(self, inFunc, inVecs):
		data = np.asarray(self.data.copy(), dtype= np.float64)
		data /= 255
		for i, vecs in enumerate(inVecs):
			#print("vecs {0} {2} - vecs shape {1}".format(i, vecs.shape, vecs))
			rgbMxs = np.empty((0,data.shape[0], data.shape[1]), dtype = np.uint8)
			for j, channel in enumerate(vecs):				
				mXs = inFunc(channel, data)
				
				mXs = np.asarray(npUtils.npRemap(mXs, np.nanmin(mXs), np.nanmax(mXs), 0, 255), dtype=np.uint8)
				#print("{0}-mXs {1} mXs shape {2}".format(j, mXs, mXs.shape))
				#mXs = np.asarray(mXs, dtype=np.uint8)
				#self.saveChannel(mXs, j, i, "mXs")
				mXs.resize((1,mXs.shape[0], mXs.shape[1]), refcheck=False)
				#self.saveChannel(mXs[0], j, str(i) + "resized", "mXs")
				#print("mXs before append {0} shape {1}".format(rgbMxs, rgbMxs.shape))
				rgbMxs = np.append(rgbMxs, mXs, axis = 0)
				#self.saveChannel(rgbMxs[-1], i, j, "after append")
				#print("mXs after append {0} shape {1}".format(rgbMxs[-1], rgbMxs[-1].shape))
			#print("rgbChannels {0} shape {1}".format(rgbMxs, rgbMxs.shape))
			#self.saveChannel(rgbMxs[0], i, 0, "genRGBmxs")
			rgbChannels = np.transpose(rgbMxs, (1,2,0))
			#self.saveOneRGB(rgbChannels, i, "genRGBmxs")
			#print("rgbChannels transposed {0} shape {1}".format(rgbChannels, rgbChannels.shape))
			yield rgbChannels

	def saveChannel(self,inChannel, RGBnum, order, position):
		img = Image.fromarray(inChannel, mode = 'L')
		myTable = ["R", "G", "B"]
		filename = "{0}_{1}-{2}.png".format(order, myTable[RGBnum], position)
		img.save(self.path + self.subDir + filename)
	
	def saveOneRGB(self,inRGBChannels, order, position):
		#print("inRGBChannels[] {0} shape {1}".format(inRGBChannels, inRGBChannels.shape))
		img = Image.fromarray(inRGBChannels, mode = 'RGB')
		filename = "{0}_{1}.png".format(order, position)
		img.save(self.path + self.subDir + filename)

	def saveRGB(self,inRGBchannels, order):
		#print("inRGBchannels {0}".format(inRGBchannels))
		# myIter = iter(inRGBchannels)
		# print("myIter {}".format(next(myIter)))
		# print("myIter {}".format(next(myIter)))
		# print("myIter {}".format(next(myIter)))
		#for i, rgbChannels in enumerate(inRGBchannels):
		img = Image.fromarray(inRGBchannels, mode = 'RGB')
		#print("self.rgbCombIndxs:[{0}] >>> {1}".format(i, self.rgbCombIndxs[i]))
		#filename = "rgbComb-" + "_".join(["{:.2f}".format(y) for y in self.origVectors[(x for x in self.rgbCombIndxs[i])]]) + "-" + "_".join(["{:.2f}".format(y) for y in self.origVectors[(x for x in self.rgbCombIndxs[i])]]) + "-" + "_".join(["{:.2f}".format(y) for y in self.origVectors[(x for x in se8lf.rgbCombIndxs[i])]]) + ".png"
		myVecsComb = []
		for x in self.rgbCombIndxs[order]:
			myVec = []
			for y in self.origVectors[x]:
				value = "{:.2f}".format(y)
				myVec.append(value)
			myVecsComb.append("-".join(myVec))
		filename = "{0}_rgbComb_".format(order) + "_".join(myVecsComb) + ".png"
		#filename = "{}-RGB".format(order) + ".png"
		img.save(self.path + self.subDir + filename)
		#mXs.resize((1,mXs.shape[0], mXs.shape[1]), refcheck=False)
		# #returnMXs = np.append(returnMXs, mXs, axis = 0)

	def setSavePath(self, inPath):
		self.path = r"" + inPath + "/"

	def setSaveSubDir(self, inPath):
		self.subDir = r"" + inPath + "/"

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
#img = img.resize((int(img.size[0]/8), int(img.size[1]/8)), Image.LANCZOS)
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
	myGenerator = CombinationGeneratorRGB_(sub_dir = "003", image = "Dan 3.jpg", save_path = "C:\_WORK", load_dir = "C:\_WORK")
else:
	myGenerator = CombinationGeneratorRGB_ \
	     ( \
		        sub_dir = "003", \
		        	image = "20190704_174810.jpg", \
		        	save_path = "/storage/emulated/0/DCIM/generated_imgs", \
		        	load_dir = "/storage/18D4-6C41/DCIM/Camera", \
		        	resize = 0.1 \
		    )
myGenerator.run()






