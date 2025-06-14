from __future__ import annotations
import asyncio
import typer
from typing_extensions import Annotated

app = typer.Typer()

@app.command("chat")
def chat(
  ctx: typer.Context,
  straight: Annotated[
    bool, typer.Option(help="Whether to use straightness or not")
  ] = False,
):
  """Start a chat session with the Goldentooth Agent."""
