from antidote import implements
from goldentooth_agent.foundation.message_provider import MessageProvider
from goldentooth_agent.foundation.persona import Persona
from datetime import datetime

@implements.protocol[MessageProvider]().when(qualified_by=["greeting", Persona.straight])
class StraightGreetingProvider(MessageProvider):
  """A greeting provider that returns a straight greeting message."""

  async def get_message(self) -> str:
    """Return a straight greeting message."""
    current_date = datetime.now()
    if current_date.hour < 12:
      return "Good morning! How can I assist you today?"
    elif current_date.hour < 18:
      return "Good afternoon! How can I assist you today?"
    else:
      return "Good evening! How can I assist you today?"
