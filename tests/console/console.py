from antidote import lazy
from rich.console import Console

@lazy
def get_console() -> Console:
  """Get a rich console instance for output."""
  return Console()

@lazy
def get_error_console() -> Console:
  """Get a rich console instance for error output."""
  return Console(stderr=True)
