from __future__ import annotations
from antidote import world
import asyncio
import typer
from typing_extensions import Annotated
from goldentooth_agent.core.straightness import StraightnessOptions
from goldentooth_agent.core.agent.middleware import inject_greeting_th
from goldentooth_agent.core.thunk import trampoline, compose_chain, final_thunk
from goldentooth_agent.core.console import console_input_th, exit_on_input_th
from goldentooth_agent.core.schema.input import wrap_input_th

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
    inject_greeting_th("assistant", "Hello, world!"),
    console_input_th(),
    exit_on_input_th(),
    wrap_input_th(),
    final_thunk(),
  )
  asyncio.run(trampoline("Hello, world!", thunks))
