import typer
from antidote import world
import asyncio
from typing_extensions import Annotated
from goldentooth_agent.plugins.chat_session import core_loop
from goldentooth_agent.foundation.persona import PersonaOptions, Persona
from goldentooth_agent.core.chat_session import ChatSession, ChatSessionContext, ChatSessionPipeline, print_message_middleware
from goldentooth_agent.plugins.greeting.main import greeting

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
  pipeline.use(print_message_middleware("Starting chat...", "bold green"))
  pipeline.use(core_loop)
  pipeline.use(print_message_middleware("✌️"))
  asyncio.run(world[ChatSession].start(chat_session_context))
