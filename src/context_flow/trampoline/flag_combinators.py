"""Flag management combinators for context-aware flow execution.

This module provides flow combinators for managing execution flags (exit, break, skip)
in context-aware trampoline patterns. These combinators enable sophisticated control
flow patterns by setting and checking flags stored in the context.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from context.main import Context
from context_flow.integration import ContextFlowCombinators
from flow.flow import Flow

from .constants import SHOULD_BREAK_KEY, SHOULD_EXIT_KEY, SHOULD_SKIP_KEY

__all__ = [
    "SHOULD_EXIT_KEY",
    "SHOULD_BREAK_KEY",
    "SHOULD_SKIP_KEY",
    "FlagCombinators",
]


class FlagCombinators:
    """Flow combinators for managing execution flags in context.

    This class provides static methods for creating Flow objects that manage
    execution flags (exit, break, skip) in the context. These flags are used
    by trampoline execution patterns to control flow behavior.

    All methods are static and return Flow objects that can be chained and
    composed with other flows for complex execution patterns.
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
            from context_flow.flag_combinators import FlagCombinators

            # Create a flow to signal exit
            exit_flow = FlagCombinators.set_should_exit(True)

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
            from context_flow.flag_combinators import FlagCombinators

            # Create a flow to signal break
            break_flow = FlagCombinators.set_should_break(True)

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
            from context_flow.flag_combinators import FlagCombinators

            # Create a flow to signal skip
            skip_flow = FlagCombinators.set_should_skip(True)

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
            from context_flow.flag_combinators import FlagCombinators

            # Create a flow to check exit signal
            check_flow = FlagCombinators.check_should_exit()

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
            stream: AsyncGenerator[Context, None],
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
            from context_flow.flag_combinators import FlagCombinators

            # Create a flow to check break signal
            check_flow = FlagCombinators.check_should_break()

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
            stream: AsyncGenerator[Context, None],
        ) -> AsyncGenerator[bool, None]:
            """Wrapper flow that ensures bool return type."""
            result_stream = base_flow(stream)
            async for result in result_stream:
                # Cast to bool since we know default=False ensures non-None result
                yield bool(result) if result is not None else False

        return Flow(_check_break_flow, name="check_should_break")

    @staticmethod
    def check_should_skip() -> Flow[Context, bool]:
        """Create a Flow that checks the skip signal in the context.

        This method creates a Flow that checks the SHOULD_SKIP_KEY in the context
        and returns its boolean value. If the key is not present in the context,
        it returns False (indicating no skip signal). This method is used by
        trampoline loops to determine whether execution should skip certain
        operations or processing steps.

        Returns:
            A Flow[Context, bool] that reads the skip flag from the context
            and returns True if skip is signaled, False otherwise.

        Example:
            ```python
            from context.main import Context
            from context_flow.flag_combinators import FlagCombinators

            # Create a flow to check skip signal
            check_flow = FlagCombinators.check_should_skip()

            # Use with a context that has the skip flag set
            context = Context()
            context[SHOULD_SKIP_KEY.path] = True
            result = check_flow.run_single(context)
            # result will be True

            # Use with a context without the flag
            empty_context = Context()
            result = check_flow.run_single(empty_context)
            # result will be False (default)
            ```

        Note:
            This method uses ContextFlowCombinators.get_key() internally to
            safely extract the SHOULD_SKIP_KEY value with False as the default.
            The returned Flow yields boolean values directly, not Context objects.
        """
        # Create a wrapper flow that ensures bool type
        base_flow = ContextFlowCombinators.get_key(SHOULD_SKIP_KEY, False)

        async def _check_skip_flow(
            stream: AsyncGenerator[Context, None],
        ) -> AsyncGenerator[bool, None]:
            """Wrapper flow that ensures bool return type."""
            result_stream = base_flow(stream)
            async for result in result_stream:
                # Cast to bool since we know default=False ensures non-None result
                yield bool(result) if result is not None else False

        return Flow(_check_skip_flow, name="check_should_skip")

    @staticmethod
    def clear_break_flag() -> Flow[Context, Context]:
        """Create a Flow that clears the break signal in the context.

        This method creates a Flow that sets the SHOULD_BREAK_KEY in the context
        to False, effectively clearing/resetting the break signal. This is equivalent
        to calling set_should_break(False) but provides a more explicit method for
        clearing the flag in trampoline execution patterns.

        Returns:
            A Flow[Context, Context] that clears the break flag and returns the
            updated context with the break flag set to False.

        Example:
            ```python
            from context.main import Context
            from context_flow.flag_combinators import FlagCombinators

            # Create a flow to clear the break flag
            clear_flow = FlagCombinators.clear_break_flag()

            # Use in a flow chain
            context = Context()
            context[SHOULD_BREAK_KEY.path] = True  # Flag is set
            result_context = clear_flow.run_single(context)
            # result_context will have the break flag set to False
            ```

        Note:
            This method uses ContextFlowCombinators.set_key() internally to
            create a type-safe flow that sets the SHOULD_BREAK_KEY to False.
            The returned flow maintains context immutability by creating new
            Context instances.
        """
        return ContextFlowCombinators.set_key(SHOULD_BREAK_KEY, False)

    @staticmethod
    def clear_skip_flag() -> Flow[Context, Context]:
        """Create a Flow that clears the skip signal in the context.

        This method creates a Flow that sets the SHOULD_SKIP_KEY in the context
        to False, effectively clearing/resetting the skip signal. This is equivalent
        to calling set_should_skip(False) but provides a more explicit method for
        clearing the flag in trampoline execution patterns.

        Returns:
            A Flow[Context, Context] that clears the skip flag and returns the
            updated context with the skip flag set to False.

        Example:
            ```python
            from context.main import Context
            from context_flow.flag_combinators import FlagCombinators

            # Create a flow to clear the skip flag
            clear_flow = FlagCombinators.clear_skip_flag()

            # Use in a flow chain
            context = Context()
            context[SHOULD_SKIP_KEY.path] = True  # Flag is set
            result_context = clear_flow.run_single(context)
            # result_context will have the skip flag set to False
            ```

        Note:
            This method uses ContextFlowCombinators.set_key() internally to
            create a type-safe flow that sets the SHOULD_SKIP_KEY to False.
            The returned flow maintains context immutability by creating new
            Context instances.
        """
        return ContextFlowCombinators.set_key(SHOULD_SKIP_KEY, False)
