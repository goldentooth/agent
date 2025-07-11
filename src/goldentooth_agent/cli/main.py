"""Main CLI application for Goldentooth Agent.

This module sets up the primary Typer application and registers all command groups.
"""

from typing import Annotated

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.traceback import install


def _extract_color_options_from_context(ctx: typer.Context) -> dict[str, bool]:
    """Extract color options from unknown arguments in context.

    Args:
        ctx: Typer context containing unknown arguments

    Returns:
        Dictionary with no_color and plain boolean values
    """
    unknown_args = getattr(ctx, "args", [])
    return {
        "no_color": "--no-color" in unknown_args,
        "plain": "--plain" in unknown_args,
    }


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
    context_settings={"ignore_unknown_options": True},
)


# Version callback
def version_callback(value: bool) -> None:
    """Print version information."""
    if value:
        console.print("🦷 Goldentooth Agent v0.1.0")
        raise typer.Exit()


# Global state for CLI options
_global_cli_options = {
    "no_color": False,
    "plain": False,
}


@app.callback()
def main(
    ctx: typer.Context,
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            "-v",
            callback=version_callback,
            help="Show version",
            is_eager=True,
        ),
    ] = False,
    no_color: Annotated[
        bool,
        typer.Option("--no-color", help="Disable colored output"),
    ] = False,
    plain: Annotated[
        bool,
        typer.Option("--plain", help="Use plain text output without formatting"),
    ] = False,
) -> None:
    """🦷 Goldentooth Agent - AI-powered document processing and chat."""
    # Extract color options from unknown arguments
    extra_options = _extract_color_options_from_context(ctx)

    # Store global options (unknown args take precedence)
    _global_cli_options["no_color"] = no_color or extra_options["no_color"]
    _global_cli_options["plain"] = plain or extra_options["plain"]

    # Store context for subcommands
    ctx.obj = _global_cli_options


def get_global_cli_options() -> dict[str, bool]:
    """Get global CLI options for use in subcommands."""
    return _global_cli_options.copy()


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
