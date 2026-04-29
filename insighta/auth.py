import hashlib
import base64
import secrets
import webbrowser
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import typer
from rich.console import Console
from insighta.api import api_request, BASE_URL
from insighta.credentials import save_credentials, load_credentials, clear_credentials

console = Console()
app = typer.Typer()

CALLBACK_PORT = 8765
captured_code = {}

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        
        if "code" in params:
            captured_code["code"] = params["code"][0]
            captured_code["state"] = params.get("state", [None])[0]
            
            # Send success response to browser
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Login successful! You can close this tab.")
        
    def log_message(self, format, *args):
        pass  # Suppress server logs

    
def generate_pkce():
    code_verifier = secrets.token_urlsafe(64)
    digest = hashlib.sha256(code_verifier.encode()).digest()
    code_challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
    return code_verifier, code_challenge


@app.command()
def login():
    """Login via GitHub OAuth"""
    code_verifier, code_challenge = generate_pkce()
    state = secrets.token_urlsafe(16)
    
    # Start local callback server
    server = HTTPServer(("localhost", CALLBACK_PORT), CallbackHandler)
    thread = threading.Thread(target=server.handle_request)
    thread.start()
    
    # Open browser
    url = f"{BASE_URL}/auth/github?code_challenge={code_challenge}&state={state}"
    console.print("[cyan]Opening browser for GitHub login...[/cyan]")
    webbrowser.open(url)
    
    # Wait for callback
    thread.join(timeout=120)
    
    if "code" not in captured_code:
        console.print("[red]Login timed out. Please try again.[/red]")
        return
    
    # Validate state
    if captured_code.get("state") != state:
        console.print("[red]State mismatch. Possible CSRF attack.[/red]")
        return
    
    # Exchange code with backend
    with console.status("[cyan]Authenticating...[/cyan]"):
        import requests
        response = requests.get(
            f"{BASE_URL}/auth/github/callback",
            params={
                "code": captured_code["code"],
                "code_verifier": code_verifier
            }
        )
    
    if response.status_code != 200:
        console.print("[red]Authentication failed. Please try again.[/red]")
        return
    
    data = response.json()
    
    # Get username from backend
    access_token = data["access_token"]
    refresh_token = data["refresh_token"]
    
    # Fetch user info
    import requests as req
    user_response = req.get(
        f"{BASE_URL}/auth/whoami",
        headers={"Authorization": f"Bearer {access_token}", "X-API-Version": "1"}
    )
    username = user_response.json().get("username", "unknown")
    
    save_credentials(access_token, refresh_token, username)
    console.print(f"[green]Logged in as @{username}[/green]")


@app.command()
def logout():
    """Logout and clear credentials"""
    creds = load_credentials()
    if not creds:
        console.print("[yellow]You are not logged in.[/yellow]")
        return
    
    api_request("POST", "/auth/logout", json={
        "refresh_token": creds.get("refresh_token")
    })
    clear_credentials()
    console.print("[green]Logged out successfully.[/green]")


@app.command()
def whoami():
    """Show current logged in user"""
    creds = load_credentials()
    if not creds:
        console.print("[red]Not logged in. Run 'insighta login' first.[/red]")
        return
    
    response = api_request("GET", "/auth/whoami")
    if response.status_code == 200:
        user = response.json()
        console.print(f"[cyan]Username:[/cyan] @{user.get('username')}")
        console.print(f"[cyan]Role:[/cyan] {user.get('role')}")
        console.print(f"[cyan]Email:[/cyan] {user.get('email')}")
    else:
        console.print("[red]Failed to fetch user info.[/red]")