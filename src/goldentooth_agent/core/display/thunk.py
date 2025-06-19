from antidote import inject
from atomic_agents.lib.base.base_io_schema import BaseIOSchema
from atomic_agents.agents.base_agent import BaseAgentOutputSchema
from goldentooth_agent.core.agent import AGENT_PREFIX_KEY
from goldentooth_agent.core.console import get_console
from goldentooth_agent.core.context import Context, context_autothunk, clear_context_key, has_context_key
from goldentooth_agent.core.thunk import Thunk, compose_chain, if_else
from goldentooth_agent.core.logging import get_logger
from logging import Logger
from rich.console import Console
from typing import Annotated, Optional
from .context import DISPLAY_INPUT_KEY
from .schema import DisplayInputConvertible, DisplayInputAdapter
from .tool import DisplayInput

def prepare_display_input() -> Thunk[Context, Context]:
  """Create a thunk that prepares text for display to the user."""
  @context_autothunk(name="prepare_display_input")
  @inject
  async def _prepare_display_input(
    input: Annotated[BaseIOSchema, DISPLAY_INPUT_KEY],
    agent_prefix: Annotated[str, AGENT_PREFIX_KEY],
    logger: Logger = inject[get_logger(__name__)],
  ) -> Annotated[Optional[BaseIOSchema], DISPLAY_INPUT_KEY]:
    """Prepare the agent input by ensuring it is in the correct format."""
    logger.debug("Preparing display input...")
    if isinstance(input, BaseAgentOutputSchema):
      return DisplayInputAdapter(input, agent_prefix).as_display_input()
    elif isinstance(input, DisplayInputConvertible):
      return input.as_display_input()
    elif isinstance(input, DisplayInput):
      return input
    else:
      logger.debug(f"Input is not convertible to DisplayInput: {input}")
      return None
  return _prepare_display_input

def display_newline() -> Thunk[Context, Context]:
  """Create a thunk that prints a line to the console."""
  @context_autothunk(name="display_newline")
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
  @clear_context_key(DISPLAY_INPUT_KEY)
  @context_autothunk(name="display_output")
  @inject
  async def _display_output(
    display: Annotated[BaseIOSchema, DISPLAY_INPUT_KEY],
    console: Console = inject[get_console()],
    logger: Logger = inject[get_logger(__name__)]
  ) -> None:
    """Print the console output."""
    logger.debug("Displaying output to the console...")
    if isinstance(display, DisplayInput):
      console.print(display.output)
  return _display_output

def display_chain() -> Thunk[Context, Context]:
  """Create a thunk chain for console output operations."""
  return compose_chain(
    if_else(
      has_context_key(DISPLAY_INPUT_KEY),
      compose_chain(
        prepare_display_input(),
        if_else(
          has_context_key(DISPLAY_INPUT_KEY),
          compose_chain(
            display_newline(),
            display_output(),
          ),
        ),
      ),
    ),
  )
