from antidote import lazy
from typer import Typer

@lazy
def get_repl_app() -> Typer:
  """Get the REPL application instance."""
  return Typer(
    name="goldentooth-repl",
    help="A REPL for the Golden Tooth Agent.",
    no_args_is_help=True,
    add_completion=False,
  )
