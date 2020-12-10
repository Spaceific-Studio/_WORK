# -*- coding: utf-8 -*-
# Copyright(c) 2020, Daniel Gercak
#Script for selecting and grouping elements by levels and other parameters for dynamo 
#resource_path: H:\_WORK\PYTHON\REVIT_API\getRTD_model.py

import sys
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
lib_path = r'H:\_WORK\PYTHON\REVIT_API\LIB'
sys.path.append(pyt_path)
sys.path.append(lib_path)

# from itertools import chain, groupby
# from RevitSelection import *
# import RevitSelection as RevitSelection
# from ListUtils import *
# import ListUtils as ListUtils

from Analyse import *
from AnalyseForm import *
from Errors import *

rtdObject = RTD_model(doc, IN[0])

if Errors.hasError():
 	OUT = Errors.report
# elif Errors.hasContent():
# 	OUT = Errors.getConntainerContent()
else:
	OUT = rtdObject