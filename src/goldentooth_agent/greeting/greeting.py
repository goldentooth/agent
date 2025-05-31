from ..initial_context import InitialContext

class Greeting:
  """A class to provide greetings based on the current date and time."""

  @staticmethod
  def get(initial_context: InitialContext) -> str:
    """Get a greeting based on the current date."""
    if initial_context.current_date.hour < 12:
      return "Good morning! How can I assist you today?"
    elif initial_context.current_date.hour < 18:
      return "Good afternoon! How can I assist you today?"
    else:
      return "Good evening! How can I assist you today?"

if __name__ == "__main__":
  # Example usage
  from datetime import datetime

  initial_context = InitialContext(current_date=datetime.now())
  greeting = Greeting.get(initial_context)
  print(greeting)
  # Output will vary based on the current time of day
  # Example output:
  # Good afternoon! How can I assist you today?
