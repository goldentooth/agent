from __future__ import annotations
from antidote import world
import asyncio
import typer
from typing_extensions import Annotated
from goldentooth_agent.core.thunk import trampoline, compose_chain

app = typer.Typer()

@app.command("chat")
def chat(
  straight: Annotated[
    bool, typer.Option(help="Whether to use straightness or not")
  ] = False,
):
  """Start a chat session with the Goldentooth Agent."""

