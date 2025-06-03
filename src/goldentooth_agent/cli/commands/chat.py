import typer
from dataclasses import dataclass
from rich import print
from antidote import world, injectable, inject
import asyncio
from typing import TYPE_CHECKING
from typing_extensions import Annotated
from ...chat import ChatOptions, ChatPersona, ChatSession

app = typer.Typer()

def autocomplete_persona(incomplete: str) -> list[str]:
  completion = []
  for name in ChatPersona.__members__.keys():
    if name.startswith(incomplete):
      completion.append(name)
  return completion

@inject
def is_chat_persona(value: str, current: str = inject[ChatOptions.persona]) -> bool: # type: ignore
  """Check if the given value matches the current chat persona."""
  return value == current

@app.command("chat")
def chat(
  persona: Annotated[
    ChatPersona, typer.Option(help="Which persona to use.")#, autocompletion=autocomplete_persona)
  ] = ChatPersona.default,
  tool_mode: Annotated[
    bool, typer.Option(help="Specialized tool-focused mode.")
  ] = False,
  raw: Annotated[
    bool, typer.Option(help="Bypass personality modifiers.")
  ] = False,
):
  """Start a chat session with the Goldentooth Agent."""
  print(f"[bold green]Starting chat...[/bold green]")
  print(f"Persona: {persona}, Tool Mode: {tool_mode}, Raw: {raw}")
  options = world[ChatOptions]
  options.persona = persona
  options.tool_mode = tool_mode
  options.raw = raw
  asyncio.run(world[ChatSession].start())
