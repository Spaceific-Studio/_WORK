"""Calculates total volume of all selected elements."""

__title__ = 'Total\nVolume'

import clr
from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, BuiltInParameter, UnitType, UnitUtils, DisplayUnitType

clr.AddReference('RevitAPIUI')
from Autodesk.Revit.UI.Selection import *

class CalculateVolume():
	def __init__(self):
		self.doc = __revit__.ActiveUIDocument.Document
		self.uidoc = __revit__.ActiveUIDocument
		self.selection = [self.doc.GetElement(elId) for elId in __revit__.ActiveUIDocument.Selection.GetElementIds()]
		if len(self.selection) == 0 or self.selection == None:
		#	__window__.Hide()
			self.selection = self.uidoc.Selection.PickElementsByRectangle()
		#	__window__.Show()
    	#	__window__.Topmost = True
	def run(self):
		# Iterate over wall and collect Volume data
		total_volume = 0.0
		values = []
		unitTypes = []
		for el in self.selection:
			vol_param = el.Parameter[BuiltInParameter.HOST_VOLUME_COMPUTED]
			if vol_param:
				unitTypes.append(vol_param.DisplayUnitType)
				values.append((UnitUtils.ConvertFromInternalUnits(vol_param.AsDouble(), DisplayUnitType.DUT_CUBIC_METERS), el.Id))
				total_volume = total_volume + vol_param.AsDouble()
		# now that results are collected, print the total
		unitConversion = UnitUtils.ConvertFromInternalUnits(total_volume, DisplayUnitType.DUT_CUBIC_METERS)
		self.volume = unitConversion
		#print("docUnits {0}".format(docUnits))
		#print("unitConversion {0}".format(unitConversion))
		for i, v in enumerate(values):
			print("{pos} - {volume} - {id}".format(pos = i, volume = v[0], id = v[1]))
		print("Number of all selected elements: {}".format(len(self.selection)))
		print("Number of elements with volume parameter: {}".format(len(values)))
		print("Total Volume is: {}".format(unitConversion))
		#print(unitTypes)
	
	def getVolume(self):
		return "Volume of selected elements is: {}".format(self.volume)

