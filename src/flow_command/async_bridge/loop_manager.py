from __future__ import annotations

import asyncio
import atexit
import logging
import threading
from collections.abc import AsyncGenerator, AsyncIterable, Coroutine, Iterable
from concurrent.futures import Future
from typing import Any, TypeVar

from flow.flow import Flow

from ..core.exceptions import FlowCommandTimeoutError

logger = logging.getLogger(__name__)

T = TypeVar("T")
U = TypeVar("U")

# Type alias for coroutines - we don't use send/yield types
AnyCoroutine = Coroutine[Any, Any, T]


class FlowEventLoop:
    """Flow-optimized background event loop with enhanced capabilities."""

    def __init__(self) -> None:
        """Initialize the flow event loop."""
        super().__init__()
        self.loop = asyncio.new_event_loop()
        self._running = True
        self._shutdown_complete = threading.Event()
        self.thread = threading.Thread(
            target=self._run_loop, daemon=True, name="FlowEventLoop"
        )
        self.thread.start()
        atexit.register(self.shutdown)

    def _run_loop(self) -> None:
        """Run the asyncio event loop in a separate thread."""
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_forever()
        finally:
            self.loop.close()
            self._shutdown_complete.set()

    def submit(self, coroutine: AnyCoroutine[T]) -> Future[T]:
        """Submit a coroutine to be run in the background event loop."""
        if not self._running:
            raise RuntimeError("Flow event loop is not running")
        return asyncio.run_coroutine_threadsafe(coroutine, self.loop)

    def execute_flow(self, flow: Flow[T, U], input_stream: AsyncIterable[T]) -> list[U]:
        """Execute a flow synchronously, returning collected results."""

        async def collect_flow() -> list[U]:
            async_gen = self._convert_to_async_generator(input_stream)
            return await flow.collect()(async_gen)

        future: Future[list[U]] = self.submit(collect_flow())
        return future.result()

    def execute_flow_streaming(
        self, flow: Flow[T, U], input_data: Iterable[T]
    ) -> list[U]:
        """Execute a flow with input data, returning results."""

        async def execute_with_data() -> list[U]:
            input_stream = self._create_async_iterable(input_data)
            async_gen = self._convert_to_async_generator(input_stream)
            return await flow.collect()(async_gen)

        future: Future[list[U]] = self.submit(execute_with_data())
        return future.result()

    def execute_with_timeout(self, coroutine: AnyCoroutine[T], timeout: float) -> T:
        """Execute coroutine with timeout handling."""
        future = self.submit(coroutine)
        try:
            return future.result(timeout=timeout)
        except TimeoutError as e:
            # Cancel the future to prevent resource leaks
            future.cancel()
            raise FlowCommandTimeoutError(
                f"Flow execution timed out after {timeout} seconds"
            ) from e

    async def _create_async_iterable(self, data: Iterable[T]) -> AsyncIterable[T]:
        """Convert iterable to async iterable."""
        for item in data:
            yield item

    async def _convert_to_async_generator(
        self, async_iterable: AsyncIterable[T]
    ) -> AsyncGenerator[T, None]:
        """Convert AsyncIterable to AsyncGenerator for Flow compatibility."""
        async for item in async_iterable:
            yield item

    def shutdown(self, timeout: float = 5.0) -> None:
        """Shutdown the flow event loop gracefully."""
        if not self._running:
            return

        self._mark_shutdown_started()
        self._stop_event_loop()
        self._wait_for_shutdown_completion(timeout)
        self._check_shutdown_success()

    def _mark_shutdown_started(self) -> None:
        """Mark the flow loop as shutting down."""
        self._running = False

    def _stop_event_loop(self) -> None:
        """Stop the event loop if it's running."""
        if self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)

    def _wait_for_shutdown_completion(self, timeout: float) -> None:
        """Wait for the shutdown to complete within the timeout."""
        self._shutdown_complete.wait(timeout)

    def _check_shutdown_success(self) -> None:
        """Check if shutdown completed successfully and log warnings."""
        if self.thread.is_alive():
            logger.warning("Flow event loop thread did not shutdown cleanly")

    @property
    def is_running(self) -> bool:
        """Check if the flow event loop is running."""
        return self._running and self.loop.is_running() and self.thread.is_alive()
