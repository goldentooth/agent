import typer
from rich import print
from antidote import world, inject
import asyncio
from typing_extensions import Annotated
from ...agent_config.persona import PersonaOptions, Persona
from ...chat import ChatSession

app = typer.Typer()

def autocomplete_persona(incomplete: str) -> list[str]:
  completion = []
  for name in Persona.__members__.keys():
    if name.startswith(incomplete):
      completion.append(name)
  return completion

@app.command("chat")
def chat(
  persona: Annotated[
    Persona, typer.Option(help="Which persona to use.")
  ] = Persona.default,
):
  """Start a chat session with the Goldentooth Agent."""
  print(f"[bold green]Starting chat...[/bold green]")
  print(f"Persona: {persona}")
  options = world[PersonaOptions]
  options.persona = persona
  asyncio.run(world[ChatSession].start())
