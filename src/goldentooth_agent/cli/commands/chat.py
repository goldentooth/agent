from __future__ import annotations
from antidote import world
import asyncio
import typer
from typing_extensions import Annotated
from goldentooth_agent.core.straightness import StraightnessOptions
from goldentooth_agent.core.agent.middleware import get_agent_th, inject_greeting_th
from goldentooth_agent.core.thunk import trampoline, compose_chain, final_thunk
from goldentooth_agent.core.tool import RequestUserInputTool, get_tool_registry_th, register_tools_th
from goldentooth_agent.core.chat import chat_loop_th

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
  thunks = compose_chain(
    get_tool_registry_th(),
    register_tools_th([RequestUserInputTool]),
    get_agent_th(),
    inject_greeting_th("assistant", "Hello, world!"),
    chat_loop_th(),
    final_thunk(),
  )
  asyncio.run(trampoline("Hello, world!", thunks))
