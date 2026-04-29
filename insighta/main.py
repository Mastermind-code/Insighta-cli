import typer
from insighta.auth import app as auth_app
from insighta.profiles import app as profiles_app

app = typer.Typer(help="Insighta Labs+ Profile Intelligence CLI")

app.add_typer(auth_app, name="auth")
app.add_typer(profiles_app, name="profiles")

if __name__ == "__main__":
    app()