import sys
#import traceback
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
lib_path = r'H:\_WORK\PYTHON\REVIT_API\LIB'
sys.path.append(pyt_path)
sys.path.append(lib_path)

from itertools import chain, groupby
from RevitSelection import *
import RevitSelection as RevitSelection
from ListUtils import *
import ListUtils as ListUtils
from Errors import *

import clr
# Import Element wrapper extension methods
clr.AddReference("RevitNodes")
import Revit
#clr.ImportExtensions(Revit.Elements)
# Import geometry conversion extension methods
#clr.ImportExtensions(Revit.GeometryConversion)
clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *

clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *

inElements = IN[0] if isinstance(IN[0], list) else [IN[0]]
windowsCgs = [Autodesk.Revit.DB.BuiltInCategory.OST_Windows]
doorsCgs = [Autodesk.Revit.DB.BuiltInCategory.OST_Doors]
windows = list(RevitSelection.getElementByCategory(windowsCgs))
doors = list(RevitSelection.getElementByCategory(doorsCgs))

def getDynamoGeometry(inElements, *args, **kwargs):
	gOptions = kwargs['options'] if 'options' in kwargs else Options()
	byElements = kwargs['byElements'] if 'byElements' in kwargs else True
	onlySolids = kwargs['onlySolids'] if 'onlySolids' in kwargs else True
	output = []
	if byElements:		
		for el in inElements:
			geo = None
			try:
				geo = el.Geometry()
			except Exception as ex:
				Errors.catch(ex, "error in RevitSelection.getDynamoGeometry byElements")
			if geo:
				enum1 = geo.GetEnumerator()
				myGeometry = []
				while enum1.MoveNext():
					geometry = enum1.Current.GetInstanceGeometry()
					if onlySolids:
						if hasattr(geometry, "Volume") and g.Volume != 0:
							myGeometry.append(geometry)
					else:
						myGeometry.append(geometry)
				if len(myGeometry) > 0:
					output.append(myGeometry)

		
	else:
		try:
			for el in inElements:
				el = UnwrapElement(el)
				geo1 = el.get_GeometrygOptions()
				enum1 = geo1.GetEnumerator()
				enum1.MoveNext()
				geo2 = enum1.Current.GetInstanceGeometry()
				for g in geo2:
					s1 = g.Convert()
					if s1 != None:
						if onlySolids:
							if hasattr(s1, "Volume") and s1.Volume != 0:
								output.append(s1)
						else:
							output.append(s1)
		except Exception as ex:
			Errors.catch(ex, "error in RevitSelection.getDynamoGeometry byElements else")
	return output

#myOutput = getDynamoGeometry(windows, onlySolids = False)
# output1 = []
# for el in inElements:
# 	unwrapped = UnwrapElement(el)
# 	output1 = unwrapped.Geometry()
myOutput = windows

if Errors.hasError():
     	OUT = Errors.report
elif Errors.hasContent():
	OUT = Errors.getConntainerContent()
else:
	OUT = myOutput