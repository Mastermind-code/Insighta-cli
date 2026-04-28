import json
from pathlib import Path

CREDENTIALS_PATH = Path.home() / ".insighta" / "credentials.json"

def save_credentials(access_token: str, refresh_token: str, username: str):
    # Create directory if it doesn't exist
    CREDENTIALS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CREDENTIALS_PATH, "w") as f:
        json.dump({
            "access_token": access_token,
            "refresh_token": refresh_token,
            "username": username
        }, f)

def load_credentials() -> dict:
    if not CREDENTIALS_PATH.exists():
        return None
    with open(CREDENTIALS_PATH, "r") as f:
        return json.load(f)

def clear_credentials():
    if CREDENTIALS_PATH.exists():
        CREDENTIALS_PATH.unlink()