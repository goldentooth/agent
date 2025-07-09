"""Context-Flow integration core module.

This module provides the core integration between Context and Flow systems,
including exception classes, combinators, and decorator functions.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING, TypeVar

from goldentooth_agent.core.background_loop import run_in_background

if TYPE_CHECKING:
    from flowengine.flow import Flow

__all__ = [
    "ContextFlowError",
    "MissingRequiredKeyError",
    "ContextTypeMismatchError",
    "_single_item_stream",
    "run_flow_with_input",
    "extend_flow_with_context",
]

T = TypeVar("T")
R = TypeVar("R")


class ContextFlowError(Exception):
    """Base exception for Context-Flow integration errors."""

    pass


class MissingRequiredKeyError(ContextFlowError):
    """Raised when a required context key is missing."""

    pass


class ContextTypeMismatchError(ContextFlowError):
    """Raised when a context key has the wrong type."""

    pass


async def _single_item_stream(item: T) -> AsyncGenerator[T, None]:
    """Create a single-item async generator."""
    yield item


def run_flow_with_input(flow: "Flow[T, R]", input_item: T) -> R:
    """Run a flow with a single input item and return the first result.

    This is a convenience function for testing and simple use cases.
    """

    async def _run() -> R:
        stream = _single_item_stream(input_item)
        result_stream = flow(stream)
        async for result in result_stream:
            return result  # Return first result
        raise RuntimeError("Flow produced no output")

    return run_in_background(_run())


def extend_flow_with_context() -> None:
    """Extend Flow class with context manipulation and convenience methods.

    This function adds convenience methods to the Flow class that make it easier
    to work with context-flow integration patterns.
    """
    from typing import Any

    from flowengine.flow import Flow

    def run(self: "Flow[Any, Any]", input_item: Any) -> Any:
        """Run this flow with a single input and return the first result.

        This is a convenience method that wraps run_flow_with_input.
        """
        return run_flow_with_input(self, input_item)

    def then(self: "Flow[Any, Any]", other: "Flow[Any, Any]") -> "Flow[Any, Any]":
        """Chain this flow with another flow (alias for >> operator).

        This provides a more readable alternative to the >> operator.
        """
        return self >> other

    # Add the methods to Flow class
    Flow.run = run  # type: ignore[attr-defined]
    Flow.then = then  # type: ignore[attr-defined]
