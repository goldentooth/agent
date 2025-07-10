"""Trampoline system for context-aware flow execution.

This module provides trampoline execution patterns for iterative and conditional
flow processing with context state management.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from .constants import (
    SHOULD_BREAK_KEY,
    SHOULD_EXIT_KEY,
    SHOULD_SKIP_KEY,
    async_iter_from_item,
)
from .execution_combinators import ExecutionCombinators
from .flag_combinators import FlagCombinators
from .flow_extensions import extend_flow_with_trampoline

if TYPE_CHECKING:
    from context.main import Context
    from flowengine.flow import Flow

__all__ = [
    "async_iter_from_item",
    "extend_flow_with_trampoline",
    "SHOULD_EXIT_KEY",
    "SHOULD_BREAK_KEY",
    "SHOULD_SKIP_KEY",
    "TrampolineFlowCombinators",
]


class TrampolineFlowCombinators:
    """Flow combinators for trampoline-style execution patterns.

    This class provides static methods that create Flow instances for
    trampoline execution patterns including conditional flow control,
    iterative execution with break/exit conditions, and context-aware
    state management.

    All methods are aggregated from specialized combinator classes:
    - Flag management from FlagCombinators
    - Execution patterns from ExecutionCombinators

    This aggregated class maintains backward compatibility with the
    original monolithic implementation while enabling modular organization.
    """

    # Flag management methods (delegated to FlagCombinators)
    @staticmethod
    def set_should_exit(value: bool = True) -> "Flow[Context, Context]":
        """Create a Flow that sets the exit signal in the context."""
        return FlagCombinators.set_should_exit(value)

    @staticmethod
    def set_should_break(value: bool = True) -> "Flow[Context, Context]":
        """Create a Flow that sets the break signal in the context."""
        return FlagCombinators.set_should_break(value)

    @staticmethod
    def set_should_skip(value: bool = True) -> "Flow[Context, Context]":
        """Create a Flow that sets the skip signal in the context."""
        return FlagCombinators.set_should_skip(value)

    @staticmethod
    def check_should_exit() -> "Flow[Context, bool]":
        """Create a Flow that checks if exit signal is set."""
        return FlagCombinators.check_should_exit()

    @staticmethod
    def check_should_break() -> "Flow[Context, bool]":
        """Create a Flow that checks if break signal is set."""
        return FlagCombinators.check_should_break()

    @staticmethod
    def check_should_skip() -> "Flow[Context, bool]":
        """Create a Flow that checks if skip signal is set."""
        return FlagCombinators.check_should_skip()

    @staticmethod
    def clear_break_flag() -> "Flow[Context, Context]":
        """Create a Flow that clears the break flag."""
        return FlagCombinators.clear_break_flag()

    @staticmethod
    def clear_skip_flag() -> "Flow[Context, Context]":
        """Create a Flow that clears the skip flag."""
        return FlagCombinators.clear_skip_flag()

    # Execution pattern methods (delegated to ExecutionCombinators)
    @staticmethod
    def exitable_chain(*flows: "Flow[Context, Context]") -> "Flow[Context, Context]":
        """Create a Flow that executes flows sequentially with exit/break support.

        This method creates a Flow that executes a sequence of flows in order,
        checking for exit and break signals after each flow. If SHOULD_EXIT_KEY
        is set to True, the chain terminates early. If SHOULD_BREAK_KEY is set
        to True, the chain restarts from the beginning with the break flag cleared.

        Args:
            *flows: Variable number of Flow[Context, Context] objects to execute
                sequentially. Each flow should take a Context and return a Context.

        Returns:
            A Flow[Context, Context] that executes the flows sequentially with
            trampoline exit/break support.

        Example:
            ```python
            from context.main import Context
            from context_flow.trampoline.execution_combinators import ExecutionCombinators
            from flowengine.flow import Flow

            # Create individual flows
            flow1 = Flow.from_sync_fn(lambda ctx: ctx.set("step", 1))
            flow2 = Flow.from_sync_fn(lambda ctx: ctx.set("step", 2))
            flow3 = Flow.from_sync_fn(lambda ctx: ctx.set("step", 3))

            # Create exitable chain
            chain = ExecutionCombinators.exitable_chain(flow1, flow2, flow3)

            # Execute chain
            context = Context()
            result = chain.run_single(context)
            # All flows executed unless exit/break was signaled
            ```

        Note:
            The chain respects exit and break signals:
            - SHOULD_EXIT_KEY=True: Terminates chain immediately
            - SHOULD_BREAK_KEY=True: Restarts chain from beginning (clears break flag)
            Empty flows list returns the input context unchanged.
        """
        return ExecutionCombinators.exitable_chain(*flows)

    @staticmethod
    def trampoline(flow: "Flow[Context, Context]") -> "Flow[Context, Context]":
        """Create a Flow that repeatedly executes a flow until exit is signaled.

        This method creates a Flow that implements a trampoline execution pattern,
        repeatedly executing the given flow and feeding its output back as input
        for the next iteration. The loop continues until SHOULD_EXIT_KEY is set
        to True in the context. If SHOULD_BREAK_KEY is set, the loop restarts
        with the original input context.

        Args:
            flow: A Flow[Context, Context] that transforms context. This flow
                will be executed repeatedly, with each iteration's output
                becoming the next iteration's input.

        Returns:
            A Flow[Context, Context] that implements the trampoline pattern,
            yielding the final context after all iterations complete.

        Example:
            ```python
            from context.main import Context
            from context_flow.trampoline.execution_combinators import ExecutionCombinators
            from flowengine.flow import Flow

            # Create a flow that increments a counter until it reaches 10
            def increment_until_10(ctx: Context) -> Context:
                result = ctx.fork()
                count = ctx.get("count", 0)
                result["count"] = count + 1
                if count >= 9:  # Will be 10 after increment
                    result[SHOULD_EXIT_KEY.path] = True
                return result

            # Create trampoline flow
            increment_flow = Flow.from_sync_fn(increment_until_10)
            trampoline = ExecutionCombinators.trampoline(increment_flow)

            # Execute trampoline
            context = Context()
            context["count"] = 0
            result = trampoline.run_single(context)
            # result["count"] == 10
            ```

        Note:
            The trampoline pattern is useful for:
            - Iterative algorithms that process until convergence
            - State machines with multiple transitions
            - Recursive-like computations without stack overflow
            - Algorithms that need multiple transformation passes

            Control signals:
            - SHOULD_EXIT_KEY=True: Stops iteration and yields final result
            - SHOULD_BREAK_KEY=True: Restarts with original input (clears break flag)
        """
        return ExecutionCombinators.trampoline(flow)

    @staticmethod
    def trampoline_chain(*flows: "Flow[Context, Context]") -> "Flow[Context, Context]":
        """Create a Flow that cycles through multiple flows until exit is signaled.

        This method creates a Flow that executes multiple flows in a repeating cycle,
        cycling back to the first flow after the last one completes. The cycle
        continues until SHOULD_EXIT_KEY is set to True. If SHOULD_BREAK_KEY is set,
        the cycle restarts from the first flow with the original input context.

        This combines the sequential execution of exitable_chain with the repetitive
        nature of trampoline, making it ideal for multi-stage iterative algorithms,
        complex state machines, and cyclic processing workflows.

        Args:
            *flows: Variable number of Flow[Context, Context] objects to execute
                in a repeating cycle. Each flow should take a Context and return a Context.

        Returns:
            A Flow[Context, Context] that executes the flows in a repeating cycle
            until exit is signaled.

        Example:
            ```python
            from context.main import Context
            from context_flow.trampoline.execution_combinators import ExecutionCombinators
            from flowengine.flow import Flow

            # Create multi-stage processing flows
            def validate_flow(ctx: Context) -> Context:
                result = ctx.fork()
                data = ctx.get("data", [])
                result["validated"] = len(data) > 0
                return result

            def transform_flow(ctx: Context) -> Context:
                result = ctx.fork()
                if ctx.get("validated", False):
                    result["transformed"] = True
                return result

            def optimize_flow(ctx: Context) -> Context:
                result = ctx.fork()
                iterations = ctx.get("iterations", 0) + 1
                result["iterations"] = iterations
                # Exit after 3 complete cycles
                if iterations >= 9:  # 3 cycles * 3 flows = 9 iterations
                    result[SHOULD_EXIT_KEY.path] = True
                return result

            # Create flows
            validate = Flow.from_sync_fn(validate_flow)
            transform = Flow.from_sync_fn(transform_flow)
            optimize = Flow.from_sync_fn(optimize_flow)

            # Create cycling chain
            chain = ExecutionCombinators.trampoline_chain(
                validate, transform, optimize
            )

            # Execute chain
            context = Context()
            context["data"] = [1, 2, 3]
            result = chain.run_single(context)
            # Executes: validate → transform → optimize → validate → transform → optimize → ...
            ```

        Note:
            The trampoline_chain pattern is useful for:
            - Multi-stage iterative algorithms with distinct phases
            - State machines with multiple states that cycle
            - Complex validation/processing loops
            - Optimization algorithms with multiple phases

            Control signals:
            - SHOULD_EXIT_KEY=True: Terminates the entire cycle immediately
            - SHOULD_BREAK_KEY=True: Restarts from first flow with original context
            Empty flows list returns the input context unchanged.
        """
        return ExecutionCombinators.trampoline_chain(*flows)

    @staticmethod
    def conditional_flow(
        predicate: Callable[["Context"], bool],
        then_flow: "Flow[Context, Context]",
        else_flow: "Flow[Context, Context] | None" = None,
    ) -> "Flow[Context, Context]":
        """Create a Flow that conditionally applies flows based on context predicate."""
        return ExecutionCombinators.conditional_flow(predicate, then_flow, else_flow)

    @staticmethod
    def skip_if(
        predicate: Callable[["Context"], bool],
        flow: "Flow[Context, Context]",
    ) -> "Flow[Context, Context]":
        """Create a Flow that conditionally skips execution based on context predicate."""
        return ExecutionCombinators.skip_if(predicate, flow)
