import random
import numpy as np
from PIL import Image
import time
#import matplotlib.pyplot as plt
import math
import os
from datetime import datetime
import platform
#import keyboard
import msvcrt

print(np.version.version)

class Ca2D_3x3(object):
	"""
		Object for generating 2D - 3x3 kernel celular automaton as a png images
		# Copyright(c) 2019, Daniel Gercak
	"""
	__title__ = "Ca2D_3x3 generator"
	__author__ = "Daniel Gercak"
		
	KERNEL_SIZE = 3
	#RULE_LENGTH = 512
	RULE_LENGTH = pow(2,KERNEL_SIZE*KERNEL_SIZE)

	def __init__(self, *args, **kwargs):

		self.setup(*args, **kwargs)

	def setup(self, *args, **kwargs):
		"""
			sets the basic attributes of Ca2D_3x3 instance

			args[0]: optional xSize of final image, type: int - default 51
			args[1]: optional ySize of final image, type: int - default 51
			args[3]: optional layCount - number of layers to generate type: int - default 50
			kwargs["saveOnlyLast"]: optional - to save only last layer as .png image into self.saveImgDir + self.dateDir, type: bool - default True
			kwargs["rndCount"]: optional - number of randomly generated rules type: int - default 500, None means infinite stream 
			kwargs["rndPart"]: optional - part of zeroed items in rule array:
										 "Q" - 3/4 of items set to zero
										 "O" - 7/8 of items set to zero
										 "H" - 1/2 of items set to zero
										 "N" - None of items set to zero
										 default "Q" 
										 type: str
			kwargs["saveRndZeroIndxs"]: optional save or not indexes of zeroed items into log file zeroIndex.txt placed in a directory with generated images
										default True
										type: bool
			kwargs["useRule"]: choose rule to use:
								"OR" - optional rule generates random rule according to rndPart attribute 
								"AR" - alpha numeric rule according to aNumRule parameter
								type: str 
			kwargs["aNumRule"]: alpha numeric representation of rule 
								type: str (36 alphanumeric characters A-Z, 0-9)

		""" 
		self.sOveralTime = time.time()
		self.xSize = args[0] if len(args) > 0 else 51 
		self.ySize = args[1] if len(args) > 1 else 51
		self.layCount = args[2] if len(args) > 2 else 50
		self.saveOnlyLast = kwargs["saveOnlyLast"] if "saveOnlyLast" in kwargs else True
		self.rndCount = kwargs["rndCount"] if "rndCount" in kwargs else 50
		self.rndPart = kwargs["rndPart"] if "rndPart" in kwargs else "Q"
		self.saveRndZeroIndxs = kwargs["saveRndZeroIndxs"] if "saveRndZeroIndxs" in kwargs else True
		myPlatform = platform.uname()
		if "Windows" in myPlatform:
			self.saveImgDir = r"H:/_WORK\DATA/PYTHON/CELULAR_AUTOMAT-2D\DATA_FOR_AI/"
		else:
			self.saveImgDir = r"/storage/emulated/0/CA/_moje pokusy/CELULAR_AUTOMAT-2D/DATA_FOR_AI/"
		myTime = time.localtime()
		self.dateDir = "{0}_{1:02}_{2:02}-{3:02}_{4:02}_{5:02}/".format(*myTime)
		if "aNumRule" in kwargs:
			self.setAlphaNumRule(kwargs["aNumRule"])
		else:
			self.setAlphaNumRule()
		self.optionalZeroRndRules = self.getOptionalZeroRndRules(self.saveImgDir + self.dateDir, self.RULE_LENGTH, rndCount=self.rndCount, rndPart=self.rndPart)
		#print("self.optionalZeroRndRules {}".format(self.optionalZeroRndRules))
		self.useRule = kwargs["useRule"] if "useRule" in kwargs else "OR"
	
	def run(self, **kwargs):
		"""
			run generation of cellular automaton with attributes sets by setup() method

			kwargs["saveOnlyLast"]: optional - to save only last layer as .png image into 
								self.saveImgDir + self.dateDir, type: bool - default True
			kwargs["useRule"]: choose rule to use:
								"OR" - optional rule generates random rule according to rndPart attribute 
								"AR" - alpha numeric rule according to aNumRule parameter
								type: str 
		""" 
		#matrix of pattern counts of all rules saved in log file
		self.patCounts = np.empty((0,self.layCount,self.RULE_LENGTH), dtype=np.uint8)
		#matrix of pattern indexes of all rules saved in log file
		self.patIndxs = np.empty((0,self.layCount,self.xSize, self.ySize), dtype=np.uint16)
		cc = 0
		#sOveralTime = time.time()		
		saveOnlyLast = kwargs["saveOnlyLast"] if "saveOnlyLast" in kwargs else self.saveOnlyLast
		self.useRule = kwargs["useRule"] if "useRule" in kwargs else self.useRule
		if self.useRule == "AR":
			npRules = self.binNpRule
		else:
			npRules = self.optionalZeroRndRules
		
		for ind, rule in enumerate(npRules):
			sT = time.time()
			print("CA_count: {} \n".format(cc))
			rndRuleStr = "".join([str(z) for z in rule])
			#bin >>>> int
			myBin = rndRuleStr
			print("binary rule >>> {}".format(myBin))
			myInt = int(myBin, 2)
			print("integer rule >>> {}".format(myInt))
			#int >>>> alfanumeric
			myAnum = np.base_repr(myInt, base=36)
			print("alphanumeric rule >>> {} \n".format(myAnum))
			myCA = self.getLayers(rule, self.xSize, self.ySize, self.layCount)
			directory = myAnum +"/"
			#saveimgDir = r"/storage/emulated/0/qpython/projects/numpy/convolve/test/" +directory
			saveimgDir = self.saveImgDir + self.dateDir +directory
			logsDir = self.saveImgDir + self.dateDir + "LOGS/"
			if saveOnlyLast == False:
				self.ensure_dir(saveimgDir)
			else:
				self.ensure_dir(self.saveImgDir + self.dateDir)
			self.ensure_dir(logsDir)
			for i, v in enumerate(myCA):
				if saveOnlyLast == False:
					v *= 255                
					fileName = "{:04d}.png".format(i)
					saveimgPath = saveimgDir + fileName
					saveimg = Image.fromarray(v, mode = 'L')
					saveimg.save(saveimgPath)
					#print("myCA shape {}".format(myCA.shape))
				if i == myCA.shape[0]-1:
					v *= 255
					#fileName = "{:04d}.png".format(i)
					patCountLogName = myAnum + "_count.txt"
					patIndxsLogName = myAnum + "_indxs.txt"
					saveimgPath = self.saveImgDir + self.dateDir + myAnum + ".png"
					saveimg = Image.fromarray(v, mode = 'L')
					saveimg = saveimg.resize((self.xSize*3, self.ySize*3), resample = Image.LANCZOS)
					saveimg.save(saveimgPath)
					writeString = ""
					for lay in self.patCounts[ind]:

						#print("lay {0} \n shape {1} \n ndim {2}".format(lay, lay.shape, lay.ndim))
						writeString += ",".join([str(nums) for nums in list(lay)])
						writeString += "\n"
					self.writeFile(logsDir, writeString, patCountLogName)
					ruleIndxs = self.patIndxs[ind]
					writeString = ""
					for lay in ruleIndxs:
						#print("lay {0} \n shape {1} \n ndim {2}".format(lay, lay.shape, lay.ndim))
						for x in lay:							
							writeString += ",".join([str(y) for y in list(x)])
							writeString += "\n"
						writeString += "\n\n"
					self.writeFile(logsDir, writeString, patIndxsLogName)
			eT = time.time()
			myT = eT - sT
			partialTime = eT - self.sOveralTime
			print("time = {0:d}m {1:.6f}s \n Overal time = {2:d}m {3:.6f}s \n" \
				.format( \
					int(myT/60), \
						myT%60, \
					int(partialTime/60), \
					partialTime%60 \
					) \
				)        
			cc +=1
		eOveralTime = time.time()
		self.OveralTime = eOveralTime - self.sOveralTime
		print("Overal time = {0:d}m {1:.6f}s \n" \
				.format( \
					int(self.OveralTime/60), \
						self.OveralTime%60 \
					) \
				)

	def genCA(self, inRule, **kwargs):
		"""
			run generation of cellular automaton with attributes sets by setup() method
			
			inRule: input rule as numpy array - type(np.ndarray, shape(RULE_LENGTH), dtype = np.uint8)
			kwargs["saveOnlyLast"]: optional - to save only last layer as .png image into 
								self.saveImgDir + self.dateDir, type: bool - default True
		""" 
		#matrix of pattern counts of all rules saved in log file
		self.patCounts = np.empty((0,self.layCount,self.RULE_LENGTH), dtype=np.uint8)
		#matrix of pattern indexes of all rules saved in log file
		self.patIndxs = np.empty((0,self.layCount,self.xSize, self.ySize), dtype=np.uint16)
		#sOveralTime = time.time()		
		saveOnlyLast = kwargs["saveOnlyLast"] if "saveOnlyLast" in kwargs else self.saveOnlyLast
		self.useRule = kwargs["useRule"] if "useRule" in kwargs else self.useRule
		rule = inRule
		print("rule >>> {}".format(rule))
		#for ind, rule in enumerate(npRules):
		sT = time.time()
		rndRuleStr = "".join([str(z) for z in list(rule)])
		#bin >>>> int
		myBin = rndRuleStr
		print("binary rule >>> {}".format(myBin))
		myInt = int(myBin, 2)
		print("integer rule >>> {}".format(myInt))
		#int >>>> alfanumeric
		myAnum = np.base_repr(myInt, base=36)
		print("alphanumeric rule >>> {} \n".format(myAnum))
		myCA = self.getLayers(rule, self.xSize, self.ySize, self.layCount)
		directory = myAnum +"/"
		#saveimgDir = r"/storage/emulated/0/qpython/projects/numpy/convolve/test/" +directory
		saveimgDir = self.saveImgDir + self.dateDir +directory
		logsDir = self.saveImgDir + self.dateDir + "LOGS/"
		if saveOnlyLast == False:
			self.ensure_dir(saveimgDir)
		else:
			self.ensure_dir(self.saveImgDir + self.dateDir)
		self.ensure_dir(logsDir)
		for i, v in enumerate(myCA):
			if saveOnlyLast == False:
				v *= 255                
				fileName = "{:04d}.png".format(i)
				saveimgPath = saveimgDir + fileName
				saveimg = Image.fromarray(v, mode = 'L')
				saveimg.save(saveimgPath)
				#print("myCA shape {}".format(myCA.shape))
			if i == myCA.shape[0]-1:
				v *= 255
				#fileName = "{:04d}.png".format(i)
				patCountLogName = myAnum + "_count.txt"
				patIndxsLogName = myAnum + "_indxs.txt"
				saveimgPath = self.saveImgDir + self.dateDir + myAnum + ".png"
				saveimg = Image.fromarray(v, mode = 'L')
				saveimg = saveimg.resize((self.xSize*3, self.ySize*3), resample = Image.LANCZOS)
				saveimg.save(saveimgPath)
				writeString = ""
				for lay in self.patCounts[0]:

					#print("lay {0} \n shape {1} \n ndim {2}".format(lay, lay.shape, lay.ndim))
					writeString += ",".join([str(nums) for nums in list(lay)])
					writeString += "\n"
				self.writeFile(logsDir, writeString, patCountLogName)
				ruleIndxs = self.patIndxs[0]
				writeString = ""
				for lay in ruleIndxs:
					#print("lay {0} \n shape {1} \n ndim {2}".format(lay, lay.shape, lay.ndim))
					for x in lay:							
						writeString += ",".join([str(y) for y in list(x)])
						writeString += "\n"
					writeString += "\n\n"
				self.writeFile(logsDir, writeString, patIndxsLogName)
			eT = time.time()
			myT = eT - sT
			partialTime = eT - self.sOveralTime
			print("time = {0:d}m {1:.6f}s \n Overal time = {2:d}m {3:.6f}s \n" \
				.format( \
					int(myT/60), \
						myT%60, \
					int(partialTime/60), \
					partialTime%60 \
					) \
				)        
			
		eOveralTime = time.time()
		self.OveralTime = eOveralTime - self.sOveralTime
		print("Overal time = {0:d}m {1:.6f}s \n" \
				.format( \
					int(self.OveralTime/60), \
						self.OveralTime%60 \
					) \
				)  

	def getLayers(self, inRule, inXSize, inYSize, layCount):
		"""
			Acquire numpy array of 2D matrices of zeros and ones numpy.ndarray of ndim = 3
			The method also appends pattern counts of layer (layPatCounts) to instance attribute patCount which holds 
			pattern counts of all cellular automaton rules

			inRule: np.array of zeroes or ones. Length of an array strictly based on a convolutional kernel size 3x3 pixels
							number of 512 is power of 9 with base 2 (2 as binary numbers)
							type: numpy.ndarray returnNpArray.ndim = 1
			inXSize = width of final image type: int - default is set by instance attribute xSize
			inYSize = height of final image type: int - default is set by instance attribute ySize
			layCount = number of layers (generations) to generate - default is set by instance atribute layCount

			return numpy.ndarray of ndim = 3 
		"""
		#npLayers = np.empty((layCount,inXSize,inYSize),dtype = 'uint8')
		#get one white (one) pix binary matrix
		nextLayerMatrix = self.getOnePixMatrix(self.xSize,  self.ySize)
		#matrix of pattern counts in layer to append to self.patIndxs
		self.layPatCounts = np.empty((0,self.RULE_LENGTH), dtype=np.uint8)
		#matrix of pattern indexes in layer to append to self.patIndxs
		self.layPatIndxs = np.empty((0,self.xSize, self.ySize), dtype=np.uint16)
		
		#cancel padding and create array with first layer 
		npLayers = nextLayerMatrix.copy()
		npLayers = np.delete(npLayers, 0, axis = 1)
		npLayers = np.delete(npLayers, npLayers.shape[1]-1, axis = 1)
		npLayers = np.delete(npLayers, 0, axis = 0)
		npLayers = np.delete(npLayers, npLayers.shape[0]-1, axis = 0)
		npLayers.resize((1,inXSize,inYSize))
		#npLayers = np.append(npLayers,nextLayerMatrix, axis = 0)

		sTime = time.time()
		for x in range(0, layCount):
			sub_matrices = self.getSubMatrices(nextLayerMatrix, self.KERNEL_SIZE)
			#reshape kernel 3x3 matrices to 1D array 
			sub_matrices2 = np.resize(sub_matrices, (sub_matrices.shape[0],sub_matrices.shape[1], sub_matrices.shape[2]*sub_matrices.shape[3]))
			# get list of all binary combinations of 3x3 kernels
			rulePaterns = self.getRulesPaternAsStringSequence(self.KERNEL_SIZE * self.KERNEL_SIZE)
			# get new layer matrix by evaluating sub_matrices according to rulePatterns  
			#ruleValues = self.getRuleValues(sub_matrices2, rulePaterns, inRule)
			npNewMatrix = self.getRuleValues(sub_matrices2, rulePaterns, inRule)
			#npNewMatrix = np.asarray(ruleValues,dtype='uint8')
			npNMX = npNewMatrix.copy()
			npNMX.resize((1,inXSize,inYSize))
			npLayers = np.append(npLayers,npNMX, axis = 0)
			#insert padding for next layers
			padding = np.zeros((npNewMatrix.shape[0]), dtype='uint8')
			#print("leftPadding {}".format(padding))
			npNewMatrix = np.insert(npNewMatrix,0,padding, axis = 1)
			npNewMatrix = np.insert(npNewMatrix,npNewMatrix.shape[1]-1,padding, axis = 1)
			padding = np.zeros((npNewMatrix.shape[1]), dtype='uint8')
			npNewMatrix = np.insert(npNewMatrix,0,padding, axis = 0)
			npNewMatrix = np.insert(npNewMatrix,npNewMatrix.shape[0]-1,padding, axis = 0)
			nextLayerMatrix = npNewMatrix.copy()
		#print("self.layPatCounts {0} \n shape {1} \n ndim {2}".format(self.layPatCounts, self.layPatCounts.shape, self.layPatCounts.ndim))
		self.layPatCounts.resize((1,self.layPatCounts.shape[0],self.layPatCounts.shape[1]))
		self.layPatIndxs.resize((1,self.layPatIndxs.shape[0],self.layPatIndxs.shape[1], self.layPatIndxs.shape[2]))
		#print("self.layPatCounts resized {0} \n shape {1} \n ndim {2}".format(self.layPatCounts, self.layPatCounts.shape, self.layPatCounts.ndim))
		#print("self.patCounts {0} \n shape {1} \n ndim {2}".format(self.patCounts, self.patCounts.shape, self.patCounts.ndim))
		self.patCounts = np.append(self.patCounts, self.layPatCounts, axis = 0)
		self.patIndxs = np.append(self.patIndxs, self.layPatIndxs, axis = 0)
		eTime = time.time()
		myTime = eTime - sTime
		# print("npLayers  {0} \n shape {3} dtype {4}\n time = {1:d}m {2:.6f}s" \
		#     .format( \
		#         npLayers, \
		#         int(myTime/60), \
		#             myTime%60, \
		#             npLayers.shape, \
		#             npLayers.dtype \
		#            ) \
		#     )
		return npLayers

	def getSubMatrices(self, inNpArray, kernelSize):
		"""
			acquire kernel matrices of 2D matrix
			inNpArray: 2D matrix of type: numpy.ndarray, numpy.ndim = 2

			return numpy.ndarray - binary 3x3 matrices of numpy.ndim = 4 
					(width of input 2D matrix, height of input 2D matrix, width of kernel, height of kernel)  
		"""
		sub_shape = (kernelSize,kernelSize) 
		view_shape = tuple(np.subtract(inNpArray.shape, sub_shape) + 1) + sub_shape
		strides = inNpArray.strides + inNpArray.strides 
		sub_matrices = np.lib.stride_tricks.as_strided(inNpArray,view_shape,strides)
		return sub_matrices

	def getRulesPaternAsStringSequence(self, inKernelLength):
		"""
			get list of all binary combinations of 3x3 kernels as 1D list of strings
			
			inKernelLength: length of kernel matrix (3x3) type: int

			return list[str,...]
		"""
		rulesCount = pow(2, inKernelLength)
		arRange = range(0, rulesCount)
		binSeqDiv = [pow(2, x) for x in range(0,inKernelLength)]
		binSeqDiv.reverse()
		myArray = [[str(math.trunc(x / y) % 2) for x in arRange] for y in binSeqDiv]
		myArray = map(list, zip(*myArray))
		returnArray = []
		for i in myArray:
			myChars = "".join(i)
			returnArray.append(myChars) 
		return returnArray

	def getRuleValues(self, inNpKernels, inPatSeq, inNpRule):
		"""
			get new layer 2D matrix by evaluating sub_matrices of previous layer matrix according to rule patterns 
			The method also appends pattern counts of layer (patCount) to instance attribute layPatCount which holds 
			pattern counts of all layers

			inNpKernels: numpy.ndarray - binary (uint8) 3x3 matrices of numpy.ndim = 3 
							(width of input 2D matrix, height of input 2D matrix, 1D array of 3x3 kernel)  
			inPatSeq: list of all binary combinations of 3x3 kernels as 1D list of strings, type: list[str,...]
			inNpRule: np.array of zeroes or ones. Length of an array strictly based on a convolutional kernel size 3x3 pixels
							number of 512 is power of 9 with base 2 (2 as binary numbers)
							type: numpy.ndarray returnNpArray.ndim = 1
			
			return returnMatrix np.ndarray of ndim = 2
		"""
		#returnArray = []
		patCount = np.zeros((len(inPatSeq))).astype(np.uint8)
		patIndxs = np.zeros((self.xSize, self.ySize)).astype(np.uint16)
		returnMatrix = np.zeros((inNpKernels.shape[0], inNpKernels.shape[1])).astype(np.uint8)
		#print("patCount {}".format(patCount))
		#npArray = np.empty((0),dtype = 'string_')
		#stringDtype = np.dtype([('sequence','S20')])
		#npKernels = inNpKernels.copy().astype('string_')
		#kernelsToList = list(npKernels)
		for i, x in enumerate(inNpKernels):
			#yArray = []
			#print("x {}".format(x))
			for j, y in enumerate(x):
				#y.astype(stringDtype)
				#charList = list(y)
				#joinedChars = np.char.join(['-'],list(y))
				#npArray = np.append(npArray, joinedChars)
				kernelStr = "".join([str(z) for z in y])
				inPatSeq = list(inPatSeq)
				patIndx = inPatSeq.index(kernelStr)
				patIndxs[i,j] = patIndx
				val = inNpRule[patIndx]
				patCount[patIndx] += 1
				if val == 1:
					returnMatrix[i,j] = 1
				#yArray.append(val)
				#print("y {}".format(y))
			#returnArray.append(yArray)
		#print("patCount {}".format(patCount))
		patCount.resize((1,patCount.shape[0]))
		patIndxs.resize((1,patIndxs.shape[0], patIndxs.shape[1]))
		self.layPatCounts = np.append(self.layPatCounts, patCount, axis = 0)
		self.layPatIndxs = np.append(self.layPatIndxs, patIndxs, axis = 0)
		return returnMatrix

	def getOnePixMatrix(self, inXSize, inYSize):
		"""
			acquire initial binary matrix with one pixel white (one) in center with padding from each side
			result matrix has more of 2 columns and rows than input size 

			inXSize: width of final image type: int - default is set by instance attribute xSize
			inYSize: height of final image type: int - default is set by instance attribute ySize

			return numpy.ndarray of ndim = 2 

		"""
		returnMX = np.zeros((inXSize +2,inYSize +2), dtype = 'uint8')
		returnMX[int((inXSize +2)/2), int((inYSize +2)/2)] = 1
		return returnMX

	def setSaveImgDir(self,inDirPath):
		"""
			sets the directory to save generated images
			images will be saved into subdirectories named according to creation date stored in self.dateDir atribute

			inDirPath: path to directory in format e.g. r"C:/dir/another_dir/"
		"""
		self.saveImgDir = inDirPath
		print ("self.saveImgDir was set >>> {}".format(self.saveImgDir))

	def setAlphaNumRule(self, *args):
		"""
			sets the alpha numerical representation of rule

			*args[0]: optional anumRuleStr - alpha numerical rule, type: str (36 alphanumeric characters A-Z, 0-9)
		"""
		self.aNumRule = args[0] if len(args) > 0 else "DANOMARTINASIMONTHEA"
		print ("alphaNumRule was set >>> {}".format(self.aNumRule))
		self.intRule = int(self.aNumRule,36)
		print ("intRule was set >>> {}".format(self.intRule))
		self.binRule = "{:0512b}".format(self.intRule)
		print ("binRule was set >>> {}".format(self.binRule))
		self.binRuleArray = [int(x,10) for x in self.binRule]
		print ("binRuleArray was set >>> {0} \n length {1} \n type {2} \n".format(self.binRuleArray, len(self.binRuleArray), type(self.binRuleArray[0])))
		self.binNpRule = np.asarray(self.binRuleArray, dtype=np.int8)
		self.binNpRule.resize((1, self.binNpRule.shape[0]))
		print ("numNpRule >>> was set {0} \n shape {1} \n dtype {2} \n".format(self.binNpRule, self.binNpRule.shape, self.binNpRule.dtype))
	
	def getOptionalZeroRndRules(self, inWrigthLogDir, *args, **kwargs):
		"""
			generates random rule (np.array of zeroes or ones of certain length)
			
			args[0]: inRuleLength: length of an array strictly based on a convolutional kernel size 3x3 pixels
							number of 512 is power of 9 with base 2 (2 as binary numbers)
			kwargs["rndPart"]: optional - part of zeroed items in rule array:
										"Q" - 3/4 of items set to zero
										"O" - 7/8 of items set to zero
										"H" - 1/2 of items set to zero
										"N" - None of items set to zero
										default "Q" 
			
			return myRule type: numpy.ndarray returnNpArray.ndim = 1
		"""
		part = kwargs["rndPart"] if "rndPart" in kwargs else "H"
		inRuleLength = args[0] if len(args) > 0 else cls.RULE_LENGTH
		myRuleCount = kwargs["rndCount"] if "rndCount" in kwargs else 1
		myRuleGen = self.generateRndRule(rndCount = None)
		myRules = np.empty((inRuleLength), dtype = np.uint8)
		myRules = np.resize(myRules, (1, myRules.shape[0]))
		for i in range(0,myRuleCount):			
			indxs = np.arange(inRuleLength)
			indxs.setflags(write=1)
			# print("indxs {0} \n shape {1} \n dtype {2} \n flags {3}" \
			# 	.format( \
			# 			indxs, \
			# 			indxs.shape, \
			# 			indxs.dtype, \
			# 			indxs.flags \
			# 			) \
			# 	)
			np.random.shuffle(indxs)
			# print("indxs {0} \n shape {1} \n dtype {2} \n flags {3}" \
			# 	.format( \
			# 			indxs, \
			# 			indxs.shape, \
			# 			indxs.dtype, \
			# 			indxs.flags \
			# 			) \
			# 	)
			if part == "O":
				returnIndxs = indxs[:int(inRuleLength*7/8)]
			elif part == "Q":
				returnIndxs = indxs[:int(inRuleLength*3/4)]
			elif part == "H":
				returnIndxs = indxs[:int(inRuleLength/2)]
			else:
				returnIndxs = indxs

			if self.saveRndZeroIndxs == True:
				returnIndxsStr = ",".join([str(x) for x in list(returnIndxs)])
				fileName = "zeroIndex.txt"
				self.writeFile(inWrigthLogDir, returnIndxsStr, fileName)
			myRule = next(myRuleGen)
			myRule[...,returnIndxs] = 0
			myRule = np.resize(myRule, (1,myRule.shape[0]))
			#print("myRule - {0} shape {1} dtype {2} myRules {3} shape {4} shape {5}".format(myRule, myRule.shape, myRule.dtype, myRules, myRules.shape, myRules.dtype))
			myRules = np.append(myRules, myRule, axis = 0)
		return myRules

	# def generateRndRule(self, *args, **kwargs):
	# 	"""
	# 		generates random rule (np.array of zeroes or ones of certain length)

	# 		args[0]: inRuleLength: length of an array strictly based on a convolutional kernel size 3x3 pixels
	# 						number of 512 is power of 9 with base 2 (2 as binary numbers)
	# 		kwargs["rndCount"]: count of randomly generated rules

	# 		return returnNpArray type: numpy.ndarray returnNpArray.ndim = 1
	# 	"""
	# 	if "rndCount" in kwargs:
	# 		count = kwargs["rndCount"]
	# 	else:
	# 		count = 1
	# 	inRuleLength = args[0] if len(args) > 0 else Ca2D_3x3.RULE_LENGTH
		
	# 	if count == None:
	# 		i = 0
	# 		while True:
	# 			returnNpArray = np.random.randint(2, size=inRuleLength)
	# 			print("self.generateRndRule {1} - {0}".format(returnNpArray,i))
	# 			# body of the loop ...
	# 			yield returnNpArray
	# 			i += 1
	# 	else:
	# 		returnNpArray = np.empty((0,inRuleLength), dtype=np.int8)
	# 		for x in range(0,count):
	# 			array = np.random.randint(2, size=inRuleLength)
	# 			array.resize(1,array.shape[0])
	# 			returnNpArray = np.append(returnNpArray, array, axis=0)
	# 		return returnNpArray

	def generateRndRule(self, *args, **kwargs):
		"""
			generates random rule (np.array of zeroes or ones of certain length)

			args[0]: inRuleLength: length of an array strictly based on a convolutional kernel size 3x3 pixels
							number of 512 is power of 9 with base 2 (2 as binary numbers)
			kwargs["rndCount"]: count of randomly generated rules

			return returnNpArray type: numpy.ndarray returnNpArray.ndim = 1
		"""
		if "rndCount" in kwargs:
			count = kwargs["rndCount"]
		else:
			count = 1
		inRuleLength = args[0] if len(args) > 0 else Ca2D_3x3.RULE_LENGTH
		
		if count == None:
			i = 0
			while True:
				returnNpArray = np.random.randint(2, size=inRuleLength, dtype=np.uint8)
				
				#print("self.generateRndRule {1} - {0}".format(returnNpArray,i))
				# body of the loop ...
				yield returnNpArray
				i += 1
	def generateRuleSequence(self, inStartPosition, inIncrement = 1, **kwargs):
		"""
			Generates increasing binary rule according to start position (000...01, 000...10, 000...11, ..) of length 512  
			
			inStartPos: start position of sequence type:int or type:str (only alphanumeric characters)
			
			inIncrement: increment or decrement number according to inc optional attribute type: int default: 1
			kwargs["inc"]: optional, increase sequence if inc == True else decrease, type: bool, default: True
			kwargs["rev"]: optional, reverse side of increasing (00000, 10000, 01000, 11000.. ), default False
		"""
		isIncreasing = kwargs["inc"] if "inc" in kwargs else True
		isReversed  = kwargs["rev"] if "rev" in kwargs else False
		count = inStartPosition if type(inStartPosition) == int else int(inStartPosition,36)
		print("Start Position - {0} \n count {1}".format(inStartPosition, count))
		while True:
			self.aNumRule = np.base_repr(count, base=36)
			self.binRule = "{:0512b}".format(count)
			self.binRuleArray = [int(x,10) for x in self.binRule]	
			self.binRuleArray = self.binRuleArray if not isReversed else self.binRuleArray[::-1]
			print("self.binRuleArray {0} len {1}".format(self.binRuleArray, len(self.binRuleArray)))
			self.binNpRule = np.asarray(self.binRuleArray, dtype=np.int8)
			#self.binNpRule.resize((1, self.binNpRule.shape[0]))
			yield self.binNpRule
			count = count + inIncrement if isIncreasing and not isReversed else count - inIncrement


	def writeFile(self, inWrigthDir, inStr, inFileName):
		"""
			writes the input string into file

			inWrightDir: path to directory in format e.g. r"C:/dir/another_dir/" type: str
			inStr: string to write, type: str
			inFileName: name of file to save e.q. log.txt
		"""
		self.ensure_dir(inWrigthDir)
		file = open(inWrigthDir + inFileName,"w")  
		file.write(inStr) 
		file.close() 
	
	def ensure_dir(self, file_path):
		directory = os.path.dirname(file_path) 
		if not os.path.exists(directory):
			os.makedirs(directory)

	def generateRndCAs(self):
		"""
			Generates infinitive loop of random celular automaton 

		"""
		i = 0	
		
		for rule in self.generateRndRule(rndCount=None):
			#print ('Testing...{}'.format(rule))
			#print("Random Rule {0}".format(rule,i))
			self.genCA(rule)
			# body of the loop ...
			if msvcrt.kbhit():
				if ord(msvcrt.getch()) == 27:
					break
			i += 1

	def generateSequenceCAs(self, inStartPosition, inIncrement = 1, **kwargs):
		"""
			Generates increasing sequence loop of celular automaton
			Increasing binary rule according to start position (00001, 00010, 00011, ..) of length 512  

			inStartPos: start position of sequence type:int
			inIncrement: increment or decrement number according to inc optional attribute type: int default: 1
			kwargs["inc"]: optional, increase sequence if inc == True else decrease, type: bool, default: True
			kwargs["rev"]: optional, reverse side of increasing (00000, 10000, 01000, 11000.. ), default False

		"""
		i = 0			
		for rule in self.generateRuleSequence(inStartPosition, inIncrement, **kwargs):
			#print ('Testing...{}'.format(rule))
			#print("Random Rule {0}".format(rule,i))
			self.genCA(rule)
			# body of the loop ...
			if msvcrt.kbhit():
				if ord(msvcrt.getch()) == 27:
					break
			i += 1


