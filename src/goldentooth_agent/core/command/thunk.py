from antidote import inject
from atomic_agents.lib.base.base_io_schema import BaseIOSchema
from goldentooth_agent.core.agent import set_should_skip_agent_key
from goldentooth_agent.core.command.context import COMMAND_INPUT_KEY, COMMAND_OUTPUT_KEY
from goldentooth_agent.core.context import Context, context_autothunk, copy_context, has_context_key, clear_context_key
from goldentooth_agent.core.display import DISPLAY_INPUT_KEY
from goldentooth_agent.core.logging import get_logger
from goldentooth_agent.core.thunk import Thunk, thunk, compose_chain, if_else
from logging import Logger
from typer import Typer
from typing import Annotated, Optional
from .context import COMMAND_INPUT_KEY, COMMAND_OUTPUT_KEY
from .inject import get_command_typer
from .registry import CommandRegistry
from .tool import CommandInput, CommandOutput, CommandTool

def setup_command_tool() -> Thunk[Context, Context]:
  """Set up the command tool in the context."""
  @thunk(name="setup_command_tool")
  @inject
  async def _setup_command_tool(
    ctx: Context,
    app: Typer = inject[get_command_typer()],
  ) -> Context:
    """Set up the command tool in the context."""
    return ctx
  return _setup_command_tool

def register_all_commands() -> Thunk[Context, Context]:
  """Register all commands in the command tool."""
  @thunk(name="register_all_commands")
  @inject
  async def _register_all_commands(
    ctx: Context,
    registry: CommandRegistry = inject.me(),
    app: Typer = inject[get_command_typer()],
    logger: Logger = inject[get_logger(__name__)]
  ) -> Context:
    """Register all commands in the command tool."""
    logger.debug("Registering all commands...")
    app.registered_commands.clear()  # Clear existing commands
    registry.register()
    logger.debug("All commands registered successfully.")
    return ctx
  return _register_all_commands

def prepare_command_input() -> Thunk[Context, Context]:
  """Check if the user input comprises a slash command."""
  @context_autothunk(name="prepare_command_input")
  @inject
  async def _prepare_command_input(
    command_input: Annotated[BaseIOSchema, COMMAND_INPUT_KEY],
    logger: Logger = inject[get_logger(__name__)],
  ) -> Annotated[Optional[BaseIOSchema], COMMAND_INPUT_KEY]:
    """Check if the user input contains a slash command."""
    from .schema import CommandInputConvertible
    logger.debug("Checking for commands in user input...")
    if isinstance(command_input, CommandInputConvertible):
      logger.debug("User input is convertible to a CommandInput, performing conversion...")
      command_input = command_input.as_command_input()
    if not isinstance(command_input, CommandInput):
      logger.debug("User input is not a CommandInput, returning None.")
      return None
    input = command_input.input
    if not input.startswith("/"):
      logger.debug("No command found in user input.")
      return None
    logger.debug("Command found, extracting...")
    command_input.input = command_input.input[1:]
    return command_input
  return _prepare_command_input

def run_command_tool() -> Thunk[Context, Context]:
  """Route slash-prefixed input to the REPL command handler."""
  @clear_context_key(COMMAND_INPUT_KEY)
  @context_autothunk(name="run_command_tool")
  @inject
  async def _run_command_tool(
    command_input: Annotated[BaseIOSchema, COMMAND_INPUT_KEY],
    context: Context,
    command_tool: CommandTool = inject.me(),
    logger: Logger = inject[get_logger(__name__)],
  ) -> Annotated[Optional[BaseIOSchema], COMMAND_OUTPUT_KEY]:
    """Run the command tool with the provided input."""
    logger.debug("Running command tool with provided input...")
    try:
      if not isinstance(command_input, CommandInput):
        logger.error("Command input is not of type CommandInput.")
        return None
      output = command_tool.run(command_input, context) # type: ignore[call-arg]
      logger.debug("Command tool executed successfully.")
      if isinstance(output, CommandOutput):
        logger.debug("Command tool returned a CommandOutput.")
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
  from goldentooth_agent.core.intake import INTAKE_KEY
  return compose_chain(
    setup_command_tool(),
    register_all_commands(),
    copy_context(INTAKE_KEY, COMMAND_INPUT_KEY),
    prepare_command_input(),
    if_else(
      has_context_key(COMMAND_INPUT_KEY),
      compose_chain(
        run_command_tool(),
        set_should_skip_agent_key(True),
        if_else(
          has_context_key(COMMAND_OUTPUT_KEY),
          copy_context(COMMAND_OUTPUT_KEY, DISPLAY_INPUT_KEY),
        ),
      ),
    ),
  )
