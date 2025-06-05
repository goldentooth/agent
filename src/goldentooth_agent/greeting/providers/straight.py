from antidote import implements
from ..provider import GreetingProvider
from ...persona import Persona

@implements.protocol[GreetingProvider]().when(qualified_by=Persona.straight)
class StraightGreetingProvider(GreetingProvider):
  """A greeting provider that returns a straight greeting message."""

  async def get_greeting(self) -> str:
    """Return a straight greeting message."""
    return "Hello! How can I assist you today?"
