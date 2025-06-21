from antidote import inject
import logging
from typing import Any, Callable, TypeVar
from goldentooth_agent.core.context import Context
from goldentooth_agent.core.thunk import Thunk, compose_chain
from logging import Logger
from .inject import get_logger

def log_thunk(
  name: str,
  level: int = logging.INFO,
  fmt: Callable[[Context], str] = lambda ctx: str(ctx)
) -> Thunk[Context, Context]:
  """Thunk that logs the context with a given logger name and level."""
  from goldentooth_agent.core.logging import get_logger
  from antidote import inject
  @inject
  async def _log(ctx: Context, logger=inject[get_logger(name)]) -> Context:
    """Log the context using the specified logger and level."""
    logger.log(level, fmt(ctx))
    return ctx
  return Thunk(_log, name=f"log_thunk({name}, {logging.getLevelName(level)})", metadata={"fmt": fmt})

def on_event_log(event_name: str, logger_name: str, level: int = logging.INFO) -> None:
  """Listen for a thunk event and log it."""
  from goldentooth_agent.core.event import get_event_emitter
  from goldentooth_agent.core.logging import get_logger
  logger = world[get_logger(logger_name)]
  ee = world[get_event_emitter()]
  ee.on(event_name, lambda ctx: logger.log(level, f"[event={event_name}] {ctx}"))

def change_log_level(
  logger_name: str,
  level: int = logging.INFO
) -> Thunk[Any, Any]:
  """Change the log level of a logger."""
  @inject
  async def _change_log_level(_, logger: Logger = inject[get_logger(logger_name)]) -> Any:
    """Change the log level of the specified logger."""
    logger.debug(f"Changing log level for {logger_name} to {logging.getLevelName(level)}")
    logger.setLevel(level)
    logger.debug(f"Log level for {logger_name} changed to {logging.getLevelName(level)}")
    return _
  return Thunk(_change_log_level, name=f"change_log_level({logger_name}, {logging.getLevelName(level)})")

TIn = TypeVar('TIn')
TOut = TypeVar('TOut')

def with_log_level(
  logger_name: str,
  level: int = logging.INFO
) -> Callable[[Thunk[TIn, TOut]], Thunk[TIn, TOut]]:
  """Decorator to set the log level for a thunk and reset it afterward."""
  @inject
  def _decorator(fn: Thunk[TIn, TOut], logger: Logger = inject[get_logger(logger_name)]) -> Thunk[TIn, TOut]:
    """Set the log level for the thunk."""
    original_level = logger.level
    return compose_chain(
      change_log_level(logger_name, level),
      fn,
      change_log_level(logger_name, original_level),
    )
  return _decorator

if __name__ == "__main__":
  # Example usage
  from antidote import world
  import asyncio
  from goldentooth_agent.core.event import get_event_emitter
  from goldentooth_agent.core.logging import get_logger
  logger = world[get_logger(__name__)]
  my_thunk = log_thunk(__name__, logging.ERROR, lambda ctx: f"Context: {ctx}")
  result = asyncio.run(my_thunk(Context()))
  logger.debug(result)

  # Example usage of on_event_log
  on_event_log("test_event", __name__, logging.ERROR)
  ee = world[get_event_emitter()]
  ee.emit("test_event", "This is a test event")
  logger.info("Event emitted.")
