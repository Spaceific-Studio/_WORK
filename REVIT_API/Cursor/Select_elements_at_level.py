# -*- coding: utf-8 -*-
import clr
import sys

# Revit API
clr.AddReference("RevitAPI")
from Autodesk.Revit.DB import *
clr.AddReference("RevitAPIUI")
from Autodesk.Revit.UI import *

# Dynamo Revit sluzby
clr.AddReference("RevitServices")
from RevitServices.Persistence import DocumentManager

# .NET
clr.AddReference("System")
from System.Collections.Generic import List
import System

doc = DocumentManager.Instance.CurrentDBDocument
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument

# IN[0] = vybrany RevitLinkInstance
# IN[1] = vybrane podlazi (Level) z tohoto linku
# IN[2] = cesta k CSV souboru (napr. C:\\Temp\\prvky_podlazi_link.csv)
link_instance = UnwrapElement(IN[0])
level = UnwrapElement(IN[1])
csv_path = IN[2]

if link_instance is None:
    OUT = "Chyba: Neni vybrany RevitLinkInstance."
elif level is None:
    OUT = "Chyba: Neni vybrane podlazi (Level) z linku."
else:
    link_doc = link_instance.GetLinkDocument()
    if link_doc is None:
        OUT = "Chyba: Nelze ziskat dokument vybraneho linku."
    else:
        level_id = level.Id
        all_elems = FilteredElementCollector(link_doc).WhereElementIsNotElementType().ToElements()
        result = []

        def get_param_text(el, bip):
            try:
                p = el.get_Parameter(bip)
                if p:
                    txt = p.AsString()
                    if not txt:
                        txt = p.AsValueString()
                    if txt:
                        return txt
            except:
                pass
            return u""

        def resolve_family_and_type(e):
            fam_name = u""
            type_name = u""
            t = None

            try:
                type_id = e.GetTypeId()
                if type_id and type_id != ElementId.InvalidElementId:
                    t = link_doc.GetElement(type_id)
            except:
                t = None

            # 1) Nejspolehliveji z typu
            if t:
                try:
                    type_name = t.Name or u""
                except:
                    type_name = u""
                fam_name = get_param_text(t, BuiltInParameter.SYMBOL_FAMILY_NAME_PARAM)
                if not fam_name:
                    try:
                        fam_name = t.FamilyName or u""
                    except:
                        fam_name = u""

            # 2) Fallback z beznych textovych parametru
            if not fam_name:
                fam_name = get_param_text(e, BuiltInParameter.ELEM_FAMILY_PARAM)
            if not fam_name and t:
                fam_name = get_param_text(t, BuiltInParameter.ELEM_FAMILY_PARAM)

            if not type_name:
                type_name = get_param_text(e, BuiltInParameter.ELEM_TYPE_PARAM)
            if not type_name and t:
                type_name = get_param_text(t, BuiltInParameter.ELEM_TYPE_PARAM)

            # 3) Posledni fallback na nazev elementu
            if not type_name:
                try:
                    type_name = Element.Name.GetValue(e) or u""
                except:
                    type_name = u""
            if not fam_name:
                fam_name = u"(bez rodiny)"
            if not type_name:
                type_name = u"(bez typu)"

            return fam_name, type_name

        def param_matches_level(e, bip):
            p = e.get_Parameter(bip)
            if p and p.StorageType == StorageType.ElementId:
                return p.AsElementId() == level_id
            return False

        for e in all_elems:
            if e.Id == level_id:
                continue
            match = False

            # 1) Priama vazba pres LevelId (kde je dostupna)
            try:
                if hasattr(e, "LevelId") and e.LevelId != ElementId.InvalidElementId and e.LevelId == level_id:
                    match = True
            except:
                pass

            # 2) Bezne parametry vazby na podlazi
            if not match:
                bips = [
                    BuiltInParameter.LEVEL_PARAM,
                    BuiltInParameter.SCHEDULE_LEVEL_PARAM,
                    BuiltInParameter.INSTANCE_REFERENCE_LEVEL_PARAM,
                    BuiltInParameter.FAMILY_LEVEL_PARAM,
                    BuiltInParameter.WALL_BASE_CONSTRAINT
                ]
                for bip in bips:
                    try:
                        if param_matches_level(e, bip):
                            match = True
                            break
                    except:
                        pass
            if match:
                result.append(e)

        # API umi vybirat jen elementy host dokumentu.
        # Proto se v Revitu oznaci pouze vybrany link instance.
        ids = List[ElementId]()
        ids.Add(link_instance.Id)
        uidoc.Selection.SetElementIds(ids)

        # Export do CSV (Excel-friendly)
        lines = [u"Nazev rodiny;Typ rodiny;ID instance"]
        for e in result:
            fam_name, type_name = resolve_family_and_type(e)
            row = u"{0};{1};{2}".format(fam_name, type_name, e.Id.Value)
            lines.append(row)

        sw = System.IO.StreamWriter(csv_path, False, System.Text.Encoding.UTF8)
        for ln in lines:
            sw.WriteLine(ln)
        sw.Close()

        try:
            level_name = level.Name
        except:
            level_name = u""

        OUT = (link_instance, level_name, result, csv_path, "Pocet prvku v linku: {0}".format(len(result)))