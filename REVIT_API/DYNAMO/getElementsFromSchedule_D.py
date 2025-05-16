# -*- coding: utf-8 -*-
# Copyright(c) 2022, Daniel Gercak
#Script for extracting elements from ScheduleView for dynamo Renumber_By_Schedule.dyn
#resource_path: H:\_WORK\PYTHON\REVIT_API\DYNAMO\getElementsFromSchedule_D.py

import sys
import re
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
lib_path = r'H:\_WORK\PYTHON\REVIT_API\LIB'
sys.path.append(pyt_path)
sys.path.append(lib_path)


# from itertools import chain, groupby
# from RevitSelection import *
# import RevitSelection as RevitSelection
# from ListUtils import *
# import ListUtils as ListUtils

import clr
clr.AddReference("RevitAPI")
#import Autodesk
import Autodesk.Revit.DB as DB

clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
doc = DocumentManager.Instance.CurrentDBDocument

clr.AddReference('ProtoGeometry')
import Autodesk.DesignScript.Geometry as DSGeometry

# Import Element wrapper extension methods
clr.AddReference("RevitNodes")
import Revit
clr.ImportExtensions(Revit.Elements)
clr.ImportExtensions(Revit.GeometryConversion)
clr.AddReference('RevitAPIUI')
from Autodesk.Revit.UI.Selection import *


clr.AddReference("System")

from System.Collections.Generic import List as Clist
from System import Enum 

doc = DocumentManager.Instance.CurrentDBDocument

""" clr.AddReference("System.Windows.Forms")
clr.AddReference("System.Drawing")

import System.Drawing
import System.Windows.Forms
from System.Drawing import *
from System.Windows.Forms import Application, Button, Form, ComboBox, Label, TextBox, DockStyle, AnchorStyles, FormBorderStyle """

class Errors(object):
	report = []
	variables = []
	varNames = []
	def __init__(self):
		pass

	@classmethod
	def hasError(cls):
		if len(cls.report) > 0:
			return True
		else:
			return False
	
	@classmethod
	def hasContent(cls):
		if len(cls.variables) > 0:
			return True
		else:
			return False
			
	@classmethod
	def catch(cls, inEx, *args):
		"""
		catches the error in Exception block as a class parameter report 

		arg: inEx: an Exception catched in Exception block
		*args[0]: inText: short description of the error. Where it ocured (function or block of commands) type: string

		Returns: None
		"""
		if len(args) > 0:
			inText = args[0]
		else:
			inText = ""
		error_type, error_instance, traceback = sys.exc_info()
		cls.report.append("{0} \
							Exception: {1} error_type: {2}, error_instance {3}, traceback -{4}" \
							.format(inText \
									,inEx \
									,error_type \
									,error_instance \
									,traceback))
	
	@classmethod
	def catchVar(cls, inVar, inName, *args, **kwargs):
		"""
		catches the variable and stores it in variables for direct acces during tuning of code 

		input:
		inVar: content of variable to store
		inName: name of variable type: string 

		Returns: None
		"""
		front = kwargs['front'] if 'front' in kwargs else False
		if front:
			cls.variables.insert(0, inVar)
			cls.varNames.insert(0, inName)
		else:
			cls.variables.append(inVar)
			cls.varNames.append(inName)

	@classmethod
	def getConntainerContent(cls, *args, **kwargs):
		withName = kwargs["withName"] if "withName" in kwargs else True
		if withName == True:			
			return zip(cls.varNames, cls.variables)
		else:
			return cls.variables

def processList(_func, _list, *args, **kwargs):
	"""Iterates trough input list and aplies a function to each item of the list

		args:
			_func: name of the func type: callable
			_list: input list - type: list 
			*args: arguments for input function

		return: list of the same structure as input list - type: list
	"""
	return map( lambda x: processList(_func, x, *args, **kwargs) if type(x)==list else _func(x, *args, **kwargs), _list )


''' TransactionManager.Instance.EnsureInTransaction(doc)
trans = DB.SubTransaction(doc)
trans.Start()

#setParams = processList(setValueByParameterName, unWrapped, "EEEEE", copyToBipName, doc, bip = copyToBip)
copyResult = copyParameterValues(unWrapped, copyFromBipName, copyToBipName, doc)

trans.Commit()
TransactionManager.Instance.TransactionTaskDone() '''

viewSchedule = IN[0]
unwraped = UnwrapElement(viewSchedule)
viewScheduleData = unwraped.GetTableData()
viewSheduleElement = doc.GetElement(unwraped.Id)
elements = DB.FilteredElementCollector(doc,unwraped.Id).WhereElementIsNotElementType().WherePasses(DB.VisibleInViewFilter(doc, viewSheduleElement.Id)).ToElements()


#.WherePasses(DB.VisibleInViewFilter(doc, viewSheduleElement.Id))

tsData = viewScheduleData.GetSectionData(DB.SectionType.Body)
rowsCount = tsData.NumberOfRows;
colsCount = tsData.NumberOfColumns;
tableText = [[None]*colsCount]*rowsCount
for r in range(rowsCount):
    for c in range(colsCount):
        tableText[r][c] = (unwraped.GetCellText(DB.SectionType.Body, r, c), unwraped.GetCellCategoryId(c))
        

myOutput = (tsData.NumberOfRows, elements)
#myOutput = (tsData.NumberOfRows, tableText, unwraped.KeyScheduleParameterName)


if Errors.hasError():
 	OUT = Errors.report
elif Errors.hasContent():
	OUT = Errors.getConntainerContent()
else:
	OUT = myOutput