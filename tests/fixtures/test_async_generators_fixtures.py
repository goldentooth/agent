"""Async generator testing utilities for flow_events module.

This module provides utilities for testing complex async generator branches
and controlling async generator execution for comprehensive test coverage.
"""

import asyncio
from typing import Any, AsyncGenerator, Callable, Generic, Optional, TypeVar, Union
from unittest.mock import Mock

T = TypeVar("T")
U = TypeVar("U")


class AsyncGeneratorTester:
    """Utilities for testing complex async generator branches."""

    def __init__(self, timeout: float = 5.0) -> None:
        """Initialize tester with default timeout."""
        super().__init__()
        self.timeout = timeout
        self.execution_log: list[str] = []

    async def collect_all_items(
        self, generator: AsyncGenerator[T, None], max_items: Optional[int] = None
    ) -> list[T]:
        """Collect all items from an async generator.

        Args:
            generator: The async generator to collect from
            max_items: Maximum number of items to collect (prevents infinite loops)

        Returns:
            List of all items yielded by the generator
        """
        items: list[T] = []
        count = 0

        try:
            async with asyncio.timeout(self.timeout):
                async for item in generator:
                    items.append(item)
                    count += 1
                    self.execution_log.append(f"collected_item_{count}: {item}")

                    if max_items is not None and count >= max_items:
                        self.execution_log.append(f"max_items_reached: {max_items}")
                        break
        except asyncio.TimeoutError:
            self.execution_log.append(f"timeout_after_{count}_items")
        except Exception as e:
            self.execution_log.append(f"exception: {type(e).__name__}: {e}")
            raise

        return items

    async def collect_until_condition(
        self, generator: AsyncGenerator[T, None], condition: Callable[[T], bool]
    ) -> list[T]:
        """Collect items until a condition is met.

        Args:
            generator: The async generator to collect from
            condition: Function that returns True when collection should stop

        Returns:
            List of items collected before condition was met
        """
        items: list[T] = []
        count = 0

        try:
            async with asyncio.timeout(self.timeout):
                async for item in generator:
                    items.append(item)
                    count += 1
                    self.execution_log.append(f"collected_item_{count}: {item}")

                    if condition(item):
                        self.execution_log.append(f"condition_met_at_item_{count}")
                        break
        except asyncio.TimeoutError:
            self.execution_log.append(f"timeout_before_condition_met_{count}_items")
        except Exception as e:
            self.execution_log.append(f"exception: {type(e).__name__}: {e}")
            raise

        return items

    async def collect_with_timing(
        self, generator: AsyncGenerator[T, None], max_duration: float
    ) -> tuple[list[T], float]:
        """Collect items for a specific duration.

        Args:
            generator: The async generator to collect from
            max_duration: Maximum time to collect for (seconds)

        Returns:
            Tuple of (collected items, actual duration)
        """
        items: list[T] = []
        start_time = asyncio.get_event_loop().time()
        count = 0

        try:
            async with asyncio.timeout(max_duration):
                async for item in generator:
                    items.append(item)
                    count += 1
                    self.execution_log.append(f"collected_item_{count}: {item}")
        except asyncio.TimeoutError:
            self.execution_log.append(f"duration_limit_reached_{count}_items")
        except Exception as e:
            self.execution_log.append(f"exception: {type(e).__name__}: {e}")
            raise

        actual_duration = asyncio.get_event_loop().time() - start_time
        return items, actual_duration

    async def inject_events_during_iteration(
        self,
        generator: AsyncGenerator[T, None],
        event_injector: Callable[[int], Any],
        inject_every: int = 1,
    ) -> list[T]:
        """Collect items while injecting events at intervals.

        Args:
            generator: The async generator to collect from
            event_injector: Function called with item count to inject events
            inject_every: Inject events every N items

        Returns:
            List of all collected items
        """
        items: list[T] = []
        count = 0

        try:
            async with asyncio.timeout(self.timeout):
                async for item in generator:
                    items.append(item)
                    count += 1
                    self.execution_log.append(f"collected_item_{count}: {item}")

                    if count % inject_every == 0:
                        try:
                            result = event_injector(count)
                            if asyncio.iscoroutine(result):
                                await result
                            self.execution_log.append(f"injected_event_at_item_{count}")
                        except Exception as e:
                            self.execution_log.append(f"injection_error_{count}: {e}")
        except asyncio.TimeoutError:
            self.execution_log.append(f"timeout_during_injection_{count}_items")
        except Exception as e:
            self.execution_log.append(f"exception: {type(e).__name__}: {e}")
            raise

        return items

    async def test_generator_branches(
        self,
        generator_factory: Callable[[], AsyncGenerator[T, None]],
        branch_conditions: dict[str, Callable[[T], bool]],
    ) -> dict[str, bool]:
        """Test which branches of a generator are executed.

        Args:
            generator_factory: Function that creates a new generator instance
            branch_conditions: Dict mapping branch names to detection functions

        Returns:
            Dict showing which branches were hit
        """
        branch_results: dict[str, bool] = {name: False for name in branch_conditions}

        generator = generator_factory()
        try:
            async with asyncio.timeout(self.timeout):
                async for item in generator:
                    self.execution_log.append(f"testing_branches_for: {item}")

                    for branch_name, condition in branch_conditions.items():
                        if not branch_results[branch_name] and condition(item):
                            branch_results[branch_name] = True
                            self.execution_log.append(f"branch_hit: {branch_name}")

                    # Stop if all branches have been hit
                    if all(branch_results.values()):
                        self.execution_log.append("all_branches_hit")
                        break
        except asyncio.TimeoutError:
            self.execution_log.append("timeout_during_branch_testing")
        except Exception as e:
            self.execution_log.append(f"exception: {type(e).__name__}: {e}")
            raise

        return branch_results

    def clear_log(self) -> None:
        """Clear the execution log."""
        self.execution_log.clear()

    def get_log(self) -> list[str]:
        """Get a copy of the execution log."""
        return self.execution_log.copy()


class ControlledAsyncGenerator(Generic[T]):
    """Async generator with controllable timing and behavior for testing."""

    def __init__(
        self,
        items: list[T],
        delay_between: float = 0.0,
        exception_at: Optional[int] = None,
        exception_type: type[Exception] = RuntimeError,
    ) -> None:
        """Initialize controlled generator.

        Args:
            items: Items to yield
            delay_between: Delay between items (seconds)
            exception_at: Item index to raise exception at (0-based)
            exception_type: Type of exception to raise
        """
        super().__init__()
        self.items = items
        self.delay_between = delay_between
        self.exception_at = exception_at
        self.exception_type = exception_type
        self.yielded_count = 0

    async def __aiter__(self) -> AsyncGenerator[T, None]:
        """Async iterator that yields items with controlled behavior."""
        for i, item in enumerate(self.items):
            if self.exception_at is not None and i == self.exception_at:
                raise self.exception_type(f"Controlled exception at item {i}")

            if self.delay_between > 0:
                await asyncio.sleep(self.delay_between)

            self.yielded_count += 1
            yield item


class EmptyAsyncGenerator:
    """Async generator that yields nothing - for testing empty stream branches."""

    def __init__(self, delay_before_exit: float = 0.0) -> None:
        """Initialize empty generator.

        Args:
            delay_before_exit: Delay before generator exits
        """
        super().__init__()
        self.delay_before_exit = delay_before_exit

    async def __aiter__(self) -> AsyncGenerator[Any, None]:
        """Async iterator that yields nothing."""
        if self.delay_before_exit > 0:
            await asyncio.sleep(self.delay_before_exit)

        # This makes it a valid async generator that yields nothing
        if False:
            yield None


class EventDrivenAsyncGenerator:
    """Async generator driven by external events for testing event flows."""

    def __init__(self, timeout: float = 1.0) -> None:
        """Initialize event-driven generator.

        Args:
            timeout: Timeout for waiting for events
        """
        super().__init__()
        self.timeout = timeout
        self.events: asyncio.Queue[Any] = asyncio.Queue()
        self.stop_event = asyncio.Event()

    async def __aiter__(self) -> AsyncGenerator[Any, None]:
        """Async iterator that yields events as they arrive."""
        while not self.stop_event.is_set():
            try:
                # Wait for next event or timeout
                event = await asyncio.wait_for(self.events.get(), timeout=self.timeout)
                yield event
            except asyncio.TimeoutError:
                # No more events within timeout
                break

    async def add_event(self, event: Any) -> None:
        """Add an event to the generator."""
        await self.events.put(event)

    def stop(self) -> None:
        """Stop the generator."""
        self.stop_event.set()

    def add_multiple_events(self, events: list[Any]) -> None:
        """Add multiple events synchronously."""
        for event in events:
            self.events.put_nowait(event)


def create_test_input_generator(*items: T) -> AsyncGenerator[T, None]:
    """Create a simple async generator for testing input.

    Args:
        *items: Items to yield

    Returns:
        Async generator that yields the items
    """

    async def generator() -> AsyncGenerator[T, None]:
        for item in items:
            yield item

    return generator()


async def create_empty_input_generator() -> AsyncGenerator[Any, None]:
    """Create an empty async generator for testing empty input streams."""
    if False:  # Makes it a valid generator function
        yield None


def create_infinite_generator(item: T, delay: float = 0.01) -> AsyncGenerator[T, None]:
    """Create an async generator that yields the same item infinitely.

    Args:
        item: Item to yield repeatedly
        delay: Delay between yields

    Returns:
        Infinite async generator
    """

    async def generator() -> AsyncGenerator[T, None]:
        while True:
            if delay > 0:
                await asyncio.sleep(delay)
            yield item

    return generator()
