import typer
from rich.console import Console
from rich.table import Table
from insighta.api import api_request

app = typer.Typer()
console = Console()

def render_table(profiles_list: list, page: int, total_pages: int, total: int):
    table = Table(
        title=f"Insighta Profiles (Page {page}/{total_pages})",
        caption=f"Total Records: {total}",
        header_style="bold magenta"
    )
    table.add_column("ID", style="dim", width=14)
    table.add_column("Name", style="cyan")
    table.add_column("Gender", justify="center")
    table.add_column("Age", justify="right")
    table.add_column("Age Group", justify="center")
    table.add_column("Country", justify="center")
    table.add_column("Gender Prob", justify="right", style="green")

    for p in profiles_list:
        table.add_row(
            str(p["id"])[:12] + "...",
            p["name"],
            p["gender"],
            str(p["age"]),
            p["age_group"],
            p["country_id"],
            f"{p.get('gender_probability', 0):.2f}"
        )
    console.print(table)


@app.command()
def list(
    gender: str = typer.Option(None, help="Filter by gender"),
    country: str = typer.Option(None, "--country", help="Filter by country ID"),
    age_group: str = typer.Option(None, "--age-group", help="Filter by age group"),
    min_age: int = typer.Option(None, "--min-age", help="Minimum age"),
    max_age: int = typer.Option(None, "--max-age", help="Maximum age"),
    sort_by: str = typer.Option("created_at", "--sort-by", help="Sort by field"),
    order: str = typer.Option("desc", help="Sort order asc/desc"),
    page: int = typer.Option(1, help="Page number"),
    limit: int = typer.Option(10, help="Results per page"),
):
    """List profiles with optional filters."""
    params = {"page": page, "limit": limit, "sort_by": sort_by, "order": order}
    if gender: params["gender"] = gender
    if country: params["country_id"] = country
    if age_group: params["age_group"] = age_group
    if min_age is not None: params["min_age"] = min_age
    if max_age is not None: params["max_age"] = max_age

    with console.status("[bold green]Fetching profiles..."):
        response = api_request("GET", "/profiles", params=params)

    if response.status_code != 200:
        console.print(f"[red]Error:[/red] {response.json().get('message')}")
        raise typer.Exit(1)

    data = response.json()
    render_table(
        data.get("data", []),
        data.get("page", 1),
        data.get("total_pages", 1),
        data.get("total", 0)
    )


@app.command()
def get(profile_id: str = typer.Argument(..., help="Profile UUID")):
    """Get a single profile by ID."""
    with console.status("[bold green]Fetching profile..."):
        response = api_request("GET", f"/profiles/{profile_id}")

    if response.status_code == 404:
        console.print("[red]Profile not found.[/red]")
        raise typer.Exit(1)

    if response.status_code != 200:
        console.print(f"[red]Error:[/red] {response.json().get('message')}")
        raise typer.Exit(1)

    p = response.json().get("data", {})
    console.print(f"\n[bold cyan]Profile Details[/bold cyan]")
    console.print(f"[cyan]ID:[/cyan]          {p['id']}")
    console.print(f"[cyan]Name:[/cyan]        {p['name']}")
    console.print(f"[cyan]Gender:[/cyan]      {p['gender']} ({p['gender_probability']:.2f})")
    console.print(f"[cyan]Age:[/cyan]         {p['age']} ({p['age_group']})")
    console.print(f"[cyan]Country:[/cyan]     {p['country_id']} - {p['country_name']}")
    console.print(f"[cyan]Created:[/cyan]     {p['created_at']}\n")


@app.command()
def search(query: str = typer.Argument(..., help="Natural language query")):
    """Search profiles using natural language."""
    with console.status("[bold green]Searching..."):
        response = api_request("GET", "/profiles/search", params={"q": query})

    if response.status_code != 200:
        console.print(f"[red]Error:[/red] {response.json().get('message')}")
        raise typer.Exit(1)

    data = response.json()
    profiles_list = data.get("data", [])

    if not profiles_list:
        console.print("[yellow]No profiles found.[/yellow]")
        return

    render_table(
        profiles_list,
        data.get("page", 1),
        data.get("total_pages", 1),
        data.get("total", 0)
    )


@app.command()
def create(name: str = typer.Option(..., "--name", help="Profile name")):
    """Create a new profile (admin only)."""
    with console.status(f"[bold green]Creating profile for '{name}'..."):
        response = api_request("POST", "/profiles", json={"name": name})

    if response.status_code == 403:
        console.print("[red]Permission denied. Admin role required.[/red]")
        raise typer.Exit(1)

    if response.status_code not in (200, 201):
        console.print(f"[red]Error:[/red] {response.json().get('message')}")
        raise typer.Exit(1)

    p = response.json().get("data", {})
    console.print(f"[green]Profile created:[/green] {p['name']} ({p['id']})")


@app.command()
def export(
    format: str = typer.Option("csv", "--format", help="Export format"),
    gender: str = typer.Option(None, help="Filter by gender"),
    country: str = typer.Option(None, "--country", help="Filter by country ID"),
    age_group: str = typer.Option(None, "--age-group", help="Filter by age group"),
):
    """Export profiles to a file."""
    if format != "csv":
        console.print("[red]Only CSV format is supported.[/red]")
        raise typer.Exit(1)

    params = {}
    if gender: params["gender"] = gender
    if country: params["country_id"] = country
    if age_group: params["age_group"] = age_group

    with console.status("[bold blue]Generating CSV export..."):
        response = api_request("GET", "/profiles/export", params=params)

    if response.status_code == 200:
        filename = "profiles_export.csv"
        with open(filename, "wb") as f:
            f.write(response.content)
        console.print(f"[green]Exported to[/green] {filename}")
    else:
        console.print("[red]Export failed. Check your permissions.[/red]")