"""Command-line interface for the Goldentooth Agent."""

from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from . import __version__
from .main import Agent

console = Console()
app = typer.Typer(
    name="goldentooth-agent",
    help="An experimental intelligent agent for Pi Bramble clusters.",
    rich_markup_mode="rich",
)


def version_callback(value: bool) -> None:
    """Show version information."""
    if value:
        console.print(f"goldentooth-agent version {__version__}")
        raise typer.Exit()


@app.callback()
def cli_main(
    version: Annotated[
        bool,
        typer.Option("--version", "-v", callback=version_callback, help="Show version"),
    ] = False,
) -> None:
    """Goldentooth Agent CLI."""
    pass


@app.command()
def status() -> None:
    """Show agent status."""
    agent = Agent()

    console.print(
        Panel(
            Text("Agent Status: Running", style="green bold"),
            title="[bold blue]Goldentooth Agent[/bold blue]",
            border_style="blue",
        )
    )

    console.print(f"[dim]Agent version: {__version__}[/dim]")
    console.print(f"[dim]Agent ID: {agent.get_id()}[/dim]")


@app.command()
def start() -> None:
    """Start the agent."""
    agent = Agent()

    console.print("[yellow]Starting Goldentooth Agent...[/yellow]")
    agent.start()
    console.print("[green]Agent started successfully![/green]")


@app.command()
def stop() -> None:
    """Stop the agent."""
    agent = Agent()

    console.print("[yellow]Stopping Goldentooth Agent...[/yellow]")
    agent.stop()
    console.print("[red]Agent stopped.[/red]")


@app.command()
def info() -> None:
    """Show detailed agent information."""
    agent = Agent()

    info_panel = Panel(
        f"""[bold]Agent Information[/bold]

Version: {__version__}
Agent ID: {agent.get_id()}
Status: Running
Type: Experimental Pi Bramble Agent

[dim]For more information, visit:[/dim]
[link]https://github.com/goldentooth/agent[/link]
""",
        title="[bold blue]Goldentooth Agent[/bold blue]",
        border_style="blue",
    )

    console.print(info_panel)


def main() -> None:
    """Main entry point for console scripts."""
    app()


if __name__ == "__main__":
    main()
