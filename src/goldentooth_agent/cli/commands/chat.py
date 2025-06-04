import typer
from antidote import world
import asyncio
from typing_extensions import Annotated
from ...agent_config.persona import PersonaOptions, Persona
from ...chat.session import ChatSession, ChatSessionPipeline
from ...chat.session_middlewares import core_loop, greeting, farewell, starting_chat

app = typer.Typer()

def autocomplete_persona(incomplete: str) -> list[str]:
  """Autocomplete function for persona options."""
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
  options = world[PersonaOptions]
  options.persona = persona
  pipeline = world[ChatSessionPipeline]
  pipeline.use(starting_chat)
  pipeline.use(greeting)
  pipeline.use(core_loop)
  pipeline.use(farewell)
  asyncio.run(world[ChatSession].start())
