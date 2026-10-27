import os
import base64
from urllib.parse import urljoin

import requests
from dotenv import load_dotenv


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

APS_CLIENT_ID = os.getenv("APS_CLIENT_ID")
APS_CLIENT_SECRET = os.getenv("APS_CLIENT_SECRET")
PROJECT_ID = os.getenv("ACC_PROJECT_ID")
ROOT_FOLDER_ID = os.getenv("ACC_ROOT_FOLDER_ID")

PAGE_LIMIT = 200

APS_BASE_URL = "https://developer.api.autodesk.com"


# ============================================================
# CONFIG VALIDATION
# ============================================================

def validate_config():
    """
    Zkontroluje povinné proměnné z .env.
    """

    required = {
        "APS_CLIENT_ID": APS_CLIENT_ID,
        "APS_CLIENT_SECRET": APS_CLIENT_SECRET,
        "ACC_PROJECT_ID": PROJECT_ID,
        "ACC_ROOT_FOLDER_ID": ROOT_FOLDER_ID
    }

    missing = [
        name
        for name, value in required.items()
        if not value
    ]

    if missing:
        print()
        print("CHYBA: V .env chybí následující hodnoty:")

        for name in missing:
            print(" -", name)

        return False

    return True


# ============================================================
# HTTP HELPERS
# ============================================================

def auth_headers(token):
    return {
        "Authorization": f"Bearer {token}"
    }


def aps_get(url, token, params=None):
    """
    Společná GET metoda pro APS API.
    """

    response = requests.get(
        url,
        headers=auth_headers(token),
        params=params,
        timeout=60
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# APS AUTHENTICATION
# ============================================================

def get_access_token():
    """
    Získá 2-legged OAuth token APS.
    """

    url = f"{APS_BASE_URL}/authentication/v2/token"

    data = {
        "grant_type": "client_credentials",
        "scope": "data:read"
    }

    response = requests.post(
        url,
        data=data,
        auth=(APS_CLIENT_ID, APS_CLIENT_SECRET),
        timeout=60
    )

    response.raise_for_status()

    return response.json()["access_token"]


# ============================================================
# ACC FOLDER PAGINATION
# ============================================================

def get_folder_contents(token, project_id, folder_id):
    """
    Načte kompletní obsah ACC složky včetně stránkování.

    Vrací položky typu:
        - folders
        - items

    Neomezuje tedy výsledky pouze na RVT.
    """

    url = (
        f"{APS_BASE_URL}/data/v1/"
        f"projects/{project_id}/"
        f"folders/{folder_id}/contents"
    )

    all_items = []

    params = {
        "page[number]": 0,
        "page[limit]": PAGE_LIMIT
    }

    while url:

        data = aps_get(
            url,
            token,
            params=params
        )

        page_items = data.get("data", [])

        all_items.extend(page_items)

        links = data.get("links", {})
        next_link = links.get("next")

        # Některé odpovědi mohou mít next jako objekt.
        if isinstance(next_link, dict):
            url = next_link.get("href")
        else:
            url = next_link

        # Pokud APS vrátí relativní URL.
        if url:
            url = urljoin(APS_BASE_URL, url)

        # Parametry další stránky již bývají v next URL.
        params = None

    return all_items


# ============================================================
# FOLDER / FILE HELPERS
# ============================================================

def split_folder_contents(items):
    """
    Rozdělí obsah složky na podsložky a soubory.
    """

    folders = []
    files = []

    for item in items:

        item_type = item.get("type")

        attributes = item.get("attributes", {})

        display_name = (
            attributes.get("displayName")
            or attributes.get("name")
            or "Bez názvu"
        )

        record = {
            "id": item.get("id"),
            "name": display_name,
            "raw": item
        }

        if item_type == "folders":
            folders.append(record)

        elif item_type == "items":
            files.append(record)

    folders.sort(
        key=lambda x: x["name"].lower()
    )

    files.sort(
        key=lambda x: x["name"].lower()
    )

    return folders, files


def get_rvt_files(files):
    """
    Vybere pouze RVT soubory.
    """

    return [
        item
        for item in files
        if item["name"].lower().endswith(".rvt")
    ]


# ============================================================
# INTERACTIVE FOLDER BROWSER
# ============================================================

def select_acc_folder(token):
    """
    Interaktivní navigace ACC složkami.

    Příkazy:
        číslo = otevření podsložky
        S     = vybrat aktuální složku
        B     = návrat
        Q     = konec
    """

    current_folder = {
        "id": ROOT_FOLDER_ID,
        "name": "ROOT"
    }

    history = []

    while True:

        print()
        print("=" * 70)
        print("ACC PROHLÍŽEČ SLOŽEK")
        print("=" * 70)

        path_names = [
            folder["name"]
            for folder in history
        ]

        path_names.append(current_folder["name"])

        print()
        print("Umístění:")
        print(" / ".join(path_names))

        print()
        print("Načítám obsah...")

        contents = get_folder_contents(
            token,
            PROJECT_ID,
            current_folder["id"]
        )

        folders, files = split_folder_contents(contents)

        rvt_files = get_rvt_files(files)

        print()
        print(
            f"Podsložky: {len(folders)} | "
            f"RVT modely: {len(rvt_files)} | "
            f"Ostatní soubory: {len(files) - len(rvt_files)}"
        )

        print()

        if folders:

            print("PODSLOŽKY")
            print("-" * 70)

            for index, folder in enumerate(
                folders,
                start=1
            ):
                print(
                    f"{index:>3}. "
                    f"[DIR] {folder['name']}"
                )

        else:
            print("Žádné podsložky.")

        print()
        print("PŘÍKAZY")
        print("-" * 70)

        print(" číslo  otevřít podsložku")
        print(" S      vybrat tuto složku")

        if history:
            print(" B      zpět")

        print(" Q      ukončit")

        print()

        selection = input("Výběr: ").strip()

        # --------------------------------------------
        # SELECT CURRENT FOLDER
        # --------------------------------------------

        if selection.upper() == "S":

            return {
                "folder": current_folder,
                "files": files,
                "rvt_files": rvt_files,
                "path": path_names
            }

        # --------------------------------------------
        # BACK
        # --------------------------------------------

        if selection.upper() == "B":

            if history:

                current_folder = history.pop()

            continue

        # --------------------------------------------
        # QUIT
        # --------------------------------------------

        if selection.upper() == "Q":
            return None

        # --------------------------------------------
        # OPEN SUBFOLDER
        # --------------------------------------------

        try:
            index = int(selection) - 1

        except ValueError:

            print()
            print("Neplatný příkaz.")
            continue

        if not 0 <= index < len(folders):

            print()
            print("Neplatné číslo složky.")
            continue

        selected_folder = folders[index]

        history.append(current_folder)

        current_folder = {
            "id": selected_folder["id"],
            "name": selected_folder["name"]
        }


# ============================================================
# SELECT RVT MODELS
# ============================================================

def select_models(rvt_files):
    """
    Umožní vybrat RVT modely.

    Syntax:
        ALL
        1
        1,3,5
        1-5
        1,3-6,9
    """

    if not rvt_files:

        print()
        print("V této složce nebyly nalezeny žádné RVT modely.")

        return []

    print()
    print("=" * 70)
    print("RVT MODELY")
    print("=" * 70)
    print()

    for index, model in enumerate(
        rvt_files,
        start=1
    ):
        print(
            f"{index:>3}. {model['name']}"
        )

    print()
    print("Možnosti výběru:")
    print()
    print(" ALL       všechny modely")
    print(" 1         jeden model")
    print(" 1,3,5     více modelů")
    print(" 1-5       rozsah")
    print(" 1,3-6,9   kombinace")
    print()

    selection = input("Výběr modelů: ").strip()

    if selection.upper() == "ALL":
        return rvt_files

    indexes = set()

    parts = selection.split(",")

    for part in parts:

        part = part.strip()

        # --------------------------------------------
        # RANGE
        # --------------------------------------------

        if "-" in part:

            try:

                start, end = part.split("-", 1)

                start = int(start)
                end = int(end)

                for value in range(
                    start,
                    end + 1
                ):
                    indexes.add(value - 1)

            except ValueError:
                continue

        # --------------------------------------------
        # SINGLE VALUE
        # --------------------------------------------

        else:

            try:

                indexes.add(
                    int(part) - 1
                )

            except ValueError:
                continue

    selected = []

    for index in sorted(indexes):

        if 0 <= index < len(rvt_files):
            selected.append(
                rvt_files[index]
            )

    return selected


# ============================================================
# ACC - LATEST VERSION
# ============================================================

def get_latest_version(token, project_id, item_id):
    """
    Získá nejnovější verzi dané ACC položky.
    """

    url = (
        f"{APS_BASE_URL}/data/v1/"
        f"projects/{project_id}/"
        f"items/{item_id}/versions"
    )

    data = aps_get(
        url,
        token,
        params={
            "page[number]": 0,
            "page[limit]": 1
        }
    )

    versions = data.get("data", [])

    if not versions:
        return None

    return versions[0]


# ============================================================
# MODEL DERIVATIVE URN
# ============================================================

def version_to_urn(version):
    """
    Získá storage URN a převede ho na URL-safe Base64.
    """

    relationships = version.get(
        "relationships",
        {}
    )

    storage = relationships.get(
        "storage",
        {}
    )

    storage_data = storage.get(
        "data",
        {}
    )

    storage_id = storage_data.get("id")

    if not storage_id:
        return None

    encoded = base64.urlsafe_b64encode(
        storage_id.encode("utf-8")
    ).decode("utf-8")

    return encoded.rstrip("=")


# ============================================================
# MODEL DERIVATIVE - METADATA
# ============================================================

def get_model_metadata(token, urn):

    url = (
        f"{APS_BASE_URL}/"
        f"modelderivative/v2/designdata/"
        f"{urn}/metadata"
    )

    return aps_get(
        url,
        token
    )


# ============================================================
# OBJECT TREE
# ============================================================

def get_object_tree(token, urn, guid):

    url = (
        f"{APS_BASE_URL}/"
        f"modelderivative/v2/designdata/"
        f"{urn}/metadata/{guid}"
    )

    return aps_get(
        url,
        token
    )


# ============================================================
# FIND PROJECT BASE POINT
# ============================================================

def find_project_base_point(node):
    """
    Rekurzivně hledá Project Base Point.

    Pro anglickou verzi Revitu hledáme:
        Project Base Point

    Přidána je také česká varianta:
        Základní bod projektu
    """

    if not isinstance(node, dict):
        return None

    name = str(
        node.get("name", "")
    ).lower()

    search_names = [
        "project base point",
        "základní bod projektu",
        "zakladni bod projektu"
    ]

    for search_name in search_names:

        if search_name in name:
            return node.get("objectid")

    for child in node.get(
        "objects",
        []
    ):

        result = find_project_base_point(
            child
        )

        if result is not None:
            return result

    return None


# ============================================================
# OBJECT PROPERTIES
# ============================================================

def get_object_properties(
    token,
    urn,
    guid,
    object_id
):
    """
    Vrátí properties jednoho objektu.
    """

    url = (
        f"{APS_BASE_URL}/"
        f"modelderivative/v2/designdata/"
        f"{urn}/metadata/{guid}/properties"
    )

    return aps_get(
        url,
        token,
        params={
            "objectid": object_id
        }
    )


# ============================================================
# EXTRACT PROJECT BASE POINT
# ============================================================

def extract_pbp_coordinates(properties_data):
    """
    Vyhledá hodnoty:
        N/S
        E/W
        Elevation

    Obsahuje několik EN/CZ variant názvů.
    """

    result = {
        "N/S": None,
        "E/W": None,
        "Elevation": None
    }

    collection = (
        properties_data
        .get("data", {})
        .get("collection", [])
    )

    for obj in collection:

        properties = obj.get(
            "properties",
            {}
        )

        for category, values in properties.items():

            if not isinstance(
                values,
                dict
            ):
                continue

            for key, value in values.items():

                key_lower = str(
                    key
                ).lower().strip()

                # ---------------------------------
                # NORTH / SOUTH
                # ---------------------------------

                ns_names = [
                    "n/s",
                    "north/south",
                    "s/z",
                    "sever/jih"
                ]

                if any(
                    name == key_lower
                    or name in key_lower
                    for name in ns_names
                ):

                    result["N/S"] = value
                    continue

                # ---------------------------------
                # EAST / WEST
                # ---------------------------------

                ew_names = [
                    "e/w",
                    "east/west",
                    "v/z",
                    "východ/západ",
                    "vychod/zapad"
                ]

                if any(
                    name == key_lower
                    or name in key_lower
                    for name in ew_names
                ):

                    result["E/W"] = value
                    continue

                # ---------------------------------
                # ELEVATION
                # ---------------------------------

                elevation_names = [
                    "elevation",
                    "výška",
                    "vyska"
                ]

                if any(
                    name == key_lower
                    or name in key_lower
                    for name in elevation_names
                ):

                    result["Elevation"] = value

    return result


# ============================================================
# PROCESS MODEL
# ============================================================

def process_model(token, model):

    print()
    print("=" * 70)
    print("MODEL:")
    print(model["name"])
    print("-" * 70)

    # --------------------------------------------
    # LATEST VERSION
    # --------------------------------------------

    version = get_latest_version(
        token,
        PROJECT_ID,
        model["id"]
    )

    if version is None:

        print(
            "CHYBA: Nebyla nalezena "
            "žádná verze."
        )

        return None

    # --------------------------------------------
    # URN
    # --------------------------------------------

    urn = version_to_urn(
        version
    )

    if not urn:

        print(
            "CHYBA: Nelze získat URN modelu."
        )

        return None

    # --------------------------------------------
    # METADATA
    # --------------------------------------------

    metadata = get_model_metadata(
        token,
        urn
    )

    metadata_items = (
        metadata
        .get("data", {})
        .get("metadata", [])
    )

    if not metadata_items:

        print(
            "CHYBA: Model nemá dostupná metadata."
        )

        return None

    # --------------------------------------------
    # FIND 3D VIEW
    # --------------------------------------------

    selected_view = None

    for item in metadata_items:

        role = str(
            item.get("role", "")
        ).lower()

        if role == "3d":

            selected_view = item
            break

    if selected_view is None:
        selected_view = metadata_items[0]

    guid = selected_view.get("guid")

    if not guid:

        print(
            "CHYBA: Viewable nemá GUID."
        )

        return None

    # --------------------------------------------
    # OBJECT TREE
    # --------------------------------------------

    tree = get_object_tree(
        token,
        urn,
        guid
    )

    roots = (
        tree
        .get("data", {})
        .get("objects", [])
    )

    project_base_point_id = None

    for node in roots:

        project_base_point_id = (
            find_project_base_point(
                node
            )
        )

        if project_base_point_id is not None:
            break

    # --------------------------------------------
    # PBP NOT AVAILABLE
    # --------------------------------------------

    if project_base_point_id is None:

        print(
            "Project Base Point nebyl "
            "v cloudových datech nalezen."
        )

        return {
            "model": model["name"],
            "status": "PBP_NOT_FOUND",
            "ns": None,
            "ew": None,
            "elevation": None
        }

    # --------------------------------------------
    # PROPERTIES
    # --------------------------------------------

    properties = get_object_properties(
        token,
        urn,
        guid,
        project_base_point_id
    )

    coordinates = extract_pbp_coordinates(
        properties
    )

    print()
    print("PROJECT BASE POINT")
    print()

    print(
        "S/Z (N/S):",
        coordinates["N/S"]
    )

    print(
        "V/Z (E/W):",
        coordinates["E/W"]
    )

    print(
        "Výška     :",
        coordinates["Elevation"]
    )

    return {
        "model": model["name"],
        "status": "OK",
        "ns": coordinates["N/S"],
        "ew": coordinates["E/W"],
        "elevation": coordinates["Elevation"]
    }


# ============================================================
# RESULTS SUMMARY
# ============================================================

def print_summary(results):

    print()
    print()
    print("=" * 100)
    print("SOUHRN")
    print("=" * 100)

    print(
        f"{'MODEL':45}"
        f"{'STATUS':18}"
        f"{'S/Z':12}"
        f"{'V/Z':12}"
        f"{'VÝŠKA':12}"
    )

    print("-" * 100)

    for result in results:

        if result is None:
            continue

        print(
            f"{str(result['model'])[:44]:45}"
            f"{str(result['status']):18}"
            f"{str(result['ns']):12}"
            f"{str(result['ew']):12}"
            f"{str(result['elevation']):12}"
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 70)
    print("ACC - PROJECT BASE POINT READER")
    print("=" * 70)

    # --------------------------------------------
    # CONFIG
    # --------------------------------------------

    if not validate_config():
        return

    # --------------------------------------------
    # LOGIN
    # --------------------------------------------

    print()
    print("Přihlašuji se do Autodesk Platform Services...")

    try:

        token = get_access_token()

    except requests.HTTPError as error:

        print()
        print(
            "Nepodařilo se získat APS token."
        )

        print(error)

        return

    print("Přihlášení OK.")

    # --------------------------------------------
    # FOLDER BROWSER
    # --------------------------------------------

    try:

        folder_result = select_acc_folder(
            token
        )

    except requests.HTTPError as error:

        print()
        print(
            "Chyba při načítání ACC složek:"
        )

        print(error)

        return

    if folder_result is None:

        print()
        print("Program ukončen.")

        return

    # --------------------------------------------
    # SELECTED FOLDER
    # --------------------------------------------

    print()
    print("Vybraná složka:")
    print(
        " / ".join(
            folder_result["path"]
        )
    )

    rvt_files = folder_result[
        "rvt_files"
    ]

    # --------------------------------------------
    # MODEL SELECTION
    # --------------------------------------------

    models = select_models(
        rvt_files
    )

    if not models:

        print()
        print(
            "Nebyl vybrán žádný RVT model."
        )

        return

    print()
    print(
        f"Vybráno modelů: {len(models)}"
    )

    # --------------------------------------------
    # PROCESS MODELS
    # --------------------------------------------

    results = []

    for model in models:

        try:

            result = process_model(
                token,
                model
            )

            results.append(
                result
            )

        except requests.HTTPError as error:

            print()
            print(
                f"APS chyba pro model "
                f"{model['name']}:"
            )

            print(error)

            results.append({
                "model": model["name"],
                "status": "API_ERROR",
                "ns": None,
                "ew": None,
                "elevation": None
            })

        except Exception as error:

            print()
            print(
                f"Neočekávaná chyba pro "
                f"{model['name']}:"
            )

            print(error)

            results.append({
                "model": model["name"],
                "status": "ERROR",
                "ns": None,
                "ew": None,
                "elevation": None
            })

    # --------------------------------------------
    # SUMMARY
    # --------------------------------------------

    print_summary(
        results
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()