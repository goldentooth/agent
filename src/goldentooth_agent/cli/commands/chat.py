from __future__ import annotations
from antidote import inject
import asyncio
import typer
from typing_extensions import Annotated
from goldentooth_agent.core.chat import ChatOptions
from goldentooth_agent.core.thunk import trampoline, compose_chain

app = typer.Typer()

@app.command("chat")
def chat(
  ctx: typer.Context,
  straight: Annotated[
    bool, typer.Option(help="Whether to use straightness or not")
  ] = False,
):
  """Start a chat session with the Goldentooth Agent."""

  @inject
  def set_chat_options(chat_options: ChatOptions = inject.me()) -> None:
    """Set the chat options for the session."""
    chat_options.is_straight = straight

  set_chat_options()


  # ctx = AgentContext(
  #   agent=DefaultAgent(),
  #   tool_registry=ToolRegistry(),
  # )
  # loop = agent_chat_loop_th(ctx)
  # asyncio.run(trampoline(None, compose_chain(loop, final_thunk())))
