import typer
from dotenv import load_dotenv

from . import commands

load_dotenv()

app = typer.Typer()
app.add_typer(commands.chat.app, help="Talk to the agent.")
app.add_typer(commands.tools.app, name="tools", help="Manage tools and utilities.")
