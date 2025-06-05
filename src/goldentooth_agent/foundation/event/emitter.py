from antidote import lazy
from pyee.asyncio import AsyncIOEventEmitter

@lazy.value
def get_event_emitter() -> AsyncIOEventEmitter:
  """Get an asyncio event emitter instance for asynchronous event handling."""
  return AsyncIOEventEmitter()
