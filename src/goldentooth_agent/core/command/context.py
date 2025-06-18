from antidote import inject
from atomic_agents.lib.base.base_io_schema import BaseIOSchema
from goldentooth_agent.core.context import context_key, SHOULD_EXIT_KEY
from goldentooth_agent.core.log import get_logger
from logging import Logger
from typer import Typer, Context as TyperContext
from .inject import get_command_typer
from .registry import enroll_command

COMMAND_INPUT_KEY = context_key("command_input", BaseIOSchema)
COMMAND_OUTPUT_KEY = context_key("command_output", BaseIOSchema)

@enroll_command
@inject
def enroll_exit_command(app: Typer = inject[get_command_typer()], logger: Logger = inject[get_logger(__name__)]) -> None:
  """Enroll the exit/quit command to exit the agent."""
  logger.debug("Enrolling exit command...")
  @app.command("exit", help="Exit the agent.")
  @app.command("quit", help="Exit the agent.", hidden=True)
  def exit_command(typer_context: TyperContext) -> None:
    """Exit the agent."""
    logger.debug("Executing quit command...")
    from goldentooth_agent.core.context import Context
    context: Context = typer_context.obj
    context.set(SHOULD_EXIT_KEY, True)
