from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote
from zoneinfo import ZoneInfo

import requests
import urllib3
import win32com.client
from requests_negotiate_sspi import HttpNegotiateAuth


# =============================================================================
# KONFIGURACE OUTLOOKU
# =============================================================================

OUTLOOK_CATEGORY = "HOMEOFFICE"
OUTLOOK_CALENDAR_FOLDER_ID = 9  # olFolderCalendar
LOCAL_TIMEZONE = ZoneInfo("Europe/Prague")


# =============================================================================
# KONFIGURACE DMS
# =============================================================================

DMS_SITE = "https://dms.pvs.cz/sites/Zadanky"
DMS_LIST_GUID = "dc08c020-45ba-4cb5-9681-5ef919daa42b"
DMS_ENTITY_TYPE = "SP.Data.HolidayRequestItem"
VERIFY_TLS = False
APPROVER_LOOKUP_TOP_ITEMS = 100

# Bezpečnostní pojistka. Skript nesmí obsahovat odeslání POSTu.
ALLOW_POST = False


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
OUTPUT_DIRECTORY = SCRIPT_DIRECTORY / "generated_homeoffice_post_requests"
SUMMARY_FILE = OUTPUT_DIRECTORY / "post_requests_current_week.json"
OUTLOOK_DIAGNOSTIC_FILE = OUTPUT_DIRECTORY / "outlook_events_current_week.json"
DMS_REFERENCE_FILE = OUTPUT_DIRECTORY / "dms_approver_reference.json"


# =============================================================================
# VÝPIS A SOUBORY
# =============================================================================


def print_header(title: str) -> None:
    print()
    print("=" * 100)
    print(title)
    print("=" * 100)


def print_separator() -> None:
    print()
    print("-" * 100)


def save_json(file_path: Path, content: Any) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(
        json.dumps(content, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    print(f"Uloženo: {file_path}")


def save_text(file_path: Path, content: str) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")
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
    sanitized = re.sub(r'[<>:"/\\|?*]+', "_", value)
    sanitized = re.sub(r"\s+", "_", sanitized).strip("._")
    return sanitized[:80] or "homeoffice"


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


# =============================================================================
# DMS HTTP RELACE A GET VOLÁNÍ
# =============================================================================


def create_dms_session() -> requests.Session:
    session = requests.Session()
    session.auth = HttpNegotiateAuth()
    session.headers.update(
        {
            "Accept": "application/json;odata=verbose",
            "User-Agent": "PVS-HomeOffice-POST-Preview/1.0",
        }
    )
    return session


def dms_get_json(session: requests.Session, url: str) -> dict[str, Any]:
    response = session.get(url, verify=VERIFY_TLS, timeout=60)
    print(f"DMS GET {response.status_code}: {response.url}")
    response.raise_for_status()
    return response.json()


def get_dms_current_user(session: requests.Session) -> dict[str, Any]:
    data = dms_get_json(session, f"{DMS_SITE}/_api/web/currentuser")["d"]
    if safe_int(data.get("Id")) is None:
        raise RuntimeError("DMS nevrátil platné ID aktuálního uživatele.")

    print_header("AKTUÁLNÍ DMS UŽIVATEL")
    print(f"ID:      {data.get('Id')}")
    print(f"Jméno:   {data.get('Title')}")
    print(f"Login:   {data.get('LoginName')}")
    print(f"E-mail:  {data.get('Email')}")
    return data


def get_request_digest(session: requests.Session) -> dict[str, Any]:
    """
    Získá FormDigestValue pomocí POST na /_api/contextinfo.

    Toto volání nevytváří ani nemění položku seznamu. Vrací pouze kontextový
    token potřebný pro budoucí zápis. Token je dočasný a jeho platnost je
    uvedena v FormDigestTimeoutSeconds.
    """
    url = f"{DMS_SITE}/_api/contextinfo"
    response = session.post(
        url,
        headers={
            "Accept": "application/json;odata=verbose",
            "Content-Type": "application/json;odata=verbose",
        },
        data="",
        verify=VERIFY_TLS,
        timeout=60,
    )
    print(f"DMS CONTEXTINFO {response.status_code}: {response.url}")
    response.raise_for_status()

    info = response.json()["d"]["GetContextWebInformation"]
    digest = info["FormDigestValue"]
    timeout_seconds = info.get("FormDigestTimeoutSeconds")

    return {
        "value": digest,
        "timeout_seconds": timeout_seconds,
        "sha256": sha256_text(digest),
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
    }


# =============================================================================
# DYNAMICKÉ NAČTENÍ SCHVALOVATELŮ
# =============================================================================


def build_approver_reference_urls(applicant_id: int) -> list[str]:
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
    expand_fields = "Rq_H_Approver1,Rq_H_Approver2"

    base = (
        f"{DMS_SITE}/_api/web/lists(guid'{DMS_LIST_GUID}')/items"
        f"?$select={select_fields}"
        f"&$expand={expand_fields}"
        f"&$orderby=Id desc"
        f"&$top={APPROVER_LOOKUP_TOP_ITEMS}"
    )

    # První dotaz je přesnější. Druhý je fallback pro prostředí, kde OData
    # nepřijme porovnání User lookup pole s null.
    filtered = (
        base
        + "&$filter="
        + quote(
            f"Rq_All_ApplicantId eq {applicant_id} "
            f"and Rq_H_Approver1Id ne null "
            f"and Rq_H_Approver2Id ne null",
            safe=" ='",
        )
    )
    fallback = (
        base
        + "&$filter="
        + quote(f"Rq_All_ApplicantId eq {applicant_id}", safe=" ='")
    )
    return [filtered, fallback]


def get_approver_reference(
    session: requests.Session,
    applicant_id: int,
) -> dict[str, Any]:
    print_header("DYNAMICKÉ NAČTENÍ SCHVALOVATELŮ")

    items: list[dict[str, Any]] = []
    last_error: Exception | None = None

    for url in build_approver_reference_urls(applicant_id):
        try:
            items = dms_get_json(session, url)["d"].get("results", [])
            if items:
                break
        except requests.HTTPError as exc:
            last_error = exc
            print(f"Dotaz na referenční žádost selhal, zkouším fallback: {exc}")

    if not items and last_error is not None:
        raise RuntimeError(
            "DMS nevrátil referenční žádost se schvalovateli."
        ) from last_error

    for item in items:
        approver_1_id = safe_int(item.get("Rq_H_Approver1Id"))
        approver_2_id = safe_int(item.get("Rq_H_Approver2Id"))
        if approver_1_id is None or approver_2_id is None:
            continue

        reference = {
            "source_item_id": item.get("Id"),
            "source_item_title": item.get("Title"),
            "source_item_created": item.get("Created"),
            "source_item_modified": item.get("Modified"),
            "source_item_status": item.get("Rq_All_StatusChoice"),
            "source_content_type_id": item.get("ContentTypeId"),
            "applicant_id": applicant_id,
            "department": item.get("Rq_H_Department"),
            "division": item.get("Rq_All_division"),
            "approver_1_id": approver_1_id,
            "approver_1": item.get("Rq_H_Approver1"),
            "approver_2_id": approver_2_id,
            "approver_2": item.get("Rq_H_Approver2"),
            "loaded_by_get_only": True,
        }
        save_json(DMS_REFERENCE_FILE, reference)
        print(f"Referenční žádost ID: {reference['source_item_id']}")
        print(f"Schvalovatel 1 ID:    {approver_1_id}")
        print(f"Schvalovatel 2 ID:    {approver_2_id}")
        return reference

    raise RuntimeError(
        "V posledních žádostech nebyla nalezena použitelná dvojice schvalovatelů."
    )


# =============================================================================
# OUTLOOK A AKTUÁLNÍ TÝDEN
# =============================================================================


def get_current_week_range() -> tuple[datetime, datetime]:
    now = datetime.now()
    monday = (now - timedelta(days=now.weekday())).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    return monday, monday + timedelta(days=7)


def get_outlook_calendar():
    outlook = win32com.client.Dispatch("Outlook.Application")
    namespace = outlook.GetNamespace("MAPI")
    return namespace.GetDefaultFolder(OUTLOOK_CALENDAR_FOLDER_ID)


def build_outlook_restriction(start: datetime, end: datetime) -> str:
    start_text = start.strftime("%m/%d/%Y %I:%M %p")
    end_text = end.strftime("%m/%d/%Y %I:%M %p")
    return f"[Start] >= '{start_text}' AND [Start] < '{end_text}'"


def parse_categories(categories_value: Any) -> list[str]:
    if categories_value is None:
        return []
    raw = str(categories_value).strip()
    if not raw:
        return []
    return [x.strip() for x in re.split(r"\s*[;,]\s*", raw) if x.strip()]


def contains_homeoffice_category(categories: list[str]) -> bool:
    expected = OUTLOOK_CATEGORY.casefold()
    return any(category.casefold() == expected for category in categories)


def safe_get_property(item: Any, name: str, default: Any = None) -> Any:
    try:
        return getattr(item, name)
    except Exception:
        return default


def outlook_datetime_to_python(value: Any) -> datetime:
    return datetime(
        value.year,
        value.month,
        value.day,
        value.hour,
        value.minute,
        value.second,
        getattr(value, "microsecond", 0),
    )


def load_current_week_events() -> list[dict[str, Any]]:
    calendar = get_outlook_calendar()
    items = calendar.Items
    items.Sort("[Start]")
    items.IncludeRecurrences = True

    week_start, week_end = get_current_week_range()
    restriction = build_outlook_restriction(week_start, week_end)

    print_header("OUTLOOK FILTR")
    print(f"Kalendář:   {calendar.Name}")
    print(f"Od:         {week_start}")
    print(f"Do:         {week_end}")
    print(f"Filtr:      {restriction}")
    print(f"Kategorie:  {OUTLOOK_CATEGORY}")

    events: list[dict[str, Any]] = []
    for item in items.Restrict(restriction):
        try:
            start_value = safe_get_property(item, "Start")
            end_value = safe_get_property(item, "End")
            if start_value is None or end_value is None:
                continue

            events.append(
                {
                    "subject": str(safe_get_property(item, "Subject", "") or ""),
                    "start": outlook_datetime_to_python(start_value),
                    "end": outlook_datetime_to_python(end_value),
                    "all_day": bool(safe_get_property(item, "AllDayEvent", False)),
                    "categories": parse_categories(
                        safe_get_property(item, "Categories", "")
                    ),
                    "is_recurring": bool(
                        safe_get_property(item, "IsRecurring", False)
                    ),
                    "entry_id": str(safe_get_property(item, "EntryID", "") or ""),
                    "global_appointment_id": str(
                        safe_get_property(item, "GlobalAppointmentID", "") or ""
                    ),
                }
            )
        except Exception as exc:
            print(f"Přeskakuji nečitelnou položku Outlooku: {exc}")

    return events


def filter_homeoffice_events(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        event
        for event in events
        if contains_homeoffice_category(event["categories"])
    ]


# =============================================================================
# DATUM A PAYLOAD
# =============================================================================


def get_request_dates(event: dict[str, Any]) -> tuple[date, date]:
    start_date = event["start"].date()
    if event["all_day"]:
        end_date = (event["end"] - timedelta(days=1)).date()
    else:
        end_date = event["end"].date()
    return start_date, max(start_date, end_date)


def count_working_days(start_date: date, end_date: date) -> int:
    result = 0
    current = start_date
    while current <= end_date:
        if current.weekday() < 5:
            result += 1
        current += timedelta(days=1)
    return result


def local_date_to_sharepoint_utc(local_date: date) -> str:
    local_dt = datetime.combine(local_date, time.min, tzinfo=LOCAL_TIMEZONE)
    utc_dt = local_dt.astimezone(timezone.utc)
    return utc_dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_related_link_value() -> str:
    return json.dumps(
        [{"Cells": ["", HOME_OFFICE_DESCRIPTION]}],
        ensure_ascii=False,
        separators=(",", ":"),
    )


def build_payload(
    event: dict[str, Any],
    applicant_id: int,
    approver_reference: dict[str, Any],
) -> dict[str, Any]:
    start_date, end_date = get_request_dates(event)
    start_utc = local_date_to_sharepoint_utc(start_date)
    end_utc = local_date_to_sharepoint_utc(end_date)

    approver_1_id = safe_int(approver_reference.get("approver_1_id"))
    approver_2_id = safe_int(approver_reference.get("approver_2_id"))
    if approver_1_id is None or approver_2_id is None:
        raise RuntimeError("Referenční žádost nemá platná ID schvalovatelů.")

    payload: dict[str, Any] = {
        "__metadata": {"type": DMS_ENTITY_TYPE},
        "Rq_All_type": REQUEST_TYPE,
        "Rq_All_ApplicantId": applicant_id,
        "Rq_H_TypeOfHoliday": TYPE_OF_HOLIDAY,
        "Rq_H_PaidHoliday": PAID_HOLIDAY_TYPE,
        "Rq_All_RelatedLink": build_related_link_value(),
        "Rq_H_ValidSince": start_utc,
        "Rq_H_ValidTo": end_utc,
        "Rq_H_ValidToHalfDay": VALID_TO_HALF_DAY,
        "Rq_H_WorkingDay": count_working_days(start_date, end_date),
        "Rq_All_StartDate": start_utc,
        "Rq_All_EndDate": end_utc,
        "Rq_H_Approver1Id": approver_1_id,
        "Rq_H_Approver2Id": approver_2_id,
        "Rq_All_ApproversId": {"results": [approver_1_id, approver_2_id]},
        "Rq_H_ClaimAndRemains": CLAIM_AND_REMAINS,
    }

    if approver_reference.get("department"):
        payload["Rq_H_Department"] = approver_reference["department"]
    if approver_reference.get("division"):
        payload["Rq_All_division"] = approver_reference["division"]

    return payload


# =============================================================================
# PŘÍPRAVA POST REQUESTU, BEZ ODESLÁNÍ
# =============================================================================


def build_post_url() -> str:
    return (
        f"{DMS_SITE}/_api/web/lists"
        f"(guid'{DMS_LIST_GUID}')/items"
    )


def prepare_post_request(
    session: requests.Session,
    payload: dict[str, Any],
    digest: str,
) -> requests.PreparedRequest:
    """
    Připraví přesnou podobu budoucího POST requestu.

    Metoda session.prepare_request() pouze serializuje URL, hlavičky a body.
    Síťové odeslání by vyžadovalo session.send(prepared), které v tomto
    skriptu záměrně nikde není.
    """
    if ALLOW_POST:
        raise RuntimeError(
            "Bezpečnostní pojistka: ALLOW_POST musí zůstat False."
        )

    request = requests.Request(
        method="POST",
        url=build_post_url(),
        headers={
            "Accept": "application/json;odata=verbose",
            "Content-Type": "application/json;odata=verbose",
            "X-RequestDigest": digest,
        },
        json=payload,
    )
    return session.prepare_request(request)


def prepared_request_to_record(
    prepared: requests.PreparedRequest,
    event: dict[str, Any],
    digest_info: dict[str, Any],
    payload: dict[str, Any],
    approver_reference: dict[str, Any],
) -> dict[str, Any]:
    body = prepared.body
    if isinstance(body, bytes):
        body_text = body.decode("utf-8")
    elif body is None:
        body_text = ""
    else:
        body_text = str(body)

    # Authorization zde nebude přítomna. U HttpNegotiateAuth vzniká až během
    # skutečné challenge-response komunikace se serverem, která se nyní nekoná.
    headers = dict(prepared.headers)

    return {
        "safety": {
            "post_was_executed": False,
            "prepared_only": True,
            "allow_post": ALLOW_POST,
            "send_called": False,
        },
        "source_outlook_event": {
            "subject": event["subject"],
            "start": event["start"].isoformat(),
            "end": event["end"].isoformat(),
            "all_day": event["all_day"],
            "categories": event["categories"],
            "is_recurring": event["is_recurring"],
            "entry_id": event["entry_id"],
            "global_appointment_id": event["global_appointment_id"],
        },
        "approver_source": approver_reference,
        "context_info": {
            "digest_retrieved_at": digest_info["retrieved_at"],
            "digest_timeout_seconds": digest_info["timeout_seconds"],
            "digest_sha256": digest_info["sha256"],
            "note": (
                "X-RequestDigest je dočasný. Pro skutečný POST se musí načíst "
                "nový těsně před odesláním."
            ),
        },
        "request": {
            "method": prepared.method,
            "url": prepared.url,
            "headers": headers,
            "body_text": body_text,
            "body_json": payload,
        },
        "authentication_note": (
            "Hlavička Authorization není součástí připraveného souboru. "
            "Windows Negotiate/NTLM ji vytváří až při skutečné výměně "
            "challenge-response v requests-negotiate-sspi."
        ),
    }


def build_raw_http_preview(record: dict[str, Any]) -> str:
    request_data = record["request"]
    url = request_data["url"]
    from urllib.parse import urlsplit

    parsed = urlsplit(url)
    target = parsed.path
    if parsed.query:
        target += "?" + parsed.query

    lines = [f"{request_data['method']} {target} HTTP/1.1"]
    lines.append(f"Host: {parsed.netloc}")

    for key, value in request_data["headers"].items():
        if key.lower() == "host":
            continue
        lines.append(f"{key}: {value}")

    lines.append("")
    lines.append(request_data["body_text"])
    return "\r\n".join(lines)


# =============================================================================
# VÝSTUPNÍ NÁZVY A DIAGNOSTIKA
# =============================================================================


def build_event_base_name(event: dict[str, Any], index: int) -> str:
    start_date, _ = get_request_dates(event)
    return (
        f"{index:02d}_{start_date.isoformat()}_"
        f"{sanitize_filename(event['subject'])}"
    )


def serialize_event(event: dict[str, Any]) -> dict[str, Any]:
    return {
        "subject": event["subject"],
        "start": event["start"].isoformat(),
        "end": event["end"].isoformat(),
        "all_day": event["all_day"],
        "categories": event["categories"],
        "is_recurring": event["is_recurring"],
        "entry_id": event["entry_id"],
        "global_appointment_id": event["global_appointment_id"],
        "is_homeoffice": contains_homeoffice_category(event["categories"]),
    }


# =============================================================================
# HLAVNÍ FUNKCE
# =============================================================================


def main() -> int:
    if not VERIFY_TLS:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    if ALLOW_POST:
        raise RuntimeError("ALLOW_POST musí být False.")

    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)

    print_header("PŘÍPRAVA POST REQUESTŮ HOME OFFICE, BEZ ODESLÁNÍ")
    print("Skript provádí čtení Outlooku, GET z DMS a POST pouze na /_api/contextinfo.")
    print("Nevytváří položku a nikde nevolá session.send() ani POST na /items.")

    dms_session = create_dms_session()
    current_user = get_dms_current_user(dms_session)
    applicant_id = safe_int(current_user.get("Id"))
    if applicant_id is None:
        raise RuntimeError("Nelze zjistit ID žadatele.")

    approver_reference = get_approver_reference(
        dms_session,
        applicant_id,
    )

    # Token se načte pouze pro věrnou reprezentaci budoucích hlaviček.
    digest_info = get_request_digest(dms_session)
    print_header("REQUEST DIGEST")
    print(f"Platnost v sekundách: {digest_info['timeout_seconds']}")
    print(f"SHA-256:             {digest_info['sha256']}")

    all_events = load_current_week_events()
    save_json(
        OUTLOOK_DIAGNOSTIC_FILE,
        {
            "generated_at": datetime.now().isoformat(),
            "category": OUTLOOK_CATEGORY,
            "events": [serialize_event(event) for event in all_events],
        },
    )

    homeoffice_events = filter_homeoffice_events(all_events)
    print_header("OUTLOOK VÝSLEDEK")
    print(f"Všechny události:     {len(all_events)}")
    print(f"Home Office události: {len(homeoffice_events)}")

    records: list[dict[str, Any]] = []

    for index, event in enumerate(homeoffice_events, start=1):
        payload = build_payload(event, applicant_id, approver_reference)
        prepared = prepare_post_request(
            dms_session,
            payload,
            digest_info["value"],
        )
        record = prepared_request_to_record(
            prepared,
            event,
            digest_info,
            payload,
            approver_reference,
        )
        records.append(record)

        base_name = build_event_base_name(event, index)
        json_file = OUTPUT_DIRECTORY / f"{base_name}_post_request.json"
        raw_file = OUTPUT_DIRECTORY / f"{base_name}_post_request.http.txt"
        body_file = OUTPUT_DIRECTORY / f"{base_name}_body.json"

        save_json(json_file, record)
        save_text(raw_file, build_raw_http_preview(record))
        save_json(body_file, payload)

        print_separator()
        print(f"Událost: {event['subject']}")
        print(f"POST URL: {prepared.url}")
        print(f"Body SHA-256: {sha256_text(record['request']['body_text'])}")
        print("POST nebyl odeslán.")

    summary = {
        "generated_at": datetime.now().isoformat(),
        "post_was_executed": False,
        "prepared_only": True,
        "applicant": {
            "id": applicant_id,
            "title": current_user.get("Title"),
            "login": current_user.get("LoginName"),
            "email": current_user.get("Email"),
        },
        "approver_reference": approver_reference,
        "context_info": {
            "digest_retrieved_at": digest_info["retrieved_at"],
            "digest_timeout_seconds": digest_info["timeout_seconds"],
            "digest_sha256": digest_info["sha256"],
        },
        "request_count": len(records),
        "requests": records,
    }
    save_json(SUMMARY_FILE, summary)

    print_header("SOUHRN")
    print(f"Připraveno POST requestů: {len(records)}")
    print(f"Výstupní složka:         {OUTPUT_DIRECTORY}")
    print("NIC NEBYLO ODESLÁNO DO SEZNAMU DMS.")
    return 0


# =============================================================================
# SPUŠTĚNÍ
# =============================================================================


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except requests.HTTPError as exc:
        print_header("HTTP CHYBA DMS")
        response = exc.response
        if response is not None:
            print(f"Status: {response.status_code}")
            print(f"URL:    {response.url}")
            print(response.text[:20000])
        else:
            print(str(exc))
        raise SystemExit(1)
    except Exception as exc:
        print_header("CHYBA")
        print(f"{type(exc).__name__}: {exc}")
        raise
