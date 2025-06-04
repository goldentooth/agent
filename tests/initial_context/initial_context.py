from datetime import datetime

class InitialContext:
  """Initial context class for initializing and managing the Goldentooth agent."""

  def __init__(self, *, current_date: datetime | None = None) -> None:
    """Initialize the context."""
    self.current_date = current_date or datetime.now()

if __name__ == "__main__":
  # Example usage
  context = InitialContext()
  print("Current date:", context.current_date)
