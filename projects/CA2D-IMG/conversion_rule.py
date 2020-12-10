# -*- coding: utf-8 -*-
import numpy as np
np.set_printoptions(threshold='nan')
import os
import math
import csv
import random
random.seed()
from PIL import Image, ImageDraw

def getNewVersionRule(inOldRule): 	
    oldRule = inOldRule 	
    newRule = [] 	
    conversionTable = [16, 20, 24, 29, 17, 22, 26, 0, 25, 30, 19, 8, 27, 3, 13, 10, 21, 18, 28, 4, 23, 12, 1, 6, 31, 5, 9, 14, 2, 7, 11, 15] 	
    for i in conversionTable: 		
        newRule.append(oldRule[i]) 	
    returnString = "".join(newRule)
    print new version rule :
    print 	returnString
    return returnString

#print getNewVersionRule("11110000000000110100110011001111"):