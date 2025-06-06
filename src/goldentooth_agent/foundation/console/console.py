from antidote import lazy
from rich.console import Console

@lazy.value
def get_console() -> Console:
  """Get a rich console instance for output."""
  return Console()
