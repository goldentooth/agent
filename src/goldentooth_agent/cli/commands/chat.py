import typer
from antidote import world
import asyncio
from typing_extensions import Annotated
from ...atoms.chat_session_middlewares import core_loop, farewell, starting_chat
from ...persona import PersonaOptions, Persona
from ...chat_session import ChatSession, ChatSessionContext, ChatSessionPipeline
from ...greeting.loop_actions import greeting

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
  chat_session_context = world[ChatSessionContext]
  chat_session_context.loop_action = greeting
  pipeline = world[ChatSessionPipeline]
  pipeline.use(starting_chat)
  pipeline.use(core_loop)
  pipeline.use(farewell)
  asyncio.run(world[ChatSession].start(chat_session_context))
