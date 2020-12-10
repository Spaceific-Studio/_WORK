import random
import numpy as np
from PIL import Image
import time
#import matplotlib.pyplot as plt
import math
import os
from datetime import datetime

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
			kwargs["rndCount"]: optional - number of randomly generated rules type: int - default 500
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
		self.rndCount = kwargs["rndCount"] if "rndCount" in kwargs else 500
		self.rndPart = kwargs["rndPart"] if "rndPart" in kwargs else "Q"
		self.saveRndZeroIndxs = kwargs["saveRndZeroIndxs"] if "saveRndZeroIndxs" in kwargs else True
		self.saveImgDir = r"C:/_WORK/PYTHON/projects/numpy/convolve/test/"
		myTime = time.localtime()
		self.dateDir = "{0}_{1:02}_{2:02}-{3:02}_{4:02}_{5:02}/".format(*myTime)
		if "aNumRule" in kwargs:
			self.setAlphaNumRule(kwargs["aNumRule"])
		else:
			self.setAlphaNumRule()
		self.optionalZeroRndRules = self.getOptionalZeroRndRules(self.saveImgDir + self.dateDir, self.RULE_LENGTH, rndCount=self.rndCount, rndPart=self.rndPart)
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
		self.patCounts = np.empty((0,self.layCount,self.RULE_LENGTH), dtype=np.uint8)
		cc = 0
		#sOveralTime = time.time()		
		saveOnlyLast = kwargs["saveOnlyLast"] if "saveOnlyLast" in kwargs else self.saveOnlyLast
		self.useRule = kwargs["useRule"] if "useRule" in kwargs else self.useRule
		if self.useRule == "AR":
			npRules = self.anumNpRule
		else:
			npRules = self.optionalZeroRndRules
		for rule in npRules:
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
			if saveOnlyLast == False:
				self.ensure_dir(saveimgDir)
			else:
				self.ensure_dir(self.saveImgDir + self.dateDir)
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
					fileName = "{:04d}.png".format(i)
					saveimgPath = self.saveImgDir + self.dateDir + myAnum + ".png"
					saveimg = Image.fromarray(v, mode = 'L')
					saveimg = saveimg.resize((self.xSize*3, self.ySize*3), resample = Image.LANCZOS)
					saveimg.save(saveimgPath)
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
		self.layPatCounts = np.empty((0,self.RULE_LENGTH), dtype=np.uint8)
		
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
			ruleValues = self.getRuleValues(sub_matrices2, rulePaterns, inRule)
			
			npNewMatrix = np.asarray(ruleValues,dtype='uint8')
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
		print("self.layPatCounts {0} \n shape {1} \n ndim {2}".format(self.layPatCounts, self.layPatCounts.shape, self.layPatCounts.ndim))
		self.layPatCounts.resize((1,self.layPatCounts.shape[0],self.layPatCounts.shape[1]))
		print("self.layPatCounts resized {0} \n shape {1} \n ndim {2}".format(self.layPatCounts, self.layPatCounts.shape, self.layPatCounts.ndim))
		print("self.patCounts {0} \n shape {1} \n ndim {2}".format(self.patCounts, self.patCounts.shape, self.patCounts.ndim))
		self.patCounts = np.append(self.patCounts, self.layPatCounts, axis = 0)
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
			get new layer 2D matrix by evaluating sub_matrices previous layer matrix according to rule patterns 
			The method also appends pattern counts of layer (patCount) to instance attribute layPatCount which holds 
			pattern counts of all layers

			inNpKernels: numpy.ndarray - binary (uint8) 3x3 matrices of numpy.ndim = 3 
							(width of input 2D matrix, height of input 2D matrix, 1D array of 3x3 kernel)  
			inPatSeq: list of all binary combinations of 3x3 kernels as 1D list of strings, type: list[str,...]
			inNpRule: np.array of zeroes or ones. Length of an array strictly based on a convolutional kernel size 3x3 pixels
							number of 512 is power of 9 with base 2 (2 as binary numbers)
							type: numpy.ndarray returnNpArray.ndim = 1
		"""
		returnArray = []
		patCount = np.zeros((len(inPatSeq))).astype(np.uint8)
		#print("patCount {}".format(patCount))
		#npArray = np.empty((0),dtype = 'string_')
		#stringDtype = np.dtype([('sequence','S20')])
		#npKernels = inNpKernels.copy().astype('string_')
		#kernelsToList = list(npKernels)
		for x in inNpKernels:
			yArray = []
			#print("x {}".format(x))
			for y in x:
				#y.astype(stringDtype)
				#charList = list(y)
				#joinedChars = np.char.join(['-'],list(y))
				#npArray = np.append(npArray, joinedChars)
				kernelStr = "".join([str(z) for z in y])
				inPatSeq = list(inPatSeq)
				patIndx = inPatSeq.index(kernelStr)
				val = inNpRule[patIndx]
				patCount[patIndx] += 1
				yArray.append(val)
				#print("y {}".format(y))
			returnArray.append(yArray)
		print("patCount {}".format(patCount))
		patCount.resize((1,patCount.shape[0]))
		self.layPatCounts = np.append(self.layPatCounts, patCount, axis = 0)
		return returnArray

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
		self.anumNpRule = np.asarray(self.binRuleArray, dtype=np.int8)
		self.anumNpRule.resize((1, self.anumNpRule.shape[0]))
		print ("numNpRule >>> was set {0} \n shape {1} \n dtype {2} \n".format(self.anumNpRule, self.anumNpRule, self.anumNpRule.dtype))
	
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
		myRule = self.generateRndRule(*args, **kwargs)
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
			writeFile(inWrigthLogDir, returnIndxsStr, fileName)
		myRule[...,returnIndxs] = 0
		return myRule

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
		inRuleLength = args[0] if len(args) > 0 else cls.RULE_LENGTH
		if count > 1:
			returnNpArray = np.empty((0,inRuleLength), dtype=np.int8)
			for x in range(0,count):
				array = np.random.randint(2, size=inRuleLength)
				array.resize(1,array.shape[0])
				returnNpArray = np.append(returnNpArray, array, axis=0)
		else:
			returnNpArray = np.random.randint(2, size=inRuleLength)
		return returnNpArray

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

def ensure_dir(file_path):
    directory = os.path.dirname(file_path) 
    if not os.path.exists(directory):
        os.makedirs(directory)

def generateRndRule(inRuleLength, **kwargs):
    if "count" in kwargs:
        count = kwargs["count"]
    else:
        count = 1
    if count > 1:
        returnNpArray = np.empty((0,inRuleLength), dtype=np.int8)
        for x in range(0,count):
            array = np.random.randint(2, size=inRuleLength)
            array.resize(1,array.shape[0])
            returnNpArray = np.append(returnNpArray, array, axis=0)
    else:
        returnNpArray = np.random.randint(2, size=inRuleLength)
    return returnNpArray

def writeFile(inWrigthDir, inStr, inFileName):
    ensure_dir(inWrigthDir)
    file = open(inWrigthDir + inFileName,"w")  
    file.write(inStr) 
    file.close() 

def getOptionalZeroRule(inRuleLength, inWrigthLogDir, **kwargs):
    part = kwargs["part"] if "part" in kwargs else "H"
    myRule = generateRndRule(inRuleLength, **kwargs)
    indxs = np.arange(inRuleLength)
    indxs.setflags(write=1)
    print("indxs {0} \n shape {1} \n dtype {2} \n flags {3}" \
        .format( \
                indxs, \
                indxs.shape, \
                indxs.dtype, \
                indxs.flags \
                ) \
        )
    np.random.shuffle(indxs)
    print("indxs {0} \n shape {1} \n dtype {2} \n flags {3}" \
        .format( \
                indxs, \
                indxs.shape, \
                indxs.dtype, \
                indxs.flags \
                ) \
        )
    if part == "O":
        halfIndxs = indxs[:int(inRuleLength*7/8)]
    elif part == "Q":
        halfIndxs = indxs[:int(inRuleLength*3/4)]
    else:
        halfIndxs = indxs[:int(inRuleLength/2)]
    print(myRule)
    halfIndxsStr = ",".join([str(x) for x in list(halfIndxs)])
    fileName = "zeroIndex.txt"
    writeFile(inWrigthLogDir, halfIndxsStr, fileName)
    myRule[...,halfIndxs] = 0
    return myRule
    
def npRemap(inNpArray, minInput, maxInput, minOutput, maxOutput):
    inputSpan = maxInput - minInput
    outputSpan = maxOutput - minOutput
    inNpArray -= minInput
    inNpArray /= inputSpan
    inNpArray *= outputSpan
    inNpArray += minOutput
    return inNpArray

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

def getSubMatrices(inNpArray, kernelSize):
    sub_shape = (kernelSize,kernelSize) 
    view_shape = tuple(np.subtract(inNpArray.shape, sub_shape) + 1) + sub_shape
    strides = inNpArray.strides + inNpArray.strides 
    sub_matrices = np.lib.stride_tricks.as_strided(inNpArray,view_shape,strides)
    return sub_matrices

def getRulesPaternSeqence(inKernelLength):
    rulesCount = pow(2, inKernelLength)
    arRange = range(0, rulesCount)
    binSeqDiv = [pow(2, x) for x in range(0,inKernelLength)]
    binSeqDiv.reverse()
    myArray = [[math.trunc(x / y) % 2 for x in arRange] for y in binSeqDiv]
    myArray = map(list, zip(*myArray)) 
    return myArray

def getRulesPaternAsStringSequence(inKernelLength):
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

def getRuleValues(inNpKernels, inPatSeq, inNpRule):
    returnArray = []
    #npArray = np.empty((0),dtype = 'string_')
    #stringDtype = np.dtype([('sequence','S20')])
    #npKernels = inNpKernels.copy().astype('string_')
    #kernelsToList = list(npKernels)
    for x in inNpKernels:
        yArray = []
        for y in x:
            #y.astype(stringDtype)
            #charList = list(y)
            #joinedChars = np.char.join(['-'],list(y))
            #npArray = np.append(npArray, joinedChars)
            kernelStr = "".join([str(z) for z in y])
            inPatSeq = list(inPatSeq)
            patIndx = inPatSeq.index(kernelStr)
            val = inNpRule[patIndx]
            yArray.append(val)
        returnArray.append(yArray)
    return returnArray

def getOnePixMatrix(inXSize,inYSize):
    returnMX = np.zeros((inXSize +2,inYSize +2), dtype = 'uint8')
    returnMX[int((inXSize +2)/2), int((inYSize +2)/2)] = 1
    return returnMX

def getLayers(inXSize, inYSize, inRule, layCount):
    #npLayers = np.empty((layCount,inXSize,inYSize),dtype = 'uint8')
    nextLayerMatrix = getOnePixMatrix(inXSize, inYSize)
    npLayers = nextLayerMatrix.copy()
    npLayers = np.delete(npLayers, 0, axis = 1)
    npLayers = np.delete(npLayers, npLayers.shape[1]-1, axis = 1)
    npLayers = np.delete(npLayers, 0, axis = 0)
    npLayers = np.delete(npLayers, npLayers.shape[0]-1, axis = 0)
    npLayers.resize((1,inXSize,inYSize))
    #npLayers = np.append(npLayers,nextLayerMatrix, axis = 0)
    sTime = time.time()
    
    for x in range(0, layCount):
        sub_matrices = getSubMatrices(nextLayerMatrix, 3)
        sub_matrices2 = np.resize(sub_matrices, (sub_matrices.shape[0],sub_matrices.shape[1], sub_matrices.shape[2]*sub_matrices.shape[3]))
        rulePaterns = getRulesPaternAsStringSequence(9)
        ruleValues = getRuleValues(sub_matrices2, rulePaterns, inRule)
        npNewMatrix = np.asarray(ruleValues,dtype='uint8')
        npNMX = npNewMatrix.copy()
        npNMX.resize((1,inXSize,inYSize))
        npLayers = np.append(npLayers,npNMX, axis = 0)
        padding = np.zeros((npNewMatrix.shape[0]), dtype='uint8')
        #print("leftPadding {}".format(padding))
        npNewMatrix = np.insert(npNewMatrix,0,padding, axis = 1)
        npNewMatrix = np.insert(npNewMatrix,npNewMatrix.shape[1]-1,padding, axis = 1)
        padding = np.zeros((npNewMatrix.shape[1]), dtype='uint8')
        npNewMatrix = np.insert(npNewMatrix,0,padding, axis = 0)
        npNewMatrix = np.insert(npNewMatrix,npNewMatrix.shape[0]-1,padding, axis = 0)
        nextLayerMatrix = npNewMatrix.copy()
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

def run(inNpRules, inXSize, inYSize, inLayCount, inSaveDir, inDateDir, **kwargs):
    cc = 0
    sOveralTime = time.time()
    if "saveOnlyLast" in kwargs:
        saveOnlyLast = kwargs["saveOnlyLast"]
    else:
        saveOnlyLast = False
    for rule in inNpRules:
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
        
        myCA = getLayers(inXSize, inYSize, rule, inLayCount)

        directory = myAnum +"/"
        #saveimgDir = r"/storage/emulated/0/qpython/projects/numpy/convolve/test/" +directory
        saveimgDir = inSaveDir + dateDir +directory
        if saveOnlyLast == False:
            ensure_dir(saveimgDir)
        else:
            ensure_dir(inSaveDir + dateDir)
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
                fileName = "{:04d}.png".format(i)
                saveimgPath = inSaveDir + dateDir + myAnum + ".png"
                saveimg = Image.fromarray(v, mode = 'L')
                saveimg = saveimg.resize((inXSize*3, inYSize*3), resample = Image.LANCZOS)
                saveimg.save(saveimgPath)
        eT = time.time()
        myT = eT - sT
        partialTime = eT - sOveralTime
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
    myOveralTime = eOveralTime - sOveralTime
    print("Overal time = {0:d}m {1:.6f}s \n" \
            .format( \
                int(myOveralTime/60), \
                    myOveralTime%60 \
                ) \
            )  

myCa = Ca2D_3x3()
myCa.run()
#imgPath =  r"/storage/emulated/0/qpython/projects/numpy/convolve/t_001.png"
#imgPath = r"C:/_WORK/PYTHON/projects/numpy/convolve/t_001.png"
#img = Image.open(imgPath)
#img.draft('L', img.size)
# img = img.convert('L')
#img2 = Image.open(imgPath)
# imgData = np.asarray(img)
# imgData.setflags(write=1)
# imgDataa = imgData.copy()
# imgDataa.setflags(write=1)
# imgData = np.asarray(imgData, dtype="float_") 
# imgData /= 255
# imgData = np.asarray(imgData, dtype="uint8") 
# #imgData = np.array(img2.getdata(), dtype=float)
# #imgData2 = np.array(img.getdata())
# imgDataXSize = imgData.shape[0]
# imgDataYSize = imgData.shape[1]
# padding = np.zeros((imgData.shape[0]), dtype='uint8')
# print("leftPadding {}".format(padding))
# imgData = np.insert(imgData,0,padding, axis = 1)
# imgData = np.insert(imgData,imgData.shape[1]-1,padding, axis = 1)
# padding = np.zeros((imgData.shape[1]), dtype='uint8')
# imgData = np.insert(imgData,0,padding, axis = 0)
# imgData = np.insert(imgData,imgData.shape[0]-1,padding, axis = 0)
# #imgData.resize((imgDataXSize*imgDataYSize,3))
# #imgData.resize((imgDataXSize,imgDataYSize,3))
# imgData = getOnePixMatrix(51,51)
# #id2 = imgData.copy()
# #id2.resize((1,51,51))
# #imgData.resize((1,51,51))
# #imgData = np.append(imgData,id2, axis=0)
# print("imgData {0} \n shape {1} \n dtype {2} \n ndim {3} \n" \
# 	    .format( \
# 	            imgData, \
# 	            imgData.shape, \
# 	            imgData.dtype, \
# 	            imgData.ndim \
# 	           ) \
# 	    )


#sTime = time.time()
#sub_shape = (3,3) 
#view_shape = tuple(np.subtract(imgData.shape, sub_shape) + 1) + sub_shape
#strides = imgData.strides + imgData.strides 
#sub_matrices = getSubMatrices(imgData, 3)
#sub_matrices2 = np.resize(sub_matrices, (sub_matrices.shape[0],sub_matrices.shape[1], sub_matrices.shape[2]*sub_matrices.shape[3]))
#vec = np.array([1,1,1,1,1,1,1,1,1], dtype='uint8')
#dotted = np.dot(sub_matrices2, vec)
# eTime = time.time()
# myTime = eTime - sTime

# print("sub_matrices2 {0} \n shape {3} dtype {4}\n time = {1:d}m {2:.6f}s" \

# 	    .format( \

#             sub_matrices2, \

#             int(myTime/60), \

# 	            myTime%60, \

# 	            sub_matrices2.shape, \

# 	            sub_matrices2.dtype \

# 	           ) \

# 	    )
# sTime = time.time()	    
# myRulePaterns = getRulesPaternAsStringSequence(9)

# mRP = np.array(myRulePaterns, np.float64)
# print("mRP {0} \n shape {3} dtype {4}\n time = {1:d}m {2:.6f}s" \

# 	    .format( \

#             mRP, \

#             int(myTime/60), \

# 	            myTime%60, \

# 	            mRP.shape, \

# 	            mRP.dtype \

# 	           ) \

# 	    )
# vec = np.array(list([1,1,1,1,1,1,1,1,1]), np.float64)
#vec = np.broadcast_to(vec, (512, 9))
# print("vec {0} \n shape {3} dtype {4}\n time = {1:d}m {2:.6f}s" \

# 	    .format( \

#             vec, \

#             int(myTime/60), \

# 	            myTime%60, \

# 	            vec.shape, \

# 	            vec.dtype \

# 	           ) \

# 	    )
# sTime = time.time()	 
# returnDotted = np.empty((0), np.float64)
# eTime = time.time()
# myTime = eTime - sTime
# for x in mRP:
#         dotted = np.dot(x, vec)
#         returnDotted = np.append(returnDotted,dotted)

#dotted = np.dot(mRP, vec)
# print("returnDotted {0} \n shape {3} dtype {4}\n time = {1:d}m {2:.6f}s" \

# 	    .format( \

#             returnDotted, \

#             int(myTime/60), \

# 	            myTime%60, \

# 	            returnDotted.shape, \

# 	            returnDotted.dtype \

# 	           ) \

# 	    )
# rndNpRule = generateRndRule(512)
# rndNpRuleStr = rndNpRule.copy().astype(np.string_)
# rndNpRule = list(rndNpRule)
# rndNpRuleStr = list(rndNpRuleStr)
# rndRuleStr = "".join([str(x) for x in rndNpRule])

#bin >>>> int
#myBin = rndRuleStr
#print("myBin {}".format(myBin))
#myInt = int(myBin, 2)
#print("myBin >>> myInt {1}".format(myBin, myInt))
#int >>>> alfanumeric
#myAnum = np.base_repr(myInt, base=36)  
#print("myInt >>> myAnum {1}".format(myInt, myAnum))

# print("rndRuleStr {0} \n shape {1}" \
# 	    .format( \
# 	            rndRuleStr, \
# 	            len(rndRuleStr) \
# 	           ) \
# 	    )
#rndRuleStr = "".join(rndNpRuleStr.decode("utf-8"))
# rndRuleStr = rndRuleStr[:25]
# eTime = time.time()
# myTime = eTime - sTime
# print("myRulePaterns {0} \n length {3} \n rndRule {4} \n time = {1:d}m {2:.6f}s" \

# 	    .format( \

#             myRulePaterns, \

#             int(myTime/60), \

# 	            myTime%60, \

# 	            len(list(myRulePaterns)), \
# 	            rndNpRule \

# 	           ) \

# 	    )
#print("myIndex {}".format(list(myRulePaterns).index("000000110")))
# sTime = time.time()	    
# ruleValues = getRuleValues(sub_matrices2, myRulePaterns,rndNpRule)
# npNewMatrix = np.asarray(ruleValues,dtype='uint8')
# eTime = time.time()
# myTime = eTime - sTime
# print("ruleValues {0} \n shape \n time = {1:d}m {2:.6f}s" \

# 	    .format( \

#              ruleValues, \

#              int(myTime/60), \

# 	            myTime%60 \

# #	            ruleValues.shape \
# #             len(ruleValues) \

# 	           ) \

# 	    )

# print("npNewMatrix {0} \n shape {3} \n time = {1:d}m {2:.6f}s" \

# 	    .format( \

#              npNewMatrix, \

#              int(myTime/60), \

# 	            myTime%60, \

#              npNewMatrix.shape \
# #             len(ruleIndxs) \

# 	           ) \

# 	    )

# npNewMatrix *= 255


#saveimgDir = r"/storage/emulated/0/qpython/projects/numpy/convolve/test/"
# saveimgDir = r"C:/_WORK/PYTHON/projects/numpy/convolve/test/"
# myTime = time.localtime()
# dateDir = "{0}_{1:02}_{2:02}-{3:02}_{4:02}_{5:02}/".format(*myTime)

#print("dateDir {}".format(dateDir))
# alphaNumRule = "KU13I07ELF1K1HKG6MMOI9JTSWT7538SKFJ9UXD9P8QXTNRQ1QYJT9FN7L71YPLHPGIRN3RJKWRH6ZXPY3HPD2EP3CQG50R80LC"
# print ("alphaNumRule >>> {}".format(alphaNumRule))
# intRule = int(alphaNumRule,36)
# print ("intRule >>> {}".format(intRule))
# binRule = "{:0512b}".format(intRule)
# print ("binRule >>> {:b}".format(intRule))
# binRuleArray = [int(x,10) for x in binRule]
# print ("binRuleArray >>> {0} \n length {1} \n type {2} \n".format(binRuleArray, len(binRuleArray), type(binRuleArray[0])))
# myNpRule = np.asarray(binRuleArray, dtype=np.int8)
# print ("myNpRule >>> {0} \n shape {1} \n dtype {2} \n".format(myNpRule, myNpRule.shape, myNpRule.dtype))

#myOptionalZeroRules = getOptionalZeroRule(512, saveimgDir+dateDir, count=500, part="Q")
#myRndRules = generateRndRule(512, count=20)

#myNpRule.resize((1,myNpRule.shape[0]))

#run(myNpRule, 101, 101, 1000, saveimgDir, dateDir, saveOnlyLast=False)
#run(myOptionalZeroRules, 51, 51, 50, saveimgDir, dateDir, saveOnlyLast=True)


# myCA = getLayers(201, 201, rndNpRule, 50)

# directory = myAnum +"/"
# #saveimgDir = r"/storage/emulated/0/qpython/projects/numpy/convolve/test/" +directory
#  +directory
# ensure_dir(saveimgDir)
# for i, v in enumerate(myCA):
#    v *= 255
    
#    fileName = "{:03d}.png".format(i)
#    saveimgPath = saveimgDir + fileName
#    saveimg = Image.fromarray(v, mode = 'L')
#    saveimg.save(saveimgPath)




