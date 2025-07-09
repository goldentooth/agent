"""Context-Flow integration core module.

This module provides the core integration between Context and Flow systems,
including exception classes, combinators, and decorator functions.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator, Callable
from typing import TYPE_CHECKING, Any, TypeVar

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
    "context_flow",
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


def context_flow(
    context_keys: list[str] | None = None,
    required_keys: list[str] | None = None,
    type_hints: dict[str, type] | None = None,
    name: str | None = None,
) -> Callable[[Callable[..., Any]], "Flow[Any, Any]"]:
    """Create a context-aware flow decorator.

    This decorator creates flows that automatically inject context values
    into the decorated function and validate context state.

    Args:
        context_keys: List of context keys to make available to the function.
                     If None, all context keys are available.
        required_keys: List of context keys that must be present.
                      Missing keys will raise MissingRequiredKeyError.
        type_hints: Dictionary mapping context keys to expected types.
                   Type mismatches will raise ContextTypeMismatchError.
        name: Optional name for the flow (defaults to function name).

    Returns:
        A decorator that creates context-aware Flow instances.

    Raises:
        MissingRequiredKeyError: When required context keys are missing.
        ContextTypeMismatchError: When context values don't match expected types.
    """
    from flowengine.flow import Flow

    def decorator(func: Callable[..., Any]) -> "Flow[Any, Any]":
        """Decorator that creates a context-aware flow."""
        flow_name = name or func.__name__

        async def context_aware_flow(
            stream: AsyncGenerator[Any, None]
        ) -> AsyncGenerator[Any, None]:
            """Context-aware flow implementation."""
            from context.main import Context

            # Process the stream with context injection
            async for item in stream:
                # Create a fresh context for each item
                context = Context()

                # Inject context into function call
                if context_keys:
                    # Create a new context with filtered keys
                    from context.frame import ContextFrame

                    filtered_frame = ContextFrame()
                    for key in context_keys:
                        if key in context:
                            filtered_frame[key] = context.get(key)
                    context_obj = Context([filtered_frame])
                else:
                    context_obj = context

                # Call the function with item and context
                result = await func(item, context_obj)

                # Validate required keys after function execution
                if required_keys:
                    for key in required_keys:
                        if key not in context_obj:
                            raise MissingRequiredKeyError(
                                f"Required context key '{key}' is missing"
                            )

                # Validate type hints after function execution
                if type_hints:
                    for key, expected_type in type_hints.items():
                        if key in context_obj:
                            value = context_obj.get(key)
                            if not isinstance(value, expected_type):
                                actual_type = type(value).__name__
                                expected_type_name = expected_type.__name__
                                raise ContextTypeMismatchError(
                                    f"Context key '{key}' expected {expected_type_name}, "
                                    + f"got {actual_type}"
                                )

                yield result

        return Flow(context_aware_flow, name=flow_name)

    return decorator
