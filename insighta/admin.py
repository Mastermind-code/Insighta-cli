import typer
from rich.console import Console
from rich.table import Table
from insighta.api import api_request

app = typer.Typer(help="Admin commands for managing users.")
console = Console()


@app.command("users")
def list_users():
    """List all users (admin only)."""
    with console.status("[bold green]Fetching users..."):
        response = api_request("GET", "/admin/users")

    if response.status_code == 403:
        console.print("[red]Permission denied. Admin role required.[/red]")
        raise typer.Exit(1)

    if response.status_code != 200:
        console.print(f"[red]Error:[/red] {response.json().get('message')}")
        raise typer.Exit(1)

    users = response.json().get("data", [])

    table = Table(
        title="All Users",
        caption=f"Total: {len(users)}",
        header_style="bold magenta"
    )
    table.add_column("ID", style="dim", width=14)
    table.add_column("Username", style="cyan")
    table.add_column("Email")
    table.add_column("Role", justify="center")
    table.add_column("Status", justify="center")
    table.add_column("Last Login", justify="right", style="dim")

    for u in users:
        status_str = "[green]Active[/green]" if u["is_active"] else "[red]Inactive[/red]"
        role_str = f"[magenta]{u['role']}[/magenta]" if u["role"] == "admin" else u["role"]
        last_login = u["last_login_at"][:10] if u["last_login_at"] else "Never"
        table.add_row(
            str(u["id"])[:12] + "...",
            f"@{u['username']}",
            u["email"] or "—",
            role_str,
            status_str,
            last_login,
        )

    console.print(table)


@app.command("role")
def set_role(
    user_id: str = typer.Argument(..., help="User ID"),
    role: str = typer.Argument(..., help="New role: admin or analyst"),
):
    """Change a user's role (admin only)."""
    if role not in ("admin", "analyst"):
        console.print("[red]Invalid role. Must be 'admin' or 'analyst'.[/red]")
        raise typer.Exit(1)

    with console.status(f"[bold green]Setting role to '{role}'..."):
        response = api_request("PATCH", f"/admin/users/{user_id}/role", json={"role": role})

    if response.status_code == 403:
        console.print("[red]Permission denied. Admin role required.[/red]")
        raise typer.Exit(1)

    if response.status_code == 400:
        console.print(f"[red]Error:[/red] {response.json().get('message')}")
        raise typer.Exit(1)

    if response.status_code == 404:
        console.print("[red]User not found.[/red]")
        raise typer.Exit(1)

    if response.status_code == 200:
        data = response.json().get("data", {})
        console.print(f"[green]@{data['username']} is now '{data['role']}'.[/green]")
    else:
        console.print(f"[red]Error:[/red] {response.json().get('message')}")
        raise typer.Exit(1)


@app.command("status")
def set_status(
    user_id: str = typer.Argument(..., help="User ID"),
    activate: bool = typer.Option(None, "--activate/--deactivate", help="Activate or deactivate the account"),
):
    """Activate or deactivate a user account (admin only)."""
    if activate is None:
        console.print("[red]Specify --activate or --deactivate.[/red]")
        raise typer.Exit(1)

    action = "activate" if activate else "deactivate"
    confirm = typer.confirm(f"Are you sure you want to {action} this user?")
    if not confirm:
        console.print("[yellow]Cancelled.[/yellow]")
        raise typer.Exit(0)

    with console.status(f"[bold green]Updating account status..."):
        response = api_request("PATCH", f"/admin/users/{user_id}/status", json={"is_active": activate})

    if response.status_code == 403:
        console.print("[red]Permission denied. Admin role required.[/red]")
        raise typer.Exit(1)

    if response.status_code == 400:
        console.print(f"[red]Error:[/red] {response.json().get('message')}")
        raise typer.Exit(1)

    if response.status_code == 404:
        console.print("[red]User not found.[/red]")
        raise typer.Exit(1)

    if response.status_code == 200:
        data = response.json().get("data", {})
        status = "activated" if data["is_active"] else "deactivated"
        console.print(f"[green]@{data['username']} has been {status}.[/green]")
    else:
        console.print(f"[red]Error:[/red] {response.json().get('message')}")
        raise typer.Exit(1)
