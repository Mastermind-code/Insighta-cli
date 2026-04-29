# Insighta CLI

A globally installable CLI tool for the Insighta Labs+
Profile Intelligence System.

## Installation

```bash
pip install -e .
```

## Usage

```bash
insighta --help
```

## Authentication

```bash
# Login via GitHub OAuth
insighta auth login

# Check current user
insighta auth whoami

# Logout
insighta auth logout
```

## Profile Commands

```bash
# List all profiles
insighta profiles list

# Filter profiles
insighta profiles list --gender male
insighta profiles list --country NG --age-group adult
insighta profiles list --min-age 25 --max-age 40
insighta profiles list --sort-by age --order desc
insighta profiles list --page 2 --limit 20

# Get single profile
insighta profiles get <id>

# Natural language search
insighta profiles search "young males from nigeria"

# Create profile (admin only)
insighta profiles create --name "Harriet Tubman"

# Export to CSV
insighta profiles export --format csv
insighta profiles export --format csv --gender male --country NG
```

## Token Handling

Credentials are stored at `~/.insighta/credentials.json`.

The CLI automatically refreshes expired access tokens using
the refresh token. If the refresh token is also expired,
you will be prompted to login again.

## Configuration

The CLI connects to the backend at:
http://localhost:8000/api/v1

## Requirements

- Python 3.8+
- Backend server running
