"""Comprehensive tests for the Flow class and stream processing functionality."""

import asyncio
import warnings

import pytest

from goldentooth_agent.flow_engine import Flow

# Filter runtime warnings about unclosed async generators during exception handling
warnings.filterwarnings(
    "ignore",
    message=".*coroutine method 'aclose'.*was never awaited",
    category=RuntimeWarning,
)


# Test fixtures - async stream generators
async def sync_stream_range(n: int):
    """Generate numbers from 0 to n-1 in a stream."""
    for i in range(n):
        yield i


async def async_stream_range(n: int):
    """Asynchronously generate numbers from 0 to n-1 with delays."""
    for i in range(n):
        await asyncio.sleep(0.01)
        yield i


async def async_fibonacci_stream(n: int):
    """Generate first n fibonacci numbers in a stream."""
    a, b = 0, 1
    for _ in range(n):
        yield a
        await asyncio.sleep(0.001)  # Small delay to make it async
        a, b = b, a + b


async def async_exception_stream(n: int):
    """Stream that raises an exception after yielding some values."""
    for i in range(n):
        if i == 2:
            raise ValueError(f"Exception at item {i}")
        yield i


async def async_empty_stream(_: int):
    """Stream that yields nothing."""
    return
    yield  # unreachable


async def async_string_stream(n: int):
    """Generate string values in a stream."""
    for i in range(n):
        yield f"item_{i}"


# Test fixtures - transformation functions
def sync_increment(x: int) -> int:
    """Increment a number."""
    return x + 1


def sync_double(x: int) -> int:
    """Double a number."""
    return x * 2


def sync_to_string(x: int) -> str:
    """Convert number to string."""
    return f"value_{x}"


async def async_increment(x: int) -> int:
    """Asynchronously increment a number."""
    await asyncio.sleep(0.001)
    return x + 1


async def async_double(x: int) -> int:
    """Asynchronously double a number."""
    await asyncio.sleep(0.001)
    return x * 2


# Test fixtures - predicate functions
def is_even(x: int) -> bool:
    """Check if number is even."""
    return x % 2 == 0


def is_positive(x: int) -> bool:
    """Check if number is positive."""
    return x > 0


def less_than_five(x: int) -> bool:
    """Check if number is less than 5."""
    return x < 5


# Test fixtures - side effect functions
side_effects = []


async def async_side_effect(x):
    """Async side effect function."""
    await asyncio.sleep(0.001)
    side_effects.append(f"side_effect: {x}")


# Test fixtures - flat map functions
async def create_range_stream(n: int):
    """Create an async iterator that yields range(n)."""
    for i in range(n):
        yield i


async def create_repeat_stream(x: int):
    """Create a stream that repeats a value twice."""
    for _ in range(2):
        yield x


async def create_conditional_stream(x: int):
    """Create a stream that only yields for even numbers."""
    if x % 2 == 0:
        yield x * 10


class TestFlowCreation:
    """Test cases for Flow creation and basic functionality."""

    def setup_method(self):
        """Clear side effects before each test."""
        side_effects.clear()

    @pytest.mark.asyncio
    async def test_flow_creation(self):
        """Test creating a Flow with a stream processing function."""

        async def identity_processor(stream):
            async for item in stream:
                yield item

        flow = Flow(identity_processor, name="identity")
        assert flow.name == "identity"
        assert flow.metadata == {}

        # Test that it's callable and returns an async iterator
        input_stream = sync_stream_range(3)
        output_stream = flow(input_stream)
        values = [item async for item in output_stream]
        assert values == [0, 1, 2]

    @pytest.mark.asyncio
    async def test_flow_creation_with_metadata(self):
        """Test creating a Flow with metadata."""

        async def identity_processor(stream):
            async for item in stream:
                yield item

        metadata = {"version": "1.0", "description": "test flow"}
        flow = Flow(identity_processor, name="identity", metadata=metadata)
        assert flow.metadata == metadata

    @pytest.mark.asyncio
    async def test_flow_name_fallback(self):
        """Test that Flow names fall back appropriately."""

        async def identity_processor(stream):
            async for item in stream:
                yield item

        # With explicit name
        flow1 = Flow(identity_processor, name="explicit")
        assert flow1.name == "explicit"

        # With default name
        flow2 = Flow(identity_processor)
        assert flow2.name == "<anonymous>"

    @pytest.mark.asyncio
    async def test_flow_call(self):
        """Test calling a Flow."""

        async def double_processor(stream):
            async for item in stream:
                yield item * 2

        flow = Flow(double_processor, name="double")

        # Should return an async iterator
        input_stream = sync_stream_range(3)
        output_stream = flow(input_stream)
        assert hasattr(output_stream, "__aiter__")

        # Collect values
        values = []
        async for item in output_stream:
            values.append(item)
        assert values == [0, 2, 4]

    @pytest.mark.asyncio
    async def test_flow_with_async_stream(self):
        """Test Flow with async input stream."""

        async def increment_processor(stream):
            async for item in stream:
                yield item + 1

        flow = Flow(increment_processor, name="increment")

        input_stream = async_stream_range(3)
        output_stream = flow(input_stream)
        values = [item async for item in output_stream]
        assert values == [1, 2, 3]  # 0+1, 1+1, 2+1

    @pytest.mark.asyncio
    async def test_flow_empty_stream(self):
        """Test Flow with empty input stream."""

        async def identity_processor(stream):
            async for item in stream:
                yield item

        flow = Flow(identity_processor, name="identity")

        input_stream = async_empty_stream(5)
        output_stream = flow(input_stream)
        values = [item async for item in output_stream]
        assert values == []

    @pytest.mark.asyncio
    async def test_flow_exception_handling(self):
        """Test that exceptions from streams are properly propagated."""

        async def identity_processor(stream):
            async for item in stream:
                yield item

        flow = Flow(identity_processor, name="identity")

        input_stream = async_exception_stream(5)
        output_stream = flow(input_stream)

        values = []
        with pytest.raises(ValueError, match="Exception at item 2"):
            async for item in output_stream:
                values.append(item)

        # Should have yielded values before the exception
        assert values == [0, 1]


class TestFlowMap:
    """Test cases for Flow.map method."""

    @pytest.mark.asyncio
    async def test_map_basic(self):
        """Test basic map functionality."""

        async def identity_processor(stream):
            async for item in stream:
                yield item

        flow = Flow(identity_processor, name="identity")
        mapped_flow = flow.map(sync_increment)

        assert mapped_flow.name == "identity.map(sync_increment)"

        input_stream = sync_stream_range(3)
        output_stream = mapped_flow(input_stream)
        values = [item async for item in output_stream]
        assert values == [1, 2, 3]  # 0+1, 1+1, 2+1

    @pytest.mark.asyncio
    async def test_map_with_lambda(self):
        """Test map with lambda function."""

        async def identity_processor(stream):
            async for item in stream:
                yield item

        flow = Flow(identity_processor, name="identity")
        mapped_flow = flow.map(lambda x: x * 10)

        assert mapped_flow.name == "identity.map(<lambda>)"

        input_stream = sync_stream_range(3)
        output_stream = mapped_flow(input_stream)
        values = [item async for item in output_stream]
        assert values == [0, 10, 20]

    @pytest.mark.asyncio
    async def test_map_type_transformation(self):
        """Test map that transforms types."""

        async def identity_processor(stream):
            async for item in stream:
                yield item

        flow = Flow(identity_processor, name="identity")
        mapped_flow = flow.map(sync_to_string)

        input_stream = sync_stream_range(3)
        output_stream = mapped_flow(input_stream)
        values = [item async for item in output_stream]
        assert values == ["value_0", "value_1", "value_2"]

    @pytest.mark.asyncio
    async def test_map_chaining(self):
        """Test chaining multiple map operations."""

        async def identity_processor(stream):
            async for item in stream:
                yield item

        flow = Flow(identity_processor, name="identity")
        chained_flow = flow.map(sync_increment).map(sync_double)

        assert chained_flow.name == "identity.map(sync_increment).map(sync_double)"

        input_stream = sync_stream_range(3)
        output_stream = chained_flow(input_stream)
        values = [item async for item in output_stream]
        assert values == [2, 4, 6]  # (0+1)*2, (1+1)*2, (2+1)*2

    @pytest.mark.asyncio
    async def test_map_empty_stream(self):
        """Test map on empty stream."""

        async def identity_processor(stream):
            async for item in stream:
                yield item

        flow = Flow(identity_processor, name="identity")
        mapped_flow = flow.map(sync_increment)

        input_stream = async_empty_stream(3)
        output_stream = mapped_flow(input_stream)
        values = [item async for item in output_stream]
        assert values == []


class TestFlowFilter:
    """Test cases for Flow.filter method."""

    @pytest.mark.asyncio
    async def test_filter_basic(self):
        """Test basic filter functionality."""

        async def identity_processor(stream):
            async for item in stream:
                yield item

        flow = Flow(identity_processor, name="identity")
        filtered_flow = flow.filter(is_even)

        assert filtered_flow.name == "identity.filter(is_even)"

        input_stream = sync_stream_range(6)
        output_stream = filtered_flow(input_stream)
        values = [item async for item in output_stream]
        assert values == [0, 2, 4]  # Even numbers from 0-5

    @pytest.mark.asyncio
    async def test_filter_with_lambda(self):
        """Test filter with lambda predicate."""

        async def identity_processor(stream):
            async for item in stream:
                yield item

        flow = Flow(identity_processor, name="identity")
        filtered_flow = flow.filter(lambda x: x > 2)

        assert filtered_flow.name == "identity.filter(<lambda>)"

        input_stream = sync_stream_range(6)
        output_stream = filtered_flow(input_stream)
        values = [item async for item in output_stream]
        assert values == [3, 4, 5]  # Numbers > 2

    @pytest.mark.asyncio
    async def test_filter_no_matches(self):
        """Test filter where no items match."""

        async def identity_processor(stream):
            async for item in stream:
                yield item

        flow = Flow(identity_processor, name="identity")
        filtered_flow = flow.filter(lambda x: x > 100)

        input_stream = sync_stream_range(5)
        output_stream = filtered_flow(input_stream)
        values = [item async for item in output_stream]
        assert values == []

    @pytest.mark.asyncio
    async def test_filter_all_match(self):
        """Test filter where all items match."""

        async def identity_processor(stream):
            async for item in stream:
                yield item

        flow = Flow(identity_processor, name="identity")
        filtered_flow = flow.filter(lambda x: x >= 0)

        input_stream = sync_stream_range(3)
        output_stream = filtered_flow(input_stream)
        values = [item async for item in output_stream]
        assert values == [0, 1, 2]

    @pytest.mark.asyncio
    async def test_filter_chaining(self):
        """Test chaining filter operations."""

        async def identity_processor(stream):
            async for item in stream:
                yield item

        flow = Flow(identity_processor, name="identity")
        chained_flow = flow.filter(is_even).filter(less_than_five)

        input_stream = sync_stream_range(10)
        output_stream = chained_flow(input_stream)
        values = [item async for item in output_stream]
        assert values == [0, 2, 4]  # Even numbers less than 5


class TestFlowFlatMap:
    """Test cases for Flow.flat_map method."""

    @pytest.mark.asyncio
    async def test_flat_map_basic(self):
        """Test basic flat_map functionality."""

        async def identity_processor(stream):
            async for item in stream:
                yield item

        flow = Flow(identity_processor, name="identity")
        flat_mapped = flow.flat_map(create_range_stream)

        assert flat_mapped.name == "identity.flat_map(create_range_stream)"

        input_stream = sync_stream_range(4)
        output_stream = flat_mapped(input_stream)
        values = [item async for item in output_stream]
        # 0: no items, 1: [0], 2: [0,1], 3: [0,1,2]
        assert values == [0, 0, 1, 0, 1, 2]

    @pytest.mark.asyncio
    async def test_flat_map_with_named_function(self):
        """Test flat_map with named function."""

        async def identity_processor(stream):
            async for item in stream:
                yield item

        flow = Flow(identity_processor, name="identity")
        flat_mapped = flow.flat_map(create_repeat_stream)

        assert flat_mapped.name == "identity.flat_map(create_repeat_stream)"

        input_stream = sync_stream_range(3)
        output_stream = flat_mapped(input_stream)
        values = [item async for item in output_stream]
        assert values == [0, 0, 1, 1, 2, 2]

    @pytest.mark.asyncio
    async def test_flat_map_empty_results(self):
        """Test flat_map where some results are empty."""

        async def identity_processor(stream):
            async for item in stream:
                yield item

        flow = Flow(identity_processor, name="identity")
        flat_mapped = flow.flat_map(create_conditional_stream)

        input_stream = sync_stream_range(4)
        output_stream = flat_mapped(input_stream)
        values = [item async for item in output_stream]
        assert values == [0, 20]  # Only even numbers * 10


class TestFlowComposition:
    """Test cases for Flow composition and piping."""

    @pytest.mark.asyncio
    async def test_rshift_operator(self):
        """Test >> operator for Flow composition."""

        async def increment_processor(stream):
            async for item in stream:
                yield item + 1

        async def double_processor(stream):
            async for item in stream:
                yield item * 2

        first_flow = Flow(increment_processor, name="increment")
        second_flow = Flow(double_processor, name="double")

        composed = first_flow >> second_flow
        assert composed.name == "increment >> double"

        input_stream = sync_stream_range(3)
        output_stream = composed(input_stream)
        values = [item async for item in output_stream]
        assert values == [2, 4, 6]  # (0+1)*2, (1+1)*2, (2+1)*2

    @pytest.mark.asyncio
    async def test_complex_composition(self):
        """Test complex chain of composed flows."""

        async def increment_processor(stream):
            async for item in stream:
                yield item + 1

        async def filter_even_processor(stream):
            async for item in stream:
                if item % 2 == 0:
                    yield item

        async def double_processor(stream):
            async for item in stream:
                yield item * 2

        increment_flow = Flow(increment_processor, name="increment")
        filter_flow = Flow(filter_even_processor, name="filter_even")
        double_flow = Flow(double_processor, name="double")

        # Build a complex pipeline
        complex_flow = increment_flow >> filter_flow >> double_flow

        input_stream = sync_stream_range(6)
        output_stream = complex_flow(input_stream)
        values = [item async for item in output_stream]
        # Original: [0,1,2,3,4,5]
        # After +1: [1,2,3,4,5,6]
        # After filter even: [2,4,6]
        # After *2: [4,8,12]
        assert values == [4, 8, 12]


class TestFlowCollectionMethods:
    """Test cases for Flow collection methods (for_each, to_list)."""

    def setup_method(self):
        """Clear side effects before each test."""
        side_effects.clear()

    @pytest.mark.asyncio
    async def test_for_each_basic(self):
        """Test basic for_each functionality."""

        async def identity_processor(stream):
            async for item in stream:
                yield item

        flow = Flow(identity_processor, name="identity")
        for_each_fn = flow.for_each(async_side_effect)

        input_stream = sync_stream_range(3)
        await for_each_fn(input_stream)

        assert side_effects == ["side_effect: 0", "side_effect: 1", "side_effect: 2"]

    @pytest.mark.asyncio
    async def test_for_each_with_transformation(self):
        """Test for_each with flow transformation."""

        async def double_processor(stream):
            async for item in stream:
                yield item * 2

        flow = Flow(double_processor, name="double")
        for_each_fn = flow.for_each(async_side_effect)

        input_stream = sync_stream_range(3)
        await for_each_fn(input_stream)

        assert side_effects == ["side_effect: 0", "side_effect: 2", "side_effect: 4"]

    @pytest.mark.asyncio
    async def test_for_each_empty_stream(self):
        """Test for_each with empty stream."""

        async def identity_processor(stream):
            async for item in stream:
                yield item

        flow = Flow(identity_processor, name="identity")
        for_each_fn = flow.for_each(async_side_effect)

        input_stream = async_empty_stream(5)
        await for_each_fn(input_stream)

        assert side_effects == []

    @pytest.mark.asyncio
    async def test_to_list_basic(self):
        """Test basic to_list functionality."""

        async def identity_processor(stream):
            async for item in stream:
                yield item

        flow = Flow(identity_processor, name="identity")
        to_list_fn = flow.to_list()

        input_stream = sync_stream_range(3)
        result = await to_list_fn(input_stream)
        assert result == [0, 1, 2]

    @pytest.mark.asyncio
    async def test_to_list_with_transformation(self):
        """Test to_list with flow transformation."""

        async def double_processor(stream):
            async for item in stream:
                yield item * 2

        flow = Flow(double_processor, name="double")
        to_list_fn = flow.to_list()

        input_stream = sync_stream_range(3)
        result = await to_list_fn(input_stream)
        assert result == [0, 2, 4]

    @pytest.mark.asyncio
    async def test_to_list_empty_stream(self):
        """Test to_list with empty stream."""

        async def identity_processor(stream):
            async for item in stream:
                yield item

        flow = Flow(identity_processor, name="identity")
        to_list_fn = flow.to_list()

        input_stream = async_empty_stream(5)
        result = await to_list_fn(input_stream)
        assert result == []

    @pytest.mark.asyncio
    async def test_to_list_with_filtering(self):
        """Test to_list with filtering."""

        async def filter_even_processor(stream):
            async for item in stream:
                if item % 2 == 0:
                    yield item

        flow = Flow(filter_even_processor, name="filter_even")
        to_list_fn = flow.to_list()

        input_stream = sync_stream_range(6)
        result = await to_list_fn(input_stream)
        assert result == [0, 2, 4]


class TestFlowFactoryMethods:
    """Test cases for Flow static factory methods."""

    @pytest.mark.asyncio
    async def test_from_value_fn_basic(self):
        """Test Flow.from_value_fn with async function."""
        flow = Flow.from_value_fn(async_increment)

        assert flow.name == "async_increment"

        input_stream = sync_stream_range(3)
        output_stream = flow(input_stream)
        values = [item async for item in output_stream]
        assert values == [1, 2, 3]  # 0+1, 1+1, 2+1

    @pytest.mark.asyncio
    async def test_from_sync_fn_basic(self):
        """Test Flow.from_sync_fn with synchronous function."""
        flow = Flow.from_sync_fn(sync_double)

        assert flow.name == "sync_double"

        input_stream = sync_stream_range(3)
        output_stream = flow(input_stream)
        values = [item async for item in output_stream]
        assert values == [0, 2, 4]  # 0*2, 1*2, 2*2

    @pytest.mark.asyncio
    async def test_from_event_fn_basic(self):
        """Test Flow.from_event_fn with async iterator function."""

        async def repeat_twice(x: int):
            yield x
            yield x

        flow = Flow.from_event_fn(repeat_twice)

        assert flow.name == "repeat_twice"

        input_stream = sync_stream_range(3)
        output_stream = flow(input_stream)
        values = [item async for item in output_stream]
        assert values == [0, 0, 1, 1, 2, 2]

    @pytest.mark.asyncio
    async def test_from_iterable_basic(self):
        """Test Flow.from_iterable with list."""
        flow = Flow.from_iterable([1, 2, 3, 4])

        assert flow.name == "from_iterable"

        # Need to provide some input stream (ignored)
        input_stream = async_empty_stream(0)
        output_stream = flow(input_stream)
        values = [item async for item in output_stream]
        assert values == [1, 2, 3, 4]

    @pytest.mark.asyncio
    async def test_from_iterable_empty(self):
        """Test Flow.from_iterable with empty list."""
        flow = Flow.from_iterable([])

        input_stream = async_empty_stream(0)
        output_stream = flow(input_stream)
        values = [item async for item in output_stream]
        assert values == []

    @pytest.mark.asyncio
    async def test_from_emitter_basic(self):
        """Test Flow.from_emitter with callback registration."""
        emitted_values = []

        def register_callback(callback):
            """Simulate an emitter that calls the callback with values."""
            # This would normally be done asynchronously by some event source
            emitted_values.append(callback)
            # Immediately emit some test values
            callback("test1")
            callback("test2")

        flow = Flow.from_emitter(register_callback)

        assert flow.name == "from_emitter"

        # The callback is only registered when the flow is actually called
        input_stream = async_empty_stream(0)
        output_stream = flow(input_stream)

        # Get first couple of values to test it works
        values = []
        async for item in output_stream:
            values.append(item)
            if len(values) >= 2:
                break  # Stop after getting test values

        assert values == ["test1", "test2"]
        assert len(emitted_values) == 1  # Callback was registered


class TestFlowLabel:
    """Test cases for Flow.label method."""

    @pytest.mark.asyncio
    async def test_label_basic(self, capsys):
        """Test basic label functionality."""

        async def identity_processor(stream):
            async for item in stream:
                yield item

        flow = Flow(identity_processor, name="identity")
        labeled_flow = flow.label("test_label")

        assert labeled_flow.name == "identity.label(test_label)"

        input_stream = sync_stream_range(2)
        output_stream = labeled_flow(input_stream)
        values = [item async for item in output_stream]

        assert values == [0, 1]

        # Check that debug output was printed
        captured = capsys.readouterr()
        assert "[Flow:test_label] starting" in captured.out
        assert "[Flow:test_label] yield: 0" in captured.out
        assert "[Flow:test_label] yield: 1" in captured.out


class TestFlowEdgeCases:
    """Test edge cases and error conditions for Flow."""

    @pytest.mark.asyncio
    async def test_flow_with_none_values(self):
        """Test Flow that processes None values."""

        async def none_processor(stream):
            async for item in stream:
                if item % 2 == 0:
                    yield None
                else:
                    yield item

        async def mixed_stream(n: int):
            for i in range(n):
                yield i

        flow = Flow(none_processor, name="none_processor")
        input_stream = mixed_stream(4)
        output_stream = flow(input_stream)
        values = [item async for item in output_stream]
        assert values == [None, 1, None, 3]

    @pytest.mark.asyncio
    async def test_flow_with_complex_objects(self):
        """Test Flow with complex object types."""

        async def dict_processor(stream):
            async for item in stream:
                yield {"id": item, "value": item * 2}

        flow = Flow(dict_processor, name="dict_processor")
        input_stream = sync_stream_range(3)
        output_stream = flow(input_stream)
        values = [item async for item in output_stream]
        expected = [{"id": 0, "value": 0}, {"id": 1, "value": 2}, {"id": 2, "value": 4}]
        assert values == expected

    @pytest.mark.asyncio
    @pytest.mark.filterwarnings("ignore:.*coroutine method 'aclose'.*:RuntimeWarning")
    async def test_flow_exception_in_transformation(self):
        """Test Flow with exception in transformation function."""

        def failing_transform(x):
            if x == 2:
                raise ValueError("Transform failed")
            return x * 2

        async def identity_processor(stream):
            async for item in stream:
                yield item

        flow = Flow(identity_processor, name="identity")
        mapped_flow = flow.map(failing_transform)

        input_stream = sync_stream_range(4)
        output_stream = mapped_flow(input_stream)

        values = []
        with pytest.raises(ValueError, match="Transform failed"):
            async for item in output_stream:
                values.append(item)

        # Should have processed values before the exception
        assert values == [0, 2]  # 0*2, 1*2, then exception at 2

    @pytest.mark.asyncio
    @pytest.mark.filterwarnings("ignore:.*coroutine method 'aclose'.*:RuntimeWarning")
    async def test_flow_exception_in_filter_predicate(self):
        """Test Flow with exception in filter predicate."""

        def failing_predicate(x):
            if x == 2:
                raise ValueError("Predicate failed")
            return x % 2 == 0

        async def identity_processor(stream):
            async for item in stream:
                yield item

        flow = Flow(identity_processor, name="identity")
        filtered_flow = flow.filter(failing_predicate)

        input_stream = sync_stream_range(4)
        output_stream = filtered_flow(input_stream)

        values = []
        with pytest.raises(ValueError, match="Predicate failed"):
            async for item in output_stream:
                values.append(item)

        # Should have processed values before the exception
        assert values == [0]  # Only even values that passed before exception


class TestFlowIntegration:
    """Integration tests combining multiple Flow operations."""

    @pytest.mark.asyncio
    async def test_complex_flow_pipeline(self):
        """Test complex pipeline with multiple operations."""

        async def identity_processor(stream):
            async for item in stream:
                yield item

        base_flow = Flow(identity_processor, name="base")

        # Build a complex pipeline
        complex_flow = (
            base_flow.map(sync_increment)  # Add 1 to each
            .filter(is_even)  # Keep only even results
            .map(lambda x: x * 10)  # Multiply by 10
        )

        input_stream = sync_stream_range(6)
        output_stream = complex_flow(input_stream)
        values = [item async for item in output_stream]
        # Original: [0,1,2,3,4,5]
        # After +1: [1,2,3,4,5,6]
        # After filter even: [2,4,6]
        # After *10: [20,40,60]
        assert values == [20, 40, 60]

    @pytest.mark.asyncio
    async def test_flow_with_different_stream_types(self):
        """Test Flow with different types of input streams."""

        async def type_processor(stream):
            async for item in stream:
                yield f"processed_{item}"

        flow = Flow(type_processor, name="type_processor")

        # Test with string stream
        input_stream = async_string_stream(3)
        output_stream = flow(input_stream)
        values = [item async for item in output_stream]
        assert values == ["processed_item_0", "processed_item_1", "processed_item_2"]

    @pytest.mark.asyncio
    async def test_flow_factory_method_composition(self):
        """Test composition of flows created from factory methods."""
        sync_flow = Flow.from_sync_fn(sync_increment)
        async_flow = Flow.from_value_fn(async_double)

        composed_flow = sync_flow >> async_flow

        input_stream = sync_stream_range(3)
        output_stream = composed_flow(input_stream)
        values = [item async for item in output_stream]
        assert values == [2, 4, 6]  # (0+1)*2, (1+1)*2, (2+1)*2

    @pytest.mark.asyncio
    async def test_flow_with_to_list_and_map_chaining(self):
        """Test chaining map operations with to_list collection."""

        async def identity_processor(stream):
            async for item in stream:
                yield item

        base_flow = Flow(identity_processor, name="base")
        transformed_flow = base_flow.map(sync_double).map(sync_to_string)
        to_list_fn = transformed_flow.to_list()

        input_stream = sync_stream_range(3)
        result = await to_list_fn(input_stream)
        assert result == ["value_0", "value_2", "value_4"]  # Double then stringify

    @pytest.mark.asyncio
    async def test_flow_flat_map_with_composition(self):
        """Test flat_map combined with other operations."""

        async def identity_processor(stream):
            async for item in stream:
                yield item

        base_flow = Flow(identity_processor, name="base")
        complex_flow = (
            base_flow.flat_map(create_repeat_stream)  # Repeat each value twice
            .filter(is_even)  # Keep only even values
            .map(lambda x: x + 100)  # Add 100
        )

        input_stream = sync_stream_range(4)
        output_stream = complex_flow(input_stream)
        values = [item async for item in output_stream]
        # Original: [0,1,2,3]
        # After flat_map: [0,0,1,1,2,2,3,3]
        # After filter even: [0,0,2,2]
        # After +100: [100,100,102,102]
        assert values == [100, 100, 102, 102]
