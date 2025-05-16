# -*- coding: utf-8 -*-
# Copyright(c) 2019, Daniel Gercak
#Script for selecting and grouping elements by levels and other parameters for dynamo 
#resource_path: H:\_WORK\PYTHON\REVIT_API\getElementById.py

import clr
import sys
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
lib_path = r'H:\_WORK\PYTHON\REVIT_API\LIB'
sys.path.append(pyt_path)
sys.path.append(lib_path)

import ListUtils as ListUtils

clr.AddReference("RevitNodes")
import Revit
clr.ImportExtensions(Revit.Elements)

clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
doc = DocumentManager.Instance.CurrentDBDocument

clr.AddReference("RevitAPI")
import Autodesk
from Autodesk.Revit.DB import *
import System

clr.AddReference("System")
from System.Collections.Generic import List as Clist

intId = IN[0]
elementId = ElementId(intId)



try:
    errorReport = None
    returnElement = doc.GetElement(elementId)
    #TransactionManager.Instance.EnsureInTransaction(doc)
    #paramValues = ListUtils.processList(getParameter, elements, builtInParamName, lookUpParameterName)

    #TransactionManager.Instance.TransactionTaskDone()
except:
    import traceback
    errorReport = traceback.format_exc()

if errorReport == None:
    #OUT = getBuiltInCategoryInstance(builtInCategoryName)
    OUT = returnElement
    #OUT = getBuiltinParam(builtInParamName, familyInstance, lookUpParameterName)
else:
    OUT = errorReport