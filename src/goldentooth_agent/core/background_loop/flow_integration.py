from __future__ import annotations
from typing import TypeVar, Callable, Awaitable, Any
from antidote import inject
import asyncio

from ..flow import Flow, map_stream, flat_map_stream
from .inject import get_background_loop, BackgroundEventLoop


T = TypeVar("T")
R = TypeVar("R")


@inject
def async_flow(
    coroutine_fn: Callable[[T], Awaitable[R]],
    background_loop: BackgroundEventLoop = inject[get_background_loop()],
) -> Flow[T, R]:
    """
    Create a Flow that runs async operations in the background loop.

    Args:
        coroutine_fn: A function that takes an item and returns a coroutine
        background_loop: The background event loop to use (injected)

    Returns:
        A Flow that transforms items asynchronously

    Example:
        # Define an async operation
        async def fetch_data(url: str) -> dict:
            await asyncio.sleep(0.1)  # Simulate async work
            return {"url": url, "data": "fetched"}

        # Create a flow that fetches data asynchronously
        urls = Flow.from_iterable(["url1", "url2", "url3"])
        results = urls >> async_flow(fetch_data)
    """

    def transform(item: T) -> R:
        future = background_loop.submit(coroutine_fn(item))
        return future.result()

    return map_stream(transform)


@inject
def schedule_flow(
    delay_seconds: float,
    background_loop: BackgroundEventLoop = inject[get_background_loop()],
) -> Flow[T, T]:
    """
    Create a Flow that delays items using the background loop.

    Args:
        delay_seconds: Seconds to delay each item
        background_loop: The background event loop to use (injected)

    Returns:
        A Flow that delays items

    Example:
        # Delay each item by 1 second
        items = Flow.from_iterable([1, 2, 3])
        delayed = items >> schedule_flow(1.0)
    """

    async def delay_item(item: T) -> T:
        await asyncio.sleep(delay_seconds)
        return item

    return async_flow(delay_item, background_loop)


@inject
def timeout_async_flow(
    coroutine_fn: Callable[[T], Awaitable[R]],
    timeout_seconds: float,
    default_value: R | None = None,
) -> Flow[T, R]:
    """
    Create a Flow that runs async operations with a timeout.

    Args:
        coroutine_fn: A function that takes an item and returns a coroutine
        timeout_seconds: Timeout in seconds
        default_value: Value to return on timeout (None to skip)

    Returns:
        A Flow that transforms items with timeout

    Example:
        # Fetch data with 5 second timeout
        urls = Flow.from_iterable(["url1", "url2", "url3"])
        results = urls >> timeout_async_flow(fetch_data, 5.0, default_value={})
    """

    async def with_timeout(item: T) -> R | None:
        try:
            return await asyncio.wait_for(coroutine_fn(item), timeout_seconds)
        except asyncio.TimeoutError:
            return default_value

    def filter_none(item: R | None) -> AsyncIterator[R]:
        async def _filter():
            if item is not None:
                yield item

        return _filter()

    return async_flow(with_timeout) >> flat_map_stream(filter_none)
