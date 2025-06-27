"""Flow-based trampoline execution system for iterative and interactive applications.

This module provides Flow combinators that enable trampoline-style execution patterns,
allowing for continuous loops with clean exit and restart conditions managed through Context state.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from ..context import Context, ContextKey
from ..context.flow_integration import ContextFlowCombinators
from ..flow import Flow


async def _async_iter_from_item(item: Any) -> AsyncIterator[Any]:
    """Helper to create async iterator from single item."""
    yield item


# Control flow context keys
SHOULD_EXIT_KEY = ContextKey.create(
    "flow.trampoline.should_exit", bool, "Signal to exit trampoline loop"
)
SHOULD_BREAK_KEY = ContextKey.create(
    "flow.trampoline.should_break", bool, "Signal to break/restart current iteration"
)
SHOULD_SKIP_KEY = ContextKey.create(
    "flow.trampoline.should_skip", bool, "Signal to skip certain operations"
)


class TrampolineFlowCombinators:
    """Flow combinators for trampoline-style execution patterns."""

    @staticmethod
    def set_should_exit(value: bool = True) -> Flow[Context, Context]:
        """Create a Flow that sets the exit signal in the context.

        Args:
            value: Whether to signal exit (default: True)

        Returns:
            Flow that sets the exit flag and returns updated context
        """
        return ContextFlowCombinators.set_key(SHOULD_EXIT_KEY, value)

    @staticmethod
    def set_should_break(value: bool = True) -> Flow[Context, Context]:
        """Create a Flow that sets the break/restart signal in the context.

        Args:
            value: Whether to signal break (default: True)

        Returns:
            Flow that sets the break flag and returns updated context
        """
        return ContextFlowCombinators.set_key(SHOULD_BREAK_KEY, value)

    @staticmethod
    def set_should_skip(value: bool = True) -> Flow[Context, Context]:
        """Create a Flow that sets the skip signal in the context.

        Args:
            value: Whether to signal skip (default: True)

        Returns:
            Flow that sets the skip flag and returns updated context
        """
        return ContextFlowCombinators.set_key(SHOULD_SKIP_KEY, value)

    @staticmethod
    def check_should_exit() -> Flow[Context, bool]:
        """Create a Flow that checks if exit has been signaled.

        Returns:
            Flow that returns True if exit is signaled, False otherwise
        """
        return ContextFlowCombinators.optional_key(SHOULD_EXIT_KEY, False)

    @staticmethod
    def check_should_break() -> Flow[Context, bool]:
        """Create a Flow that checks if break/restart has been signaled.

        Returns:
            Flow that returns True if break is signaled, False otherwise
        """
        return ContextFlowCombinators.optional_key(SHOULD_BREAK_KEY, False)

    @staticmethod
    def check_should_skip() -> Flow[Context, bool]:
        """Create a Flow that checks if skip has been signaled.

        Returns:
            Flow that returns True if skip is signaled, False otherwise
        """
        return ContextFlowCombinators.optional_key(SHOULD_SKIP_KEY, False)

    @staticmethod
    def clear_break_flag() -> Flow[Context, Context]:
        """Create a Flow that clears the break flag.

        Returns:
            Flow that removes the break flag from context
        """
        return ContextFlowCombinators.set_key(SHOULD_BREAK_KEY, False)

    @staticmethod
    def clear_skip_flag() -> Flow[Context, Context]:
        """Create a Flow that clears the skip flag.

        Returns:
            Flow that removes the skip flag from context
        """
        return ContextFlowCombinators.set_key(SHOULD_SKIP_KEY, False)

    @staticmethod
    def exitable_chain(*flows: Flow[Context, Context]) -> Flow[Context, Context]:
        """Create a Flow that executes a chain of flows with exit/break checking.

        Executes each flow in sequence, checking for exit or break signals after each.
        If exit is signaled, stops execution immediately.
        If break is signaled, clears the flag and starts the chain over.

        Args:
            *flows: Sequence of flows to execute

        Returns:
            Flow that executes the chain with exit/break handling
        """
        if not flows:
            return Flow.identity()

        async def exitable_chain_impl(
            stream: AsyncIterator[Context],
        ) -> AsyncIterator[Context]:
            async for context in stream:
                current_context = context

                while True:  # Loop for break/restart handling
                    # Execute each flow in the chain
                    for flow in flows:
                        # Run the flow using async execution
                        result_stream = flow(_async_iter_from_item(current_context))
                        async for result_context in result_stream:
                            current_context = result_context
                            break  # Take first result

                        # Check for exit signal
                        should_exit = current_context.get(SHOULD_EXIT_KEY.path, False)
                        if should_exit:
                            yield current_context
                            return

                        # Check for break signal
                        should_break = current_context.get(SHOULD_BREAK_KEY.path, False)
                        if should_break:
                            # Clear break flag and restart chain
                            current_context = current_context.fork()
                            current_context[SHOULD_BREAK_KEY.path] = False
                            break  # Break inner loop to restart chain
                    else:
                        # If we completed the entire chain without break, we're done
                        yield current_context
                        break  # Exit the while loop

        flow_names = [getattr(f, "name", "unnamed") for f in flows]
        return Flow(
            exitable_chain_impl, name=f"exitable_chain({', '.join(flow_names)})"
        )

    @staticmethod
    def trampoline(flow: Flow[Context, Context]) -> Flow[Context, Context]:
        """Create a Flow that runs another flow in trampoline style until exit.

        Repeatedly executes the given flow until SHOULD_EXIT is signaled.
        Handles SHOULD_BREAK by restarting the current iteration.

        Args:
            flow: The flow to execute repeatedly

        Returns:
            Flow that runs the input flow in trampoline style
        """

        async def trampoline_impl(
            stream: AsyncIterator[Context],
        ) -> AsyncIterator[Context]:
            async for context in stream:
                current_context = context

                while True:
                    # Execute the flow using async execution
                    result_stream = flow(_async_iter_from_item(current_context))
                    async for result_context in result_stream:
                        current_context = result_context
                        break  # Take first result

                    # Check for exit signal
                    should_exit = current_context.get(SHOULD_EXIT_KEY.path, False)
                    if should_exit:
                        yield current_context
                        return

                    # Check for break signal
                    should_break = current_context.get(SHOULD_BREAK_KEY.path, False)
                    if should_break:
                        # Clear break flag and continue (restart iteration)
                        current_context = current_context.fork()
                        current_context[SHOULD_BREAK_KEY.path] = False
                        continue

        flow_name = getattr(flow, "name", "unnamed")
        return Flow(trampoline_impl, name=f"trampoline({flow_name})")

    @staticmethod
    def trampoline_chain(*flows: Flow[Context, Context]) -> Flow[Context, Context]:
        """Create a Flow that runs a chain of flows in trampoline style.

        Combines exitable_chain and trampoline - repeatedly executes the chain
        until exit is signaled, with break/restart support.

        Args:
            *flows: Sequence of flows to execute repeatedly

        Returns:
            Flow that executes the chain in trampoline style
        """
        chain = TrampolineFlowCombinators.exitable_chain(*flows)
        return TrampolineFlowCombinators.trampoline(chain)

    @staticmethod
    def conditional_flow(
        condition_flow: Flow[Context, bool],
        then_flow: Flow[Context, Context],
        else_flow: Flow[Context, Context] | None = None,
    ) -> Flow[Context, Context]:
        """Create a Flow that conditionally executes based on a boolean flow result.

        Args:
            condition_flow: Flow that returns a boolean condition
            then_flow: Flow to execute if condition is True
            else_flow: Optional flow to execute if condition is False

        Returns:
            Flow that conditionally executes then_flow or else_flow
        """

        async def conditional_impl(
            stream: AsyncIterator[Context],
        ) -> AsyncIterator[Context]:
            async for context in stream:
                # Evaluate condition using async execution
                condition_stream = condition_flow(_async_iter_from_item(context))
                condition_result = False
                async for result in condition_stream:
                    condition_result = result
                    break  # Take first result

                if condition_result:
                    # Execute then_flow
                    then_stream = then_flow(_async_iter_from_item(context))
                    async for result_context in then_stream:
                        yield result_context
                        break  # Take first result
                elif else_flow is not None:
                    # Execute else_flow
                    else_stream = else_flow(_async_iter_from_item(context))
                    async for result_context in else_stream:
                        yield result_context
                        break  # Take first result
                else:
                    # No else_flow, just pass through context
                    yield context

        condition_name = getattr(condition_flow, "name", "condition")
        then_name = getattr(then_flow, "name", "then")
        else_name = getattr(else_flow, "name", "else") if else_flow else "none"

        return Flow(
            conditional_impl,
            name=f"conditional({condition_name} ? {then_name} : {else_name})",
        )

    @staticmethod
    def skip_if(
        condition_flow: Flow[Context, bool], target_flow: Flow[Context, Context]
    ) -> Flow[Context, Context]:
        """Create a Flow that skips execution of target_flow if condition is True.

        Args:
            condition_flow: Flow that returns boolean condition
            target_flow: Flow to potentially skip

        Returns:
            Flow that conditionally executes target_flow
        """
        return TrampolineFlowCombinators.conditional_flow(
            condition_flow,
            then_flow=Flow.identity(),  # Skip by doing nothing
            else_flow=target_flow,  # Execute if condition is False
        )


# Extend Flow class with trampoline methods
def extend_flow_with_trampoline() -> None:
    """Extend Flow class with trampoline manipulation methods."""

    # Control signal operations
    Flow.set_should_exit = staticmethod(TrampolineFlowCombinators.set_should_exit)  # type: ignore[attr-defined]
    Flow.set_should_break = staticmethod(TrampolineFlowCombinators.set_should_break)  # type: ignore[attr-defined]
    Flow.set_should_skip = staticmethod(TrampolineFlowCombinators.set_should_skip)  # type: ignore[attr-defined]

    # Control signal checks
    Flow.check_should_exit = staticmethod(TrampolineFlowCombinators.check_should_exit)  # type: ignore[attr-defined]
    Flow.check_should_break = staticmethod(TrampolineFlowCombinators.check_should_break)  # type: ignore[attr-defined]
    Flow.check_should_skip = staticmethod(TrampolineFlowCombinators.check_should_skip)  # type: ignore[attr-defined]

    # Control signal clearing
    Flow.clear_break_flag = staticmethod(TrampolineFlowCombinators.clear_break_flag)  # type: ignore[attr-defined]
    Flow.clear_skip_flag = staticmethod(TrampolineFlowCombinators.clear_skip_flag)  # type: ignore[attr-defined]

    # Trampoline execution patterns
    Flow.exitable_chain = staticmethod(TrampolineFlowCombinators.exitable_chain)  # type: ignore[attr-defined]
    Flow.trampoline = staticmethod(TrampolineFlowCombinators.trampoline)  # type: ignore[attr-defined]
    Flow.trampoline_chain = staticmethod(TrampolineFlowCombinators.trampoline_chain)  # type: ignore[attr-defined]

    # Conditional execution
    Flow.conditional_flow = staticmethod(TrampolineFlowCombinators.conditional_flow)  # type: ignore[attr-defined]
    Flow.skip_if = staticmethod(TrampolineFlowCombinators.skip_if)  # type: ignore[attr-defined]
