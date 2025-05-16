# -*- coding: utf-8 -*-
# Copyright(c) 2021, Daniel Gercak
#Revit Python Shell script to transform pointCloud element to specified position
#Moves point cloud to point defined by XYZ() object and aplying rotation around Z axis 
#resource_path: https://github.com/Spaceific-Studio/_WORK/REVIT_API/getTransformCoordinates_forPointCloud.py

#!!! Leave moveElement False If you don't want to move selected element only find out coordinates
moveElement = False
rotateElement = False

import Autodesk
import Autodesk.Revit.DB as DB
import Autodesk.Revit.UI as UI
import math

selIds = list(__revit__.ActiveUIDocument.Selection.GetElementIds())
doc = __revit__.ActiveUIDocument.Document
element = doc.GetElement(selIds[0])
print(dir(element))
print(element)

test_E1_BasisX = DB.XYZ(-3.28083989501312, 4.01787007594276E-16, 0)
test_E2_BasisX = DB.XYZ(6.192188785639E-15, -3.28083989501312, 0)
testAngleDifRad = test_E1_BasisX.AngleTo(test_E2_BasisX)
testAngleDifDegrees = DB.UnitUtils.Convert(testAngleDifRad, DB.DisplayUnitType.DUT_RADIANS, DB.DisplayUnitType.DUT_DECIMAL_DEGREES)
print("testAngleDifDegrees {0}".format(testAngleDifDegrees))

#inserted target revit model
tm_BasisX = DB.XYZ(-3.28083558509697, -0.00531791981143481, 0)
tm_BasisY = DB.XYZ(0.00531791981143481, -3.28083558509697, 0)
tm_Origin = DB.XYZ(197.46210274951, -57.2230255966043, -0.150851077)

#current inserted revit model
cm_BasisX = DB.XYZ(-3.28083989501312, 4.01787007594276E-16, 0)
cm_BasisY = DB.XYZ(-4.01787007594276E-16, -3.28083989501312, 0)
cm_Origin = DB.XYZ(197.600419011, -57.284730545, -0.150851077)


#new inserted pointCloud
ip_BasisX = DB.XYZ(1.0, 0.0, 0.0)
ip_BasisY = DB.XYZ(0.0, 1.0, 0.0)
ip_Origin = DB.XYZ(0.0, 0.0, 0.0)

#already placed pointCloud
pp_BasisX = DB.XYZ(-3.28083989501312, -3.64246399155234E-16, 0)
pp_BasisY = DB.XYZ(3.64246399155234E-16, -3.28083989501312, 0)
pp_Origin = DB.XYZ(197.600419011327, -57.2847305451009, -0.150851076982152)

print("tm_BasisX.AngleTo(cm_BasisX) - {0} v stupnich {1}".format(tm_BasisX.AngleTo(cm_BasisX), tm_BasisX.AngleTo(cm_BasisX) * 180 / math.pi))


if isinstance(element, Autodesk.Revit.DB.PointCloudInstance):

	origin = element.GetTransform().Origin
	originX = UnitUtils.ConvertFromInternalUnits(origin.X, DisplayUnitType.DUT_MILLIMETERS)
	originY = UnitUtils.ConvertFromInternalUnits(origin.Y, DisplayUnitType.DUT_MILLIMETERS)
	originZ = UnitUtils.ConvertFromInternalUnits(origin.Z, DisplayUnitType.DUT_MILLIMETERS)
	basisX =  (UnitUtils.ConvertFromInternalUnits(origin.BasisX.X, DisplayUnitType.DUT_MILLIMETERS), \
				UnitUtils.ConvertFromInternalUnits(origin.BasisX.Y, DisplayUnitType.DUT_MILLIMETERS), \
				UnitUtils.ConvertFromInternalUnits(origin.BasisX.Z, DisplayUnitType.DUT_MILLIMETERS))
	basisY = (UnitUtils.ConvertFromInternalUnits(origin.BasisY.X, DisplayUnitType.DUT_MILLIMETERS), \
				UnitUtils.ConvertFromInternalUnits(origin.BasisY.Y, DisplayUnitType.DUT_MILLIMETERS), \
				UnitUtils.ConvertFromInternalUnits(origin.BasisY.Z, DisplayUnitType.DUT_MILLIMETERS))
	basisZ = (UnitUtils.ConvertFromInternalUnits(origin.BasisZ.X, DisplayUnitType.DUT_MILLIMETERS), \
				UnitUtils.ConvertFromInternalUnits(origin.BasisZ.Y, DisplayUnitType.DUT_MILLIMETERS), \
				UnitUtils.ConvertFromInternalUnits(origin.BasisZ.Z, DisplayUnitType.DUT_MILLIMETERS))
	
	print("element.GetTransform().Origin.BasisX {}".format(element.GetTransform().Origin.BasisX))
	print("element.GetTransform.Origin X {0}, Y {1}, Z {2}".format(originX, originY, originZ))
	print("element.GetTransform.Origin.Basis X {0}, Y {1}, Z {2}".format(basisX, basisY, basisZ))	
	if rotateElement:
	
		p1 = origin
		p2 = p1.Add(DB.XYZ(0, 0, 100))
		print("p1 {0} and p2 {1}".format(p1, p2))
		myLine = Line.CreateBound(p1, p2)
		degrees_to_rotate = 180
		#converted_value = float(degrees_to_rotate) * (math.pi / 180.0)
		angleDifRad = ip_BasisX.AngleTo(pp_BasisX)
		t = DB.Transaction(doc, 'Rotating Element')
		t.Start()
		DB.ElementTransformUtils.RotateElement(doc, selIds[0], myLine, angleDifRad)
		t.Commit()

	if moveElement:
		#original position of PCL
		fromPoint = origin
		difVec = DB.XYZ(0.275887, 0.515614, 0.063912)
		toPoint = fromPoint.Subtract(difVec)
		#toPoint = DB.XYZ(197.600419011, -57.284730545, -0.1508510770)
		#toPoint = pp_Origin
		#toPoint = DB.XYZ(0, 0, 0)
		#moveVec = toPoint.Subtract(origin)
		#moveVec = toPoint.Subtract(ip_Origin)
		moveVec = toPoint.Subtract(fromPoint)
		print("moveVec {0}".format(moveVec))
		t = DB.Transaction(doc, 'Moving Element')
		# Begin new transaction
		t.Start()
		DB.ElementTransformUtils.MoveElement(doc, selIds[0], moveVec)
		t.Commit()
		# Close the transaction

elif isinstance(element, Autodesk.Revit.DB.RevitLinkInstance):

	origin = element.GetTransform().Origin
	originX = UnitUtils.ConvertFromInternalUnits(origin.X, DisplayUnitType.DUT_MILLIMETERS)
	originY = UnitUtils.ConvertFromInternalUnits(origin.Y, DisplayUnitType.DUT_MILLIMETERS)
	originZ = UnitUtils.ConvertFromInternalUnits(origin.Z, DisplayUnitType.DUT_MILLIMETERS)
	basisX =  (UnitUtils.ConvertFromInternalUnits(origin.BasisX.X, DisplayUnitType.DUT_MILLIMETERS), \
				UnitUtils.ConvertFromInternalUnits(origin.BasisX.Y, DisplayUnitType.DUT_MILLIMETERS), \
				UnitUtils.ConvertFromInternalUnits(origin.BasisX.Z, DisplayUnitType.DUT_MILLIMETERS))
	basisY = (UnitUtils.ConvertFromInternalUnits(origin.BasisY.X, DisplayUnitType.DUT_MILLIMETERS), \
				UnitUtils.ConvertFromInternalUnits(origin.BasisY.Y, DisplayUnitType.DUT_MILLIMETERS), \
				UnitUtils.ConvertFromInternalUnits(origin.BasisY.Z, DisplayUnitType.DUT_MILLIMETERS))
	basisZ = (UnitUtils.ConvertFromInternalUnits(origin.BasisZ.X, DisplayUnitType.DUT_MILLIMETERS), \
				UnitUtils.ConvertFromInternalUnits(origin.BasisZ.Y, DisplayUnitType.DUT_MILLIMETERS), \
				UnitUtils.ConvertFromInternalUnits(origin.BasisZ.Z, DisplayUnitType.DUT_MILLIMETERS))
	
	print("element.GetTransform().Origin.BasisX {}".format(element.GetTransform().Origin.BasisX))
	print("element.GetTransform.Origin X {0}, Y {1}, Z {2}".format(originX, originY, originZ))
	print("element.GetTransform.Origin.Basis X {0}, Y {1}, Z {2}".format(basisX, basisY, basisZ))	
	if rotateElement:
	
		p1 = origin
		p2 = p1.Add(DB.XYZ(0, 0, 100))
		print("p1 {0} and p2 {1}".format(p1, p2))
		myLine = Line.CreateBound(p1, p2)
		degrees_to_rotate = 180
		#converted_value = float(degrees_to_rotate) * (math.pi / 180.0)
		angleDifRad = tm_BasisX.AngleTo(cm_BasisX)
		t = DB.Transaction(doc, 'Rotating Element')
		t.Start()
		DB.ElementTransformUtils.RotateElement(doc, selIds[0], myLine, angleDifRad)
		t.Commit()

	if moveElement:
		#original position of PCL
		#toPoint = DB.XYZ(197.600419011, -57.284730545, -0.1508510770)
		toPoint = tm_Origin
		#toPoint = DB.XYZ(0, 0, 0)
		#moveVec = toPoint.Subtract(origin)
		moveVec = toPoint.Subtract(cm_Origin)
		print("moveVec {0}".format(moveVec))
		t = DB.Transaction(doc, 'Moving Element')
		# Begin new transaction
		t.Start()
		DB.ElementTransformUtils.MoveElement(doc, selIds[0], moveVec)
		t.Commit()
		# Close the transaction
		
	
	
		
elif isinstance(element, Autodesk.Revit.DB.Wall):
	loc = element.Location
	print(loc)
	if isinstance(loc, Autodesk.Revit.DB.LocationCurve):
		curve = loc.Curve
		print("curve")
		print(dir(curve))
		print("origin")
		origin = curve.Origin
		originX = UnitUtils.ConvertFromInternalUnits(origin[0], DisplayUnitType.DUT_MILLIMETERS)
		originY = UnitUtils.ConvertFromInternalUnits(origin[1], DisplayUnitType.DUT_MILLIMETERS)
		originZ = UnitUtils.ConvertFromInternalUnits(origin[2], DisplayUnitType.DUT_MILLIMETERS)
		print((originX, originY, originZ))
		print("Curve Length")
		cLength = UnitUtils.ConvertFromInternalUnits(curve.Length, DisplayUnitType.DUT_MILLIMETERS)
		print(cLength)
		wallOrigin = DB.XYZ(curve.Origin[0],curve.Origin[1], curve.Origin[2])
		toPoint = DB.XYZ(197.600419011, -57.284730545, -0.1508510770)
		moveVec = toPoint.Subtract(wallOrigin)
		print("moveVec {0}".format(moveVec))
		t = DB.Transaction(doc, 'Moving Element')
		# Begin new transaction
		t.Start()
		DB.ElementTransformUtils.MoveElement(doc, selIds[0], moveVec)
		# Close the transaction
		t.Commit()

