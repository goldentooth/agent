import typer
from dotenv import load_dotenv

from . import commands

load_dotenv()

app = typer.Typer()
app.add_typer(commands.chat.app, help="Talk to the agent.")
app.add_typer(commands.tools.app, name="tools", help="Manage tools and utilities.")
app.add_typer(commands.flow.app, name="flow", help="Execute and manage flows.")
app.add_typer(
    commands.context.app, name="context", help="Inspect and manage context state."
)
app.add_typer(commands.agents.app, name="agents", help="Manage agent instances.")
app.add_typer(
    commands.debug.app, name="debug", help="System debugging and diagnostics."
)
app.add_typer(
    commands.demo.app, name="demo", help="Interactive demonstrations and tutorials."
)
