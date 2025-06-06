from antidote import interface
from typing import Protocol, runtime_checkable

@interface
@runtime_checkable
class MessageProvider(Protocol):
  """Abstract base class for message providers, which just provide a message."""

  async def get_message(self) -> str: ...
