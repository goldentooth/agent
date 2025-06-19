from antidote import inject
from goldentooth_agent.core.command import get_command_typer, enroll_command
from goldentooth_agent.core.context import SHOULD_EXIT_KEY
from goldentooth_agent.core.logging import get_logger
from logging import Logger
from typer import Typer, Context as TyperContext

@enroll_command
@inject
def enroll_exit_command(app: Typer = inject[get_command_typer()], logger: Logger = inject[get_logger(__name__)]) -> None:
  """Enroll the exit command."""
  logger.debug("Enrolling exit command...")
  @app.command("exit", help="Exit the agent.")
  @app.command("quit", help="Exit the agent.", hidden=True)
  def _command(typer_context: TyperContext) -> None:
    """Exit the agent."""
    logger.debug("Executing quit command...")
    from goldentooth_agent.core.context import Context
    context: Context = typer_context.obj
    context.set(SHOULD_EXIT_KEY, True)
