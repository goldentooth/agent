import typer
from rich import print
from antidote import world, inject
import asyncio
from typing_extensions import Annotated
from ...agent_config.persona import PersonaOptions, Persona
from ...chat.session import ChatSession, ChatSessionPipeline
from ...chat.session_middlewares import greeting_mw

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
  pipeline = world[ChatSessionPipeline]
  pipeline.use(greeting_mw)
  asyncio.run(world[ChatSession].start())
