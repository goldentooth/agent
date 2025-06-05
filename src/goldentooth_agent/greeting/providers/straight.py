from antidote import implements
from ..provider import GreetingProvider
from ...persona import Persona
from datetime import datetime

@implements.protocol[GreetingProvider]().when(qualified_by=Persona.straight)
class StraightGreetingProvider(GreetingProvider):
  """A greeting provider that returns a straight greeting message."""

  async def get_greeting(self) -> str:
    """Return a straight greeting message."""
    current_date = datetime.now()
    if current_date.hour < 12:
      return "Good morning! How can I assist you today?"
    elif current_date.hour < 18:
      return "Good afternoon! How can I assist you today?"
    else:
      return "Good evening! How can I assist you today?"
