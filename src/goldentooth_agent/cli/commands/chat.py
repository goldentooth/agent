from __future__ import annotations
import typer
from antidote import world
import asyncio
from typing_extensions import Annotated
from goldentooth_agent.core.chat_session import ChatSession, ChatSessionContext, ChatSessionPipeline, print_message_middleware
from goldentooth_agent.core.straightness import StraightnessOptions
from goldentooth_agent.plugins.chat_session import core_loop
from goldentooth_agent.plugins.greeting.main import greeting

app = typer.Typer()

@app.command("chat")
def chat(
  straight: Annotated[
    bool, typer.Option(help="Whether to use straightness or not")
  ] = False,
):
  """Start a chat session with the Goldentooth Agent."""
  options = world[StraightnessOptions]
  options.enabled = straight
  chat_session_context = world[ChatSessionContext]
  chat_session_context.loop_action = greeting
  pipeline = world[ChatSessionPipeline]
  pipeline.use(print_message_middleware("Starting chat...", "bold green"))
  pipeline.use(core_loop)
  pipeline.use(print_message_middleware("✌️"))
  asyncio.run(world[ChatSession].start(chat_session_context))
