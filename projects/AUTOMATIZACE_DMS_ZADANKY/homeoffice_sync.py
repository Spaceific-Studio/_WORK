from __future__ import annotations

import json
import logging
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import msal
import requests
from requests_negotiate_sspi import HttpNegotiateAuth


BASE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = BASE_DIR / "config.json"


def load_config() -> dict:
    with CONFIG_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


CONFIG = load_config()

DMS_SITE = CONFIG["dms"]["site_url"].rstrip("/")
DMS_LIST_GUID = CONFIG["dms"]["list_guid"]
VERIFY_TLS = CONFIG["dms"].get("verify_tls", True)

TIMEZONE = ZoneInfo(CONFIG["runtime"]["timezone"])
DRY_RUN = CONFIG["runtime"].get("dry_run", True)
DATABASE_PATH = Path(CONFIG["runtime"]["database"])
LOG_FILE = Path(CONFIG["runtime"]["log_file"])


def configure_logging() -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


def create_database() -> None:
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS processed_events (
                event_key TEXT PRIMARY KEY,
                graph_event_id TEXT NOT NULL,
                event_subject TEXT,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                dms_item_id INTEGER,
                status TEXT NOT NULL,
                processed_at TEXT NOT NULL
            )
            """
        )
        connection.commit()


def already_processed(event_key: str) -> bool:
    with sqlite3.connect(DATABASE_PATH) as connection:
        row = connection.execute(
            """
            SELECT 1
            FROM processed_events
            WHERE event_key = ?
              AND status = 'created'
            """,
            (event_key,),
        ).fetchone()

    return row is not None


def save_result(
    event_key: str,
    graph_event_id: str,
    subject: str,
    start_date: str,
    end_date: str,
    status: str,
    dms_item_id: int | None = None,
) -> None:
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            INSERT INTO processed_events (
                event_key,
                graph_event_id,
                event_subject,
                start_date,
                end_date,
                dms_item_id,
                status,
                processed_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(event_key) DO UPDATE SET
                graph_event_id = excluded.graph_event_id,
                event_subject = excluded.event_subject,
                start_date = excluded.start_date,
                end_date = excluded.end_date,
                dms_item_id = excluded.dms_item_id,
                status = excluded.status,
                processed_at = excluded.processed_at
            """,
            (
                event_key,
                graph_event_id,
                subject,
                start_date,
                end_date,
                dms_item_id,
                status,
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        connection.commit()


def create_dms_session() -> requests.Session:
    session = requests.Session()

    # Použije přihlašovací kontext Windows procesu.
    session.auth = HttpNegotiateAuth()

    session.headers.update(
        {
            "Accept": "application/json;odata=verbose",
            "User-Agent": "PVS-HomeOffice-Automation/1.0",
        }
    )

    return session


def check_dms_current_user(session: requests.Session) -> dict:
    url = f"{DMS_SITE}/_api/web/currentuser"

    response = session.get(
        url,
        timeout=30,
        verify=VERIFY_TLS,
    )
    response.raise_for_status()

    data = response.json()
    user = data["d"]

    logging.info(
        "DMS přihlášení OK: %s, ID=%s",
        user.get("LoginName"),
        user.get("Id"),
    )

    return user


def get_dms_list_metadata(session: requests.Session) -> dict:
    url = (
        f"{DMS_SITE}/_api/web/lists"
        f"(guid'{DMS_LIST_GUID}')"
        f"?$select=Id,Title,ListItemEntityTypeFullName"
    )

    response = session.get(
        url,
        timeout=30,
        verify=VERIFY_TLS,
    )
    response.raise_for_status()

    metadata = response.json()["d"]

    logging.info(
        "DMS seznam: %s, typ entity: %s",
        metadata.get("Title"),
        metadata.get("ListItemEntityTypeFullName"),
    )

    return metadata


def get_dms_fields(session: requests.Session) -> list[dict]:
    url = (
        f"{DMS_SITE}/_api/web/lists"
        f"(guid'{DMS_LIST_GUID}')/fields"
        f"?$select=Title,InternalName,TypeAsString,Required,ReadOnlyField,Hidden"
    )

    response = session.get(
        url,
        timeout=30,
        verify=VERIFY_TLS,
    )
    response.raise_for_status()

    fields = response.json()["d"]["results"]

    relevant_fields = [
        field
        for field in fields
        if not field.get("Hidden")
        and (
            field.get("Required")
            or field.get("InternalName", "").startswith("Rq_")
        )
    ]

    for field in relevant_fields:
        logging.info(
            "Pole DMS: %-35s | %-35s | typ=%-15s | required=%s | readonly=%s",
            field.get("Title"),
            field.get("InternalName"),
            field.get("TypeAsString"),
            field.get("Required"),
            field.get("ReadOnlyField"),
        )

    return fields


def get_request_digest(session: requests.Session) -> str:
    url = f"{DMS_SITE}/_api/contextinfo"

    response = session.post(
        url,
        headers={
            "Accept": "application/json;odata=verbose",
            "Content-Type": "application/json;odata=verbose",
        },
        timeout=30,
        verify=VERIFY_TLS,
    )
    response.raise_for_status()

    return response.json()["d"]["GetContextWebInformation"]["FormDigestValue"]


def get_graph_access_token() -> str:
    outlook = CONFIG["outlook"]

    private_key = Path(outlook["private_key_path"]).read_text(
        encoding="utf-8"
    )

    application = msal.ConfidentialClientApplication(
        client_id=outlook["client_id"],
        authority=f"https://login.microsoftonline.com/{outlook['tenant_id']}",
        client_credential={
            "private_key": private_key,
            "thumbprint": outlook["certificate_thumbprint"],
        },
    )

    result = application.acquire_token_for_client(
        scopes=["https://graph.microsoft.com/.default"]
    )

    access_token = result.get("access_token")

    if not access_token:
        raise RuntimeError(
            "Nepodařilo se získat Graph token: "
            + json.dumps(result, ensure_ascii=False)
        )

    return access_token


def get_week_interval() -> tuple[datetime, datetime]:
    now = datetime.now(TIMEZONE)

    monday = now - timedelta(days=now.weekday())
    start = monday.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=7)

    return start, end


def get_homeoffice_events(access_token: str) -> list[dict]:
    outlook = CONFIG["outlook"]
    start, end = get_week_interval()

    mailbox = outlook["mailbox"]

    url = (
        f"https://graph.microsoft.com/v1.0/users/{mailbox}/calendarView"
    )

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "Prefer": f'outlook.timezone="{CONFIG["runtime"]["timezone"]}"',
    }

    params = {
        "startDateTime": start.isoformat(),
        "endDateTime": end.isoformat(),
        "$select": (
            "id,subject,start,end,categories,isCancelled,"
            "isAllDay,lastModifiedDateTime"
        ),
        "$orderby": "start/dateTime",
        "$top": "100",
    }

    events = []

    while url:
        response = requests.get(
            url,
            headers=headers,
            params=params if not events else None,
            timeout=30,
        )
        response.raise_for_status()

        data = response.json()
        events.extend(data.get("value", []))
        url = data.get("@odata.nextLink")

    required_category = outlook["category"].casefold()

    return [
        event
        for event in events
        if not event.get("isCancelled", False)
        and any(
            category.casefold() == required_category
            for category in event.get("categories", [])
        )
    ]


def build_event_key(event: dict) -> str:
    start = event["start"]["dateTime"]
    end = event["end"]["dateTime"]

    return f"{event['id']}|{start}|{end}"


def prepare_request(event: dict, current_user: dict) -> dict:
    """
    Toto mapování je pouze návrh.
    Interní názvy a datové typy musí být ověřeny z /fields
    a jednou ručně vytvořenou žádostí.
    """

    return {
        "event_id": event["id"],
        "subject": event.get("subject", ""),
        "start": event["start"]["dateTime"],
        "end": event["end"]["dateTime"],
        "applicant_id": current_user.get("Id"),
    }


def create_dms_request(
    session: requests.Session,
    list_entity_type: str,
    request_data: dict,
) -> int:
    if DRY_RUN:
        logging.info(
            "DRY-RUN: žádanka nebude vytvořena: %s",
            json.dumps(request_data, ensure_ascii=False),
        )
        return 0

    raise RuntimeError(
        "Ostrý zápis je zablokován. "
        "Nejdříve je nutné ověřit mapování polí a spuštění workflow."
    )


def main() -> int:
    configure_logging()
    create_database()

    logging.info("Zahájena synchronizace Home Office.")
    logging.info("Režim nanečisto: %s", DRY_RUN)

    dms_session = create_dms_session()

    current_user = check_dms_current_user(dms_session)
    list_metadata = get_dms_list_metadata(dms_session)
    get_dms_fields(dms_session)

    digest = get_request_digest(dms_session)
    logging.info("RequestDigest získán, délka=%s.", len(digest))

    access_token = get_graph_access_token()
    events = get_homeoffice_events(access_token)

    logging.info(
        "Nalezeno událostí s kategorií HOMEOFFICE: %s",
        len(events),
    )

    for event in events:
        event_key = build_event_key(event)

        if already_processed(event_key):
            logging.info(
                "Přeskakuji již zpracovanou událost: %s",
                event.get("subject"),
            )
            continue

        request_data = prepare_request(event, current_user)

        try:
            dms_item_id = create_dms_request(
                session=dms_session,
                list_entity_type=list_metadata[
                    "ListItemEntityTypeFullName"
                ],
                request_data=request_data,
            )

            status = "dry_run" if DRY_RUN else "created"

            save_result(
                event_key=event_key,
                graph_event_id=event["id"],
                subject=event.get("subject", ""),
                start_date=event["start"]["dateTime"],
                end_date=event["end"]["dateTime"],
                status=status,
                dms_item_id=dms_item_id or None,
            )

        except Exception:
            logging.exception(
                "Chyba při zpracování události: %s",
                event.get("subject"),
            )

            save_result(
                event_key=event_key,
                graph_event_id=event["id"],
                subject=event.get("subject", ""),
                start_date=event["start"]["dateTime"],
                end_date=event["end"]["dateTime"],
                status="failed",
            )

    logging.info("Synchronizace dokončena.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        logging.exception("Synchronizace skončila kritickou chybou.")
        raise SystemExit(1)