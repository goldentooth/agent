from __future__ import annotations
from antidote import inject
import asyncio
from goldentooth_agent.core.context import Context
import typer

app = typer.Typer()

@app.command("chat")
def chat():
  """
  Start a chat session with the Goldentooth Agent.

  The chat session has a very simple structure.

  The user input is assumed to contain either a command (which always begins with a forward slash `/`)
  or a message to the agent. If the input is a command, it will be executed immediately, and control
  will return to the user. If the input is a message, it will be sent to the agent for processing, and
  the agent's response will be displayed to the user.
  """
  @inject
  def handle(ctx: Context = inject.me()) -> None:
    """Handle the chat session."""
    from goldentooth_agent.core.context import trampoline_chain
    from goldentooth_agent.core.intake import intake_chain
    from goldentooth_agent.core.command import command_chain
    from goldentooth_agent.core.agent import agent_chain
    from goldentooth_agent.core.display import display_chain
    chain = trampoline_chain(   # Run the chat session in a trampoline style.
      intake_chain(),           # Get user input from the console.
      command_chain(),          # Check for commands and run them if available.
      agent_chain(),            # Check for agent input and run the agent if available.
      display_chain(),          # Display the output to the console.
    )
    asyncio.run(chain(ctx))
  handle()
