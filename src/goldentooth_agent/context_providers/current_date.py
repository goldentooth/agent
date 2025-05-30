from typing import List
from .base import ContextProviderBase

class CurrentDate(ContextProviderBase):
  """Context provider that provides information about the current date."""

  def get_instructions(self) -> List[str]:
    date_string = self.initial_context.current_date.strftime("%Y-%m-%d")
    return [
      f"The current date is {date_string}.",
      "You can use this date to provide context for your responses.",
    ]
