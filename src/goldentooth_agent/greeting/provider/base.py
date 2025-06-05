from antidote import interface
from typing import Protocol, runtime_checkable

@interface
@runtime_checkable
class GreetingProvider(Protocol):
  """Abstract base class for greeting providers."""

  async def get_greeting(self) -> str: ...
