from antidote import inject
from goldentooth_agent.core.agent import dump_agent_registry
from goldentooth_agent.core.background_loop import run_in_background
from goldentooth_agent.core.command import get_command_typer, enroll_command
from goldentooth_agent.core.context import Context
from goldentooth_agent.core.logging import get_logger
from logging import Logger
from typer import Typer, Context as TyperContext

@enroll_command
@inject
def enroll_dump_agent_registry_command(
  app: Typer = inject[get_command_typer()],
  logger: Logger = inject[get_logger(__name__)],
) -> None:
  """Enroll the dump-agent-registry command."""
  logger.debug("Enrolling dump-agent-registry command...")
  @app.command("dump-agent-registry", help="Dump the agent registry.")
  @app.command("dump_agent_registry", help="Dump the agent registry.", hidden=True)
  def _command(typer_context: TyperContext) -> None:
    """Dump the context."""
    logger.debug("Executing dump-context command...")
    context: Context = typer_context.obj
    run_in_background(dump_agent_registry()(context))
