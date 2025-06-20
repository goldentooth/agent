from antidote import inject, lazy
import asyncio
from concurrent.futures import Future
import threading
from typing import Any

class BackgroundEventLoop:
  """A class to manage an asyncio event loop in a background thread."""

  def __init__(self):
    """Initialize the background event loop."""
    self.loop = asyncio.new_event_loop()
    self.thread = threading.Thread(target=self._run_loop, daemon=True)
    self.thread.start()

  def _run_loop(self):
    """Run the asyncio event loop in a separate thread."""
    asyncio.set_event_loop(self.loop)
    self.loop.run_forever()

  def submit(self, coroutine):
    """Submit a coroutine to be run in the background event loop."""
    return asyncio.run_coroutine_threadsafe(coroutine, self.loop)

@lazy
def get_background_loop() -> BackgroundEventLoop:
  """Get the background event loop instance."""
  return BackgroundEventLoop()

@inject
def run_in_background(coroutine, background_loop: BackgroundEventLoop = inject[get_background_loop()]):
  """Run a coroutine in the background event loop."""
  return background_loop.submit(coroutine).result()
