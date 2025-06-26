import typer
from rich.console import Console
from antidote import inject
from goldentooth_agent.core.console import get_console
from goldentooth_agent.core.tool import ToolRegistry

app = typer.Typer()


@app.command("list")
def list_tools() -> None:
    """List available tools."""

    @inject
    def handle(
        console: Console = inject[get_console()],
        tool_registry: ToolRegistry = inject.me(),
    ) -> None:
        """Handle the listing of tools."""
        tools = tool_registry.items()
        if not tools:
            console.print("[bold red]No tools registered.[/bold red]")
        else:
            console.print("[bold cyan]Available tools:[/bold cyan]")
            for tool_name, tool in tools:
                console.print(
                    f"- [bold cyan]{tool_name.split('.')[-1]}[/bold cyan]: {tool.tool_description}"
                )

    handle()
