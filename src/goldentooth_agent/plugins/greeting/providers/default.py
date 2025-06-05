from antidote import implements
from goldentooth_agent.foundation.message_provider import MessageProvider
from goldentooth_agent.foundation.persona import Persona

@implements.protocol[MessageProvider]().when(qualified_by=["greeting", Persona.default])
class DefaultGreetingProvider(MessageProvider):
  """A greeting provider that returns a greeting message for the default persona."""

  async def get_message(self) -> str:
    """Return a straight greeting message."""
    return "Oh god, it's you again."
