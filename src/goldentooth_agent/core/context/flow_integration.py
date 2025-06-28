"""Flow-Context integration providing type-safe context operations with Flow combinators."""

from __future__ import annotations

import asyncio
import copy
from collections.abc import AsyncIterator, Awaitable, Callable
from typing import Any, TypeVar

from ..flow import Flow
from .key import ContextKey
from .main import Context

# Type aliases for context-flow integration
AnyContextKey = ContextKey[Any]  # type: ignore[explicit-any]
AnyValue = Any  # type: ignore[explicit-any]
ContextFlowFunction = Callable[[Context], Context | Awaitable[Context]]
ContextFlowDecorator = Callable[[ContextFlowFunction], Flow[Context, Context]]

T = TypeVar("T")
R = TypeVar("R")


class ContextFlowError(Exception):
    """Base exception for Flow-Context integration errors."""

    pass


class MissingRequiredKeyError(ContextFlowError):
    """Raised when a required context key is missing."""

    pass


class ContextTypeMismatchError(ContextFlowError):
    """Raised when a context key has the wrong type."""

    pass


async def _single_item_stream(item: T) -> AsyncIterator[T]:
    """Create a single-item async iterator."""
    yield item


def run_flow_with_input(flow: Flow[T, R], input_item: T) -> R:
    """Run a flow with a single input item and return the first result.

    This is a convenience function for testing and simple use cases.
    """

    async def _run() -> R:
        stream = _single_item_stream(input_item)
        result_stream = flow(stream)
        async for result in result_stream:
            return result  # Return first result
        raise RuntimeError("Flow produced no output")

    return asyncio.run(_run())


class ContextFlowCombinators:
    """Flow combinators for context manipulation with type safety."""

    @staticmethod
    def get_key(
        key: ContextKey[T], default: T | None = None
    ) -> Flow[Context, T | None]:
        """Create a Flow that extracts a value from a context key.

        Args:
            key: The context key to extract
            default: Default value if key is missing (None means raise error)

        Returns:
            Flow that extracts the value or returns default

        Raises:
            MissingRequiredKeyError: If key is missing and no default provided
            ContextTypeMismatchError: If value exists but has wrong type
        """

        def extract_key(context: Context) -> T | None:
            try:
                value = context[key.path]
                if not isinstance(value, key.type_):
                    raise ContextTypeMismatchError(
                        f"Key '{key.path}' expected {key.type_.__name__}, got {type(value).__name__}"
                    )
                return value  # type: ignore[return-value]
            except KeyError as e:
                if default is None:
                    raise MissingRequiredKeyError(
                        f"Required key '{key.path}' not found in context"
                    ) from e
                return default

        async def extract_flow_impl(
            stream: AsyncIterator[Context],
        ) -> AsyncIterator[T | None]:
            async for context in stream:
                yield extract_key(context)

        return Flow(extract_flow_impl, name=f"get_key({key.path})")

    @staticmethod
    def set_key(key: ContextKey[T], value: T) -> Flow[Context, Context]:
        """Create a Flow that sets a context key to a specific value.

        Args:
            key: The context key to set
            value: The value to set

        Returns:
            Flow that returns updated context

        Raises:
            ContextTypeMismatchError: If value has wrong type
        """

        def set_key_value(context: Context) -> Context:
            if not isinstance(value, key.type_):
                raise ContextTypeMismatchError(
                    f"Key '{key.path}' expected {key.type_.__name__}, got {type(value).__name__}"
                )

            # Create a copy to avoid mutation
            new_context = context.fork()
            new_context[key.path] = value
            return new_context

        async def set_flow_impl(
            stream: AsyncIterator[Context],
        ) -> AsyncIterator[Context]:
            async for context in stream:
                yield set_key_value(context)

        return Flow(set_flow_impl, name=f"set_key({key.path}={value})")

    @staticmethod
    def require_key(key: ContextKey[T]) -> Flow[Context, T]:
        """Create a Flow that requires a context key to be present and returns its value.

        Args:
            key: The context key that must be present

        Returns:
            Flow that returns the key's value

        Raises:
            MissingRequiredKeyError: If key is missing
            ContextTypeMismatchError: If value has wrong type
        """

        def require_key_value(context: Context) -> T:
            try:
                value = context[key.path]
                if not isinstance(value, key.type_):
                    raise ContextTypeMismatchError(
                        f"Key '{key.path}' expected {key.type_.__name__}, got {type(value).__name__}"
                    )
                return value  # type: ignore[return-value]
            except KeyError as e:
                raise MissingRequiredKeyError(
                    f"Required key '{key.path}' not found in context"
                ) from e

        async def require_flow_impl(stream: AsyncIterator[Context]) -> AsyncIterator[T]:
            async for context in stream:
                yield require_key_value(context)

        return Flow(require_flow_impl, name=f"require_key({key.path})")

    @staticmethod
    def optional_key(key: ContextKey[T], default: T) -> Flow[Context, T]:
        """Create a Flow that gets an optional context key with a default value.

        Args:
            key: The context key to get
            default: Default value if key is missing

        Returns:
            Flow that returns the key's value or default

        Raises:
            ContextTypeMismatchError: If value exists but has wrong type
        """

        def get_optional_key(context: Context) -> T:
            try:
                value = context[key.path]
                if not isinstance(value, key.type_):
                    raise ContextTypeMismatchError(
                        f"Key '{key.path}' expected {key.type_.__name__}, got {type(value).__name__}"
                    )
                return value  # type: ignore[return-value]
            except KeyError:
                return default

        async def optional_flow_impl(
            stream: AsyncIterator[Context],
        ) -> AsyncIterator[T]:
            async for context in stream:
                yield get_optional_key(context)

        return Flow(
            optional_flow_impl, name=f"optional_key({key.path}, default={default})"
        )

    @staticmethod
    def move_key(
        source: ContextKey[T], destination: ContextKey[T]
    ) -> Flow[Context, Context]:
        """Create a Flow that moves a value from one context key to another.

        Args:
            source: The source context key
            destination: The destination context key

        Returns:
            Flow that returns updated context with value moved

        Raises:
            MissingRequiredKeyError: If source key is missing
            ContextTypeMismatchError: If source value has wrong type
        """

        def move_key_value(context: Context) -> Context:
            try:
                value = context[source.path]
                if not isinstance(value, source.type_):
                    raise ContextTypeMismatchError(
                        f"Source key '{source.path}' expected {source.type_.__name__}, got {type(value).__name__}"
                    )

                # Create a copy to avoid mutation
                new_context = context.fork()
                del new_context.frames[-1][source.path]  # Remove from source
                new_context[destination.path] = value
                return new_context
            except KeyError as e:
                raise MissingRequiredKeyError(
                    f"Source key '{source.path}' not found in context"
                ) from e

        async def move_flow_impl(
            stream: AsyncIterator[Context],
        ) -> AsyncIterator[Context]:
            async for context in stream:
                yield move_key_value(context)

        return Flow(
            move_flow_impl, name=f"move_key({source.path} -> {destination.path})"
        )

    @staticmethod
    def copy_key(
        source: ContextKey[T], destination: ContextKey[T]
    ) -> Flow[Context, Context]:
        """Create a Flow that copies a value from one context key to another.

        Args:
            source: The source context key
            destination: The destination context key

        Returns:
            Flow that returns updated context with value copied

        Raises:
            MissingRequiredKeyError: If source key is missing
            ContextTypeMismatchError: If source value has wrong type
        """

        def copy_key_value(context: Context) -> Context:
            try:
                value = context[source.path]
                if not isinstance(value, source.type_):
                    raise ContextTypeMismatchError(
                        f"Source key '{source.path}' expected {source.type_.__name__}, got {type(value).__name__}"
                    )

                # Create a copy to avoid mutation
                new_context = context.fork()
                new_context[destination.path] = copy.deepcopy(value)
                return new_context
            except KeyError as e:
                raise MissingRequiredKeyError(
                    f"Source key '{source.path}' not found in context"
                ) from e

        async def copy_flow_impl(
            stream: AsyncIterator[Context],
        ) -> AsyncIterator[Context]:
            async for context in stream:
                yield copy_key_value(context)

        return Flow(
            copy_flow_impl, name=f"copy_key({source.path} -> {destination.path})"
        )

    @staticmethod
    def forget_key(key: ContextKey[T]) -> Flow[Context, Context]:
        """Create a Flow that removes a key from the context.

        Args:
            key: The context key to remove

        Returns:
            Flow that returns updated context with key removed
        """

        def forget_key_value(context: Context) -> Context:
            # Create a copy to avoid mutation
            new_context = context.fork()
            if key.path in new_context.frames[-1]:
                del new_context.frames[-1][key.path]
            return new_context

        async def forget_flow_impl(
            stream: AsyncIterator[Context],
        ) -> AsyncIterator[Context]:
            async for context in stream:
                yield forget_key_value(context)

        return Flow(forget_flow_impl, name=f"forget_key({key.path})")

    @staticmethod
    def require_keys(*keys: AnyContextKey) -> Flow[Context, Context]:
        """Create a Flow that validates multiple required keys are present.

        Args:
            keys: The context keys that must be present

        Returns:
            Flow that returns the same context if all keys are present

        Raises:
            MissingRequiredKeyError: If any key is missing
            ContextTypeMismatchError: If any value has wrong type
        """

        def validate_required_keys(context: Context) -> Context:
            for key in keys:
                try:
                    value = context[key.path]
                    if not isinstance(value, key.type_):
                        raise ContextTypeMismatchError(
                            f"Key '{key.path}' expected {key.type_.__name__}, got {type(value).__name__}"
                        )
                except KeyError as e:
                    raise MissingRequiredKeyError(
                        f"Required key '{key.path}' not found in context"
                    ) from e
            return context

        key_names = [k.path for k in keys]

        async def validate_flow_impl(
            stream: AsyncIterator[Context],
        ) -> AsyncIterator[Context]:
            async for context in stream:
                yield validate_required_keys(context)

        return Flow(validate_flow_impl, name=f"require_keys({', '.join(key_names)})")

    @staticmethod
    def transform_key(
        key: ContextKey[T],
        transform_fn: Callable[[T], R],
        result_key: ContextKey[R] | None = None,
    ) -> Flow[Context, Context | R]:
        """Create a Flow that transforms a context key's value.

        Args:
            key: The context key to transform
            transform_fn: Function to transform the value
            result_key: Optional key to store result in context

        Returns:
            Flow that returns transformed value or updated context

        Raises:
            MissingRequiredKeyError: If key is missing
            ContextTypeMismatchError: If value has wrong type
        """

        def transform_key_value(context: Context) -> Context | R:
            try:
                value = context[key.path]
                if not isinstance(value, key.type_):
                    raise ContextTypeMismatchError(
                        f"Key '{key.path}' expected {key.type_.__name__}, got {type(value).__name__}"
                    )

                transformed = transform_fn(value)  # type: ignore[arg-type]

                if result_key is not None:
                    # Store in context and return context
                    new_context = context.fork()
                    new_context[result_key.path] = transformed
                    return new_context
                else:
                    # Return transformed value directly
                    return transformed

            except KeyError as e:
                raise MissingRequiredKeyError(
                    f"Key '{key.path}' not found in context"
                ) from e

        operation = f"store_in({result_key.path})" if result_key else "return_value"

        async def transform_flow_impl(
            stream: AsyncIterator[Context],
        ) -> AsyncIterator[Context | R]:
            async for context in stream:
                yield transform_key_value(context)

        return Flow(transform_flow_impl, name=f"transform_key({key.path}, {operation})")


# Add static methods to Flow class for convenient access
def extend_flow_with_context() -> None:
    """Extend Flow class with context manipulation methods."""

    # Context key operations
    Flow.get_key = staticmethod(ContextFlowCombinators.get_key)  # type: ignore[attr-defined]
    Flow.set_key = staticmethod(ContextFlowCombinators.set_key)  # type: ignore[attr-defined]
    Flow.require_key = staticmethod(ContextFlowCombinators.require_key)  # type: ignore[attr-defined]
    Flow.optional_key = staticmethod(ContextFlowCombinators.optional_key)  # type: ignore[attr-defined]

    # Context manipulation
    Flow.move_key = staticmethod(ContextFlowCombinators.move_key)  # type: ignore[attr-defined]
    Flow.copy_key = staticmethod(ContextFlowCombinators.copy_key)  # type: ignore[attr-defined]
    Flow.forget_key = staticmethod(ContextFlowCombinators.forget_key)  # type: ignore[attr-defined]
    Flow.require_keys = staticmethod(ContextFlowCombinators.require_keys)  # type: ignore[attr-defined]
    Flow.transform_key = staticmethod(ContextFlowCombinators.transform_key)  # type: ignore[attr-defined]

    # Add convenience methods for testing and composition
    def run(self: AnyValue, input_item: AnyValue) -> AnyValue:
        """Run this flow with a single input and return the first result."""
        return run_flow_with_input(self, input_item)

    def then(self: AnyValue, other: AnyValue) -> AnyValue:
        """Chain this flow with another flow (alias for >> operator)."""
        return self >> other

    Flow.run = run  # type: ignore[attr-defined]
    Flow.then = then  # type: ignore[attr-defined]


# Decorator for creating context-aware flows
def context_flow(
    *,
    inputs: list[AnyContextKey] | None = None,
    outputs: list[AnyContextKey] | None = None,
    optional: dict[AnyContextKey, AnyValue] | None = None,
    name: str | None = None,
) -> ContextFlowDecorator:
    """Decorator to create a context-aware Flow with declared dependencies.

    Args:
        inputs: List of required input context keys
        outputs: List of output context keys this flow will set
        optional: Dict of optional keys with their default values
        name: Optional name for the flow
    """

    def decorator(
        func: Callable[[Context], Context | Awaitable[Context]]
    ) -> Flow[Context, Context]:
        """Decorate a function to be a context-aware Flow."""

        # Create validation flow for inputs
        validation_flow: Flow[Context, Context] = Flow.identity()
        if inputs:
            validation_flow = ContextFlowCombinators.require_keys(*inputs)

        # Create the main flow
        async def main_flow_impl(
            stream: AsyncIterator[Context],
        ) -> AsyncIterator[Context]:
            async for context in stream:
                result = func(context)
                if asyncio.iscoroutine(result):
                    # Handle async case - this is a simplification for now
                    result = await result
                yield result  # type: ignore[misc]

        main_flow = Flow(main_flow_impl, name=name or func.__name__)

        # Compose validation + main flow
        composed_flow = validation_flow >> main_flow

        # Add metadata about dependencies
        composed_flow.metadata = {
            "input_dependencies": inputs or [],
            "output_dependencies": outputs or [],
            "optional_dependencies": optional or {},
            "context_aware": True,
        }

        return composed_flow

    return decorator
