from typing import List
from .base import ContextProviderBase

class CurrentDate(ContextProviderBase):
  """Context provider that provides information about the current date."""

  def get_instructions(self) -> List[str]:
    """Get instructions for the current date context provider."""
    date_string = self.initial_context.current_date.strftime("%Y-%m-%d")
    return [
      f"The current date is {date_string}.",
      "You can use this date to provide context for your responses.",
    ]

if __name__ == "__main__":
  # Example usage
  from ..initial_context import InitialContext
  from datetime import datetime

  initial_context = InitialContext(current_date=datetime.now())
  current_date_provider = CurrentDate(initial_context)

  print("Instructions:")
  for instruction in current_date_provider.get_instructions():
    print(f"- {instruction}")

  print("Current date context provided.")
