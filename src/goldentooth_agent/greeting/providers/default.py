from antidote import implements
from ..provider import GreetingProvider
from ...persona import Persona

@implements.protocol[GreetingProvider]().when(qualified_by=Persona.default)
class DefaultGreetingProvider(GreetingProvider):
  """A greeting provider that returns a greeting message for the default persona."""

  async def get_greeting(self) -> str:
    """Return a straight greeting message."""
    return "Oh god, it's you again."
