import logging
from typing import Any, Callable
from goldentooth_agent.core.thunk import Thunk

def log_thunk(
  name: str,
  level: int = logging.INFO,
  fmt: Callable[[Any], str] = lambda ctx: str(ctx)
) -> Thunk[Any, Any]:
  """Thunk that logs the context with a given logger name and level."""
  from goldentooth_agent.core.log import get_logger
  from antidote import inject
  @inject
  async def _log(ctx, logger=inject[get_logger(name)]):
    """Log the context using the specified logger and level."""
    logger.log(level, fmt(ctx))
    return ctx
  return Thunk(_log)

def on_event_log(event_name: str, logger_name: str, level: int = logging.INFO) -> None:
  """Listen for a thunk event and log it."""
  from goldentooth_agent.core.event import get_event_emitter
  from goldentooth_agent.core.log import get_logger
  logger = world[get_logger(logger_name)]
  ee = world[get_event_emitter()]
  ee.on(event_name, lambda ctx: logger.log(level, f"[event={event_name}] {ctx}"))

if __name__ == "__main__":
  # Example usage
  from antidote import world
  import asyncio
  from goldentooth_agent.core.event import get_event_emitter
  from goldentooth_agent.core.log import get_logger
  logger = world[get_logger(__name__)]
  thunk = log_thunk(__name__, logging.ERROR, lambda ctx: f"Context: {ctx}")
  result = asyncio.run(thunk("Test context"))
  logger.debug(result)

  # Example usage of on_event_log
  on_event_log("test_event", __name__, logging.ERROR)
  ee = world[get_event_emitter()]
  ee.emit("test_event", "This is a test event")
  logger.info("Event emitted.")
