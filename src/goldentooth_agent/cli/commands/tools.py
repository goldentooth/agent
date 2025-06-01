import typer
from rich import print

app = typer.Typer()

@app.command("list")
def list_tools():
  """List available tools."""
  print("[bold cyan]Available tools:[/bold cyan]")
  # TODO: Query DI registry
  print("- log_sifter")
  print("- chaos_injector")
  print("- blog_writer")

@app.command("run")
def run_tool(name: str, args: str = typer.Option("", help="Optional args as string or JSON.")):
  """Run a specific tool."""
  print(f"[bold yellow]Running tool:[/bold yellow] {name}")
  print(f"With args: {args}")
  # TODO: Resolve tool from registry and run with args
