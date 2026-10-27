# -*- coding: utf-8 -*-

__title__ = "Batch PBP"
__author__ = "Daniel Gercak"
__doc__ = """
Davkove nacteni Project Base Point z vice RVT modelu.

Vystup:
- PBP V/Z v milimetrech,
- PBP S/Z v milimetrech,
- PBP vyska v milimetrech,
- PBP uhel v radianech a stupnich,
- PBP Position X/Y/Z v milimetrech,
- parametr R_PROJEKTOVA_NULA z Project Information,
- CSV report ve zdrojove slozce.
"""

import os
import re
import math
import shutil
import tempfile
import traceback
import codecs

from datetime import datetime

from pyrevit import forms
from pyrevit import script

from Autodesk.Revit.DB import (
    BasePoint,
    BuiltInParameter,
    ModelPathUtils,
    OpenOptions,
    StorageType,
    UnitUtils,
    UnitTypeId
)


# ============================================================
# REVIT / PYREVIT
# ============================================================

output = script.get_output()
output.set_title("PVS Batch PBP")

app = __revit__.Application


# ============================================================
# NASTAVENI
# ============================================================

DELETE_TEMP_COPIES = True
DECIMAL_PLACES = 6
CSV_DELIMITER = u";"
DEGREE_SYMBOL = u"\u00b0"

PROJECT_ZERO_PARAMETER_NAME = u"R_PROJEKTOVA_NULA"


# ============================================================
# TEXTOVE FUNKCE
# ============================================================

def safe_text(value):
    """Bezpecny prevod hodnoty na Unicode pro IronPython 2.7."""

    if value is None:
        return u""

    try:
        return unicode(value)

    except Exception:
        try:
            return unicode(
                str(value),
                "utf-8",
                "replace"
            )

        except Exception:
            return u"<nelze prevest>"


def clean_error(exception):
    """Prevede chybu na jeden radek."""

    text = safe_text(exception)

    text = text.replace(u"\r", u" ")
    text = text.replace(u"\n", u" ")

    while u"  " in text:
        text = text.replace(u"  ", u" ")

    return text.strip()


def format_number_for_csv(value):
    """
    Formatuje cislo pro cesky Excel:
    - pevny pocet desetinnych mist,
    - desetinna carka.
    """

    if value is None:
        return u""

    format_string = (
        u"{0:."
        + safe_text(DECIMAL_PLACES)
        + u"f}"
    )

    text = format_string.format(value)

    return text.replace(
        u".",
        u","
    )


def format_number_for_output(value):
    """Formatuje cislo pro pyRevit Output."""

    if value is None:
        return u"N/A"

    format_string = (
        u"{0:."
        + safe_text(DECIMAL_PLACES)
        + u"f}"
    )

    return format_string.format(value)


# ============================================================
# REVIT JEDNOTKY A PARAMETRY
# ============================================================

def to_millimeters(value):
    """
    Prevede interni delkovou jednotku Revitu na milimetry.

    Revit uklada delky interne ve stopach.
    """

    if value is None:
        return None

    return UnitUtils.ConvertFromInternalUnits(
        value,
        UnitTypeId.Millimeters
    )


def radians_to_degrees(radians):
    """
    Explicitni prevod uhlu z radianu na stupne.

    stupne = radiany * 180 / pi
    """

    if radians is None:
        return None

    return (
        float(radians)
        * 180.0
        / math.pi
    )


def get_double_parameter(element, built_in_parameter):
    """Bezpecne nacte parametr typu Double."""

    parameter = element.get_Parameter(
        built_in_parameter
    )

    if parameter is None:
        return None

    try:
        if not parameter.HasValue:
            return None

    except Exception:
        pass

    try:
        if parameter.StorageType != StorageType.Double:
            return None

    except Exception:
        return None

    try:
        return parameter.AsDouble()

    except Exception:
        return None


def get_storage_type_name(parameter):
    """Vrati citelny nazev datoveho typu parametru."""

    if parameter is None:
        return u""

    try:
        storage_type = parameter.StorageType

        if storage_type == StorageType.String:
            return u"String"

        if storage_type == StorageType.Double:
            return u"Double"

        if storage_type == StorageType.Integer:
            return u"Integer"

        if storage_type == StorageType.ElementId:
            return u"ElementId"

        if storage_type == StorageType.None:
            return u"None"

        return safe_text(storage_type)

    except Exception:
        return u"NEZNAMY_TYP"


# ============================================================
# VYHLEDANI RVT
# ============================================================

def is_backup_rvt(file_name):
    """
    Vylouci zalohy typu:
    Model.0001.rvt
    Model.0012.rvt
    """

    match = re.search(
        r"\.\d{4}\.rvt$",
        file_name,
        re.IGNORECASE
    )

    return match is not None


def find_rvt_files(folder):
    """Najde RVT primo ve zvolene slozce."""

    found_files = []

    for file_name in os.listdir(folder):

        file_path = os.path.join(
            folder,
            file_name
        )

        if not os.path.isfile(file_path):
            continue

        if not file_name.lower().endswith(".rvt"):
            continue

        if file_name.startswith("~"):
            continue

        if is_backup_rvt(file_name):
            continue

        found_files.append(file_path)

    found_files.sort(
        key=lambda path: path.lower()
    )

    return found_files


# ============================================================
# VYSLEDKOVY ZAZNAM
# ============================================================

def create_result(source_path):
    """Vytvori prazdny vysledkovy zaznam modelu."""

    return {
        "file_name": os.path.basename(source_path),
        "source_path": source_path,

        "status": u"ERROR",
        "error": u"",

        "east_west_mm": None,
        "north_south_mm": None,
        "elevation_mm": None,

        "angle_radians": None,
        "angle_degrees": None,

        "position_x_mm": None,
        "position_y_mm": None,
        "position_z_mm": None,

        "project_zero_status": u"NEZKONTROLOVANO",
        "project_zero_storage_type": u"",
        "project_zero_value": u"",
        "project_zero_mm": None
    }


# ============================================================
# CTENI PROJECT BASE POINT
# ============================================================

def read_pbp(document, result):
    """Nacte Project Base Point z otevreneho RVT."""

    pbp = BasePoint.GetProjectBasePoint(
        document
    )

    if pbp is None:
        raise Exception(
            u"Project Base Point nebyl nalezen."
        )

    east_west_raw = get_double_parameter(
        pbp,
        BuiltInParameter.BASEPOINT_EASTWEST_PARAM
    )

    north_south_raw = get_double_parameter(
        pbp,
        BuiltInParameter.BASEPOINT_NORTHSOUTH_PARAM
    )

    elevation_raw = get_double_parameter(
        pbp,
        BuiltInParameter.BASEPOINT_ELEVATION_PARAM
    )

    angle_radians = get_double_parameter(
        pbp,
        BuiltInParameter.BASEPOINT_ANGLETON_PARAM
    )

    result["east_west_mm"] = to_millimeters(
        east_west_raw
    )

    result["north_south_mm"] = to_millimeters(
        north_south_raw
    )

    result["elevation_mm"] = to_millimeters(
        elevation_raw
    )

    result["angle_radians"] = angle_radians

    result["angle_degrees"] = radians_to_degrees(
        angle_radians
    )

    try:
        position = pbp.Position

        result["position_x_mm"] = to_millimeters(
            position.X
        )

        result["position_y_mm"] = to_millimeters(
            position.Y
        )

        result["position_z_mm"] = to_millimeters(
            position.Z
        )

    except Exception as position_error:
        print(
            u"PBP.Position nelze precist: {0}".format(
                clean_error(position_error)
            )
        )


# ============================================================
# R_PROJEKTOVA_NULA
# ============================================================

def read_project_zero_parameter(document, result):
    """
    Nacte parametr R_PROJEKTOVA_NULA z Project Information.

    Osetruje:
    - parametr neexistuje,
    - parametr nema hodnotu,
    - String,
    - Double,
    - Integer,
    - ElementId,
    - neznamy datovy typ.

    U Double se ulozi:
    - zobrazena hodnota pres AsValueString,
    - ciselna hodnota prevedena z internich jednotek
      Revitu na milimetry.
    """

    result["project_zero_status"] = u"PARAMETR_NENALEZEN"
    result["project_zero_storage_type"] = u""
    result["project_zero_value"] = u""
    result["project_zero_mm"] = None

    try:
        project_information = document.ProjectInformation

    except Exception as project_info_error:
        result["project_zero_status"] = (
            u"PROJECT_INFORMATION_CHYBA"
        )

        result["project_zero_value"] = clean_error(
            project_info_error
        )

        return

    if project_information is None:
        result["project_zero_status"] = (
            u"PROJECT_INFORMATION_NENALEZEN"
        )

        return

    try:
        parameter = project_information.LookupParameter(
            PROJECT_ZERO_PARAMETER_NAME
        )

    except Exception as lookup_error:
        result["project_zero_status"] = (
            u"LOOKUP_CHYBA"
        )

        result["project_zero_value"] = clean_error(
            lookup_error
        )

        return

    if parameter is None:
        result["project_zero_status"] = (
            u"PARAMETR_NENALEZEN"
        )

        return

    result["project_zero_storage_type"] = (
        get_storage_type_name(parameter)
    )

    try:
        has_value = parameter.HasValue

    except Exception:
        has_value = True

    if not has_value:
        result["project_zero_status"] = (
            u"PARAMETR_BEZ_HODNOTY"
        )

        return

    storage_type = parameter.StorageType

    # --------------------------------------------------------
    # STRING
    # --------------------------------------------------------

    if storage_type == StorageType.String:

        try:
            value = parameter.AsString()

        except Exception:
            value = None

        result["project_zero_value"] = safe_text(
            value
        )

        if result["project_zero_value"]:
            result["project_zero_status"] = u"OK"

        else:
            result["project_zero_status"] = (
                u"PARAMETR_BEZ_HODNOTY"
            )

        return

    # --------------------------------------------------------
    # DOUBLE
    # --------------------------------------------------------

    if storage_type == StorageType.Double:

        raw_value = None
        display_value = None

        try:
            raw_value = parameter.AsDouble()

        except Exception:
            raw_value = None

        try:
            display_value = parameter.AsValueString()

        except Exception:
            display_value = None

        result["project_zero_value"] = safe_text(
            display_value
        )

        if raw_value is not None:

            try:
                result["project_zero_mm"] = (
                    to_millimeters(raw_value)
                )

                result["project_zero_status"] = u"OK"

            except Exception as conversion_error:

                result["project_zero_status"] = (
                    u"PREVOD_NA_MM_CHYBA"
                )

                if not result["project_zero_value"]:
                    result["project_zero_value"] = (
                        clean_error(conversion_error)
                    )

        else:
            result["project_zero_status"] = (
                u"PARAMETR_BEZ_HODNOTY"
            )

        return

    # --------------------------------------------------------
    # INTEGER
    # --------------------------------------------------------

    if storage_type == StorageType.Integer:

        try:
            integer_value = parameter.AsInteger()

            result["project_zero_value"] = safe_text(
                integer_value
            )

            result["project_zero_status"] = u"OK"

        except Exception as integer_error:
            result["project_zero_status"] = (
                u"CTENI_INTEGER_CHYBA"
            )

            result["project_zero_value"] = clean_error(
                integer_error
            )

        return

    # --------------------------------------------------------
    # ELEMENT ID
    # --------------------------------------------------------

    if storage_type == StorageType.ElementId:

        try:
            element_id = parameter.AsElementId()

            try:
                element_id_value = element_id.Value

            except Exception:
                element_id_value = element_id.IntegerValue

            result["project_zero_value"] = safe_text(
                element_id_value
            )

            result["project_zero_status"] = u"OK"

        except Exception as element_id_error:
            result["project_zero_status"] = (
                u"CTENI_ELEMENTID_CHYBA"
            )

            result["project_zero_value"] = clean_error(
                element_id_error
            )

        return

    # --------------------------------------------------------
    # JINY DATOVY TYP
    # --------------------------------------------------------

    result["project_zero_status"] = (
        u"NEPODPOROVANY_DATOVY_TYP"
    )

    try:
        result["project_zero_value"] = safe_text(
            parameter.AsValueString()
        )

    except Exception:
        result["project_zero_value"] = u""


# ============================================================
# ZPRACOVANI JEDNOHO MODELU
# ============================================================

def process_model(source_path, index, total):
    """
    Zpracuje jeden RVT:
    - vytvori TEMP kopii,
    - otevre TEMP kopii,
    - precte PBP,
    - precte R_PROJEKTOVA_NULA,
    - zavre dokument bez ulozeni,
    - odstrani TEMP kopii.
    """

    result = create_result(
        source_path
    )

    document = None
    temp_folder = None

    file_name = os.path.basename(
        source_path
    )

    print(u"")
    print(u"=" * 70)

    print(
        u"[{0}/{1}] {2}".format(
            index,
            total,
            safe_text(file_name)
        )
    )

    print(u"=" * 70)

    try:
        # ----------------------------------------------------
        # KONTROLA ZDROJE
        # ----------------------------------------------------

        print(
            u"Zdroj: {0}".format(
                safe_text(source_path)
            )
        )

        if not os.path.isfile(source_path):
            raise Exception(
                u"Zdrojovy RVT neni dostupny."
            )

        source_size = os.path.getsize(
            source_path
        )

        print(
            u"Velikost zdroje: {0} bytes".format(
                source_size
            )
        )

        if source_size <= 0:
            raise Exception(
                u"Zdrojovy RVT ma nulovou velikost."
            )

        # ----------------------------------------------------
        # TEMP KOPIE
        # ----------------------------------------------------

        temp_folder = tempfile.mkdtemp(
            prefix="PVS_PBP_BATCH_"
        )

        local_path = os.path.join(
            temp_folder,
            file_name
        )

        print(
            u"TEMP: {0}".format(
                safe_text(local_path)
            )
        )

        print(u"Kopiruji model do TEMP...")

        shutil.copy2(
            source_path,
            local_path
        )

        if not os.path.isfile(local_path):
            raise Exception(
                u"TEMP kopie nebyla vytvorena."
            )

        local_size = os.path.getsize(
            local_path
        )

        print(
            u"Velikost TEMP kopie: {0} bytes".format(
                local_size
            )
        )

        if local_size != source_size:
            raise Exception(
                u"Velikost TEMP kopie neodpovida zdroji."
            )

        # ----------------------------------------------------
        # MODEL PATH
        # ----------------------------------------------------

        model_path = (
            ModelPathUtils.ConvertUserVisiblePathToModelPath(
                local_path
            )
        )

        open_options = OpenOptions()

        try:
            open_options.Audit = False

        except Exception:
            pass

        # ----------------------------------------------------
        # OTEVRENI
        # ----------------------------------------------------

        print(u"Oteviram RVT...")

        document = app.OpenDocumentFile(
            model_path,
            open_options
        )

        if document is None:
            raise Exception(
                u"OpenDocumentFile vratil None."
            )

        print(
            u"Otevreno: {0}".format(
                safe_text(document.Title)
            )
        )

        # ----------------------------------------------------
        # PROJECT BASE POINT
        # ----------------------------------------------------

        print(u"Ctu Project Base Point...")

        read_pbp(
            document,
            result
        )

        # ----------------------------------------------------
        # R_PROJEKTOVA_NULA
        # ----------------------------------------------------

        print(
            u"Ctu parametr {0}...".format(
                PROJECT_ZERO_PARAMETER_NAME
            )
        )

        read_project_zero_parameter(
            document,
            result
        )

        result["status"] = u"OK"
        result["error"] = u""

        # ----------------------------------------------------
        # VYSTUP
        # ----------------------------------------------------

        print(
            u"V/Z: {0} mm".format(
                format_number_for_output(
                    result["east_west_mm"]
                )
            )
        )

        print(
            u"S/Z: {0} mm".format(
                format_number_for_output(
                    result["north_south_mm"]
                )
            )
        )

        print(
            u"Vyska: {0} mm".format(
                format_number_for_output(
                    result["elevation_mm"]
                )
            )
        )

        print(
            u"Uhel RAW: {0} rad".format(
                format_number_for_output(
                    result["angle_radians"]
                )
            )
        )

        print(
            u"Uhel: {0} {1}".format(
                format_number_for_output(
                    result["angle_degrees"]
                ),
                DEGREE_SYMBOL
            )
        )

        print(
            u"{0} - stav: {1}".format(
                PROJECT_ZERO_PARAMETER_NAME,
                result["project_zero_status"]
            )
        )

        print(
            u"{0} - typ: {1}".format(
                PROJECT_ZERO_PARAMETER_NAME,
                result["project_zero_storage_type"]
            )
        )

        print(
            u"{0} - hodnota: {1}".format(
                PROJECT_ZERO_PARAMETER_NAME,
                result["project_zero_value"]
            )
        )

        if result["project_zero_mm"] is not None:

            print(
                u"{0}: {1} mm".format(
                    PROJECT_ZERO_PARAMETER_NAME,
                    format_number_for_output(
                        result["project_zero_mm"]
                    )
                )
            )

        print(u"Stav modelu: OK")

    except Exception as exception:

        result["status"] = u"ERROR"

        result["error"] = clean_error(
            exception
        )

        print(u"Stav modelu: ERROR")

        print(
            u"Chyba: {0}".format(
                result["error"]
            )
        )

        print(u"")

        print(
            safe_text(
                traceback.format_exc()
            )
        )

    finally:
        # ----------------------------------------------------
        # ZAVRENI RVT
        # ----------------------------------------------------

        if document is not None:

            try:
                if document.IsValidObject:

                    print(u"Zaviram RVT bez ulozeni...")

                    document.Close(False)

                    print(u"RVT zavren.")

            except Exception as close_error:

                close_message = (
                    u"Chyba pri zavirani: {0}".format(
                        clean_error(close_error)
                    )
                )

                print(close_message)

                if result["error"]:
                    result["error"] += (
                        u" | " + close_message
                    )

                else:
                    result["error"] = close_message

                if result["status"] == u"OK":
                    result["status"] = u"WARNING"

        # ----------------------------------------------------
        # ODSTRANENI TEMP
        # ----------------------------------------------------

        if (
            DELETE_TEMP_COPIES
            and temp_folder
            and os.path.isdir(temp_folder)
        ):

            try:
                shutil.rmtree(
                    temp_folder
                )

                print(u"TEMP odstranen.")

            except Exception as temp_error:

                temp_message = (
                    u"TEMP nelze odstranit: {0}".format(
                        clean_error(temp_error)
                    )
                )

                print(temp_message)

                if result["error"]:
                    result["error"] += (
                        u" | " + temp_message
                    )

                else:
                    result["error"] = temp_message

                if result["status"] == u"OK":
                    result["status"] = u"WARNING"

    return result


# ============================================================
# CSV
# ============================================================

CSV_COLUMNS = [
    (
        u"Soubor",
        "file_name",
        "text"
    ),
    (
        u"Zdrojova cesta",
        "source_path",
        "text"
    ),
    (
        u"Stav",
        "status",
        "text"
    ),
    (
        u"Chyba",
        "error",
        "text"
    ),
    (
        u"PBP V/Z - East/West [mm]",
        "east_west_mm",
        "number"
    ),
    (
        u"PBP S/Z - North/South [mm]",
        "north_south_mm",
        "number"
    ),
    (
        u"PBP vyska [mm]",
        "elevation_mm",
        "number"
    ),
    (
        u"PBP uhel RAW [rad]",
        "angle_radians",
        "number"
    ),
    (
        u"PBP uhel [{0}]".format(
            DEGREE_SYMBOL
        ),
        "angle_degrees",
        "number"
    ),
    (
        u"PBP Position X [mm]",
        "position_x_mm",
        "number"
    ),
    (
        u"PBP Position Y [mm]",
        "position_y_mm",
        "number"
    ),
    (
        u"PBP Position Z [mm]",
        "position_z_mm",
        "number"
    ),
    (
        u"R_PROJEKTOVA_NULA - stav",
        "project_zero_status",
        "text"
    ),
    (
        u"R_PROJEKTOVA_NULA - datovy typ",
        "project_zero_storage_type",
        "text"
    ),
    (
        u"R_PROJEKTOVA_NULA - zobrazena hodnota",
        "project_zero_value",
        "text"
    ),
    (
        u"R_PROJEKTOVA_NULA [mm]",
        "project_zero_mm",
        "number"
    )
]


def csv_escape(value):
    """Escapuje jednu CSV bunku."""

    text = safe_text(value)

    text = text.replace(
        u'"',
        u'""'
    )

    return u'"' + text + u'"'


def get_csv_value(result, key, value_type):
    """Pripravi hodnotu pro CSV."""

    value = result.get(key)

    if value_type == "number":
        return format_number_for_csv(
            value
        )

    return safe_text(value)


def write_csv(report_path, results):
    """
    Zapise CSV:
    - UTF-8 s BOM,
    - strednik,
    - desetinna carka.
    """

    handle = codecs.open(
        report_path,
        "w",
        "utf-8"
    )

    try:
        handle.write(u"\ufeff")

        header = []

        for column in CSV_COLUMNS:

            column_title = column[0]

            header.append(
                csv_escape(column_title)
            )

        handle.write(
            CSV_DELIMITER.join(header)
            + u"\r\n"
        )

        for result in results:

            row = []

            for column in CSV_COLUMNS:

                key = column[1]
                value_type = column[2]

                value = get_csv_value(
                    result,
                    key,
                    value_type
                )

                row.append(
                    csv_escape(value)
                )

            handle.write(
                CSV_DELIMITER.join(row)
                + u"\r\n"
            )

    finally:
        handle.close()


# ============================================================
# SOUHRN
# ============================================================

def count_status(results, status):
    """Spocita zaznamy daneho stavu."""

    count = 0

    for result in results:

        if result["status"] == status:
            count += 1

    return count


# ============================================================
# MAIN
# ============================================================

def main():
    """Hlavni beh batch prikazu."""

    print(u"=" * 70)
    print(u"PVS BATCH PBP")
    print(u"=" * 70)

    print(
        u"Revit: {0}".format(
            safe_text(app.VersionNumber)
        )
    )

    # --------------------------------------------------------
    # VYBER SLOZKY
    # --------------------------------------------------------

    folder = forms.pick_folder(
        title="Vyber slozku s RVT modely"
    )

    if not folder:

        print(u"Vyber slozky byl zrusen.")

        return

    print(
        u"Slozka: {0}".format(
            safe_text(folder)
        )
    )

    # --------------------------------------------------------
    # RVT SOUBORY
    # --------------------------------------------------------

    rvt_paths = find_rvt_files(
        folder
    )

    if not rvt_paths:

        forms.alert(
            u"Ve vybrane slozce nejsou zadne RVT modely.",
            title=u"PVS Batch PBP",
            warn_icon=True
        )

        return

    file_names = []

    for path in rvt_paths:

        file_names.append(
            os.path.basename(path)
        )

    # --------------------------------------------------------
    # VICENASOBNY VYBER
    # --------------------------------------------------------

    selected_names = forms.SelectFromList.show(
        file_names,
        title="Vyber RVT modely",
        multiselect=True,
        button_name="Nacist PBP",
        width=800,
        height=600
    )

    if not selected_names:

        print(u"Vyber modelu byl zrusen.")

        return

    selected_paths = []

    for selected_name in selected_names:

        selected_path = os.path.join(
            folder,
            safe_text(selected_name)
        )

        selected_paths.append(
            selected_path
        )

    total = len(selected_paths)

    print(
        u"Vybrano modelu: {0}".format(
            total
        )
    )

    # --------------------------------------------------------
    # POTVRZENI
    # --------------------------------------------------------

    continue_batch = forms.alert(
        (
            u"Bude zpracovano {0} RVT modelu.\n\n"
            u"Modely budou otevreny z TEMP kopii "
            u"a zavreny bez ulozeni.\n\n"
            u"Pokracovat?"
        ).format(
            total
        ),
        title=u"PVS Batch PBP",
        yes=True,
        no=True
    )

    if not continue_batch:

        print(u"Batch byl zrusen uzivatelem.")

        return

    # --------------------------------------------------------
    # ZPRACOVANI S PROGRESS BAREM
    # --------------------------------------------------------

    results = []
    cancelled = False

    with forms.ProgressBar(
        title=(
            u"PVS Batch PBP "
            u"{value} z {max_value}"
        ),
        cancellable=True,
        step=1
    ) as progress_bar:

        index = 0

        for source_path in selected_paths:

            index += 1

            file_name = os.path.basename(
                source_path
            )

            try:
                progress_bar.title = (
                    u"PVS Batch PBP | {0}/{1} | {2}"
                ).format(
                    index,
                    total,
                    safe_text(file_name)
                )

            except Exception:
                pass

            progress_bar.update_progress(
                index - 1,
                total
            )

            if progress_bar.cancelled:

                cancelled = True

                print(
                    u"Zpracovani zruseno uzivatelem."
                )

                break

            result = process_model(
                source_path,
                index,
                total
            )

            results.append(
                result
            )

            progress_bar.update_progress(
                index,
                total
            )

            if progress_bar.cancelled:

                cancelled = True

                print(
                    u"Zpracovani zruseno uzivatelem."
                )

                break

    # --------------------------------------------------------
    # BEZ VYSLEDKU
    # --------------------------------------------------------

    if not results:

        forms.alert(
            u"Nebyl zpracovan zadny model.",
            title=u"PVS Batch PBP",
            warn_icon=True
        )

        return

    # --------------------------------------------------------
    # CSV REPORT
    # --------------------------------------------------------

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    report_name = (
        "PBP_Report_{0}.csv".format(
            timestamp
        )
    )

    report_path = os.path.join(
        folder,
        report_name
    )

    print(u"")
    print(u"Zapisuji CSV report...")

    write_csv(
        report_path,
        results
    )

    print(
        u"CSV vytvoreno: {0}".format(
            safe_text(report_path)
        )
    )

    # --------------------------------------------------------
    # SOUHRN
    # --------------------------------------------------------

    ok_count = count_status(
        results,
        u"OK"
    )

    warning_count = count_status(
        results,
        u"WARNING"
    )

    error_count = count_status(
        results,
        u"ERROR"
    )

    if cancelled:
        completion_text = (
            u"Batch PBP byl prerusen uzivatelem."
        )

    else:
        completion_text = (
            u"Batch PBP byl dokoncen."
        )

    message = (
        completion_text
        + u"\n\n"
        + u"Vybrano modelu: {0}\n"
        + u"Zpracovano: {1}\n"
        + u"Uspesne: {2}\n"
        + u"Varovani: {3}\n"
        + u"Chyby: {4}\n\n"
        + u"CSV report:\n{5}"
    ).format(
        total,
        len(results),
        ok_count,
        warning_count,
        error_count,
        safe_text(report_path)
    )

    forms.alert(
        message,
        title=u"PVS Batch PBP"
    )

    forms.ask_for_string(
        default=safe_text(report_path),
        prompt=(
            u"Cesta k CSV reportu.\n"
            u"Oznacte text a stisknete Ctrl+C."
        ),
        title=u"PVS Batch PBP - CSV"
    )


# ============================================================
# SPUSTENI
# ============================================================

try:

    print(u"START SCRIPT")

    print(
        u"Aktivni soubor: {0}".format(
            safe_text(__file__)
        )
    )

    main()


except Exception as exception:

    print(u"")
    print(u"=" * 70)
    print(u"KRITICKA CHYBA")
    print(u"=" * 70)

    print(
        clean_error(exception)
    )

    print(u"")

    print(
        safe_text(
            traceback.format_exc()
        )
    )

    forms.alert(
        (
            u"Batch PBP skoncil chybou.\n\n"
            u"{0}\n\n"
            u"Detail je v pyRevit Output."
        ).format(
            clean_error(exception)
        ),
        title=u"PVS Batch PBP - ERROR",
        warn_icon=True
    )


finally:

    print(u"")
    print(u"END SCRIPT")