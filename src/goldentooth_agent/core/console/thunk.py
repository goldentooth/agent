from antidote import inject
from atomic_agents.lib.base.base_io_schema import BaseIOSchema
from goldentooth_agent.core.context import Context, context_autothunk, SHOULD_EXIT_KEY
from goldentooth_agent.core.thunk import Thunk
from typing import Annotated
from .context import USER_INPUT_KEY
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