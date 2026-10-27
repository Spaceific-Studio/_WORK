from __future__ import annotations

import json
from pathlib import Path

import requests
import urllib3
from requests_negotiate_sspi import HttpNegotiateAuth

# ============================================================================
# KONFIGURACE
# ============================================================================

DMS_SITE = "https://dms.pvs.cz/sites/Zadanky"

LIST_GUID = "dc08c020-45ba-4cb5-9681-5ef919daa42b"

ITEM_ID = 14455

VERIFY_TLS = False

OUTPUT_FILE = Path("item_14455_full.json")

# ============================================================================
# SESSION
# ============================================================================

def create_session() -> requests.Session:

    session = requests.Session()

    session.auth = HttpNegotiateAuth()

    session.headers.update(
        {
            "Accept": "application/json;odata=verbose",
            "User-Agent": "PVS-DMS-Diagnostics/1.0",
        }
    )

    return session


# ============================================================================
# LOAD ITEM
# ============================================================================

def load_item(
    session: requests.Session,
) -> dict:

    url = (
        f"{DMS_SITE}/_api/web/lists"
        f"(guid'{LIST_GUID}')"
        f"/items({ITEM_ID})"
    )

    response = session.get(
        url,
        verify=VERIFY_TLS,
        timeout=60,
    )

    print()
    print("URL:")
    print(response.url)

    print()
    print("HTTP STATUS:")
    print(response.status_code)

    response.raise_for_status()

    return response.json()["d"]


# ============================================================================
# PRINT ITEM
# ============================================================================

def print_item(data: dict):

    print()
    print("=" * 100)
    print(f"DETAIL POLOŽKY {ITEM_ID}")
    print("=" * 100)

    for key in sorted(data.keys()):

        if key == "__metadata":
            continue

        value = data[key]

        if isinstance(value, dict):
            print()
            print(f"{key}:")
            print(json.dumps(
                value,
                indent=2,
                ensure_ascii=False
            ))

        else:
            print(f"{key}: {value}")


# ============================================================================
# SAVE
# ============================================================================

def save_json(data: dict):

    OUTPUT_FILE.write_text(
        json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
            default=str,
        ),
        encoding="utf-8",
    )

    print()
    print(
        f"JSON uložen do:\n"
        f"{OUTPUT_FILE.resolve()}"
    )


# ============================================================================
# MAIN
# ============================================================================

def main():

    if not VERIFY_TLS:
        urllib3.disable_warnings(
            urllib3.exceptions.InsecureRequestWarning
        )

    print()
    print("=" * 100)
    print("DMS - DETAIL ŽÁDANKY")
    print("=" * 100)

    session = create_session()

    item = load_item(session)

    print_item(item)

    save_json(item)

    print()
    print("=" * 100)
    print("HOTOVO")
    print("=" * 100)


if __name__ == "__main__":
    main()