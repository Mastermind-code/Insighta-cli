import requests
from insighta.credentials import load_credentials, save_credentials, clear_credentials

BASE_URL = "http://localhost:8000/api/v1"

def refresh_tokens(refresh_token: str) -> dict:
    """Calls the backend to get a new token pair."""
    response = requests.post(
        f"{BASE_URL}/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    if response.status_code == 200:
        return response.json()
    return None

def api_request(method: str, endpoint: str, **kwargs) -> requests.Response:
    creds = load_credentials()
    headers = kwargs.pop("headers", {})
    headers["X-API-Version"] = "1"  # Required by backend

    if creds and "access_token" in creds:
        headers["Authorization"] = f"Bearer {creds['access_token']}"

    response = requests.request(
        method,
        f"{BASE_URL}{endpoint}",
        headers=headers,
        **kwargs
    )

    # Auto-refresh on 401
    if response.status_code == 401 and creds and "refresh_token" in creds:
        new_tokens = refresh_tokens(creds["refresh_token"])

        if new_tokens:
            # Save new tokens
            save_credentials(
                access_token=new_tokens["access_token"],
                refresh_token=new_tokens["refresh_token"],
                username=creds.get("username", "")
            )
            # Retry original request with new token
            headers["Authorization"] = f"Bearer {new_tokens['access_token']}"
            response = requests.request(
                method,
                f"{BASE_URL}{endpoint}",
                headers=headers,
                **kwargs
            )
        else:
            # Refresh failed — clear credentials and prompt re-login
            clear_credentials()
            from rich.console import Console
            Console().print("[red]Session expired. Please run 'insighta login' again.[/red]")

    return response