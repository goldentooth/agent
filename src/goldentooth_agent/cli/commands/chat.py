from __future__ import annotations
from antidote import world
import asyncio
import typer
from typing_extensions import Annotated
from goldentooth_agent.core.agent import AgentContext, DefaultAgent, agent_chat_loop_th
from goldentooth_agent.core.straightness import StraightnessOptions
from goldentooth_agent.core.thunk import trampoline, compose_chain, final_thunk
from goldentooth_agent.core.tool import ToolRegistry

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
  ctx = AgentContext(
    agent=DefaultAgent(),
    tool_registry=ToolRegistry(),
  )
  loop = agent_chat_loop_th(ctx)
  asyncio.run(trampoline(None, compose_chain(loop, final_thunk())))
