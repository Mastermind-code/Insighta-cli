# Insighta CLI

Globally installable CLI for the Insighta Labs+ Profile Intelligence System.

## Installation

```bash
pip install -e .
```

After installation the `insighta` command is available globally from any directory.

## Authentication

```bash
insighta login       # Opens browser for GitHub OAuth
insighta whoami      # Show current logged-in user
insighta logout      # Revoke session and clear credentials
```

### How login works (PKCE flow)
1. CLI generates a `code_verifier` and derives `code_challenge` (SHA-256 + base64url)
2. A temporary local server starts on `localhost:8765`
3. Your browser opens GitHub OAuth with `code_challenge` attached
4. After you authorise, GitHub redirects to `localhost:8765/callback`
5. CLI validates the `state` parameter (CSRF protection)
6. CLI sends `code` + `code_verifier` to the backend
7. Backend verifies PKCE, creates your user, returns an access + refresh token pair
8. Credentials are saved to `~/.insighta/credentials.json`

## Profiles

```bash
# List profiles
insighta profiles list
insighta profiles list --gender male
insighta profiles list --country NG --age-group adult
insighta profiles list --min-age 25 --max-age 40
insighta profiles list --sort-by age --order desc
insighta profiles list --page 2 --limit 20

# Get a single profile
insighta profiles get <uuid>

# Natural language search
insighta profiles search "young males from nigeria"

# Create a profile (admin only)
insighta profiles create --name "Harriet Tubman"

# Export to CSV (saved in the current working directory)
insighta profiles export --format csv
insighta profiles export --format csv --gender male --country NG
insighta profiles export --format csv --sort-by age --order asc
```

## Token Handling

- Credentials are stored at `~/.insighta/credentials.json`
- On every `401 Unauthorized` response the CLI automatically calls `POST /auth/refresh` to get a new token pair and retries the original request
- If the refresh token is also expired you will see: `Session expired. Please run 'insighta login' again.`
- Refresh tokens are single-use — a new pair is issued and the old one is revoked on every refresh

## Configuration

The backend URL defaults to the deployed Vercel API. Override with an environment variable:

```bash
export INSIGHTA_API_URL=http://localhost:8000/api/v1
```

## Requirements

- Python 3.8+
- pip
