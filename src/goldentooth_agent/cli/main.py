"""Main CLI application for Goldentooth Agent.

This module sets up the primary Typer application and registers all command groups.
"""

from typing import Annotated

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.traceback import install

# Configure rich traceback for better error messages
install(show_locals=True)

# Load environment variables
load_dotenv()

# Create console for rich output
console = Console()

# Main CLI application
app = typer.Typer(
    name="goldentooth-agent",
    help="""🦷 Goldentooth Agent - AI-powered document processing and chat.

A sophisticated AI agent system for document analysis, chat interactions,
and intelligent workflow automation.
""",
    rich_markup_mode="rich",
    pretty_exceptions_enable=True,
    pretty_exceptions_show_locals=False,
)


# Version callback
def version_callback(value: bool) -> None:
    """Print version information."""
    if value:
        console.print("🦷 Goldentooth Agent v0.1.0")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool,
        typer.Option("--version", "-v", callback=version_callback, help="Show version"),
    ] = False,
) -> None:
    """🦷 Goldentooth Agent - AI-powered document processing and chat."""
    pass


# Import and register command groups
from .commands import flow

# Register flow command group
app.add_typer(flow.app, name="flow")

# TODO: Import other command groups as they are implemented
# from .commands import agents, chat, tools, debug
# app.add_typer(agents.app, name="agents")
# app.add_typer(chat.app, name="chat")
# app.add_typer(tools.app, name="tools")
# app.add_typer(debug.app, name="debug")
