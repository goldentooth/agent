"""Factory functions for creating event flow instances."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

from .flow import AsyncEventFlow, SyncEventFlow

T = TypeVar("T")

# Type aliases
AnyAsyncEventFlow = AsyncEventFlow[Any]
AnySyncEventFlow = SyncEventFlow[Any]


def create_sync_event_flow(event_name: str) -> AnySyncEventFlow:
    """Create a synchronous event flow for the given event name.

    Args:
        event_name: Name of the event to handle

    Returns:
        A synchronous event flow instance
    """
    return SyncEventFlow[Any](event_name)


def create_async_event_flow(event_name: str) -> AnyAsyncEventFlow:
    """Create an asynchronous event flow for the given event name.

    Args:
        event_name: Name of the event to handle

    Returns:
        An asynchronous event flow instance
    """
    return AsyncEventFlow[Any](event_name)


def create_typed_sync_event_flow(
    event_name: str,
) -> Callable[[type[T]], SyncEventFlow[T]]:
    """Create a typed synchronous event flow factory.

    Args:
        event_name: Name of the event to handle

    Returns:
        A factory function that creates typed synchronous event flows
    """

    def factory(_: type[T]) -> SyncEventFlow[T]:
        """Create a typed synchronous event flow.

        Args:
            _: Type parameter (used for type inference only)

        Returns:
            A typed synchronous event flow instance
        """
        return SyncEventFlow[T](event_name)

    return factory


def create_typed_async_event_flow(
    event_name: str,
) -> Callable[[type[T]], AsyncEventFlow[T]]:
    """Create a typed asynchronous event flow factory.

    Args:
        event_name: Name of the event to handle

    Returns:
        A factory function that creates typed asynchronous event flows
    """

    def factory(_: type[T]) -> AsyncEventFlow[T]:
        """Create a typed asynchronous event flow.

        Args:
            _: Type parameter (used for type inference only)

        Returns:
            A typed asynchronous event flow instance
        """
        return AsyncEventFlow[T](event_name)

    return factory
