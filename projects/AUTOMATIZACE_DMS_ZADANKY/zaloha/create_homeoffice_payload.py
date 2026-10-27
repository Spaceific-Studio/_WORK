from __future__ import annotations

import json
import re
import sys
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import requests
import urllib3
import win32com.client
from requests_negotiate_sspi import HttpNegotiateAuth


# =============================================================================
# KONFIGURACE OUTLOOKU
# =============================================================================

OUTLOOK_CATEGORY = "HOMEOFFICE"

# 9 = olFolderCalendar
OUTLOOK_CALENDAR_FOLDER_ID = 9

LOCAL_TIMEZONE = ZoneInfo("Europe/Prague")


# =============================================================================
# KONFIGURACE DMS
# =============================================================================

DMS_SITE = "https://dms.pvs.cz/sites/Zadanky"

DMS_LIST_GUID = "dc08c020-45ba-4cb5-9681-5ef919daa42b"

DMS_ENTITY_TYPE = "SP.Data.HolidayRequestItem"

# Dočasně False kvůli interní certifikační autoritě PVS.
# Pro produkční provoz použij cestu k firemnímu CA certifikátu.
VERIFY_TLS = False

# Kolik posledních žádanek se má prohledat při hledání
# aktuální schvalovací cesty.
APPROVER_LOOKUP_TOP_ITEMS = 100


# =============================================================================
# KONFIGURACE HOME OFFICE
# =============================================================================

TYPE_OF_HOLIDAY = "Placené volno"

PAID_HOLIDAY_TYPE = "Jiné"

REQUEST_TYPE = "Absence"

HOME_OFFICE_DESCRIPTION = "Home office"

VALID_TO_HALF_DAY = False

CLAIM_AND_REMAINS = "1"


# =============================================================================
# VÝSTUPNÍ SOUBORY
# =============================================================================

SCRIPT_DIRECTORY = Path(__file__).resolve().parent

OUTPUT_DIRECTORY = (
    SCRIPT_DIRECTORY
    / "generated_homeoffice_payloads"
)

SUMMARY_FILE = (
    OUTPUT_DIRECTORY
    / "homeoffice_payloads_current_week.json"
)

OUTLOOK_DIAGNOSTIC_FILE = (
    OUTPUT_DIRECTORY
    / "outlook_events_current_week.json"
)

DMS_REFERENCE_FILE = (
    OUTPUT_DIRECTORY
    / "dms_approver_reference.json"
)


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
# OBECNÉ POMOCNÉ FUNKCE
# =============================================================================

def safe_int(value: Any) -> int | None:
    if value is None:
        return None

    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def sanitize_filename(value: str) -> str:
    sanitized = re.sub(
        r'[<>:"/\\|?*]+',
        "_",
        value,
    )

    sanitized = re.sub(
        r"\s+",
        "_",
        sanitized,
    )

    sanitized = sanitized.strip("._")

    return sanitized[:80] or "homeoffice"


# =============================================================================
# DMS HTTP RELACE
# =============================================================================

def create_dms_session() -> requests.Session:
    session = requests.Session()

    # Použije přihlášení Windows procesu.
    session.auth = HttpNegotiateAuth()

    session.headers.update(
        {
            "Accept": "application/json;odata=verbose",
            "User-Agent": (
                "PVS-HomeOffice-Payload-Generator/2.0"
            ),
        }
    )

    return session


def dms_get_json(
    session: requests.Session,
    url: str,
) -> dict[str, Any]:
    response = session.get(
        url,
        verify=VERIFY_TLS,
        timeout=60,
    )

    print(
        f"DMS GET {response.status_code}: "
        f"{response.url}"
    )

    response.raise_for_status()

    return response.json()


# =============================================================================
# AKTUÁLNÍ DMS UŽIVATEL
# =============================================================================

def get_dms_current_user(
    session: requests.Session,
) -> dict[str, Any]:
    url = f"{DMS_SITE}/_api/web/currentuser"

    data = dms_get_json(
        session=session,
        url=url,
    )["d"]

    user_id = safe_int(data.get("Id"))

    if user_id is None:
        raise RuntimeError(
            "DMS nevrátil platné ID aktuálního uživatele."
        )

    print_header("AKTUÁLNÍ DMS UŽIVATEL")

    print(f"ID:       {user_id}")
    print(f"Jméno:    {data.get('Title')}")
    print(f"Login:    {data.get('LoginName')}")
    print(f"E-mail:   {data.get('Email')}")

    return data


# =============================================================================
# DYNAMICKÉ NAČTENÍ SCHVALOVATELŮ
# =============================================================================

def build_approver_reference_url(
    applicant_id: int,
) -> str:
    select_fields = ",".join(
        (
            "Id",
            "Title",
            "Created",
            "Modified",
            "ContentTypeId",
            "Rq_H_Department",
            "Rq_H_Approver1Id",
            "Rq_H_Approver2Id",
            "Rq_All_ApplicantId",
            "Rq_All_division",
            "Rq_H_TypeOfHoliday",
            "Rq_H_PaidHoliday",
            "Rq_All_StatusChoice",
            "Rq_H_Approver1/Id",
            "Rq_H_Approver1/Title",
            "Rq_H_Approver1/EMail",
            "Rq_H_Approver2/Id",
            "Rq_H_Approver2/Title",
            "Rq_H_Approver2/EMail",
        )
    )

    expand_fields = ",".join(
        (
            "Rq_H_Approver1",
            "Rq_H_Approver2",
        )
    )

    # Filtrujeme pouze žádosti aktuálního žadatele.
    # Neomezujeme typ volna, protože schvalovací cesta je
    # zpravidla organizační údaj, nikoliv vlastnost Home Office.
    filter_expression = (
        f"Rq_All_ApplicantId eq {applicant_id} "
        f"and Rq_H_Approver1Id ne null "
        f"and Rq_H_Approver2Id ne null"
    )

    return (
        f"{DMS_SITE}/_api/web/lists"
        f"(guid'{DMS_LIST_GUID}')"
        f"/items"
        f"?$select={select_fields}"
        f"&$expand={expand_fields}"
        f"&$filter={filter_expression}"
        f"&$orderby=Id desc"
        f"&$top={APPROVER_LOOKUP_TOP_ITEMS}"
    )


def get_approver_reference(
    session: requests.Session,
    applicant_id: int,
) -> dict[str, Any]:
    """
    Najde nejnovější existující žádanku aktuálního uživatele,
    která má vyplněného schvalovatele 1 i schvalovatele 2.

    Funkce provádí pouze GET.
    """

    print_header(
        "DYNAMICKÉ NAČTENÍ SCHVALOVATELŮ Z DMS"
    )

    url = build_approver_reference_url(
        applicant_id=applicant_id,
    )

    data = dms_get_json(
        session=session,
        url=url,
    )

    items = data["d"].get(
        "results",
        [],
    )

    if not items:
        raise RuntimeError(
            "DMS nevrátil žádnou existující žádost "
            "aktuálního uživatele s vyplněnými poli "
            "Rq_H_Approver1Id a Rq_H_Approver2Id."
        )

    for item in items:
        approver_1_id = safe_int(
            item.get("Rq_H_Approver1Id")
        )

        approver_2_id = safe_int(
            item.get("Rq_H_Approver2Id")
        )

        if (
            approver_1_id is None
            or approver_2_id is None
        ):
            continue

        reference = {
            "source_item_id": item.get("Id"),
            "source_item_title": item.get("Title"),
            "source_item_created": item.get("Created"),
            "source_item_modified": item.get("Modified"),
            "source_item_status": (
                item.get("Rq_All_StatusChoice")
            ),
            "source_item_type_of_holiday": (
                item.get("Rq_H_TypeOfHoliday")
            ),
            "source_content_type_id": (
                item.get("ContentTypeId")
            ),
            "applicant_id": applicant_id,
            "department": (
                item.get("Rq_H_Department")
            ),
            "division": (
                item.get("Rq_All_division")
            ),
            "approver_1_id": approver_1_id,
            "approver_1": (
                item.get("Rq_H_Approver1")
            ),
            "approver_2_id": approver_2_id,
            "approver_2": (
                item.get("Rq_H_Approver2")
            ),
            "loaded_by_get_only": True,
        }

        print(
            "Referenční žádost ID: "
            f"{reference['source_item_id']}"
        )

        print(
            "Referenční žádost:    "
            f"{reference['source_item_title']}"
        )

        print(
            "Oddělení:             "
            f"{reference['department']}"
        )

        print(
            "Divize:               "
            f"{reference['division']}"
        )

        print(
            "Schvalovatel 1 ID:    "
            f"{reference['approver_1_id']}"
        )

        approver_1 = reference.get("approver_1")

        if isinstance(approver_1, dict):
            print(
                "Schvalovatel 1:       "
                f"{approver_1.get('Title')}"
            )

        print(
            "Schvalovatel 2 ID:    "
            f"{reference['approver_2_id']}"
        )

        approver_2 = reference.get("approver_2")

        if isinstance(approver_2, dict):
            print(
                "Schvalovatel 2:       "
                f"{approver_2.get('Title')}"
            )

        save_json(
            DMS_REFERENCE_FILE,
            reference,
        )

        return reference

    raise RuntimeError(
        "V načtených žádostech nebyla nalezena "
        "použitelná dvojice schvalovatelů."
    )


# =============================================================================
# AKTUÁLNÍ TÝDEN
# =============================================================================

def get_current_week_range() -> tuple[datetime, datetime]:
    now = datetime.now()

    monday = now - timedelta(
        days=now.weekday()
    )

    monday = monday.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    next_monday = monday + timedelta(days=7)

    return monday, next_monday


# =============================================================================
# OUTLOOK
# =============================================================================

def get_outlook_calendar():
    outlook = win32com.client.Dispatch(
        "Outlook.Application"
    )

    namespace = outlook.GetNamespace("MAPI")

    return namespace.GetDefaultFolder(
        OUTLOOK_CALENDAR_FOLDER_ID
    )


def build_outlook_restriction(
    start: datetime,
    end: datetime,
) -> str:
    start_text = start.strftime(
        "%m/%d/%Y %I:%M %p"
    )

    end_text = end.strftime(
        "%m/%d/%Y %I:%M %p"
    )

    return (
        f"[Start] >= '{start_text}' "
        f"AND [Start] < '{end_text}'"
    )


def parse_categories(
    categories_value: Any,
) -> list[str]:
    if categories_value is None:
        return []

    raw_value = str(
        categories_value
    ).strip()

    if not raw_value:
        return []

    categories = re.split(
        r"\s*[;,]\s*",
        raw_value,
    )

    return [
        category.strip()
        for category in categories
        if category.strip()
    ]


def contains_homeoffice_category(
    categories: list[str],
) -> bool:
    expected = OUTLOOK_CATEGORY.casefold()

    return any(
        category.casefold() == expected
        for category in categories
    )


def safe_get_property(
    outlook_item: Any,
    property_name: str,
    default: Any = None,
) -> Any:
    try:
        return getattr(
            outlook_item,
            property_name,
        )
    except Exception:
        return default


def outlook_datetime_to_python(
    value: Any,
) -> datetime:
    return datetime(
        year=value.year,
        month=value.month,
        day=value.day,
        hour=value.hour,
        minute=value.minute,
        second=value.second,
        microsecond=getattr(
            value,
            "microsecond",
            0,
        ),
    )


def load_current_week_events() -> list[dict[str, Any]]:
    calendar = get_outlook_calendar()

    items = calendar.Items

    items.Sort("[Start]")

    items.IncludeRecurrences = True

    week_start, week_end = get_current_week_range()

    restriction = build_outlook_restriction(
        start=week_start,
        end=week_end,
    )

    print_header("OUTLOOK FILTR")

    print(f"Kalendář:   {calendar.Name}")
    print(f"Od:         {week_start}")
    print(f"Do:         {week_end}")
    print(f"Filtr:      {restriction}")
    print(f"Kategorie:  {OUTLOOK_CATEGORY}")

    restricted_items = items.Restrict(
        restriction
    )

    events: list[dict[str, Any]] = []

    for outlook_item in restricted_items:
        try:
            subject = str(
                safe_get_property(
                    outlook_item,
                    "Subject",
                    "",
                )
                or ""
            )

            categories = parse_categories(
                safe_get_property(
                    outlook_item,
                    "Categories",
                    "",
                )
            )

            start_value = safe_get_property(
                outlook_item,
                "Start",
            )

            end_value = safe_get_property(
                outlook_item,
                "End",
            )

            if (
                start_value is None
                or end_value is None
            ):
                continue

            start_datetime = (
                outlook_datetime_to_python(
                    start_value
                )
            )

            end_datetime = (
                outlook_datetime_to_python(
                    end_value
                )
            )

            events.append(
                {
                    "subject": subject,
                    "start": start_datetime,
                    "end": end_datetime,
                    "all_day": bool(
                        safe_get_property(
                            outlook_item,
                            "AllDayEvent",
                            False,
                        )
                    ),
                    "categories": categories,
                    "is_recurring": bool(
                        safe_get_property(
                            outlook_item,
                            "IsRecurring",
                            False,
                        )
                    ),
                    "entry_id": str(
                        safe_get_property(
                            outlook_item,
                            "EntryID",
                            "",
                        )
                        or ""
                    ),
                    "global_appointment_id": str(
                        safe_get_property(
                            outlook_item,
                            "GlobalAppointmentID",
                            "",
                        )
                        or ""
                    ),
                }
            )

        except Exception as exception:
            print(
                "Položku Outlooku se nepodařilo načíst: "
                f"{type(exception).__name__}: "
                f"{exception}"
            )

    return events


def filter_homeoffice_events(
    events: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    return [
        event
        for event in events
        if contains_homeoffice_category(
            event["categories"]
        )
    ]


# =============================================================================
# DATUM ŽÁDANKY
# =============================================================================

def get_request_dates(
    event: dict[str, Any],
) -> tuple[date, date]:
    start_datetime: datetime = event["start"]
    end_datetime: datetime = event["end"]

    start_date = start_datetime.date()

    if event["all_day"]:
        end_date = (
            end_datetime - timedelta(days=1)
        ).date()
    else:
        end_date = end_datetime.date()

    if end_date < start_date:
        end_date = start_date

    return start_date, end_date


def count_working_days(
    start_date: date,
    end_date: date,
) -> int:
    result = 0

    current_date = start_date

    while current_date <= end_date:
        if current_date.weekday() < 5:
            result += 1

        current_date += timedelta(days=1)

    return result


def local_date_to_sharepoint_utc(
    local_date: date,
) -> str:
    local_datetime = datetime.combine(
        local_date,
        time.min,
        tzinfo=LOCAL_TIMEZONE,
    )

    utc_datetime = local_datetime.astimezone(
        timezone.utc
    )

    return (
        utc_datetime
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


# =============================================================================
# SOUVISEJÍCÍ ODKAZ
# =============================================================================

def build_related_link_value() -> str:
    return json.dumps(
        [
            {
                "Cells": [
                    "",
                    HOME_OFFICE_DESCRIPTION,
                ]
            }
        ],
        ensure_ascii=False,
        separators=(",", ":"),
    )


# =============================================================================
# PAYLOAD
# =============================================================================

def build_payload(
    event: dict[str, Any],
    applicant_id: int,
    approver_reference: dict[str, Any],
) -> dict[str, Any]:
    start_date, end_date = get_request_dates(
        event
    )

    start_utc = local_date_to_sharepoint_utc(
        start_date
    )

    end_utc = local_date_to_sharepoint_utc(
        end_date
    )

    approver_1_id = safe_int(
        approver_reference.get(
            "approver_1_id"
        )
    )

    approver_2_id = safe_int(
        approver_reference.get(
            "approver_2_id"
        )
    )

    if (
        approver_1_id is None
        or approver_2_id is None
    ):
        raise RuntimeError(
            "Referenční žádost neobsahuje platná "
            "ID obou schvalovatelů."
        )

    department = approver_reference.get(
        "department"
    )

    payload: dict[str, Any] = {
        "__metadata": {
            "type": DMS_ENTITY_TYPE,
        },

        "Rq_All_type": REQUEST_TYPE,

        "Rq_All_ApplicantId": applicant_id,

        "Rq_H_TypeOfHoliday": (
            TYPE_OF_HOLIDAY
        ),

        "Rq_H_PaidHoliday": (
            PAID_HOLIDAY_TYPE
        ),

        "Rq_All_RelatedLink": (
            build_related_link_value()
        ),

        "Rq_H_ValidSince": start_utc,
        "Rq_H_ValidTo": end_utc,

        "Rq_H_ValidToHalfDay": (
            VALID_TO_HALF_DAY
        ),

        "Rq_H_WorkingDay": (
            count_working_days(
                start_date,
                end_date,
            )
        ),

        "Rq_All_StartDate": start_utc,
        "Rq_All_EndDate": end_utc,

        "Rq_H_Approver1Id": (
            approver_1_id
        ),

        "Rq_H_Approver2Id": (
            approver_2_id
        ),

        "Rq_All_ApproversId": {
            "results": [
                approver_1_id,
                approver_2_id,
            ]
        },

        "Rq_H_ClaimAndRemains": (
            CLAIM_AND_REMAINS
        ),
    }

    if department:
        payload["Rq_H_Department"] = (
            department
        )

    division = approver_reference.get(
        "division"
    )

    if division:
        payload["Rq_All_division"] = (
            division
        )

    return payload


def build_payload_record(
    event: dict[str, Any],
    applicant_id: int,
    approver_reference: dict[str, Any],
) -> dict[str, Any]:
    start_date, end_date = get_request_dates(
        event
    )

    return {
        "source_outlook_event": {
            "subject": event["subject"],
            "start": event["start"].isoformat(),
            "end": event["end"].isoformat(),
            "all_day": event["all_day"],
            "categories": event["categories"],
            "is_recurring": event["is_recurring"],
            "entry_id": event["entry_id"],
            "global_appointment_id": (
                event["global_appointment_id"]
            ),
        },

        "approver_source": {
            "source_item_id": (
                approver_reference.get(
                    "source_item_id"
                )
            ),
            "source_item_title": (
                approver_reference.get(
                    "source_item_title"
                )
            ),
            "approver_1_id": (
                approver_reference.get(
                    "approver_1_id"
                )
            ),
            "approver_1": (
                approver_reference.get(
                    "approver_1"
                )
            ),
            "approver_2_id": (
                approver_reference.get(
                    "approver_2_id"
                )
            ),
            "approver_2": (
                approver_reference.get(
                    "approver_2"
                )
            ),
        },

        "calculated_values": {
            "request_start_date": (
                start_date.isoformat()
            ),
            "request_end_date": (
                end_date.isoformat()
            ),
            "working_days": (
                count_working_days(
                    start_date,
                    end_date,
                )
            ),
        },

        "target": {
            "site": DMS_SITE,
            "list_guid": DMS_LIST_GUID,
            "intended_method": "POST",
            "post_was_executed": False,
        },

        "payload": build_payload(
            event=event,
            applicant_id=applicant_id,
            approver_reference=(
                approver_reference
            ),
        ),
    }


# =============================================================================
# DIAGNOSTIKA OUTLOOKU
# =============================================================================

def serialize_event(
    event: dict[str, Any],
) -> dict[str, Any]:
    return {
        "subject": event["subject"],
        "start": event["start"].isoformat(),
        "end": event["end"].isoformat(),
        "all_day": event["all_day"],
        "categories": event["categories"],
        "is_recurring": event["is_recurring"],
        "entry_id": event["entry_id"],
        "global_appointment_id": (
            event["global_appointment_id"]
        ),
        "is_homeoffice": (
            contains_homeoffice_category(
                event["categories"]
            )
        ),
    }


def build_event_output_filename(
    event: dict[str, Any],
    index: int,
) -> str:
    start_date, _ = get_request_dates(event)

    subject = sanitize_filename(
        event["subject"]
    )

    return (
        f"{index:02d}_"
        f"{start_date.isoformat()}_"
        f"{subject}_payload.json"
    )


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
        "GENERÁTOR HOME OFFICE PAYLOADŮ"
    )

    print(
        "BEZPEČNÝ REŽIM: skript provádí pouze "
        "GET z DMS a čtení z Outlooku."
    )

    print(
        "Neobsahuje POST, PATCH, MERGE ani DELETE."
    )

    dms_session = create_dms_session()

    current_user = get_dms_current_user(
        session=dms_session,
    )

    applicant_id = safe_int(
        current_user.get("Id")
    )

    if applicant_id is None:
        raise RuntimeError(
            "Nelze zjistit ID žadatele."
        )

    approver_reference = get_approver_reference(
        session=dms_session,
        applicant_id=applicant_id,
    )

    all_events = load_current_week_events()

    save_json(
        OUTLOOK_DIAGNOSTIC_FILE,
        {
            "generated_at": (
                datetime.now().isoformat()
            ),
            "category": OUTLOOK_CATEGORY,
            "events": [
                serialize_event(event)
                for event in all_events
            ],
        },
    )

    homeoffice_events = filter_homeoffice_events(
        all_events
    )

    print_header("OUTLOOK VÝSLEDEK")

    print(
        f"Všechny události: "
        f"{len(all_events)}"
    )

    print(
        f"Home Office události: "
        f"{len(homeoffice_events)}"
    )

    payload_records: list[
        dict[str, Any]
    ] = []

    for index, event in enumerate(
        homeoffice_events,
        start=1,
    ):
        record = build_payload_record(
            event=event,
            applicant_id=applicant_id,
            approver_reference=(
                approver_reference
            ),
        )

        payload_records.append(record)

        output_file = (
            OUTPUT_DIRECTORY
            / build_event_output_filename(
                event=event,
                index=index,
            )
        )

        save_json(
            output_file,
            record,
        )

        print_separator()

        print(f"Událost: {event['subject']}")
        print(f"Začátek: {event['start']}")
        print(f"Konec:   {event['end']}")
        print()
        print("Payload:")

        print(
            json.dumps(
                record["payload"],
                indent=2,
                ensure_ascii=False,
            )
        )

    summary = {
        "generated_at": (
            datetime.now().isoformat()
        ),
        "post_was_executed": False,
        "applicant": {
            "id": applicant_id,
            "title": current_user.get("Title"),
            "login": current_user.get(
                "LoginName"
            ),
            "email": current_user.get(
                "Email"
            ),
        },
        "approver_reference": (
            approver_reference
        ),
        "payload_count": len(
            payload_records
        ),
        "items": payload_records,
    }

    save_json(
        SUMMARY_FILE,
        summary,
    )

    print_header("SOUHRN")

    print(
        f"Referenční žádost ID: "
        f"{approver_reference.get('source_item_id')}"
    )

    print(
        f"Schvalovatel 1 ID: "
        f"{approver_reference.get('approver_1_id')}"
    )

    print(
        f"Schvalovatel 2 ID: "
        f"{approver_reference.get('approver_2_id')}"
    )

    print(
        f"Vygenerováno payloadů: "
        f"{len(payload_records)}"
    )

    print()
    print(
        "NIC NEBYLO ODESLÁNO DO DMS."
    )

    print_header("HOTOVO")

    return 0


# =============================================================================
# SPUŠTĚNÍ
# =============================================================================

if __name__ == "__main__":
    try:
        raise SystemExit(main())

    except requests.HTTPError as exception:
        print_header("HTTP CHYBA DMS")

        response = exception.response

        if response is not None:
            print(
                f"Status: "
                f"{response.status_code}"
            )
            print(f"URL: {response.url}")
            print()
            print(response.text[:20000])
        else:
            print(str(exception))

        raise SystemExit(1)

    except Exception as exception:
        print_header("CHYBA")

        print(
            f"{type(exception).__name__}: "
            f"{exception}"
        )

        raise