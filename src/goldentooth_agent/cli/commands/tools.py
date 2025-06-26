import typer
from rich.console import Console
from antidote import inject

app = typer.Typer()


@app.command("list")
def list_tools() -> None:
    """List available tools."""

    @inject
    def handle(
    ) -> None:
        """Handle the listing of tools."""
    handle()
