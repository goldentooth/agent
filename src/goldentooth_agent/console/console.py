from antidote import lazy
from rich.console import Console

@lazy.value
def get_console() -> Console:
  return Console()