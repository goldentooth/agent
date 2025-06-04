from antidote import lazy
from pyee.asyncio import AsyncIOEventEmitter

@lazy.value
def get_event_emitter() -> AsyncIOEventEmitter:
  return AsyncIOEventEmitter()
