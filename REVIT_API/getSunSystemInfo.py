# -*- coding: utf-8 -*-
# Copyright(c) 2021, Daniel Gercak
#Script for reading information from sun path element
#Uses detail component sun_altitude_helper.rvt as a helper to define sun altitude
#according to active view SunPathSettings
#https://github.com/Spaceific-Studio/_WORK/REVIT_API/getSunSystemInfo.py

import sys
if "IronPython" in sys.prefix:
	pytPath = r'C:\Program Files (x86)\IronPython 2.7\Lib'
	sys.path.append(pytPath)
import os
import platform
import time

try:
	sys.modules['__main__']
	hasMainAttr = True	
except:
	hasMainAttr = False

if hasMainAttr:
	#import clr
	if "pydroid" in sys.prefix:
		pass
	elif "Python38" in sys.prefix:
		pass
	else:
		from Autodesk.Revit.UI.Selection import *
		import Autodesk.Revit.DB as DB
		import Autodesk.Revit.UI as UI
		import Autodesk
		from Autodesk.Revit.DB import IFailuresPreprocessor, BuiltInFailures
		import System
		import threading
		from System.Collections.Generic import List as Clist
		from System import Type
		from System import DateTime, DateTimeKind
		#from System.Collections.Generic import Ilist
		#import System.Drawing
		import clr
		clr.AddReferenceByPartialName('System.Windows.Forms')
		clr.AddReference("System.Drawing")
		clr.AddReference('System')
		#import System.Windows.Forms
		from System.Threading import ThreadStart, Thread
		from System.Windows.Forms import *
		from System.Drawing import *
		doc = __revit__.ActiveUIDocument.Document
		uidoc = __revit__.ActiveUIDocument
		#clr.AddReference("RevitServices")
		#import RevitServices
		#from RevitServices.Transactions import TransactionManager
		pass

else:
	if "pydroid" in sys.prefix:
		pass
	elif "Python38" in sys.prefix:
		pass
	else:
		import clr
		clr.AddReference('ProtoGeometry')
		from Autodesk.DesignScript.Geometry import *
		clr.AddReference("RevitAPI")
		import Autodesk
		import Autodesk.Revit.DB as DB
		clr.AddReference("RevitServices")
		import RevitServices
		from RevitServices.Persistence import DocumentManager
		from RevitServices.Transactions import TransactionManager
		doc = DocumentManager.Instance.CurrentDBDocument

# clr.AddReference("RevitAPI")
# import Autodesk
# import Autodesk.Revit.DB as DB

try:
	import Autodesk
	sys.modules['Autodesk']
	hasAutodesk = True	
except:
	hasAutodesk = False

print("module : {0} ; hasMainAttr = {1}".format(__file__, hasMainAttr))
print("module : {0} ; hasAutodesk = {1}".format(__file__, hasAutodesk))

if sys.platform.startswith('linux'):
	libPath = r"/storage/emulated/0/_WORK/REVIT_API/LIB"
elif sys.platform.startswith('win') or sys.platform.startswith('cli'):
	scriptDir = "\\".join(__file__.split("\\")[:-1])
	scriptDisk = __file__.split(":")[0]
	if scriptDisk == "B" or scriptDisk == "b":
		libPath = r"B:/Podpora Revit/Rodiny/141/_STAVEBNI/_REVITPYTHONSHELL/LIB"
	elif scriptDisk == "C" or scriptDisk == "c":
		libPath = r"C:/_WORK/PYTHON/REVIT_API/LIB"
	elif scriptDisk == "H" or scriptDisk == "h":
		libPath = r"H:/_WORK/PYTHON/REVIT_API/LIB"

if sys.platform.startswith('linux'):
	pythLibPath = r"/storage/emulated/0/_WORK/LIB"
#elif sys.platform.startswith('win') or sys.platform.startswith('cli'):
#	pythLibPath = r"C:/_WORK/PYTHON/LIB"

sys.path.append(libPath)
#sys.path.append(pythLibPath)


mySelection = uidoc.Selection.GetElementIds()
sunSystemSettings = doc.GetElement(mySelection[0]) if len(mySelection) > 0 else []
#print(sunSystemSettings)
#print("Altitude angle {}".format(sunSystemSettings.GetFrameAltitude()))
selectedElId = mySelection[0] if len(mySelection) > 0 else None
mySelectedElement = doc.GetElement(selectedElId)  if selectedElId else None
myHelperInstance = mySelectedElement if (mySelectedElement and mySelectedElement.Name == "sun_altitude_helper") else None
altParamName = "Altitude angle"
altParameter = myHelperInstance.LookupParameter(altParamName) if myHelperInstance else None
altTextParamName = "Altitude_text"
altTextParam = myHelperInstance.LookupParameter(altTextParamName) if myHelperInstance else None
summerSolsticeAltitudeParameterName = "summer_solstice_angle-12AM"
summerSolsticeAltitudeParameter = myHelperInstance.LookupParameter(summerSolsticeAltitudeParameterName) if myHelperInstance else None
winterSolsticeAltitudeParameterName = "winter_solstice_angle-12AM"
winterSolsticeAltitudeParameter = myHelperInstance.LookupParameter(winterSolsticeAltitudeParameterName) if myHelperInstance else None
dateTimeParameterName = "dateTime"
dateTimeParameter = myHelperInstance.LookupParameter(dateTimeParameterName) if myHelperInstance else None
longitudeParameterName = "Longitude"
longitudeParameter = myHelperInstance.LookupParameter(longitudeParameterName) if myHelperInstance else None
latitudeParameterName = "Latitude"
latitudeParameter = myHelperInstance.LookupParameter(latitudeParameterName) if myHelperInstance else None
WSA12AM_textParamName = "WSA12AM_text"
WSA12AM_textParam = myHelperInstance.LookupParameter(WSA12AM_textParamName) if myHelperInstance else None
WSA12AM_dateParamName = "WSA12AM_date"
WSA12AM_dateParam = myHelperInstance.LookupParameter(WSA12AM_dateParamName) if myHelperInstance else None
SSA12AM_textParamName = "SSA12AM_text"
SSA12AM_textParam = myHelperInstance.LookupParameter(SSA12AM_textParamName) if myHelperInstance else None
SSA12AM_dateParamName = "SSA12AM_date"
SSA12AM_dateParam = myHelperInstance.LookupParameter(SSA12AM_dateParamName) if myHelperInstance else None





print("altParameter {}".format(altParameter.Definition.Name if altParameter else None))
print("summerSolsticeAltitudeParameter {}".format(summerSolsticeAltitudeParameter.Definition.Name if altParameter else None))
print("winterSolsticeAltitudeParameter {}".format(winterSolsticeAltitudeParameter.Definition.Name if altParameter else None))

print("myHelper {}".format(myHelperInstance.Name if myHelperInstance else None))
activeSSsettings = uidoc.ActiveView.SunAndShadowSettings
activeSSsettings = sunSystemSettings if (len(mySelection) > 0 and isinstance(sunSystemSettings, DB.SunAndShadowSettings)) else activeSSsettings
frameAltitude = activeSSsettings.GetFrameAltitude(activeSSsettings.ActiveFrame)
frameAzimuth = activeSSsettings.GetFrameAzimuth(activeSSsettings.ActiveFrame)

summerSolsticeDateTime = DateTime.SpecifyKind(DateTime(2021,06,21,12,0,0), DateTimeKind.Local)
winterSolsticeDateTime = DateTime.SpecifyKind(DateTime(2021,12,21,12,0,0), DateTimeKind.Local)
#summerSolsticeDateTime = DateTime.Parse("21.06.2021 12:00:00")

activeDateTimeHolder = activeSSsettings.StartDateAndTime
t = DB.Transaction(doc, "StartDateAndTime temporary set")
t.Start()
activeSSsettings.StartDateAndTime = summerSolsticeDateTime.ToLocalTime()

summerSolsticeAltitude = activeSSsettings.GetFrameAltitude(activeSSsettings.ActiveFrame)
activeSSsettings.StartDateAndTime = winterSolsticeDateTime.ToLocalTime()
winterSolsticeAltitude = activeSSsettings.GetFrameAltitude(activeSSsettings.ActiveFrame)
t.RollBack()


print("summerSolsticeDateTime {0}".format(summerSolsticeDateTime.ToLocalTime()))
print("winterSolsticeDateTime {0}".format(winterSolsticeDateTime.ToLocalTime()))
summerSolsticeAltitudeDegrees = DB.UnitUtils.Convert(summerSolsticeAltitude, DB.DisplayUnitType.DUT_RADIANS, DB.DisplayUnitType.DUT_DECIMAL_DEGREES)
print("summerSolsticeAltitude {0} summerSolsticeAltitudeDegrees {1}".format(summerSolsticeAltitude, summerSolsticeAltitudeDegrees))
winterSolsticeAltitudeDegrees = DB.UnitUtils.Convert(winterSolsticeAltitude, DB.DisplayUnitType.DUT_RADIANS, DB.DisplayUnitType.DUT_DECIMAL_DEGREES)
print("winterSolsticeAltitude {0} winterSolsticeAltitudeDegrees {1}".format(winterSolsticeAltitude, winterSolsticeAltitudeDegrees))

latitude = DB.UnitUtils.Convert(activeSSsettings.Latitude, DB.DisplayUnitType.DUT_RADIANS, DB.DisplayUnitType.DUT_DEGREES_AND_MINUTES)
longitude = DB.UnitUtils.Convert(activeSSsettings.Longitude, DB.DisplayUnitType.DUT_RADIANS, DB.DisplayUnitType.DUT_DEGREES_AND_MINUTES)

#print("activeSSsettings {}".format(activeSSsettings))
#print("activeSSsettings.GetFrameAltitude() {0}".format(activeSSsettings.GetFrameAltitude(activeSSsettings.ActiveFrame)))
print("Location - Latitude {0} Longitude {1}".format(latitude, longitude))
print("activeSSsettings.StartDateAndTime {}".format(activeSSsettings.StartDateAndTime))
print("DateTime.ToLocalTime() {}".format(activeSSsettings.StartDateAndTime.ToLocalTime()))
print("DateTime.ToUniversalTime() {}".format(activeSSsettings.StartDateAndTime.ToUniversalTime()))
print("activeSSsettings.GetFrameTime() {0}".format(activeSSsettings.GetFrameTime(activeSSsettings.ActiveFrame)))
print("")
print("frameAltitude in degrees {0}".format(DB.UnitUtils.Convert(frameAltitude, DB.DisplayUnitType.DUT_RADIANS, DB.DisplayUnitType.DUT_DECIMAL_DEGREES)))
print("frameAzimuth in degrees {0}".format(DB.UnitUtils.Convert(frameAzimuth, DB.DisplayUnitType.DUT_RADIANS, DB.DisplayUnitType.DUT_DECIMAL_DEGREES)))


if altParameter:
	t = DB.Transaction(doc, "Altitude angle set")
	t.Start()
	altParameter.Set(frameAltitude)
	altTextParam.Set("{}°".format(DB.UnitUtils.Convert(frameAltitude, DB.DisplayUnitType.DUT_RADIANS, DB.DisplayUnitType.DUT_DECIMAL_DEGREES)))
	summerSolsticeAltitudeParameter.Set(summerSolsticeAltitude)
	SSA12AM_textParam.Set("{}°".format(DB.UnitUtils.Convert(summerSolsticeAltitude, DB.DisplayUnitType.DUT_RADIANS, DB.DisplayUnitType.DUT_DECIMAL_DEGREES)))
	SSA12AM_dateParam.Set("{}".format(summerSolsticeDateTime))
	print("summerSolsticeAltitude {0} summerSolsticeAltitudeDegrees {1} WAS SET".format(summerSolsticeAltitude, summerSolsticeAltitudeDegrees))

	winterSolsticeAltitudeParameter.Set(winterSolsticeAltitude)
	WSA12AM_textParam.Set("{}°".format(DB.UnitUtils.Convert(winterSolsticeAltitude, DB.DisplayUnitType.DUT_RADIANS, DB.DisplayUnitType.DUT_DECIMAL_DEGREES)))
	WSA12AM_dateParam.Set("{}".format(winterSolsticeDateTime))
	print("winterSolsticeAltitude {0} winterSolsticeAltitudeDegrees {1} WAS SET".format(winterSolsticeAltitude, winterSolsticeAltitudeDegrees))
	dateTimeParameter.Set("{}".format(activeSSsettings.StartDateAndTime.ToLocalTime()))
	latitudeParameter.Set("{}".format(latitude))
	longitudeParameter.Set("{}".format(longitude))
	t.Commit()