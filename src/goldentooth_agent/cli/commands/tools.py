import typer
from rich import print
from rich.console import Console
from antidote import world, inject
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
    tools = tool_registry.keys()
    if not tools:
      console.print("[bold red]No tools registered.[/bold red]")
    else:
      console.print("[bold cyan]Available tools:[/bold cyan]")
      for tool in tools:
        console.print(f"- {tool}")
  handle()
