from antidote import lazy
from typer import Typer

@lazy
def get_command_typer() -> Typer:
  """Get the command Typer instance."""
  return Typer(
    name="goldentooth-agent",
    help="A command processor for the Goldentooth Agent.",
    no_args_is_help=True,
    add_completion=False,
  )

