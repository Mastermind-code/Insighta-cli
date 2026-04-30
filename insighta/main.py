import typer
from insighta.auth import login, logout, whoami
from insighta.profiles import app as profiles_app
from insighta.admin import app as admin_app

app = typer.Typer(help="Insighta Labs+ Profile Intelligence CLI")

# Top-level auth commands (insighta login / logout / whoami)
app.command("login")(login)
app.command("logout")(logout)
app.command("whoami")(whoami)

# Profiles subcommand group
app.add_typer(profiles_app, name="profiles")

# Admin subcommand group
app.add_typer(admin_app, name="admin")

if __name__ == "__main__":
    app()
