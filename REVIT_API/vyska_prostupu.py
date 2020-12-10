# -*- coding: utf-8 -*-
# Copyright(c) 2020, Daniel Gercak
#Script for parameters update of family "Prostup (SWECO)"
#resource_path: H:\_WORK\PYTHON\REVIT_API\vyska_prostupu.py
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB.Architecture import *
from Autodesk.Revit.DB.Analysis import *
from Autodesk.Revit.UI import *
import sys
#if "Windows" in platform.uname():
	#lib_path = r'H:/_WORK/PYTHON/LIB'
lib_path = r'H:/_WORK/PYTHON/REVIT_API/LIB'
sys.path.append(lib_path)

import clr
from RevitSelection import getFamilyInstancesByName, getValuesByParameterName, setValuesByParameterName

clr.AddReferenceByPartialName('PresentationCore')
clr.AddReferenceByPartialName('PresentationFramework')
clr.AddReferenceByPartialName('System.Windows.Forms')
import System.Windows

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
selection = [doc.GetElement(elId) for elId in __revit__.ActiveUIDocument.Selection.GetElementIds()]
#print(dir(__revit__))

familyName = "Prostup (SWECO)"
prostupy = getFamilyInstancesByName(doc, familyName)
oznaceniValues = getValuesByParameterName(prostupy, "ALL_MODEL_MARK", doc)
popisekValues = getValuesByParameterName(prostupy, "Popisek", doc)
stenovyValues = getValuesByParameterName(prostupy, "stěnový", doc)
prumerValues = getValuesByParameterName(prostupy, "Průměr", doc)
sirkaValues = getValuesByParameterName(prostupy, "Šířka", doc)
vyskaValues = getValuesByParameterName(prostupy, "Výška", doc)
basePoint = list(FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_ProjectBasePoint))
param_ID = ElementId(BuiltInParameter.BASEPOINT_ELEVATION_PARAM)
basePointElevation = UnitUtils.ConvertFromInternalUnits(ParameterValueProvider(param_ID).GetDoubleValue(basePoint[0]), DisplayUnitType.DUT_MILLIMETERS)

print("Script pro update parametrů rodiny \"Prostup (SWECO)\"\n")
print("Výška základního bodu projektu: {0:.3f} m.n.m\n".format(basePointElevation/1000))
#print("{0} - {1}".format(popisekValues[0][0], ord(popisekValues[0][0])))
#absoluteElevations = [UnitUtils.ConvertFromInternalUnits(x.Location.Point[2], DisplayUnitType.DUT_MILLIMETERS) + basePointElevation for x in prostupy]
absoluteElevations = []
textsForPopisek = []
neprepisovat_1 = []
for i, el in enumerate(prostupy):
    prostupZ = UnitUtils.ConvertFromInternalUnits(el.Location.Point[2], DisplayUnitType.DUT_MILLIMETERS)
    prostupPrumer = prumerValues[i]
    prostupVyska = vyskaValues[i]
    prostupSirka = sirkaValues[i]
    #if el.Host.Category.BuiltInCategory.ToString() == "OST.Walls":
    #if hasattr(el.Host, "WallType"):
    if stenovyValues[i] == 1:
        if prostupPrumer > 0:
            textAbsElev = "OSA {0:.3f}".format((basePointElevation + prostupZ)/1000)
            nepr_1 = (basePointElevation + prostupZ)/1000
            textForPopisek = "{0}{1:.0f} mm".format(chr(248), prostupPrumer)
        elif prostupVyska > 0:
            textAbsElev = "SH {0:.3f}".format((basePointElevation + (prostupZ-(prostupVyska/2)))/1000)
            nepr_1 = (basePointElevation + prostupZ)/1000
            textForPopisek = "{0:.0f}x{1:.0f} mm".format(prostupSirka, prostupVyska)
    else:
        textAbsElev = "L {0:.3f}".format((basePointElevation + prostupZ)/1000)
        nepr_1 = (basePointElevation + prostupZ)/1000
        if prostupPrumer > 0:
            textForPopisek = "{0}{1:.0f} mm".format(chr(248), prostupPrumer)
        elif prostupVyska > 0:
            textForPopisek = "{0:.0f}x{1:.0f} mm".format(prostupSirka, prostupVyska)
    neprepisovat_1.append(nepr_1)
    absoluteElevations.append(textAbsElev)
    textsForPopisek.append(textForPopisek)

print("Seznam prostupů ve výkresu:\nNalezeno: {0}\n".format(len(prostupy)))
print("popisekValues:\n {0}\n".format(popisekValues))
print("sirkaValues:\n {0}\n".format(sirkaValues))
print("vyskaValues:\n {0}\n".format(vyskaValues))
print("absoluteElevations:\n {0}\n".format(absoluteElevations))
print("oznaceniValues:\n {0}\n".format(oznaceniValues))
print("stenovyValues:\n {0}\n".format(stenovyValues))
for i, el in enumerate(prumerValues):
	print("{9} >> {11} >> {0} >> X = {3} Y = {4} Z = {5}  >> stenovy = {10} >> absolutni vyska = {8} >> prumer = {1} >> vyska = {6} >> sirka = {7} >> popisek = {2}\n".format(prostupy[i].Name, \
                                                                                        el, \
                                                                                        popisekValues[i], \
                                                                                        UnitUtils.ConvertFromInternalUnits(prostupy[i].Location.Point[0], DisplayUnitType.DUT_MILLIMETERS), \
                                                                                        UnitUtils.ConvertFromInternalUnits(prostupy[i].Location.Point[1], DisplayUnitType.DUT_MILLIMETERS), \
                                                                                        UnitUtils.ConvertFromInternalUnits(prostupy[i].Location.Point[2], DisplayUnitType.DUT_MILLIMETERS), \
                                                                                        sirkaValues[i], \
                                                                                        vyskaValues[i], \
                                                                                        absoluteElevations[i], \
                                                                                        oznaceniValues[i] if oznaceniValues[i] != "" else "N/A", \
                                                                                        stenovyValues[i], \
                                                                                        prostupy[i].Id 
                                                                                            ))
t = Transaction(doc, "Update prostupy parameters")
t.Start()
#oznaceniValuesSet = setValuesByParameterName(prostupy, absoluteElevations, "ALL_MODEL_MARK")
myAbsoluteElevationValuesSet = setValuesByParameterName(prostupy, absoluteElevations, "NEPŘEPISOVAT 2")
myPopisekValuesSet = setValuesByParameterName(prostupy, textsForPopisek, "Popisek")
neprepisovat_1_ValuesSet = setValuesByParameterName(prostupy, neprepisovat_1, "NEPŘEPISOVAT 1")
t.Commit()

print("\nVýsledek: \n")
for i, x in enumerate(myAbsoluteElevationValuesSet):
    #print("{}".format(oznaceniValuesSet[i]))
    print("{}".format(myPopisekValuesSet[i]))
    print("{}".format(neprepisovat_1_ValuesSet[i]))
    print("{}\n".format(x))



