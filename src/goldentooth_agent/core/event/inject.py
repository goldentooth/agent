from pyee import EventEmitter
from pyee.asyncio import AsyncIOEventEmitter

# Global singleton emitters
_sync_emitter = EventEmitter()
_async_emitter = AsyncIOEventEmitter()


def get_sync_event_emitter() -> EventEmitter:
    """Get an event emitter instance for synchronous event handling."""
    return _sync_emitter


def get_async_event_emitter() -> AsyncIOEventEmitter:
    """Get an asyncio event emitter instance for asynchronous event handling."""
    return _async_emitter
