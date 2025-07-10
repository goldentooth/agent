"""Trampoline system for context-aware flow execution.

This module provides trampoline execution patterns for iterative and conditional
flow processing with context state management.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator, Callable
from typing import Any, TypeVar

from context.key import ContextKey
from context.main import Context
from context_flow.integration import ContextFlowCombinators
from flowengine.flow import Flow
from goldentooth_agent.core.background_loop import run_in_background

__all__ = [
    "_async_iter_from_item",
    "extend_flow_with_trampoline",
    "SHOULD_EXIT_KEY",
    "SHOULD_BREAK_KEY",
    "SHOULD_SKIP_KEY",
    "TrampolineFlowCombinators",
]

T = TypeVar("T")

# Control flow context keys
SHOULD_EXIT_KEY: ContextKey[bool] = ContextKey(
    "flow.trampoline.should_exit", bool, "Signal to exit trampoline loop"
)
SHOULD_BREAK_KEY: ContextKey[bool] = ContextKey(
    "flow.trampoline.should_break", bool, "Signal to break/restart current iteration"
)
SHOULD_SKIP_KEY: ContextKey[bool] = ContextKey(
    "flow.trampoline.should_skip", bool, "Signal to skip certain operations"
)


async def _async_iter_from_item(item: T) -> AsyncGenerator[T, None]:
    """Create an async generator that yields a single item.

    This utility function converts a single item into an async generator
    that yields that item exactly once. This is useful for creating
    single-item streams for flow processing.

    Args:
        item: The item to be yielded by the async generator.

    Returns:
        An async generator that yields the item once.

    Example:
        ```python
        async for value in _async_iter_from_item("hello"):
            print(value)  # Prints: hello
        ```
    """
    yield item


def extend_flow_with_trampoline() -> None:
    """Extend Flow class with trampoline execution convenience methods.

    This function adds trampoline-related convenience methods to the Flow class
    that make it easier to work with single-item processing, repetitive execution,
    and conditional flow control patterns.

    Added methods:
        - run_single: Execute flow with single item and return first result
        - as_single_stream: Convert single item to flow stream
        - repeat_until: Repeat flow execution until condition is met
        - exit_on: Exit flow execution when condition is met

    Example:
        ```python
        from flowengine.flow import Flow
        from context_flow.trampoline import extend_flow_with_trampoline

        # Extend Flow class with trampoline methods
        extend_flow_with_trampoline()

        # Now Flow instances have trampoline methods
        flow = Flow(some_flow_function)
        result = flow.run_single("input")
        ```
    """
    from flowengine.flow import Flow

    def run_single(self: "Flow[Any, Any]", item: Any) -> Any:
        """Execute this flow with a single item and return the first result.

        This is a convenience method that converts a single item to an async
        stream, runs the flow, and returns the first result.

        Args:
            item: The item to process through the flow.

        Returns:
            The first result from the flow execution.

        Example:
            ```python
            flow = Flow(some_flow_function)
            result = flow.run_single("input_item")
            ```
        """

        async def _run() -> Any:
            stream = _async_iter_from_item(item)
            result_stream = self(stream)
            async for result in result_stream:
                return result  # Return first result
            raise RuntimeError("Flow produced no output")

        return run_in_background(_run())

    def as_single_stream(self: "Flow[Any, Any]", item: Any) -> "Flow[Any, Any]":
        """Create a new flow that processes a single item through this flow.

        This method creates a new Flow that wraps this flow with single-item
        stream processing, allowing it to be composed with other flows.

        Args:
            item: The item to be processed.

        Returns:
            A new Flow that processes the single item.

        Example:
            ```python
            flow = Flow(some_flow_function)
            single_flow = flow.as_single_stream("input_item")
            ```
        """

        async def _single_stream_flow(
            stream: AsyncGenerator[Any, None]
        ) -> AsyncGenerator[Any, None]:
            """Flow that processes single item ignoring input stream."""
            # Ignore the input stream and process our single item
            single_item_stream = _async_iter_from_item(item)
            result_stream = self(single_item_stream)
            async for result in result_stream:
                yield result

        return Flow(_single_stream_flow, name=f"{self.name}_single({item})")

    def repeat_until(
        self: "Flow[Any, Any]", condition: Callable[[Any], bool]
    ) -> "Flow[Any, Any]":
        """Create a flow that repeats this flow until condition is met.

        This method creates a new Flow that repeatedly executes this flow
        on its output until the condition function returns True.

        Args:
            condition: Function that takes flow output and returns True to stop.

        Returns:
            A new Flow that repeats until condition is met.

        Example:
            ```python
            flow = Flow(increment_flow)
            repeat_flow = flow.repeat_until(lambda x: x >= 10)
            ```
        """

        async def _repeat_until_flow(
            stream: AsyncGenerator[Any, None]
        ) -> AsyncGenerator[Any, None]:
            """Flow that repeats until condition is met."""
            async for initial_item in stream:
                current_item = initial_item
                while True:
                    # Process current item through this flow
                    single_stream = _async_iter_from_item(current_item)
                    result_stream = self(single_stream)

                    async for result in result_stream:
                        current_item = result
                        if condition(current_item):
                            yield current_item
                            return
                        break  # Only process first result

        return Flow(_repeat_until_flow, name=f"repeat_{self.name}_until")

    def exit_on(
        self: "Flow[Any, Any]", condition: Callable[[Any], bool]
    ) -> "Flow[Any, Any]":
        """Create a flow that exits when condition is met.

        This method creates a new Flow that processes items through this flow
        but stops yielding results when the condition function returns True.

        Args:
            condition: Function that takes flow output and returns True to exit.

        Returns:
            A new Flow that exits when condition is met.

        Example:
            ```python
            flow = Flow(some_flow_function)
            exit_flow = flow.exit_on(lambda x: x == "stop")
            ```
        """

        async def _exit_on_flow(
            stream: AsyncGenerator[Any, None]
        ) -> AsyncGenerator[Any, None]:
            """Flow that exits when condition is met."""
            result_stream = self(stream)
            async for result in result_stream:
                if condition(result):
                    return  # Exit without yielding
                yield result

        return Flow(_exit_on_flow, name=f"{self.name}_exit_on")

    # Add the methods to Flow class
    Flow.run_single = run_single  # type: ignore[attr-defined]
    Flow.as_single_stream = as_single_stream  # type: ignore[attr-defined]
    Flow.repeat_until = repeat_until  # type: ignore[attr-defined]
    Flow.exit_on = exit_on  # type: ignore[attr-defined]


class TrampolineFlowCombinators:
    """Flow combinators for trampoline-style execution patterns.

    This class provides static methods for creating Flow objects that work with
    trampoline execution patterns, including setting and checking control flow
    signals like exit, break, and skip flags in the context.

    All methods are static and return Flow[Context, Context] objects that can
    be chained and composed with other flows for complex execution patterns.
    """

    @staticmethod
    def set_should_exit(value: bool = True) -> Flow[Context, Context]:
        """Create a Flow that sets the exit signal in the context.

        This method creates a Flow that sets the SHOULD_EXIT_KEY in the context
        to signal that trampoline execution should terminate. When this flag is
        set to True, trampoline loops will exit cleanly after the current
        iteration completes.

        Args:
            value: Whether to signal exit (default: True). Set to True to
                signal termination, False to clear the exit signal.

        Returns:
            A Flow[Context, Context] that sets the exit flag and returns the
            updated context with the flag set to the specified value.

        Example:
            ```python
            from context.main import Context
            from context_flow.trampoline import TrampolineFlowCombinators

            # Create a flow to signal exit
            exit_flow = TrampolineFlowCombinators.set_should_exit(True)

            # Use in a flow chain
            context = Context()
            result_context = exit_flow.run_single(context)
            # result_context will have the exit flag set to True
            ```

        Note:
            This method uses ContextFlowCombinators.set_key() internally to
            create a type-safe flow that sets the SHOULD_EXIT_KEY. The returned
            flow maintains context immutability by creating new Context instances.
        """
        return ContextFlowCombinators.set_key(SHOULD_EXIT_KEY, value)

    @staticmethod
    def set_should_break(value: bool = True) -> Flow[Context, Context]:
        """Create a Flow that sets the break signal in the context.

        This method creates a Flow that sets the SHOULD_BREAK_KEY in the context
        to signal that trampoline execution should break/restart the current
        iteration. When this flag is set to True, trampoline loops will break
        out of the current iteration and restart processing.

        Args:
            value: Whether to signal break (default: True). Set to True to
                signal break/restart, False to clear the break signal.

        Returns:
            A Flow[Context, Context] that sets the break flag and returns the
            updated context with the flag set to the specified value.

        Example:
            ```python
            from context.main import Context
            from context_flow.trampoline import TrampolineFlowCombinators

            # Create a flow to signal break
            break_flow = TrampolineFlowCombinators.set_should_break(True)

            # Use in a flow chain
            context = Context()
            result_context = break_flow.run_single(context)
            # result_context will have the break flag set to True
            ```

        Note:
            This method uses ContextFlowCombinators.set_key() internally to
            create a type-safe flow that sets the SHOULD_BREAK_KEY. The returned
            flow maintains context immutability by creating new Context instances.
        """
        return ContextFlowCombinators.set_key(SHOULD_BREAK_KEY, value)

    @staticmethod
    def set_should_skip(value: bool = True) -> Flow[Context, Context]:
        """Create a Flow that sets the skip signal in the context.

        This method creates a Flow that sets the SHOULD_SKIP_KEY in the context
        to signal that trampoline execution should skip certain operations.
        When this flag is set to True, trampoline loops will skip specific
        operations or processing steps as determined by the trampoline logic.

        Args:
            value: Whether to signal skip (default: True). Set to True to
                signal skip operations, False to clear the skip signal.

        Returns:
            A Flow[Context, Context] that sets the skip flag and returns the
            updated context with the flag set to the specified value.

        Example:
            ```python
            from context.main import Context
            from context_flow.trampoline import TrampolineFlowCombinators

            # Create a flow to signal skip
            skip_flow = TrampolineFlowCombinators.set_should_skip(True)

            # Use in a flow chain
            context = Context()
            result_context = skip_flow.run_single(context)
            # result_context will have the skip flag set to True
            ```

        Note:
            This method uses ContextFlowCombinators.set_key() internally to
            create a type-safe flow that sets the SHOULD_SKIP_KEY. The returned
            flow maintains context immutability by creating new Context instances.
        """
        return ContextFlowCombinators.set_key(SHOULD_SKIP_KEY, value)

    @staticmethod
    def check_should_exit() -> Flow[Context, bool]:
        """Create a Flow that checks the exit signal in the context.

        This method creates a Flow that checks the SHOULD_EXIT_KEY in the context
        and returns its boolean value. If the key is not present in the context,
        it returns False (indicating no exit signal). This method is used by
        trampoline loops to determine whether execution should terminate.

        Returns:
            A Flow[Context, bool] that reads the exit flag from the context
            and returns True if exit is signaled, False otherwise.

        Example:
            ```python
            from context.main import Context
            from context_flow.trampoline import TrampolineFlowCombinators

            # Create a flow to check exit signal
            check_flow = TrampolineFlowCombinators.check_should_exit()

            # Use with a context that has the exit flag set
            context = Context()
            context[SHOULD_EXIT_KEY.path] = True
            result = check_flow.run_single(context)
            # result will be True

            # Use with a context without the flag
            empty_context = Context()
            result = check_flow.run_single(empty_context)
            # result will be False (default)
            ```

        Note:
            This method uses ContextFlowCombinators.get_key() internally to
            safely extract the SHOULD_EXIT_KEY value with False as the default.
            The returned Flow yields boolean values directly, not Context objects.
        """
        # Create a wrapper flow that ensures bool type
        base_flow = ContextFlowCombinators.get_key(SHOULD_EXIT_KEY, False)

        async def _check_exit_flow(
            stream: AsyncGenerator[Context, None]
        ) -> AsyncGenerator[bool, None]:
            """Wrapper flow that ensures bool return type."""
            result_stream = base_flow(stream)
            async for result in result_stream:
                # Cast to bool since we know default=False ensures non-None result
                yield bool(result) if result is not None else False

        return Flow(_check_exit_flow, name="check_should_exit")

    @staticmethod
    def check_should_break() -> Flow[Context, bool]:
        """Create a Flow that checks the break signal in the context.

        This method creates a Flow that checks the SHOULD_BREAK_KEY in the context
        and returns its boolean value. If the key is not present in the context,
        it returns False (indicating no break signal). This method is used by
        trampoline loops to determine whether execution should break/restart
        the current iteration.

        Returns:
            A Flow[Context, bool] that reads the break flag from the context
            and returns True if break is signaled, False otherwise.

        Example:
            ```python
            from context.main import Context
            from context_flow.trampoline import TrampolineFlowCombinators

            # Create a flow to check break signal
            check_flow = TrampolineFlowCombinators.check_should_break()

            # Use with a context that has the break flag set
            context = Context()
            context[SHOULD_BREAK_KEY.path] = True
            result = check_flow.run_single(context)
            # result will be True

            # Use with a context without the flag
            empty_context = Context()
            result = check_flow.run_single(empty_context)
            # result will be False (default)
            ```

        Note:
            This method uses ContextFlowCombinators.get_key() internally to
            safely extract the SHOULD_BREAK_KEY value with False as the default.
            The returned Flow yields boolean values directly, not Context objects.
        """
        # Create a wrapper flow that ensures bool type
        base_flow = ContextFlowCombinators.get_key(SHOULD_BREAK_KEY, False)

        async def _check_break_flow(
            stream: AsyncGenerator[Context, None]
        ) -> AsyncGenerator[bool, None]:
            """Wrapper flow that ensures bool return type."""
            result_stream = base_flow(stream)
            async for result in result_stream:
                # Cast to bool since we know default=False ensures non-None result
                yield bool(result) if result is not None else False

        return Flow(_check_break_flow, name="check_should_break")
