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

if __name__ == "__main__":
  # Example usage
  from antidote import world
  console = world[get_console()]
  console.print("This is a test message.")

  error_console = world[get_error_console()]
  error_console.print("This is an error message.", style="bold red")
