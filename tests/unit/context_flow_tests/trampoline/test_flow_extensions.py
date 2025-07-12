"""Tests for context_flow.trampoline.flow_extensions module."""

from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import AsyncMock, Mock, patch

import pytest

from context_flow.trampoline.flow_extensions import extend_flow_with_trampoline
from flow.flow import Flow


class TestExtendFlowWithTrampoline:
    """Test suite for extend_flow_with_trampoline function."""

    def test_extend_flow_with_trampoline_adds_methods(self) -> None:
        """Test that extend_flow_with_trampoline adds methods to Flow class."""
        # Extend Flow with trampoline methods
        extend_flow_with_trampoline()

        # Check that trampoline methods are added
        assert hasattr(Flow, "run_single")
        assert hasattr(Flow, "as_single_stream")
        assert hasattr(Flow, "repeat_until")
        assert hasattr(Flow, "exit_on")
        assert callable(getattr(Flow, "run_single"))
        assert callable(getattr(Flow, "as_single_stream"))
        assert callable(getattr(Flow, "repeat_until"))
        assert callable(getattr(Flow, "exit_on"))

    def test_extend_flow_with_trampoline_preserves_existing_methods(self) -> None:
        """Test that extending Flow preserves existing methods."""
        # Check that original methods exist before extending
        assert hasattr(Flow, "from_sync_fn")
        assert hasattr(Flow, "__rshift__")
        assert hasattr(Flow, "map")
        assert hasattr(Flow, "filter")

        extend_flow_with_trampoline()

        # Check that original methods still exist after extending
        assert hasattr(Flow, "from_sync_fn")
        assert hasattr(Flow, "__rshift__")
        assert hasattr(Flow, "map")
        assert hasattr(Flow, "filter")


class TestRunSingleMethod:
    """Test suite for run_single method added to Flow."""

    def test_run_single_basic_functionality(self) -> None:
        """Test basic functionality of run_single method."""
        extend_flow_with_trampoline()

        # Create a simple flow that doubles input
        flow: Flow[int, int] = Flow.from_sync_fn(lambda x: x * 2)

        # Test run_single method
        result: int = flow.run_single(5)  # type: ignore[attr-defined]
        assert result == 10

    def test_run_single_with_string_input(self) -> None:
        """Test run_single with string input/output."""
        extend_flow_with_trampoline()

        # Create a flow that uppercases strings
        flow: Flow[str, str] = Flow.from_sync_fn(lambda x: x.upper())

        # Test run_single method
        result: str = flow.run_single("hello")  # type: ignore[attr-defined]
        assert result == "HELLO"

    def test_run_single_with_type_transformation(self) -> None:
        """Test run_single with input/output type transformation."""
        extend_flow_with_trampoline()

        # Create a flow that converts int to string
        flow: Flow[int, str] = Flow.from_sync_fn(lambda x: str(x))

        # Test run_single method
        result: str = flow.run_single(42)  # type: ignore[attr-defined]
        assert result == "42"

    def test_run_single_with_async_flow(self) -> None:
        """Test run_single with async flow function."""
        extend_flow_with_trampoline()

        # Create an async flow
        async def async_double(x: int) -> int:
            return x * 2

        flow: Flow[int, int] = Flow.from_value_fn(async_double)

        # Test run_single method works with async flows
        result: int = flow.run_single(5)  # type: ignore[attr-defined]
        assert result == 10

    def test_run_single_raises_error_on_no_output(self) -> None:
        """Test that run_single raises RuntimeError when flow produces no output."""
        extend_flow_with_trampoline()

        # Create a flow that produces no output
        async def empty_flow(stream: Any) -> AsyncGenerator[Any, None]:
            # Return empty generator
            if False:
                yield  # Make it a generator function but yield nothing

        flow = Flow(empty_flow)

        # Test that RuntimeError is raised
        with pytest.raises(RuntimeError, match="Flow produced no output"):
            flow.run_single("test")  # type: ignore[attr-defined]

    def test_run_single_calls_run_in_background(self) -> None:
        """Test that run_single calls run_in_background."""
        extend_flow_with_trampoline()

        flow: Flow[str, str] = Flow.from_sync_fn(lambda x: x.upper())

        # Test that run_single works and implicitly uses run_in_background
        result = flow.run_single("test")  # type: ignore[attr-defined]
        assert result == "TEST"

    def test_run_single_uses_single_item_conversion(self) -> None:
        """Test that run_single properly converts single item to stream."""
        extend_flow_with_trampoline()

        # Track values processed by the flow
        processed_values = []

        def track_values(x: str) -> str:
            processed_values.append(x)
            return x.upper()

        flow: Flow[str, str] = Flow.from_sync_fn(track_values)

        # Call run_single
        result = flow.run_single("test")  # type: ignore[attr-defined]

        # Verify the single item was processed
        assert processed_values == ["test"]
        assert result == "TEST"


class TestAsSingleStreamMethod:
    """Test suite for as_single_stream method added to Flow."""

    def test_as_single_stream_creates_new_flow(self) -> None:
        """Test that as_single_stream creates a new Flow instance."""
        extend_flow_with_trampoline()

        flow: Flow[int, int] = Flow.from_sync_fn(lambda x: x * 2)
        single_flow = flow.as_single_stream(5)  # type: ignore[attr-defined]

        # Should return a new Flow instance
        assert isinstance(single_flow, Flow)
        assert single_flow is not flow

    def test_as_single_stream_sets_correct_name(self) -> None:
        """Test that as_single_stream sets correct flow name."""
        extend_flow_with_trampoline()

        flow: Flow[int, int] = Flow.from_sync_fn(lambda x: x * 2)
        flow.name = "double"  # Set name after creation
        single_flow = flow.as_single_stream(5)  # type: ignore[attr-defined]

        # Should have name with _single suffix and item
        assert single_flow.name == "double_single(5)"

    def test_as_single_stream_flow_functionality(self) -> None:
        """Test that as_single_stream flow works correctly."""
        extend_flow_with_trampoline()

        # Create a flow that doubles input
        original_flow: Flow[int, int] = Flow.from_sync_fn(lambda x: x * 2)

        # Create single stream flow
        single_flow = original_flow.as_single_stream(5)  # type: ignore[attr-defined]

        # Test that single flow works (ignoring input stream)
        result = single_flow.run_single("ignored_input")
        assert result == 10  # 5 * 2

    def test_as_single_stream_with_different_types(self) -> None:
        """Test as_single_stream with different input/output types."""
        extend_flow_with_trampoline()

        # Create flow that converts to string
        flow: Flow[int, str] = Flow.from_sync_fn(lambda x: f"number_{x}")
        single_flow = flow.as_single_stream(42)  # type: ignore[attr-defined]

        # Test the single stream flow
        result = single_flow.run_single("ignored")
        assert result == "number_42"

    def test_as_single_stream_with_complex_object(self) -> None:
        """Test as_single_stream with complex object as item."""
        extend_flow_with_trampoline()

        # Create flow that processes dictionary
        flow: Flow[dict[str, Any], str] = Flow.from_sync_fn(
            lambda x: x.get("name", "unknown")
        )
        test_dict = {"name": "test_user", "id": 123}
        single_flow = flow.as_single_stream(test_dict)  # type: ignore[attr-defined]

        # Test the single stream flow
        result = single_flow.run_single("ignored")
        assert result == "test_user"

    def test_as_single_stream_uses_configured_item(self) -> None:
        """Test that as_single_stream uses the configured item."""
        extend_flow_with_trampoline()

        # Track values processed
        processed_values = []

        def track_and_double(x: int) -> int:
            processed_values.append(x)
            return x * 2

        flow: Flow[int, int] = Flow.from_sync_fn(track_and_double)
        single_flow = flow.as_single_stream(5)  # type: ignore[attr-defined]

        # Execute the single stream flow (input should be ignored)
        result = single_flow.run_single("ignored_input")

        # Verify the configured item (5) was processed, not the run_single input
        assert processed_values == [5]
        assert result == 10


class TestRepeatUntilMethod:
    """Test suite for repeat_until method added to Flow."""

    def test_repeat_until_creates_new_flow(self) -> None:
        """Test that repeat_until creates a new Flow instance."""
        extend_flow_with_trampoline()

        flow: Flow[int, int] = Flow.from_sync_fn(lambda x: x + 1)
        repeat_flow = flow.repeat_until(lambda x: x >= 10)  # type: ignore[attr-defined]

        # Should return a new Flow instance
        assert isinstance(repeat_flow, Flow)
        assert repeat_flow is not flow

    def test_repeat_until_sets_correct_name(self) -> None:
        """Test that repeat_until sets correct flow name."""
        extend_flow_with_trampoline()

        flow: Flow[int, int] = Flow.from_sync_fn(lambda x: x + 1)
        flow.name = "increment"  # Set name after creation
        repeat_flow = flow.repeat_until(lambda x: x >= 10)  # type: ignore[attr-defined]

        # Should have name with repeat_ prefix and _until suffix
        assert repeat_flow.name == "repeat_increment_until"

    def test_repeat_until_basic_functionality(self) -> None:
        """Test basic functionality of repeat_until."""
        extend_flow_with_trampoline()

        # Create a flow that increments by 1
        flow: Flow[int, int] = Flow.from_sync_fn(lambda x: x + 1)

        # Create repeat_until flow that stops when value >= 5
        repeat_flow = flow.repeat_until(lambda x: x >= 5)  # type: ignore[attr-defined]

        # Test starting from 1, should repeat until reaching 5
        result = repeat_flow.run_single(1)
        assert result == 5

    def test_repeat_until_with_immediate_condition(self) -> None:
        """Test repeat_until when condition is immediately met."""
        extend_flow_with_trampoline()

        flow: Flow[int, int] = Flow.from_sync_fn(lambda x: x + 1)

        # Condition that is immediately true
        repeat_flow = flow.repeat_until(lambda x: x >= 1)  # type: ignore[attr-defined]

        # Should process once and then stop because condition is met
        result = repeat_flow.run_single(1)
        assert result == 2  # 1 + 1

    def test_repeat_until_with_doubling(self) -> None:
        """Test repeat_until with doubling operation."""
        extend_flow_with_trampoline()

        # Create a flow that doubles the input
        flow: Flow[int, int] = Flow.from_sync_fn(lambda x: x * 2)

        # Repeat until value >= 100
        repeat_flow = flow.repeat_until(lambda x: x >= 100)  # type: ignore[attr-defined]

        # Starting from 3: 3 -> 6 -> 12 -> 24 -> 48 -> 96 -> 192 (stop at 192)
        result = repeat_flow.run_single(3)
        assert result == 192

    def test_repeat_until_with_string_operation(self) -> None:
        """Test repeat_until with string operations."""
        extend_flow_with_trampoline()

        # Create a flow that appends 'x' to string
        flow: Flow[str, str] = Flow.from_sync_fn(lambda x: x + "x")

        # Repeat until string length >= 5
        repeat_flow = flow.repeat_until(lambda x: len(x) >= 5)  # type: ignore[attr-defined]

        # Starting from "a": "a" -> "ax" -> "axx" -> "axxx" -> "axxxx"
        # Stops when result "axxxx" meets condition len >= 5
        result = repeat_flow.run_single("a")
        assert result == "axxxx"

    def test_repeat_until_condition_function_types(self) -> None:
        """Test repeat_until with different condition function types."""
        extend_flow_with_trampoline()

        flow: Flow[int, int] = Flow.from_sync_fn(lambda x: x + 2)

        # Test with lambda condition
        repeat_flow1 = flow.repeat_until(lambda x: x > 10)  # type: ignore[attr-defined]
        result1 = repeat_flow1.run_single(1)
        assert result1 == 11  # 1 -> 3 -> 5 -> 7 -> 9 -> 11

        # Test with named function condition
        def is_even_and_greater_than_6(x: int) -> bool:
            return x % 2 == 0 and x > 6

        repeat_flow2 = flow.repeat_until(is_even_and_greater_than_6)  # type: ignore[attr-defined]
        result2 = repeat_flow2.run_single(2)
        assert result2 == 8  # 2 -> 4 -> 6 -> 8

    def test_repeat_until_processes_items_multiple_times(self) -> None:
        """Test that repeat_until processes items through the flow multiple times."""
        extend_flow_with_trampoline()

        # Track processing calls
        process_count = 0

        def increment_and_count(x: int) -> int:
            nonlocal process_count
            process_count += 1
            return x + 1

        flow: Flow[int, int] = Flow.from_sync_fn(increment_and_count)
        repeat_flow = flow.repeat_until(lambda x: x >= 3)  # type: ignore[attr-defined]

        # Starting from 1: 1 -> 2 -> 3 (stops)
        result = repeat_flow.run_single(1)

        assert result == 3
        assert process_count == 2  # Called twice: 1->2, 2->3


class TestExitOnMethod:
    """Test suite for exit_on method added to Flow."""

    def test_exit_on_creates_new_flow(self) -> None:
        """Test that exit_on creates a new Flow instance."""
        extend_flow_with_trampoline()

        flow: Flow[int, int] = Flow.from_sync_fn(lambda x: x + 1)
        exit_flow = flow.exit_on(lambda x: x > 5)  # type: ignore[attr-defined]

        # Should return a new Flow instance
        assert isinstance(exit_flow, Flow)
        assert exit_flow is not flow

    def test_exit_on_sets_correct_name(self) -> None:
        """Test that exit_on sets correct flow name."""
        extend_flow_with_trampoline()

        flow: Flow[int, int] = Flow.from_sync_fn(lambda x: x + 1)
        flow.name = "increment"  # Set name after creation
        exit_flow = flow.exit_on(lambda x: x > 5)  # type: ignore[attr-defined]

        # Should have name with _exit_on suffix
        assert exit_flow.name == "increment_exit_on"

    def test_exit_on_basic_functionality(self) -> None:
        """Test basic functionality of exit_on."""
        extend_flow_with_trampoline()

        # Create a flow that processes a stream of numbers
        async def number_generator(
            stream: AsyncGenerator[Any, None]
        ) -> AsyncGenerator[int, None]:
            # Generate numbers 1, 2, 3, 4, 5, 6, 7
            for i in range(1, 8):
                yield i

        flow = Flow(number_generator)

        # Create exit_on flow that stops when value > 4
        exit_flow = flow.exit_on(lambda x: x > 4)  # type: ignore[attr-defined]

        # Collect all results from the flow
        results = []

        # Need to create a proper async function to test exit_on
        async def collect_results() -> list[int]:
            # Create an async generator from empty input
            async def empty_gen() -> AsyncGenerator[Any, None]:
                if False:
                    yield  # Make it async generator

            stream = empty_gen()
            result_stream = exit_flow(stream)
            collected = []
            async for item in result_stream:
                collected.append(item)
            return collected

        from goldentooth_agent.core.background_loop import run_in_background

        results = run_in_background(collect_results())

        # Should get 1, 2, 3, 4 (stops at 5 because 5 > 4)
        assert results == [1, 2, 3, 4]

    def test_exit_on_with_immediate_exit_condition(self) -> None:
        """Test exit_on when condition is immediately met."""
        extend_flow_with_trampoline()

        # Create a flow that processes a stream starting with a value that meets exit condition
        async def immediate_exit_generator(
            stream: AsyncGenerator[Any, None]
        ) -> AsyncGenerator[int, None]:
            yield 10  # This should trigger immediate exit
            yield 5  # This should not be yielded
            yield 3

        flow = Flow(immediate_exit_generator)

        # Exit when value >= 10
        exit_flow = flow.exit_on(lambda x: x >= 10)  # type: ignore[attr-defined]

        # Collect all results from the flow
        async def collect_results() -> list[int]:
            async def empty_gen() -> AsyncGenerator[Any, None]:
                if False:
                    yield

            stream = empty_gen()
            result_stream = exit_flow(stream)
            collected = []
            async for item in result_stream:
                collected.append(item)
            return collected

        from goldentooth_agent.core.background_loop import run_in_background

        results = run_in_background(collect_results())

        # Should get no results because first item (10) triggers exit
        assert results == []

    def test_exit_on_with_no_exit_condition_met(self) -> None:
        """Test exit_on when exit condition is never met."""
        extend_flow_with_trampoline()

        # Create a flow that processes a stream where exit condition is never met
        async def no_exit_generator(
            stream: AsyncGenerator[Any, None]
        ) -> AsyncGenerator[int, None]:
            for i in [1, 2, 3, 4, 5]:
                yield i

        flow = Flow(no_exit_generator)

        # Exit when value > 10 (never happens)
        exit_flow = flow.exit_on(lambda x: x > 10)  # type: ignore[attr-defined]

        # Collect all results from the flow
        async def collect_results() -> list[int]:
            async def empty_gen() -> AsyncGenerator[Any, None]:
                if False:
                    yield

            stream = empty_gen()
            result_stream = exit_flow(stream)
            collected = []
            async for item in result_stream:
                collected.append(item)
            return collected

        from goldentooth_agent.core.background_loop import run_in_background

        results = run_in_background(collect_results())

        # Should get all results since exit condition is never met
        assert results == [1, 2, 3, 4, 5]

    def test_exit_on_with_string_condition(self) -> None:
        """Test exit_on with string-based exit condition."""
        extend_flow_with_trampoline()

        # Create a flow that processes strings
        async def string_generator(
            stream: AsyncGenerator[Any, None]
        ) -> AsyncGenerator[str, None]:
            words = ["hello", "world", "stop", "here", "please"]
            for word in words:
                yield word

        flow = Flow(string_generator)

        # Exit when string equals "stop"
        exit_flow = flow.exit_on(lambda x: x == "stop")  # type: ignore[attr-defined]

        # Collect all results from the flow
        async def collect_results() -> list[str]:
            async def empty_gen() -> AsyncGenerator[Any, None]:
                if False:
                    yield

            stream = empty_gen()
            result_stream = exit_flow(stream)
            collected = []
            async for item in result_stream:
                collected.append(item)
            return collected

        from goldentooth_agent.core.background_loop import run_in_background

        results = run_in_background(collect_results())

        # Should get "hello", "world" (stops at "stop")
        assert results == ["hello", "world"]

    def test_exit_on_condition_function_types(self) -> None:
        """Test exit_on with different condition function types."""
        extend_flow_with_trampoline()

        async def number_generator(
            stream: AsyncGenerator[Any, None]
        ) -> AsyncGenerator[int, None]:
            for i in range(1, 11):  # 1 to 10
                yield i

        flow = Flow(number_generator)

        # Test with lambda condition
        exit_flow1 = flow.exit_on(lambda x: x % 7 == 0)  # type: ignore[attr-defined]

        async def collect_results1() -> list[int]:
            async def empty_gen() -> AsyncGenerator[Any, None]:
                if False:
                    yield

            stream = empty_gen()
            result_stream = exit_flow1(stream)
            collected = []
            async for item in result_stream:
                collected.append(item)
            return collected

        from goldentooth_agent.core.background_loop import run_in_background

        results1 = run_in_background(collect_results1())
        assert results1 == [1, 2, 3, 4, 5, 6]  # Stops at 7

        # Test with named function condition
        def is_greater_than_4(x: int) -> bool:
            return x > 4

        exit_flow2 = flow.exit_on(is_greater_than_4)  # type: ignore[attr-defined]

        async def collect_results2() -> list[int]:
            async def empty_gen() -> AsyncGenerator[Any, None]:
                if False:
                    yield

            stream = empty_gen()
            result_stream = exit_flow2(stream)
            collected = []
            async for item in result_stream:
                collected.append(item)
            return collected

        results2 = run_in_background(collect_results2())
        assert results2 == [1, 2, 3, 4]  # Stops at 5


class TestTrampolineFlowExtensionsIntegration:
    """Integration tests for all trampoline flow extension methods."""

    def test_all_methods_work_together(self) -> None:
        """Test that all trampoline methods can be used together."""
        extend_flow_with_trampoline()

        # Create a base flow that doubles input
        base_flow: Flow[int, int] = Flow.from_sync_fn(lambda x: x * 2)

        # Test run_single
        single_result = base_flow.run_single(3)  # type: ignore[attr-defined]
        assert single_result == 6

        # Test as_single_stream
        single_stream_flow = base_flow.as_single_stream(4)  # type: ignore[attr-defined]
        stream_result = single_stream_flow.run_single("ignored")
        assert stream_result == 8

        # Test repeat_until
        repeat_flow = base_flow.repeat_until(lambda x: x >= 50)  # type: ignore[attr-defined]
        repeat_result = repeat_flow.run_single(3)
        assert repeat_result == 96  # 3 -> 6 -> 12 -> 24 -> 48 -> 96

    def test_chaining_trampoline_methods(self) -> None:
        """Test chaining trampoline methods with regular flow operations."""
        extend_flow_with_trampoline()

        # Create flows
        double_flow: Flow[int, int] = Flow.from_sync_fn(lambda x: x * 2)
        add_one_flow: Flow[int, int] = Flow.from_sync_fn(lambda x: x + 1)

        # Chain flows using >> operator
        chained_flow = double_flow >> add_one_flow

        # Use trampoline methods on chained flow
        result = chained_flow.run_single(5)  # type: ignore[attr-defined]
        assert result == 11  # (5 * 2) + 1

        # Create repeat flow from chained flow
        repeat_chained = chained_flow.repeat_until(lambda x: x >= 100)  # type: ignore[attr-defined]
        repeat_result = repeat_chained.run_single(1)
        # 1 -> 3 -> 7 -> 15 -> 31 -> 63 -> 127
        assert repeat_result == 127

    def test_multiple_extend_calls_are_safe(self) -> None:
        """Test that calling extend_flow_with_trampoline multiple times is safe."""
        # Call extend multiple times
        extend_flow_with_trampoline()
        extend_flow_with_trampoline()
        extend_flow_with_trampoline()

        # Should still work correctly
        flow: Flow[int, int] = Flow.from_sync_fn(lambda x: x * 3)
        result = flow.run_single(4)  # type: ignore[attr-defined]
        assert result == 12

    def test_trampoline_methods_preserve_flow_type_hints(self) -> None:
        """Test that trampoline methods preserve proper type hints."""
        extend_flow_with_trampoline()

        # Create a typed flow
        int_to_str_flow: Flow[int, str] = Flow.from_sync_fn(lambda x: str(x * 2))

        # Use trampoline methods - these should maintain type safety
        result: str = int_to_str_flow.run_single(5)  # type: ignore[attr-defined]
        assert result == "10"

        single_stream: Flow[Any, str] = int_to_str_flow.as_single_stream(7)  # type: ignore[attr-defined]
        stream_result: str = single_stream.run_single("ignored")  # type: ignore[attr-defined]
        assert stream_result == "14"

    def test_error_propagation_through_trampoline_methods(self) -> None:
        """Test that errors are properly propagated through trampoline methods."""
        extend_flow_with_trampoline()

        # Create a flow that raises an error
        def error_flow_fn(x: int) -> int:
            if x == 5:
                raise ValueError("Test error")
            return x * 2

        error_flow: Flow[int, int] = Flow.from_sync_fn(error_flow_fn)

        # Test error propagation through run_single
        with pytest.raises(ValueError, match="Test error"):
            error_flow.run_single(5)  # type: ignore[attr-defined]

        # Test normal operation still works
        result = error_flow.run_single(3)  # type: ignore[attr-defined]
        assert result == 6
