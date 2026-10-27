import os
from pathlib import Path

import requests
from dotenv import load_dotenv


SCRIPT_DIR = Path(__file__).resolve().parent
ENV_FILE = SCRIPT_DIR / ".env"

load_dotenv(
    dotenv_path=ENV_FILE,
    override=True
)

client_id = (os.getenv("APS_CLIENT_ID") or "").strip()
client_secret = (os.getenv("APS_CLIENT_SECRET") or "").strip()


print("ENV:", ENV_FILE)
print("ENV existuje:", ENV_FILE.exists())
print("Client ID načten:", bool(client_id))
print("Client ID délka:", len(client_id))
print("Secret načten:", bool(client_secret))
print("Secret délka:", len(client_secret))


url = "https://developer.api.autodesk.com/authentication/v2/token"

response = requests.post(
    url,
    auth=(client_id, client_secret),
    headers={
        "Content-Type": "application/x-www-form-urlencoded"
    },
    data={
        "grant_type": "client_credentials",
        "scope": "data:read"
    },
    timeout=30
)


print()
print("HTTP:", response.status_code)

try:
    print("Response:", response.json())
except Exception:
    print("Response:", response.text)