from antidote import inject
from atomic_agents.lib.base.base_io_schema import BaseIOSchema
from goldentooth_agent.core.context import Context, context_autothunk, copy_context, has_context_key
from goldentooth_agent.core.display import DISPLAY_KEY
from goldentooth_agent.core.intake import INTAKE_KEY
from goldentooth_agent.core.log import get_logger
from goldentooth_agent.core.thunk import Thunk, compose_chain, if_else
from goldentooth_agent.core.tool import thunkify_tool
from logging import Logger
from typing import Annotated, Optional
from .context import COMMAND_INPUT_KEY, COMMAND_OUTPUT_KEY
from .tool import CommandInput, CommandOutput, CommandTool

def prepare_command_input() -> Thunk[Context, Context]:
  """Check if the user input comprises a slash command."""
  @context_autothunk
  async def _prepare_command_input(
    command_input: Annotated[BaseIOSchema, COMMAND_INPUT_KEY],
  ) -> Annotated[Optional[BaseIOSchema], COMMAND_INPUT_KEY]:
    """Check if the user input contains a slash command."""
    from .schema import CommandInputConvertible
    print("Checking for commands in user input...")
    if isinstance(command_input, CommandInputConvertible):
      print("User input is convertible to a CommandInput, performing conversion...")
      command_input = command_input.as_command_input()
    if not isinstance(command_input, CommandInput):
      print("User input is not a CommandInput, returning None.")
      return None
    input = command_input.input
    if not input.startswith("/"):
      print("No command found in user input.")
      return None
    print("Command found, extracting...")
    command_input.input = command_input.input[1:]
    return command_input
  return _prepare_command_input

def run_command_tool() -> Thunk[Context, Context]:
  """Route slash-prefixed input to the REPL command handler."""
  @context_autothunk
  @inject
  async def _run_command_tool(
    command_input: Annotated[BaseIOSchema, COMMAND_INPUT_KEY],
    command_tool: CommandTool = inject.me(),
    logger: Logger = inject[get_logger(__name__)],
  ) -> Annotated[Optional[BaseIOSchema], COMMAND_OUTPUT_KEY]:
    """Run the command tool with the provided input."""
    tool_thunk = thunkify_tool(command_tool)
    print("Running command tool with provided input...")
    try:
      output = await tool_thunk(command_input)
      print("Command tool executed successfully.")
      if isinstance(output, CommandOutput):
        print("Command tool returned a CommandOutput.")
        return output
      else:
        logger.warning("Command tool did not return a CommandOutput.")
        return None
    except Exception as e:
      logger.error(f"Error running command tool: {e}")
      return None
  return _run_command_tool

def command_chain() -> Thunk[Context, Context]:
  """Create a thunk that composes the command chain."""
  return compose_chain(
    copy_context(INTAKE_KEY, COMMAND_INPUT_KEY),
    prepare_command_input(),
    if_else(
      has_context_key(COMMAND_INPUT_KEY),
      compose_chain(
        run_command_tool(),
        if_else(
          has_context_key(COMMAND_INPUT_KEY),
          copy_context(COMMAND_OUTPUT_KEY, DISPLAY_KEY),
        ),
      ),
    ),
  )
