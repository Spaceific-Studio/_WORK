# -*- coding: utf-8 -*-
# Copyright(c) 2020, Daniel Gercak
#Classes to cath errors and exceptions in order to use them in Dynamo pythonScript
#There are also functions for geometry transform to Dynamo
#resource_path: H:\_WORK\PYTHON\REVIT_API\LIB\Errors.py

import sys
#Class for errors reporting
if "pydroid" in sys.prefix:
	    pass
else:
    import clr
    clr.AddReference("System.Drawing")
    #import System.Drawing
    from System.Drawing import Color

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


class ModelConsistency(object):
	report = []
	errTypes = { \
					"Err_01" : "Unable to extract outer and inner shells, at least one object in your model is not enclosed or is without inner spaces", \
					"Err_02" : "Unassigned materials to faces", \
					"Err_03" : "Lambda parameter in material not assigned", \
					"Err_04" : "Unable to acquire assigned room to inner shell", \
					"Err_05" : "Opening fills count does not equal to subtracted openings count"
				}
	errColors = { \
					"Err_01" : [Color.Blue], \
					"Err_02" : [Color.MistyRose, Color.Salmon, Color.Red], \
					"Err_03" : [Color.Honeydew, Color.LightGreen, Color.Green],\
					"Err_04" : [Color.Violet],\
					"Err_05" : [Color.Gold]
				}
	ID_stack = { \
					"Err_01" : [], \
					"Err_02" : [], \
					"Err_03" : [], \
					"Err_04" : [], \
					"Err_05" : [], \
				}

	def __init__(self):
		pass

	@classmethod
	def hasError(cls):
		if len(cls.report) > 0:
			return True
		else:
			return False
			
	@classmethod
	def catch(cls, inEr, *args):
		"""
		catches the error with error type and optional ID of element

		arg: inEr: type: str,  an error type listed in errTypes of format "Err_01", ..
		*args[0]: inId: type int, optional parameter carries Autodesk.Revit.DB.ElementId.IntegerValue

		Returns: None
		"""
		inId = args[0] if len(args) > 0 else None

		if inEr not in cls.report:
			cls.report.append(inEr)
		if inId:
			cls.ID_stack[inEr].append(inId)