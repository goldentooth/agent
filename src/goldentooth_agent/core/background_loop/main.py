from __future__ import annotations

import asyncio
import atexit
import logging
import threading
from collections.abc import Coroutine
from concurrent.futures import Future
from typing import Any, TypeVar

from antidote import inject, injectable

logger = logging.getLogger(__name__)

T = TypeVar("T")

# Type alias for coroutines - we don't use send/yield types
AnyCoroutine = Coroutine[Any, Any, T]  # type: ignore[explicit-any]


@injectable(factory_method="create")
class BackgroundEventLoop:
    """A class to manage an asyncio event loop in a background thread."""

    def __init__(self) -> None:
        """Initialize the background event loop."""
        self.loop = asyncio.new_event_loop()
        self._running = True
        self._shutdown_complete = threading.Event()
        self.thread = threading.Thread(
            target=self._run_loop, daemon=True, name="BackgroundEventLoop"
        )
        self.thread.start()
        # Register cleanup on exit
        atexit.register(self.shutdown)

    @classmethod
    def create(cls) -> BackgroundEventLoop:
        """Create a new instance of BackgroundEventLoop."""
        return cls()

    def _run_loop(self) -> None:
        """Run the asyncio event loop in a separate thread."""
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_forever()
        finally:
            self.loop.close()
            self._shutdown_complete.set()

    @inject
    def submit(self, coroutine: AnyCoroutine[T]) -> Future[T]:
        """Submit a coroutine to be run in the background event loop.

        Args:
            coroutine: The coroutine to run

        Returns:
            A Future that will contain the result

        Raises:
            RuntimeError: If the event loop is not running
        """
        if not self._running:
            raise RuntimeError("Background event loop is not running")
        return asyncio.run_coroutine_threadsafe(coroutine, self.loop)

    def shutdown(self, timeout: float = 5.0) -> None:
        """Shutdown the background event loop gracefully.

        Args:
            timeout: Maximum time to wait for shutdown in seconds
        """
        if not self._running:
            return

        self._running = False

        # Schedule loop stop in the event loop thread
        if self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)

        # Wait for the thread to complete
        self._shutdown_complete.wait(timeout)

        if self.thread.is_alive():
            logger.warning("Background event loop thread did not shutdown cleanly")

    @property
    def is_running(self) -> bool:
        """Check if the background event loop is running."""
        return self._running and self.loop.is_running() and self.thread.is_alive()


@inject
def run_in_background(
    coroutine: AnyCoroutine[T],
    background_loop: BackgroundEventLoop = inject[BackgroundEventLoop],
) -> T:
    """Run a coroutine in the background event loop."""
    return background_loop.submit(coroutine).result()
