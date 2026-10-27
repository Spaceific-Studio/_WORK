from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import quote

import requests
import urllib3

# Soubor musí být ve stejné složce jako create_homeoffice_payload.py.
import create_homeoffice_payload as base


# =============================================================================
# KONFIGURACE
# =============================================================================

# Automaticky vybere chronologicky první HOMEOFFICE událost,
# pro kterou ještě v DMS neexistuje odpovídající žádost.
AUTO_SELECT_FIRST_UNSENT = True

# Použije se pouze při AUTO_SELECT_FIRST_UNSENT = False.
TARGET_EVENT_DATE = "2026-09-04"

# Při automatickém výběru ignoruje události před dnešním dnem.
SKIP_PAST_EVENTS = True

# False = pouze náhled. True = skutečný POST jedné položky.
SEND_TO_DMS = False

# Druhá nezávislá pojistka. Pro ostrý POST musí být přesně uvedený text.
CONFIRMATION_TEXT = "NEODESILAT"
EXPECTED_CONFIRMATION = "ODESLAT_JEDNU_HOME_OFFICE_ZADOST"

# Při nalezení duplicity se žádost nikdy nevytvoří.
BLOCK_IF_DUPLICATE_EXISTS = True

# Po úspěšném POSTu načte vytvořenou položku kontrolním GETem.
VERIFY_CREATED_ITEM = True

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
OUTPUT_DIRECTORY = SCRIPT_DIRECTORY / "test_single_homeoffice_post"
PREVIEW_FILE = OUTPUT_DIRECTORY / "selected_event_post_preview.json"
RAW_HTTP_FILE = OUTPUT_DIRECTORY / "selected_event_post_preview.http.txt"
SELECTION_FILE = OUTPUT_DIRECTORY / "automatic_selection_diagnostics.json"
RESPONSE_FILE = OUTPUT_DIRECTORY / "post_response.json"
VERIFICATION_FILE = OUTPUT_DIRECTORY / "created_item_verification.json"


# =============================================================================
# SOUBORY A DATUM
# =============================================================================


def save_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    print(f"Uloženo: {path.resolve()}")


def save_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")
    print(f"Uloženo: {path.resolve()}")


def parse_target_date(value: str):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError("TARGET_EVENT_DATE musí mít formát YYYY-MM-DD.") from exc


# =============================================================================
# DUPLICITY V DMS
# =============================================================================


def build_duplicate_check_url(
    applicant_id: int,
    payload: dict[str, Any],
) -> str:
    filter_expression = (
        f"Rq_All_ApplicantId eq {applicant_id} "
        f"and Rq_H_ValidSince eq datetime'{payload['Rq_H_ValidSince']}' "
        f"and Rq_H_ValidTo eq datetime'{payload['Rq_H_ValidTo']}' "
        f"and Rq_H_TypeOfHoliday eq '{base.TYPE_OF_HOLIDAY}' "
        f"and Rq_H_PaidHoliday eq '{base.PAID_HOLIDAY_TYPE}'"
    )

    select_fields = ",".join(
        (
            "Id",
            "Title",
            "Created",
            "Rq_H_ValidSince",
            "Rq_H_ValidTo",
            "Rq_H_TypeOfHoliday",
            "Rq_H_PaidHoliday",
            "Rq_All_RelatedLink",
            "Rq_All_StatusChoice",
        )
    )

    encoded_filter = quote(filter_expression, safe=" ='")

    return (
        f"{base.DMS_SITE}/_api/web/lists"
        f"(guid'{base.DMS_LIST_GUID}')/items"
        f"?$select={select_fields}"
        f"&$filter={encoded_filter}"
        f"&$top=10"
    )


def find_existing_duplicates(
    session: requests.Session,
    applicant_id: int,
    payload: dict[str, Any],
) -> list[dict[str, Any]]:
    url = build_duplicate_check_url(applicant_id, payload)
    response = session.get(
        url,
        verify=base.VERIFY_TLS,
        timeout=60,
    )
    print(f"DMS DUPLICATE CHECK {response.status_code}: {response.url}")
    response.raise_for_status()

    items = response.json()["d"].get("results", [])

    return [
        item
        for item in items
        if "home office" in str(item.get("Rq_All_RelatedLink", "")).casefold()
    ]


# =============================================================================
# VÝBĚR UDÁLOSTI
# =============================================================================


def select_event_by_date(
    events: list[dict[str, Any]],
    target_date,
) -> dict[str, Any]:
    matches = []

    for event in events:
        start_date, end_date = base.get_request_dates(event)
        if start_date <= target_date <= end_date:
            matches.append(event)

    if len(matches) != 1:
        raise RuntimeError(
            f"Pro datum {target_date.isoformat()} musí existovat přesně jedna "
            f"HOMEOFFICE událost. Nalezeno: {len(matches)}."
        )

    return matches[0]


def select_first_unsent_event(
    session: requests.Session,
    events: list[dict[str, Any]],
    applicant_id: int,
    approver_reference: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    """Vrátí první budoucí/dnešní HOMEOFFICE událost bez duplicity v DMS."""
    today = datetime.now().date()
    diagnostics: list[dict[str, Any]] = []

    for event in sorted(events, key=lambda item: item["start"]):
        start_date, end_date = base.get_request_dates(event)

        if SKIP_PAST_EVENTS and end_date < today:
            diagnostics.append(
                {
                    "subject": event["subject"],
                    "start": event["start"].isoformat(),
                    "end": event["end"].isoformat(),
                    "result": "skipped_past_event",
                    "duplicate_count": None,
                }
            )
            continue

        payload = base.build_payload(
            event=event,
            applicant_id=applicant_id,
            approver_reference=approver_reference,
        )

        duplicates = find_existing_duplicates(
            session=session,
            applicant_id=applicant_id,
            payload=payload,
        )

        diagnostic = {
            "subject": event["subject"],
            "start": event["start"].isoformat(),
            "end": event["end"].isoformat(),
            "request_start_date": start_date.isoformat(),
            "request_end_date": end_date.isoformat(),
            "result": "duplicate_exists" if duplicates else "selected_first_unsent",
            "duplicate_count": len(duplicates),
            "duplicate_item_ids": [item.get("Id") for item in duplicates],
        }
        diagnostics.append(diagnostic)

        if duplicates:
            print(
                f"Kontrola {start_date.isoformat()}: duplicita, "
                f"DMS ID {diagnostic['duplicate_item_ids']}"
            )
            continue

        print(
            f"Kontrola {start_date.isoformat()}: bez duplicity, "
            "událost byla vybrána."
        )
        return event, payload, diagnostics

    save_json(SELECTION_FILE, diagnostics)
    raise RuntimeError(
        "V prohledávaném Outlook období nebyla nalezena žádná neodeslaná "
        "HOMEOFFICE událost. Pokud je další událost za horní hranicí, zvětši "
        "rozsah v get_current_week_range() v create_homeoffice_payload.py."
    )


# =============================================================================
# POST A KONTROLNÍ GET
# =============================================================================


def create_item(
    session: requests.Session,
    payload: dict[str, Any],
    request_digest: str,
) -> requests.Response:
    response = session.post(
        base.build_post_url(),
        headers={
            "Accept": "application/json;odata=verbose",
            "Content-Type": "application/json;odata=verbose",
            "X-RequestDigest": request_digest,
        },
        json=payload,
        verify=base.VERIFY_TLS,
        timeout=60,
    )
    print(f"DMS CREATE ITEM {response.status_code}: {response.url}")
    return response


def get_created_item(
    session: requests.Session,
    item_id: int,
) -> dict[str, Any]:
    url = (
        f"{base.DMS_SITE}/_api/web/lists"
        f"(guid'{base.DMS_LIST_GUID}')/items({item_id})"
    )
    response = session.get(
        url,
        headers={"Accept": "application/json;odata=verbose"},
        verify=base.VERIFY_TLS,
        timeout=60,
    )
    print(f"DMS VERIFY ITEM {response.status_code}: {response.url}")
    response.raise_for_status()
    return response.json()["d"]


# =============================================================================
# MAIN
# =============================================================================


def main() -> int:
    if not base.VERIFY_TLS:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)

    base.print_header("TEST ODESLÁNÍ JEDNÉ HOME OFFICE UDÁLOSTI")
    print(f"Automatický výběr první neodeslané: {AUTO_SELECT_FIRST_UNSENT}")
    print(f"Přeskakovat minulé události: {SKIP_PAST_EVENTS}")
    print(f"SEND_TO_DMS: {SEND_TO_DMS}")
    print("Režim: " + ("OSTRÝ POST JEDNÉ POLOŽKY" if SEND_TO_DMS else "POUZE NÁHLED"))

    session = base.create_dms_session()
    current_user = base.get_dms_current_user(session)
    applicant_id = base.safe_int(current_user.get("Id"))

    if applicant_id is None:
        raise RuntimeError("Nelze zjistit ID aktuálního žadatele v DMS.")

    approver_reference = base.get_approver_reference(
        session=session,
        applicant_id=applicant_id,
    )

    homeoffice_events = base.load_current_week_events()

    if not homeoffice_events:
        raise RuntimeError(
            f"V Outlook období nebyla nalezena žádná událost {base.OUTLOOK_CATEGORY}."
        )

    if AUTO_SELECT_FIRST_UNSENT:
        selected_event, payload, selection_diagnostics = select_first_unsent_event(
            session=session,
            events=homeoffice_events,
            applicant_id=applicant_id,
            approver_reference=approver_reference,
        )
    else:
        target_date = parse_target_date(TARGET_EVENT_DATE)
        selected_event = select_event_by_date(homeoffice_events, target_date)
        payload = base.build_payload(
            event=selected_event,
            applicant_id=applicant_id,
            approver_reference=approver_reference,
        )
        selection_diagnostics = [
            {
                "result": "selected_by_explicit_date",
                "target_date": target_date.isoformat(),
            }
        ]

    selected_start_date, _ = base.get_request_dates(selected_event)

    # Náhled používá aktuální digest. Pro ostrý POST se níže načte nový.
    digest_info = base.get_request_digest(session)
    prepared = base.prepare_post_request(
        session=session,
        payload=payload,
        request_digest=digest_info["value"],
    )

    preview = {
        "safety": {
            "selection_mode": "first_unsent" if AUTO_SELECT_FIRST_UNSENT else "explicit_date",
            "selected_event_date": selected_start_date.isoformat(),
            "send_to_dms": SEND_TO_DMS,
            "confirmation_matches": CONFIRMATION_TEXT == EXPECTED_CONFIRMATION,
            "maximum_items_to_create": 1,
        },
        "selected_outlook_event": base.serialize_event(selected_event),
        "selection_diagnostics": selection_diagnostics,
        "approver_reference": approver_reference,
        "request": base.prepared_request_as_json(
            prepared=prepared,
            payload=payload,
            digest_info=digest_info,
        ),
    }

    save_json(PREVIEW_FILE, preview)
    save_json(SELECTION_FILE, selection_diagnostics)
    save_text(RAW_HTTP_FILE, base.build_raw_http_preview(prepared))

    base.print_header("AUTOMATICKY VYBRANÁ UDÁLOST")
    print(json.dumps(preview["selected_outlook_event"], indent=2, ensure_ascii=False))

    base.print_header("PAYLOAD")
    print(json.dumps(payload, indent=2, ensure_ascii=False))

    # Druhá kontrola duplicity těsně před rozhodnutím o POSTu.
    final_duplicates = find_existing_duplicates(session, applicant_id, payload)

    base.print_header("FINÁLNÍ KONTROLA DUPLICITY")
    print(f"Nalezeno odpovídajících položek v DMS: {len(final_duplicates)}")

    if final_duplicates and BLOCK_IF_DUPLICATE_EXISTS:
        print(json.dumps(final_duplicates, indent=2, ensure_ascii=False, default=str))
        print("POST zablokován, protože odpovídající žádost již existuje.")
        return 2

    if not SEND_TO_DMS:
        base.print_header("NÁHLED DOKONČEN")
        print("Nic nebylo odesláno do DMS.")
        print("Pro ostrý test nastav:")
        print("SEND_TO_DMS = True")
        print(f'CONFIRMATION_TEXT = "{EXPECTED_CONFIRMATION}"')
        return 0

    if CONFIRMATION_TEXT != EXPECTED_CONFIRMATION:
        raise RuntimeError(
            "Ostrý POST je zablokovaný. CONFIRMATION_TEXT nemá požadovanou hodnotu."
        )

    # Čerstvý digest bezprostředně před jediným POSTem na /items.
    fresh_digest = base.get_request_digest(session)

    base.print_header("ODESÍLÁM JEDNU POLOŽKU DO DMS")
    response = create_item(session, payload, fresh_digest["value"])

    response_record: dict[str, Any] = {
        "status_code": response.status_code,
        "reason": response.reason,
        "url": response.url,
        "headers": dict(response.headers),
        "body_text": response.text,
    }

    try:
        response_record["body_json"] = response.json()
    except ValueError:
        response_record["body_json"] = None

    save_json(RESPONSE_FILE, response_record)
    response.raise_for_status()

    response_json = response.json()
    created_data = response_json.get("d", response_json)
    created_item_id = base.safe_int(created_data.get("Id"))

    base.print_header("VÝSLEDEK POSTU")
    print(f"HTTP status: {response.status_code} {response.reason}")
    print(f"Nové Item ID: {created_item_id}")

    if VERIFY_CREATED_ITEM and created_item_id is not None:
        created_item = get_created_item(session, created_item_id)
        save_json(VERIFICATION_FILE, created_item)
        print("Kontrolní GET nové položky proběhl úspěšně.")

    print("Byla vytvořena právě jedna položka DMS.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except requests.HTTPError as exception:
        base.print_header("HTTP CHYBA DMS")
        response = exception.response
        if response is not None:
            print(f"Status: {response.status_code} {response.reason}")
            print(f"URL: {response.url}")
            print(response.text[:20000])
        else:
            print(str(exception))
        raise SystemExit(1)
    except Exception as exception:
        base.print_header("CHYBA")
        print(f"{type(exception).__name__}: {exception}")
        raise
