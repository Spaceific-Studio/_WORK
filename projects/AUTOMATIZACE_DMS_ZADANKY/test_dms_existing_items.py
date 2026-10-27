import json
import requests
from requests_negotiate_sspi import HttpNegotiateAuth

# ============================================================================
# KONFIGURACE
# ============================================================================

DMS_SITE = "https://dms.pvs.cz/sites/Zadanky"

LIST_GUID = "dc08c020-45ba-4cb5-9681-5ef919daa42b"

VERIFY_TLS = False

TOP_ITEMS = 10

# ============================================================================
# SESSION
# ============================================================================

def create_session():

    session = requests.Session()

    session.auth = HttpNegotiateAuth()

    session.headers.update(
        {
            "Accept": "application/json;odata=verbose",
            "User-Agent": "PVS-DMS-Diagnostics/1.0"
        }
    )

    return session


# ============================================================================
# LOAD ITEMS
# ============================================================================

def get_items(session):

    url = (
        f"{DMS_SITE}/_api/web/lists"
        f"(guid'{LIST_GUID}')"
        f"/items"
        f"?$top={TOP_ITEMS}"
        f"&$orderby=Id desc"
    )

    response = session.get(
        url,
        verify=VERIFY_TLS,
        timeout=30
    )

    response.raise_for_status()

    return response.json()["d"]["results"]


# ============================================================================
# PRINT
# ============================================================================

def print_items(items):

    print()
    print("=" * 80)
    print(f"NALEZENO {len(items)} POLOŽEK")
    print("=" * 80)

    for item in items:

        print()
        print("=" * 80)

        print("ID:", item.get("Id"))

        interesting_fields = [
            "Title",
            "Rq_H_TypeOfHoliday",
            "Rq_H_PaidHoliday",
            "Rq_H_SpecifyOther",
            "Rq_H_ValidSince",
            "Rq_H_ValidTo",
            "Rq_All_type",
            "Rq_All_StatusChoice",
            "Rq_All_RequestNumber",
        ]

        for field in interesting_fields:

            if field in item:

                print(
                    f"{field}: "
                    f"{item.get(field)}"
                )


# ============================================================================
# SAVE RAW JSON
# ============================================================================

def save_json(items):

    with open(
        "holiday_items.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            items,
            f,
            indent=2,
            ensure_ascii=False
        )

    print()
    print("JSON uložen:")
    print("holiday_items.json")


# ============================================================================
# MAIN
# ============================================================================

def main():

    print()
    print("=" * 80)
    print("DMS EXISTUJÍCÍ ŽÁDANKY")
    print("=" * 80)

    session = create_session()

    items = get_items(session)

    print_items(items)

    save_json(items)

    print()
    print("=" * 80)
    print("HOTOVO")
    print("=" * 80)


if __name__ == "__main__":
    main()