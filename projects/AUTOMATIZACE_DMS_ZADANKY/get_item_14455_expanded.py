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

OUTPUT_FILE = Path("item_14455_expanded.json")

# ============================================================================
# SESSION
# ============================================================================

def create_session() -> requests.Session:

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
# LOAD ITEM
# ============================================================================

def load_item(session: requests.Session) -> dict:

    select_fields = ",".join(
        [
            "*",

            "Rq_All_Applicant/Id",
            "Rq_All_Applicant/Title",
            "Rq_All_Applicant/EMail",

            "Rq_All_ApplicantManager/Id",
            "Rq_All_ApplicantManager/Title",
            "Rq_All_ApplicantManager/EMail",

            "Rq_H_Approver1/Id",
            "Rq_H_Approver1/Title",
            "Rq_H_Approver1/EMail",

            "Rq_H_Approver2/Id",
            "Rq_H_Approver2/Title",
            "Rq_H_Approver2/EMail",
        ]
    )

    expand_fields = ",".join(
        [
            "Rq_All_Applicant",
            "Rq_All_ApplicantManager",
            "Rq_H_Approver1",
            "Rq_H_Approver2",
        ]
    )

    url = (
        f"{DMS_SITE}/_api/web/lists"
        f"(guid'{LIST_GUID}')"
        f"/items({ITEM_ID})"
        f"?$select={select_fields}"
        f"&$expand={expand_fields}"
    )

    response = session.get(
        url,
        verify=VERIFY_TLS,
        timeout=60,
    )

    print()
    print("URL")
    print("=" * 80)
    print(response.url)

    print()
    print("HTTP STATUS")
    print("=" * 80)
    print(response.status_code)

    response.raise_for_status()

    return response.json()["d"]


# ============================================================================
# PRINT DICTIONARY
# ============================================================================

def print_recursive(data, indent=0):

    prefix = " " * indent

    if isinstance(data, dict):

        for key, value in data.items():

            if isinstance(value, (dict, list)):

                print(f"{prefix}{key}:")

                print_recursive(
                    value,
                    indent + 4
                )

            else:

                print(f"{prefix}{key}: {value}")

    elif isinstance(data, list):

        for index, item in enumerate(data):

            print(f"{prefix}[{index}]:")

            print_recursive(
                item,
                indent + 4
            )


# ============================================================================
# PRINT IMPORTANT FIELDS
# ============================================================================

def print_important(data):

    print()
    print("=" * 100)
    print("DŮLEŽITÁ POLE")
    print("=" * 100)

    important_fields = [
        "Title",
        "Rq_H_TypeOfHoliday",
        "Rq_H_PaidHoliday",
        "Rq_All_type",
        "Rq_All_RelatedLink",
        "Rq_H_ValidSince",
        "Rq_H_ValidTo",
        "Rq_H_WorkingDay",
        "Rq_All_StatusChoice",
    ]

    for field in important_fields:

        if field in data:

            print(
                f"{field}: "
                f"{data[field]}"
            )

    print()
    print("=" * 100)
    print("ŽADATEL")
    print("=" * 100)

    print(
        json.dumps(
            data.get("Rq_All_Applicant"),
            indent=2,
            ensure_ascii=False,
        )
    )

    print()
    print("=" * 100)
    print("NADŘÍZENÝ")
    print("=" * 100)

    print(
        json.dumps(
            data.get(
                "Rq_All_ApplicantManager"
            ),
            indent=2,
            ensure_ascii=False,
        )
    )

    print()
    print("=" * 100)
    print("SCHVALOVATEL 1")
    print("=" * 100)

    print(
        json.dumps(
            data.get("Rq_H_Approver1"),
            indent=2,
            ensure_ascii=False,
        )
    )

    print()
    print("=" * 100)
    print("SCHVALOVATEL 2")
    print("=" * 100)

    print(
        json.dumps(
            data.get("Rq_H_Approver2"),
            indent=2,
            ensure_ascii=False,
        )
    )


# ============================================================================
# SAVE
# ============================================================================

def save_json(data):

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
    print("DMS DETAIL POLOŽKY S EXPANDEM")
    print("=" * 100)

    session = create_session()

    item = load_item(session)

    print_important(item)

    save_json(item)

    print()
    print("=" * 100)
    print("KOMPLETNÍ JSON")
    print("=" * 100)

    print_recursive(item)

    print()
    print("=" * 100)
    print("HOTOVO")
    print("=" * 100)


if __name__ == "__main__":
    main()