from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path
from typing import Any

import requests
import urllib3
from requests_negotiate_sspi import HttpNegotiateAuth


# =============================================================================
# KONFIGURACE
# =============================================================================

DMS_SITE = "https://dms.pvs.cz/sites/Zadanky"

LIST_GUID = "dc08c020-45ba-4cb5-9681-5ef919daa42b"

VERIFY_TLS = False

TOP_ITEMS = 100

OUTPUT_DIRECTORY = (
    Path(__file__).resolve().parent
    / "dms_homeoffice_reference"
)

# Pole žádanky
FIELD_TITLE = "Title"
FIELD_TYPE_OF_HOLIDAY = "Rq_H_TypeOfHoliday"
FIELD_PAID_HOLIDAY = "Rq_H_PaidHoliday"
FIELD_SPECIFY_OTHER = "Rq_H_SpecifyOther"
FIELD_VALID_SINCE = "Rq_H_ValidSince"
FIELD_VALID_TO = "Rq_H_ValidTo"
FIELD_WORKING_DAYS = "Rq_H_WorkingDay"
FIELD_APPLICANT = "Rq_All_Applicant"
FIELD_MANAGER = "Rq_All_ApplicantManager"
FIELD_REQUEST_TYPE = "Rq_All_type"
FIELD_STATUS = "Rq_All_StatusChoice"
FIELD_REQUEST_NUMBER = "Rq_All_RequestNumber"
FIELD_RELATED_LINK = "Rq_All_RelatedLink"

# Hodnoty, které očekáváme pro Home Office
HOME_OFFICE_TYPE_OF_HOLIDAY = "Placené volno"
HOME_OFFICE_PAID_HOLIDAY = "Jiné"
HOME_OFFICE_DESCRIPTION = "Home office"


# =============================================================================
# VÝPIS
# =============================================================================

def print_header(title: str) -> None:
    print()
    print("=" * 100)
    print(title)
    print("=" * 100)


def print_separator() -> None:
    print()
    print("-" * 100)


# =============================================================================
# SOUBORY
# =============================================================================

def save_text(
    file_path: Path,
    content: str,
) -> None:
    file_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    file_path.write_text(
        content,
        encoding="utf-8",
    )

    print(f"Uloženo: {file_path}")


def save_json(
    file_path: Path,
    content: Any,
) -> None:
    file_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    file_path.write_text(
        json.dumps(
            content,
            indent=2,
            ensure_ascii=False,
            default=str,
        ),
        encoding="utf-8",
    )

    print(f"Uloženo: {file_path}")


# =============================================================================
# HTTP RELACE
# =============================================================================

def create_session() -> requests.Session:
    """
    Vytvoří relaci používající Windows autentizaci Negotiate/NTLM.

    Skript použije účet Windows, pod kterým je Python spuštěn.
    """

    session = requests.Session()

    session.auth = HttpNegotiateAuth()

    session.headers.update(
        {
            "Accept": "application/json;odata=verbose",
            "User-Agent": (
                "PVS-DMS-HomeOffice-Reference-Diagnostics/1.0"
            ),
        }
    )

    return session


def get_json(
    session: requests.Session,
    url: str,
) -> dict[str, Any]:
    response = session.get(
        url,
        verify=VERIFY_TLS,
        timeout=60,
    )

    print(
        f"GET {response.status_code}: "
        f"{response.url}"
    )

    response.raise_for_status()

    return response.json()


# =============================================================================
# AKTUÁLNÍ UŽIVATEL
# =============================================================================

def get_current_user(
    session: requests.Session,
) -> dict[str, Any]:
    url = f"{DMS_SITE}/_api/web/currentuser"

    data = get_json(
        session,
        url,
    )["d"]

    print_header("AKTUÁLNÍ UŽIVATEL")

    print(f"ID:       {data.get('Id')}")
    print(f"Jméno:    {data.get('Title')}")
    print(f"Login:    {data.get('LoginName')}")
    print(f"E-mail:   {data.get('Email')}")

    return data


# =============================================================================
# DEFINICE POLE SOUVISEJÍCÍ ODKAZ
# =============================================================================

def get_related_link_field_definition(
    session: requests.Session,
) -> dict[str, Any]:
    url = (
        f"{DMS_SITE}/_api/web/lists"
        f"(guid'{LIST_GUID}')"
        f"/fields"
        f"/GetByInternalNameOrTitle"
        f"('{FIELD_RELATED_LINK}')"
    )

    data = get_json(
        session,
        url,
    )["d"]

    print_header(
        f"DEFINICE POLE {FIELD_RELATED_LINK}"
    )

    keys = (
        "Title",
        "InternalName",
        "StaticName",
        "TypeAsString",
        "Required",
        "ReadOnlyField",
        "Hidden",
        "DefaultValue",
        "RichText",
        "RichTextMode",
        "AppendOnly",
        "AllowHyperlink",
        "Description",
    )

    for key in keys:
        print(f"{key}: {data.get(key)}")

    save_json(
        OUTPUT_DIRECTORY
        / "related_link_field_definition.json",
        data,
    )

    schema_xml = data.get("SchemaXml")

    if schema_xml:
        save_text(
            OUTPUT_DIRECTORY
            / "related_link_field_schema.xml",
            str(schema_xml),
        )

    return data


# =============================================================================
# SESTAVENÍ REST DOTAZU
# =============================================================================

def build_items_url(
    current_user_id: int,
    filter_by_applicant: bool,
) -> str:
    select_fields = ",".join(
        (
            "Id",
            FIELD_TITLE,
            "Created",
            "Modified",
            FIELD_TYPE_OF_HOLIDAY,
            FIELD_PAID_HOLIDAY,
            FIELD_SPECIFY_OTHER,
            FIELD_VALID_SINCE,
            FIELD_VALID_TO,
            FIELD_WORKING_DAYS,
            FIELD_REQUEST_TYPE,
            FIELD_STATUS,
            FIELD_REQUEST_NUMBER,
            FIELD_RELATED_LINK,
            f"{FIELD_APPLICANT}/Id",
            f"{FIELD_APPLICANT}/Title",
            f"{FIELD_APPLICANT}/EMail",
            f"{FIELD_MANAGER}/Id",
            f"{FIELD_MANAGER}/Title",
            f"{FIELD_MANAGER}/EMail",
        )
    )

    expand_fields = ",".join(
        (
            FIELD_APPLICANT,
            FIELD_MANAGER,
        )
    )

    url = (
        f"{DMS_SITE}/_api/web/lists"
        f"(guid'{LIST_GUID}')"
        f"/items"
        f"?$select={select_fields}"
        f"&$expand={expand_fields}"
        f"&$orderby=Id desc"
        f"&$top={TOP_ITEMS}"
    )

    filters = [
        (
            f"{FIELD_TYPE_OF_HOLIDAY} "
            f"eq '{HOME_OFFICE_TYPE_OF_HOLIDAY}'"
        ),
        (
            f"{FIELD_PAID_HOLIDAY} "
            f"eq '{HOME_OFFICE_PAID_HOLIDAY}'"
        ),
    ]

    if filter_by_applicant:
        filters.append(
            f"{FIELD_APPLICANT}/Id eq {current_user_id}"
        )

    url += "&$filter=" + " and ".join(filters)

    return url


# =============================================================================
# NAČTENÍ POLOŽEK
# =============================================================================

def get_candidate_items(
    session: requests.Session,
    current_user_id: int,
) -> list[dict[str, Any]]:
    print_header(
        "NAČÍTÁNÍ KANDIDÁTNÍCH HOME OFFICE ŽÁDANEK"
    )

    filtered_url = build_items_url(
        current_user_id=current_user_id,
        filter_by_applicant=True,
    )

    try:
        data = get_json(
            session,
            filtered_url,
        )

        items = data["d"]["results"]

        print(
            "Použit filtr podle pole Žadatel "
            f"s ID {current_user_id}."
        )

        return items

    except requests.HTTPError as exception:
        print()
        print(
            "SharePoint nepřijal OData filtr podle "
            "uživatelského pole."
        )
        print(f"Detail: {exception}")
        print(
            "Provádím náhradní načtení položek "
            "bez filtru žadatele."
        )

    fallback_url = build_items_url(
        current_user_id=current_user_id,
        filter_by_applicant=False,
    )

    data = get_json(
        session,
        fallback_url,
    )

    all_items = data["d"]["results"]

    filtered_items = []

    for item in all_items:
        applicant = item.get(FIELD_APPLICANT)

        if (
            isinstance(applicant, dict)
            and applicant.get("Id") == current_user_id
        ):
            filtered_items.append(item)

    return filtered_items


# =============================================================================
# ANALÝZA HTML / TEXTU
# =============================================================================

def normalize_value(value: Any) -> str:
    if value is None:
        return ""

    return str(value)


def strip_html(value: str) -> str:
    text = re.sub(
        r"<br\s*/?>",
        "\n",
        value,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"</(?:p|div|tr|li|td|th)>",
        "\n",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"<[^>]+>",
        "",
        text,
    )

    text = html.unescape(text)

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    return "\n".join(lines)


def contains_home_office(value: Any) -> bool:
    text = normalize_value(value)
    plain_text = strip_html(text).casefold()

    variants = (
        "home office",
        "homeoffice",
        "home-office",
    )

    return any(
        variant in plain_text
        for variant in variants
    )


def detect_serialization(value: Any) -> str:
    text = normalize_value(value).strip()

    if not text:
        return "prázdná hodnota"

    if text.startswith("{") or text.startswith("["):
        try:
            json.loads(text)
            return "JSON"
        except json.JSONDecodeError:
            pass

    if re.search(
        r"<(?:table|tbody|tr|td|th)\b",
        text,
        flags=re.IGNORECASE,
    ):
        return "HTML tabulka"

    if text.startswith("<") and text.endswith(">"):
        return "HTML nebo XML"

    return "prostý text nebo vlastní serializace"


# =============================================================================
# VÝPIS POLOŽEK
# =============================================================================

def print_item(
    item: dict[str, Any],
) -> None:
    applicant = item.get(FIELD_APPLICANT)
    manager = item.get(FIELD_MANAGER)

    if not isinstance(applicant, dict):
        applicant = {}

    if not isinstance(manager, dict):
        manager = {}

    related_link = normalize_value(
        item.get(FIELD_RELATED_LINK)
    )

    print_separator()

    print(f"ID:                    {item.get('Id')}")
    print(
        f"Title:                 "
        f"{item.get(FIELD_TITLE)}"
    )
    print(f"Created:               {item.get('Created')}")
    print(f"Modified:              {item.get('Modified')}")

    print(
        f"Žadatel ID:            "
        f"{applicant.get('Id')}"
    )
    print(
        f"Žadatel:               "
        f"{applicant.get('Title')}"
    )
    print(
        f"Žadatel e-mail:        "
        f"{applicant.get('EMail')}"
    )

    print(
        f"Nadřízený ID:          "
        f"{manager.get('Id')}"
    )
    print(
        f"Nadřízený:             "
        f"{manager.get('Title')}"
    )

    print(
        f"Typ volna:             "
        f"{item.get(FIELD_TYPE_OF_HOLIDAY)}"
    )
    print(
        f"Placené volno:         "
        f"{item.get(FIELD_PAID_HOLIDAY)}"
    )
    print(
        f"Specifikujte:          "
        f"{item.get(FIELD_SPECIFY_OTHER)}"
    )
    print(
        f"Datum od:              "
        f"{item.get(FIELD_VALID_SINCE)}"
    )
    print(
        f"Datum do:              "
        f"{item.get(FIELD_VALID_TO)}"
    )
    print(
        f"Počet pracovních dní:  "
        f"{item.get(FIELD_WORKING_DAYS)}"
    )
    print(
        f"Typ žádanky:           "
        f"{item.get(FIELD_REQUEST_TYPE)}"
    )
    print(
        f"Stav:                  "
        f"{item.get(FIELD_STATUS)}"
    )
    print(
        f"Číslo žádanky:         "
        f"{item.get(FIELD_REQUEST_NUMBER)}"
    )

    print(
        f"Serializace odkazu:    "
        f"{detect_serialization(related_link)}"
    )

    print()
    print(
        f"{FIELD_RELATED_LINK}, běžný výpis:"
    )
    print(related_link or "<PRÁZDNÁ HODNOTA>")

    print()
    print(
        f"{FIELD_RELATED_LINK}, přesný repr:"
    )
    print(repr(related_link))

    print()
    print("Text po odstranění HTML:")
    print(
        strip_html(related_link)
        or "<PRÁZDNÁ HODNOTA>"
    )

    if contains_home_office(related_link):
        print()
        print(
            "*** TATO POLOŽKA OBSAHUJE TEXT HOME OFFICE ***"
        )


# =============================================================================
# EXPORT POLOŽEK
# =============================================================================

def export_item(
    item: dict[str, Any],
) -> None:
    item_id = item.get("Id")

    item_directory = (
        OUTPUT_DIRECTORY
        / f"item_{item_id}"
    )

    save_json(
        item_directory
        / "item.json",
        item,
    )

    related_link = normalize_value(
        item.get(FIELD_RELATED_LINK)
    )

    save_text(
        item_directory
        / "Rq_All_RelatedLink_raw.txt",
        related_link,
    )

    save_text(
        item_directory
        / "Rq_All_RelatedLink_repr.txt",
        repr(related_link),
    )

    save_text(
        item_directory
        / "Rq_All_RelatedLink_plain.txt",
        strip_html(related_link),
    )

    if (
        related_link
        and "<" in related_link
        and ">" in related_link
    ):
        save_text(
            item_directory
            / "Rq_All_RelatedLink_preview.html",
            related_link,
        )


# =============================================================================
# SOUHRN
# =============================================================================

def analyze_items(
    items: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    print_header("ANALÝZA POLOŽEK")

    matching_items = []

    for item in items:
        print_item(item)
        export_item(item)

        if contains_home_office(
            item.get(FIELD_RELATED_LINK)
        ):
            matching_items.append(item)

    print_header("SOUHRN")

    print(
        f"Kandidátní položky:              "
        f"{len(items)}"
    )

    print(
        f"Položky obsahující Home office:  "
        f"{len(matching_items)}"
    )

    save_json(
        OUTPUT_DIRECTORY
        / "candidate_items.json",
        items,
    )

    save_json(
        OUTPUT_DIRECTORY
        / "matching_homeoffice_items.json",
        matching_items,
    )

    return matching_items


# =============================================================================
# HLAVNÍ FUNKCE
# =============================================================================

def main() -> int:
    if not VERIFY_TLS:
        urllib3.disable_warnings(
            urllib3.exceptions.InsecureRequestWarning
        )

    OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    print_header(
        "DMS DIAGNOSTIKA HOME OFFICE REFERENCE"
    )

    print(f"DMS web:           {DMS_SITE}")
    print(f"Seznam GUID:       {LIST_GUID}")
    print(
        f"Typ volna:         "
        f"{HOME_OFFICE_TYPE_OF_HOLIDAY}"
    )
    print(
        f"Placené volno:     "
        f"{HOME_OFFICE_PAID_HOLIDAY}"
    )
    print(
        f"Hledaný popis:     "
        f"{HOME_OFFICE_DESCRIPTION}"
    )
    print(f"TLS ověřování:     {VERIFY_TLS}")
    print(f"Max. položek:      {TOP_ITEMS}")
    print(f"Výstupní složka:   {OUTPUT_DIRECTORY}")

    session = create_session()

    current_user = get_current_user(session)

    current_user_id = current_user.get("Id")

    if not isinstance(current_user_id, int):
        raise RuntimeError(
            "DMS nevrátil platné číselné ID "
            "aktuálního uživatele."
        )

    get_related_link_field_definition(session)

    items = get_candidate_items(
        session=session,
        current_user_id=current_user_id,
    )

    matching_items = analyze_items(items)

    print_header("VÝSLEDEK")

    if matching_items:
        print(
            "Byla nalezena existující žádanka, "
            "která odpovídá hodnotám:"
        )
        print(
            f"  {FIELD_TYPE_OF_HOLIDAY} = "
            f"{HOME_OFFICE_TYPE_OF_HOLIDAY}"
        )
        print(
            f"  {FIELD_PAID_HOLIDAY} = "
            f"{HOME_OFFICE_PAID_HOLIDAY}"
        )
        print(
            f"  {FIELD_RELATED_LINK} obsahuje "
            f"{HOME_OFFICE_DESCRIPTION}"
        )
        print()
        print(
            "Přesnou strukturu pole použijeme jako "
            "předlohu budoucího POST payloadu."
        )
    else:
        print(
            "Nebyla nalezena položka s textem "
            f"'{HOME_OFFICE_DESCRIPTION}' v poli "
            f"{FIELD_RELATED_LINK}."
        )
        print()
        print(
            "Zkontroluj soubory candidate_items.json "
            "a item_<ID>/Rq_All_RelatedLink_raw.txt."
        )
        print(
            "Pokud tabulka není uložena přímo v tomto poli, "
            "může být její obsah uložen v jiné související "
            "entitě nebo samostatném seznamu."
        )

    print()
    print(
        "Skript neprovádí POST a nijak nemění DMS."
    )

    print_header("HOTOVO")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())

    except requests.HTTPError as exception:
        print_header("HTTP CHYBA")

        response = exception.response

        if response is not None:
            print(f"Status: {response.status_code}")
            print(f"URL:    {response.url}")
            print()
            print("Odpověď serveru:")
            print(response.text[:20000])
        else:
            print(str(exception))

        raise SystemExit(1)

    except requests.RequestException as exception:
        print_header("CHYBA KOMUNIKACE S DMS")
        print(str(exception))
        raise SystemExit(1)

    except Exception as exception:
        print_header("NEOČEKÁVANÁ CHYBA")
        print(
            f"{type(exception).__name__}: "
            f"{exception}"
        )
        raise