from __future__ import annotations
from antidote import inject
import asyncio
import typer

app = typer.Typer()


@app.command("chat")
def chat():
    """Start a chat session with the Goldentooth Agent."""

    @inject
    def handle() -> None:
        """Handle the chat session."""

    handle()
