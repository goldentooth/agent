"""Execution pattern combinators for trampoline-style flow control.

This module provides static methods for creating Flow objects that implement
complex execution patterns including chaining, trampolines, conditionals,
and skip patterns for context-aware flow execution.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator, Callable

from context.main import Context
from context_flow.trampoline.constants import (
    SHOULD_BREAK_KEY,
    SHOULD_EXIT_KEY,
    async_iter_from_item,
)
from flow.flow import Flow

__all__ = [
    "ExecutionCombinators",
]


class ExecutionCombinators:
    """Flow combinators for complex execution patterns and flow control.

    This class provides static methods for creating Flow objects that implement
    sophisticated execution patterns including sequential chaining with exit/break
    support, trampoline execution, cycling chains, conditional flows, and skip patterns.

    All methods are static and return Flow[Context, Context] objects that can
    be chained and composed with other flows for complex execution patterns.
    """

    @staticmethod
    def exitable_chain(*flows: Flow[Context, Context]) -> Flow[Context, Context]:
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
            from flow.flow import Flow

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
        if not flows:
            # Return identity flow for empty flows list
            return Flow.identity()

        async def _exitable_chain_flow(
            stream: AsyncGenerator[Context, None],
        ) -> AsyncGenerator[Context, None]:
            """Flow that executes flows sequentially with exit/break support."""
            async for initial_context in stream:
                current_context = initial_context

                # Restart loop for break handling
                while True:
                    # Execute flows sequentially
                    for flow in flows:
                        # Execute current flow
                        flow_stream = async_iter_from_item(current_context)
                        result_stream = flow(flow_stream)

                        # Get result from flow
                        flow_result = None
                        async for result_context in result_stream:
                            flow_result = result_context
                            break  # Take first result

                        # Update context only if flow produced a result
                        if flow_result is not None:
                            current_context = flow_result

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
                            break  # Break from flows loop to restart
                    else:
                        # All flows completed successfully, exit restart loop
                        break

                yield current_context

        return Flow(_exitable_chain_flow, name="exitable_chain")

    @staticmethod
    def trampoline(flow: Flow[Context, Context]) -> Flow[Context, Context]:
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
            from flow.flow import Flow

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

        async def _trampoline_flow(
            stream: AsyncGenerator[Context, None],
        ) -> AsyncGenerator[Context, None]:
            """Flow that repeatedly executes a flow until exit is signaled."""
            async for initial_context in stream:
                original_context = initial_context
                current_context = initial_context

                # Trampoline loop
                while True:
                    # Execute the flow with current context
                    flow_stream = async_iter_from_item(current_context)
                    result_stream = flow(flow_stream)

                    # Get result from flow
                    flow_result = None
                    async for result_context in result_stream:
                        flow_result = result_context
                        break  # Take first result

                    # Update context only if flow produced a result
                    if flow_result is not None:
                        current_context = flow_result

                    # Check for exit signal
                    should_exit = current_context.get(SHOULD_EXIT_KEY.path, False)
                    if should_exit:
                        yield current_context
                        return

                    # Check for break signal
                    should_break = current_context.get(SHOULD_BREAK_KEY.path, False)
                    if should_break:
                        # Clear break flag and restart with original context
                        current_context = original_context.fork()
                        current_context[SHOULD_BREAK_KEY.path] = False

        return Flow(_trampoline_flow, name="trampoline")

    @staticmethod
    def trampoline_chain(*flows: Flow[Context, Context]) -> Flow[Context, Context]:
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
            from flow.flow import Flow

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
        if not flows:
            # Return identity flow for empty flows list
            return Flow.identity()

        async def _trampoline_chain_flow(
            stream: AsyncGenerator[Context, None],
        ) -> AsyncGenerator[Context, None]:
            """Flow that cycles through flows repeatedly until exit is signaled."""
            async for initial_context in stream:
                original_context = initial_context
                current_context = initial_context
                flow_index = 0  # Track current position in the flow cycle

                # Trampoline cycle loop
                while True:
                    # Get current flow (cycle through flows)
                    current_flow = flows[flow_index]

                    # Execute current flow
                    flow_stream = async_iter_from_item(current_context)
                    result_stream = current_flow(flow_stream)

                    # Get result from flow
                    flow_result = None
                    async for result_context in result_stream:
                        flow_result = result_context
                        break  # Take first result

                    # Update context only if flow produced a result
                    if flow_result is not None:
                        current_context = flow_result

                    # Check for exit signal
                    should_exit = current_context.get(SHOULD_EXIT_KEY.path, False)
                    if should_exit:
                        yield current_context
                        return

                    # Check for break signal
                    should_break = current_context.get(SHOULD_BREAK_KEY.path, False)
                    if should_break:
                        # Clear break flag and restart cycle with original context
                        current_context = original_context.fork()
                        current_context[SHOULD_BREAK_KEY.path] = False
                        flow_index = 0  # Reset to first flow
                        continue

                    # Move to next flow in cycle
                    flow_index = (flow_index + 1) % len(flows)

        return Flow(_trampoline_chain_flow, name="trampoline_chain")

    @staticmethod
    def conditional_flow(
        predicate: Callable[[Context], bool],
        then_flow: Flow[Context, Context],
        else_flow: Flow[Context, Context] | None = None,
    ) -> Flow[Context, Context]:
        """Create a Flow that conditionally applies flows based on context predicate.

        This method creates a Flow that evaluates a predicate function on the input
        Context and applies either the then_flow or else_flow accordingly. This enables
        context-aware branching logic in trampoline execution patterns.

        The predicate function receives the Context object and should return True to
        execute the then_flow, or False to execute the else_flow. If no else_flow is
        provided and the predicate returns False, the original context is passed through
        unchanged.

        Args:
            predicate: Function that takes a Context and returns bool to determine
                which flow to execute. Should be a pure function without side effects.
            then_flow: Flow[Context, Context] to execute when predicate returns True.
                This flow will receive the original context as input.
            else_flow: Optional Flow[Context, Context] to execute when predicate returns
                False. If None, the original context is passed through unchanged.

        Returns:
            A Flow[Context, Context] that conditionally executes flows based on the
            predicate evaluation.

        Example:
            ```python
            from context.main import Context
            from context_flow.trampoline.execution_combinators import ExecutionCombinators
            from flow.flow import Flow

            # Create predicate that checks if processing is needed
            def needs_processing(ctx: Context) -> bool:
                return ctx.get("status", "") != "completed"

            # Create conditional flows
            process_flow = Flow.from_sync_fn(lambda ctx: ctx.fork().set("status", "completed"))
            skip_flow = Flow.from_sync_fn(lambda ctx: ctx.fork().set("skipped", True))

            # Create conditional flow
            conditional = ExecutionCombinators.conditional_flow(
                needs_processing, process_flow, skip_flow
            )

            # Execute conditional flow
            context = Context()
            context["status"] = "pending"
            result = conditional.run_single(context)
            # result will have status="completed" since predicate returned True
            ```

        Note:
            The conditional_flow pattern is useful for:
            - Context-based branching logic in trampoline execution
            - Skip/process decisions based on context state
            - Routing flows based on context conditions
            - Implementing state-dependent flow execution

            The predicate function should be deterministic and avoid side effects
            to ensure predictable flow behavior in trampoline patterns.
        """

        async def _conditional_flow(
            stream: AsyncGenerator[Context, None],
        ) -> AsyncGenerator[Context, None]:
            """Flow that conditionally applies flows based on context predicate."""
            async for context in stream:
                # Evaluate predicate on the context
                if predicate(context):
                    # Execute then_flow
                    then_stream = async_iter_from_item(context)
                    result_stream = then_flow(then_stream)

                    # Yield results from then_flow
                    async for result_context in result_stream:
                        yield result_context
                        break  # Take first result only
                elif else_flow is not None:
                    # Execute else_flow
                    else_stream = async_iter_from_item(context)
                    result_stream = else_flow(else_stream)

                    # Yield results from else_flow
                    async for result_context in result_stream:
                        yield result_context
                        break  # Take first result only
                else:
                    # No else_flow provided, pass through original context
                    yield context

        return Flow(_conditional_flow, name="conditional_flow")

    @staticmethod
    def skip_if(
        predicate: Callable[[Context], bool],
        flow: Flow[Context, Context],
    ) -> Flow[Context, Context]:
        """Create a Flow that conditionally skips execution based on context predicate.

        This method creates a Flow that evaluates a predicate function on the input
        Context and either executes the provided flow or skips it (passing through
        the original context unchanged). When the predicate returns True, the flow
        is skipped and the original context is passed through. When the predicate
        returns False, the flow is executed normally.

        This is useful for implementing conditional execution patterns where certain
        flows should be bypassed based on context state, such as skipping expensive
        operations when they're not needed or avoiding processing when certain
        conditions are already met.

        Args:
            predicate: Function that takes a Context and returns bool. When True,
                the flow is skipped and context passed through unchanged. When False,
                the flow is executed normally. Should be a pure function without side effects.
            flow: Flow[Context, Context] to execute when predicate returns False.
                This flow will receive the original context as input when executed.

        Returns:
            A Flow[Context, Context] that conditionally executes the flow based on
            the predicate evaluation.

        Example:
            ```python
            from context.main import Context
            from context_flow.trampoline.execution_combinators import ExecutionCombinators
            from flow.flow import Flow

            # Create predicate that checks if processing should be skipped
            def already_processed(ctx: Context) -> bool:
                return ctx.get("status", "") == "completed"

            # Create expensive processing flow
            def expensive_processing(ctx: Context) -> Context:
                result = ctx.fork()
                result["status"] = "completed"
                result["processed_data"] = "expensive_result"
                return result

            process_flow = Flow.from_sync_fn(expensive_processing)

            # Create skip_if flow
            skip_if_processed = ExecutionCombinators.skip_if(
                already_processed, process_flow
            )

            # Execute with already completed context (will skip)
            context1 = Context()
            context1["status"] = "completed"
            result1 = skip_if_processed.run_single(context1)
            # result1 will be unchanged (no processing occurred)

            # Execute with pending context (will process)
            context2 = Context()
            context2["status"] = "pending"
            result2 = skip_if_processed.run_single(context2)
            # result2 will have status="completed" and processed_data
            ```

        Note:
            The skip_if pattern is useful for:
            - Avoiding expensive operations when they're not needed
            - Conditional processing based on context state
            - Implementing caching-like behavior in flow chains
            - Skipping redundant operations in trampoline loops

            The predicate function should be deterministic and avoid side effects
            to ensure predictable skipping behavior. When skipped, the original
            context is passed through completely unchanged, preserving all data
            and maintaining context immutability.
        """

        async def _skip_if_flow(
            stream: AsyncGenerator[Context, None],
        ) -> AsyncGenerator[Context, None]:
            """Flow that conditionally skips execution based on context predicate."""
            async for context in stream:
                # Evaluate predicate on the context
                if predicate(context):
                    # Skip execution, pass through original context unchanged
                    yield context
                else:
                    # Execute the flow normally
                    flow_stream = async_iter_from_item(context)
                    result_stream = flow(flow_stream)

                    # Yield results from flow execution
                    async for result_context in result_stream:
                        yield result_context
                        break  # Take first result only

        return Flow(_skip_if_flow, name="skip_if")
