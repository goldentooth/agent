from __future__ import annotations
from antidote import inject
import asyncio
from goldentooth_agent.core.agent import prepare_agent_input, run_agent, inject_agent, inject_agent_text, AGENT_INPUT_KEY, AGENT_OUTPUT_KEY
from goldentooth_agent.core.console import get_console_input, prepare_console_output, print_console_output, print_newline, check_console_exit, USER_INPUT_KEY, CONSOLE_OUTPUT_KEY
from goldentooth_agent.core.context import Context, trampoline_chain, move_context
from goldentooth_agent.core.thunk import compose_chain
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
    chain = inject_agent() \
      .chain(inject_agent_text()) \
      .chain(
        trampoline_chain(
          get_console_input(),
          check_console_exit(),
          move_context(USER_INPUT_KEY, AGENT_INPUT_KEY),
          prepare_agent_input(),
          run_agent(),
          move_context(AGENT_OUTPUT_KEY, CONSOLE_OUTPUT_KEY),
          prepare_console_output(),
          print_newline(),
          print_console_output(),
        )
      )
    asyncio.run(chain(ctx))
  handle()
