from antidote import inject
from atomic_agents.lib.base.base_io_schema import BaseIOSchema
from goldentooth_agent.core.console import get_console
from goldentooth_agent.core.context import Context, context_autothunk, clear_context_key, has_context_key
from goldentooth_agent.core.thunk import Thunk, compose_chain, if_else
from goldentooth_agent.core.logging import get_logger
from logging import Logger
from rich.console import Console
from typing import Annotated
from .context import DISPLAY_KEY
from .schema import DisplayInputConvertible

def prepare_display_input() -> Thunk[Context, Context]:
  """Create a thunk that prepares text for display to the user."""
  @context_autothunk
  async def _prepare_display_input(
    input: Annotated[BaseIOSchema, DISPLAY_KEY],
    logger: Logger = inject[get_logger(__name__)],
  ) -> Annotated[BaseIOSchema, DISPLAY_KEY]:
    """Prepare the agent input by ensuring it is in the correct format."""
    logger.debug("Preparing display input...")
    if isinstance(input, DisplayInputConvertible):
      return input.as_display_input()
    return input
  return _prepare_display_input

def display_newline() -> Thunk[Context, Context]:
  """Create a thunk that prints a line to the console."""
  @context_autothunk
  @inject
  async def _print_line(
    console: Console = inject[get_console()],
    logger: Logger = inject[get_logger(__name__)]
  ) -> None:
    """Print a line to the console."""
    logger.debug("Printing a newline to the console...")
    console.print()
  return _print_line

def display_output() -> Thunk[Context, Context]:
  """Create a thunk that prints the console output."""
  @clear_context_key(DISPLAY_KEY)
  @context_autothunk
  @inject
  async def _display_output(
    display: Annotated[BaseIOSchema, DISPLAY_KEY],
    console: Console = inject[get_console()],
    logger: Logger = inject[get_logger(__name__)]
  ) -> None:
    """Print the console output."""
    logger.debug("Displaying output to the console...")
    if hasattr(display, 'output'):
      console.print(display.output) # type: ignore
    else:
      console.print(display)
  return _display_output

def display_chain() -> Thunk[Context, Context]:
  """Create a thunk chain for console output operations."""
  return compose_chain(
    if_else(
      has_context_key(DISPLAY_KEY),
      prepare_display_input(),
      if_else(
        has_context_key(DISPLAY_KEY),
        compose_chain(
          display_newline(),
          display_output(),
        ),
      ),
    ),
  )
