from __future__ import annotations

import json
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any
from urllib.parse import quote

import requests
import urllib3

# Tento soubor musí být uložen ve stejné složce jako:
# create_homeoffice_payload.py
import create_homeoffice_payload as base


# =============================================================================
# KONFIGURACE TESTU
# =============================================================================

# Vyber přesně jeden den Home Office z Outlooku ve formátu YYYY-MM-DD.
# Podle posledního testu jsou dostupné například 2026-09-02 a 2026-09-04.
TARGET_EVENT_DATE = "2026-09-04"

# False = pouze náhled, nic se nevytvoří.
# True  = povolí skutečný POST, ale jen pokud současně sedí CONFIRMATION_TEXT.
SEND_TO_DMS = False

# Druhá nezávislá pojistka proti nechtěnému odeslání.
# Pro ostrý test musí být přesně:
# CONFIRMATION_TEXT = "ODESLAT_JEDNU_HOME_OFFICE_ZADOST"
CONFIRMATION_TEXT = "NEODESILAT"

# Pokud už DMS obsahuje žádost stejného žadatele pro stejný den,
# skript ostrý POST zablokuje.
BLOCK_IF_DUPLICATE_EXISTS = True

# Po úspěšném vytvoření provede kontrolní GET nové položky.
VERIFY_CREATED_ITEM = True

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
OUTPUT_DIRECTORY = SCRIPT_DIRECTORY / "test_single_homeoffice_post"
PREVIEW_FILE = OUTPUT_DIRECTORY / "selected_event_post_preview.json"
RAW_HTTP_FILE = OUTPUT_DIRECTORY / "selected_event_post_preview.http.txt"
RESPONSE_FILE = OUTPUT_DIRECTORY / "post_response.json"
VERIFICATION_FILE = OUTPUT_DIRECTORY / "created_item_verification.json"

EXPECTED_CONFIRMATION = "ODESLAT_JEDNU_HOME_OFFICE_ZADOST"


# =============================================================================
# POMOCNÉ FUNKCE
# =============================================================================


def parse_target_date(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exception:
        raise ValueError(
            "TARGET_EVENT_DATE musí mít formát YYYY-MM-DD, například 2026-09-04."
        ) from exception


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


def select_one_event(
    events: list[dict[str, Any]],
    target_date: date,
) -> dict[str, Any]:
    matches = []

    for event in events:
        start_date, end_date = base.get_request_dates(event)

        if start_date <= target_date <= end_date:
            matches.append(event)

    if not matches:
        available = sorted(
            {
                base.get_request_dates(event)[0].isoformat()
                for event in events
            }
        )
        raise RuntimeError(
            f"Pro datum {target_date.isoformat()} nebyla nalezena událost "
            f"s kategorií {base.OUTLOOK_CATEGORY}. Dostupná data: {available}"
        )

    if len(matches) > 1:
        details = [
            {
                "subject": event["subject"],
                "start": event["start"].isoformat(),
                "end": event["end"].isoformat(),
            }
            for event in matches
        ]
        raise RuntimeError(
            "Pro vybraný den bylo nalezeno více HOMEOFFICE událostí. "
            "Skript z důvodu bezpečnosti nic neodešle. Nálezy: "
            + json.dumps(details, ensure_ascii=False)
        )

    return matches[0]


def build_duplicate_check_url(
    applicant_id: int,
    payload: dict[str, Any],
) -> str:
    start_utc = payload["Rq_H_ValidSince"]
    end_utc = payload["Rq_H_ValidTo"]

    filter_expression = (
        f"Rq_All_ApplicantId eq {applicant_id} "
        f"and Rq_H_ValidSince eq datetime'{start_utc}' "
        f"and Rq_H_ValidTo eq datetime'{end_utc}' "
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

    return (
        f"{base.DMS_SITE}/_api/web/lists"
        f"(guid'{base.DMS_LIST_GUID}')/items"
        f"?$select={select_fields}"
        f"&$filter={quote(filter_expression, safe=chr(32) + chr(61) + chr(39))}"
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

    # Rozlišení Home Office podle serializovaného pole souvisejícího odkazu.
    return [
        item
        for item in items
        if "home office" in str(item.get("Rq_All_RelatedLink", "")).casefold()
    ]


def create_item(
    session: requests.Session,
    payload: dict[str, Any],
    request_digest: str,
) -> requests.Response:
    url = base.build_post_url()

    response = session.post(
        url,
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
# HLAVNÍ FUNKCE
# =============================================================================


def main() -> int:
    if not base.VERIFY_TLS:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    target_date = parse_target_date(TARGET_EVENT_DATE)

    base.print_header("TEST ODESLÁNÍ JEDNÉ HOME OFFICE UDÁLOSTI")
    print(f"Cílové datum: {target_date.isoformat()}")
    print(f"SEND_TO_DMS: {SEND_TO_DMS}")
    print(
        "Režim: "
        + ("OSTRÝ POST JEDNÉ POLOŽKY" if SEND_TO_DMS else "POUZE NÁHLED")
    )

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
    selected_event = select_one_event(homeoffice_events, target_date)

    payload = base.build_payload(
        event=selected_event,
        applicant_id=applicant_id,
        approver_reference=approver_reference,
    )

    # Digest načítáme co nejblíže případnému odeslání.
    digest_info = base.get_request_digest(session)
    prepared = base.prepare_post_request(
        session=session,
        payload=payload,
        request_digest=digest_info["value"],
    )

    preview = {
        "safety": {
            "target_event_date": target_date.isoformat(),
            "send_to_dms": SEND_TO_DMS,
            "confirmation_matches": CONFIRMATION_TEXT == EXPECTED_CONFIRMATION,
            "maximum_items_to_create": 1,
        },
        "selected_outlook_event": base.serialize_event(selected_event),
        "approver_reference": approver_reference,
        "request": base.prepared_request_as_json(
            prepared=prepared,
            payload=payload,
            digest_info=digest_info,
        ),
    }

    save_json(PREVIEW_FILE, preview)
    save_text(RAW_HTTP_FILE, base.build_raw_http_preview(prepared))

    base.print_header("VYBRANÁ UDÁLOST")
    print(json.dumps(preview["selected_outlook_event"], indent=2, ensure_ascii=False))

    base.print_header("PAYLOAD")
    print(json.dumps(payload, indent=2, ensure_ascii=False))

    duplicates = find_existing_duplicates(session, applicant_id, payload)

    base.print_header("KONTROLA DUPLICITY")
    print(f"Nalezeno odpovídajících položek v DMS: {len(duplicates)}")

    if duplicates:
        print(json.dumps(duplicates, indent=2, ensure_ascii=False, default=str))
        if BLOCK_IF_DUPLICATE_EXISTS:
            print("POST zablokován, protože odpovídající žádost již existuje.")
            return 2

    if not SEND_TO_DMS:
        base.print_header("NÁHLED DOKONČEN")
        print("Nic nebylo odesláno do DMS.")
        print(f"Pro skutečný test nastav SEND_TO_DMS = True a")
        print(f'CONFIRMATION_TEXT = "{EXPECTED_CONFIRMATION}"')
        return 0

    if CONFIRMATION_TEXT != EXPECTED_CONFIRMATION:
        raise RuntimeError(
            "Ostrý POST je zablokovaný. CONFIRMATION_TEXT neodpovídá "
            "požadované bezpečnostní hodnotě."
        )

    # Získáme čerstvý digest bezprostředně před skutečným POSTem.
    fresh_digest = base.get_request_digest(session)

    base.print_header("ODESÍLÁM JEDNU POLOŽKU DO DMS")
    response = create_item(
        session=session,
        payload=payload,
        request_digest=fresh_digest["value"],
    )

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

    print()
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
