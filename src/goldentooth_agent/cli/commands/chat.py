from __future__ import annotations
from antidote import inject
import asyncio
from goldentooth_agent.core.context import Context
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
  @inject
  def handle(
    ctx: Context = inject.me(),
  ) -> None:
    """Handle the chat session."""
    from goldentooth_agent.core.agent import agent_chain, inject_agent, inject_agent_prefix
    from goldentooth_agent.core.command import command_chain, register_all_commands, setup_command_tool
    from goldentooth_agent.core.context import trampoline_chain
    from goldentooth_agent.core.display import display_chain
    from goldentooth_agent.core.intake import get_intake
    from goldentooth_agent.core.thunk import compose_chain
    chain = compose_chain(
      setup_command_tool(),     # Set up the command tool in the context.
      register_all_commands(),  # Register all commands.
      inject_agent(),           # Inject the agent into the context.
      inject_agent_prefix(),    # Inject the agent's output prefix.
      trampoline_chain(         # Run the chat session in a trampoline style.
        get_intake(),           # Get user input from the console.
        command_chain(),        # Check for commands and run them if available.
        agent_chain(),          # Check for agent input and run the agent if available.
        display_chain(),        # Display the output to the console.
      ),
    )
    asyncio.run(chain(ctx))
  handle()
