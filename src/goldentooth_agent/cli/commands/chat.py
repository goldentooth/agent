import typer
from rich import print
from antidote import world
import asyncio
from typing import TYPE_CHECKING
from ...chat import ChatSession

app = typer.Typer()

@app.command("chat")
def chat(
  persona: str = typer.Option("default", help="Which persona to use."),
  tool_mode: str = typer.Option(None, help="Specialized tool-focused mode."),
  raw: bool = typer.Option(False, help="Bypass personality modifiers.")
):
  """Start a chat session with the Goldentooth Agent."""
  print(f"[bold green]Starting chat...[/bold green]")
  print(f"Persona: {persona}, Tool Mode: {tool_mode}, Raw: {raw}")
  asyncio.run(world[ChatSession].start())
