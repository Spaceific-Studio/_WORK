from pathlib import Path
import json
import requests
from requests_negotiate_sspi import HttpNegotiateAuth

# ============================================================================
# KONFIGURACE
# ============================================================================

DMS_SITE = "https://dms.pvs.cz/sites/Zadanky"

LIST_GUID = "dc08c020-45ba-4cb5-9681-5ef919daa42b"

VERIFY_TLS = False

FIELD_NAME = "Rq_H_TypeOfHoliday"

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
# CURRENT USER
# ============================================================================

def print_current_user(session):

    url = f"{DMS_SITE}/_api/web/currentuser"

    response = session.get(
        url,
        verify=VERIFY_TLS,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()["d"]

    print()
    print("=" * 80)
    print("AKTUÁLNÍ UŽIVATEL")
    print("=" * 80)

    print("ID:", data.get("Id"))
    print("Login:", data.get("LoginName"))
    print("Email:", data.get("Email"))
    print("Titulek:", data.get("Title"))


# ============================================================================
# LIST
# ============================================================================

def print_list_info(session):

    url = (
        f"{DMS_SITE}/_api/web/lists"
        f"(guid'{LIST_GUID}')"
        f"?$select=Id,Title,ListItemEntityTypeFullName"
    )

    response = session.get(
        url,
        verify=VERIFY_TLS,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()["d"]

    print()
    print("=" * 80)
    print("SEZNAM")
    print("=" * 80)

    print("Název:", data.get("Title"))
    print("GUID :", data.get("Id"))
    print("Entity Type:", data.get("ListItemEntityTypeFullName"))


# ============================================================================
# DETAIL POLE
# ============================================================================

def print_field_details(session):

    url = (
        f"{DMS_SITE}/_api/web/lists"
        f"(guid'{LIST_GUID}')"
        f"/fields"
        f"/GetByInternalNameOrTitle('{FIELD_NAME}')"
    )

    response = session.get(
        url,
        verify=VERIFY_TLS,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()["d"]

    print()
    print("=" * 80)
    print("DETAIL POLE")
    print("=" * 80)

    interesting_keys = [
        "Title",
        "InternalName",
        "TypeAsString",
        "DefaultValue",
        "Required",
        "FillInChoice"
    ]

    for key in interesting_keys:

        print(f"{key}: {data.get(key)}")

    print()
    print("=" * 80)
    print("CHOICES")
    print("=" * 80)

    choices = data.get("Choices")

    if isinstance(choices, dict):

        values = choices.get("results", [])

        for idx, value in enumerate(values, start=1):

            print(f"{idx}. {value}")

    else:

        print(choices)


# ============================================================================
# RAW JSON
# ============================================================================

def save_json(session):

    url = (
        f"{DMS_SITE}/_api/web/lists"
        f"(guid'{LIST_GUID}')"
        f"/fields"
        f"/GetByInternalNameOrTitle('{FIELD_NAME}')"
    )

    response = session.get(
        url,
        verify=VERIFY_TLS,
        timeout=30
    )

    response.raise_for_status()

    output = response.json()

    output_file = Path("Rq_H_TypeOfHoliday.json")

    output_file.write_text(
        json.dumps(
            output,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    print()
    print(f"JSON uložen do: {output_file.resolve()}")


# ============================================================================
# MAIN
# ============================================================================

def main():

    print()
    print("=" * 80)
    print("DMS DIAGNOSTIKA - TYP VOLNA")
    print("=" * 80)

    session = create_session()

    print_current_user(session)

    print_list_info(session)

    print_field_details(session)

    save_json(session)

    print()
    print("=" * 80)
    print("HOTOVO")
    print("=" * 80)


if __name__ == "__main__":
    main()