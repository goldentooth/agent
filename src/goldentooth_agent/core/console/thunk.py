from antidote import inject
from atomic_agents.lib.base.base_io_schema import BaseIOSchema
from goldentooth_agent.core.context import Context, context_autothunk, SHOULD_EXIT_KEY, clear_key
from goldentooth_agent.core.thunk import Thunk
from rich.console import Console
from typing import Annotated
from .context import USER_INPUT_KEY, CONSOLE_OUTPUT_KEY
from .inject import get_console
from .schema import ConsoleOutputConvertible
from .tool import ConsoleTool, ConsoleInput, ConsoleOutput, ConsoleQuitOutput

def get_console_input() -> Thunk[Context, Context]:
  """Get a thunk that retrieves user input from the console."""
  @context_autothunk
  @inject
  async def _get_console_input(
    console_tool: ConsoleTool = inject.me(),
  ) -> Annotated[BaseIOSchema, USER_INPUT_KEY]:
    input_schema = ConsoleInput(prompt="You:", style="bold blue")
    console_tool.input_schema = ConsoleInput
    console_tool.output_schema = ConsoleOutput
    return console_tool.run(input_schema) # type: ignore
  return _get_console_input

def check_console_exit() -> Thunk[Context, Context]:
  """Check if the user input indicates a request to exit the console."""
  @context_autothunk
  async def _check_console_exit(
    user_input: Annotated[BaseIOSchema, USER_INPUT_KEY],
  ) -> Annotated[bool, SHOULD_EXIT_KEY]:
    """Check if the user input indicates an exit request."""
    return isinstance(user_input, ConsoleQuitOutput)
  return _check_console_exit

def prepare_console_output() -> Thunk[Context, Context]:
  """Create a thunk that prepares the console output."""
  @context_autothunk
  async def _prepare_agent_input(
    input: Annotated[BaseIOSchema, CONSOLE_OUTPUT_KEY],
  ) -> Annotated[BaseIOSchema, CONSOLE_OUTPUT_KEY]:
    """Prepare the agent input by ensuring it is in the correct format."""
    if isinstance(input, ConsoleOutputConvertible):
      return input.as_console_output()
    return input
  return _prepare_agent_input

def print_console_output() -> Thunk[Context, Context]:
  """Create a thunk that prints the console output."""
  @clear_key(CONSOLE_OUTPUT_KEY)
  @context_autothunk
  async def _print_console_output(
    output: Annotated[BaseIOSchema, CONSOLE_OUTPUT_KEY],
    console: Console = inject[get_console()],
  ) -> None:
    """Print the console output."""
    console.print(output)
  return _print_console_output
