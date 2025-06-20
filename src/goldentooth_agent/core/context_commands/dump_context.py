from antidote import inject, world
from goldentooth_agent.core.background_loop import BackgroundEventLoop, run_in_background
from goldentooth_agent.core.command import get_command_typer, enroll_command
from goldentooth_agent.core.context import Context, dump_context
from goldentooth_agent.core.logging import get_logger
from logging import Logger
from typer import Typer, Context as TyperContext

@enroll_command
@inject
def enroll_dump_context_command(app: Typer = inject[get_command_typer()], logger: Logger = inject[get_logger(__name__)]) -> None:
  """Enroll the dump-context command."""
  logger.debug("Enrolling dump_context command...")
  @app.command("dump-context", help="Dump the context.")
  @app.command("dump_context", help="Dump the context.", hidden=True)
  def _command(typer_context: TyperContext) -> None:
    """Dump the context."""
    logger.debug("Executing dump-context command...")
    context: Context = typer_context.obj
    run_in_background(dump_context()(context))
