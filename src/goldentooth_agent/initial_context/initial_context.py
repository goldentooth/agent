from datetime import datetime

class InitialContext:
  """Initial context class for initializing and managing the Goldentooth agent."""

  def __init__(self, *, current_date: datetime | None = None) -> None:
    """Initialize the context."""
    self.current_date = current_date or datetime.now()

  def get_greeting(self) -> str:
    """Get a greeting based on the current date."""
    if self.current_date.hour < 12:
      return "Good morning! How can I assist you today?"
    elif self.current_date.hour < 18:
      return "Good afternoon! How can I assist you today?"
    else:
      return "Good evening! How can I assist you today?"

if __name__ == "__main__":
  # Example usage
  context = InitialContext()
  print(context.get_greeting())
  print("Current date:", context.current_date)

  # You can also set a specific date
  specific_context = InitialContext(current_date=datetime(2023, 10, 1, 15, 30))
  print(specific_context.get_greeting())
  print("Specific date:", specific_context.current_date)
