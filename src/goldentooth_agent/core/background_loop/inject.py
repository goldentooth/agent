from __future__ import annotations
from antidote import inject, injectable, lazy
import asyncio
from concurrent.futures import Future
from goldentooth_agent.core.logging import get_logger
from logging import Logger
import threading
from typing import Any

@injectable(factory_method='create')
class BackgroundEventLoop:
  """A class to manage an asyncio event loop in a background thread."""

  def __init__(self, logger: Logger = inject[get_logger(__name__)]):
    """Initialize the background event loop."""
    logger.debug("Initializing BackgroundEventLoop")
    self.loop = asyncio.new_event_loop()
    self.thread = threading.Thread(target=self._run_loop, daemon=True)
    self.thread.start()

  @classmethod
  def create(cls) -> BackgroundEventLoop:
    """Create a new instance of BackgroundEventLoop."""
    return cls()

  def _run_loop(self):
    """Run the asyncio event loop in a separate thread."""
    asyncio.set_event_loop(self.loop)
    self.loop.run_forever()

  @inject
  def submit(self, coroutine, logger: Logger = inject[get_logger(__name__)]):
    """Submit a coroutine to be run in the background event loop."""
    logger.debug(f"Submitting coroutine {coroutine} to background loop")
    return asyncio.run_coroutine_threadsafe(coroutine, self.loop)

@lazy
def get_background_loop() -> BackgroundEventLoop:
  """Get the background event loop instance."""
  return BackgroundEventLoop()

@inject
def run_in_background(
  coroutine,
  background_loop: BackgroundEventLoop = inject[get_background_loop()],
  logger: Logger = inject[get_logger(__name__)],
) -> Any:
  """Run a coroutine in the background event loop."""
  logger.debug(f"Running coroutine {coroutine} in background loop")
  return background_loop.submit(coroutine).result()
