"""Comprehensive tests for the StreamThunk class and stream-related functionality."""

import asyncio
import pytest
from unittest.mock import AsyncMock, Mock
from goldentooth_agent.core.stream_thunk import StreamThunk
from goldentooth_agent.core.thunk import Thunk


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


class TestStreamThunkCreation:
    """Test cases for StreamThunk creation and basic functionality."""

    def setup_method(self):
        """Clear side effects before each test."""
        side_effects.clear()

    @pytest.mark.asyncio
    async def test_stream_thunk_creation(self):
        """Test creating a StreamThunk with a stream processing function."""

        async def identity_processor(stream):
            async for item in stream:
                yield item

        stream_thunk = StreamThunk(identity_processor, name="identity")
        assert stream_thunk.name == "identity"
        assert stream_thunk.metadata == {}

        # Test that it's callable and returns an async iterator
        input_stream = sync_stream_range(3)
        output_stream = stream_thunk(input_stream)
        values = [item async for item in output_stream]
        assert values == [0, 1, 2]

    def test_stream_thunk_creation_non_callable_raises_error(self):
        """Test that creating a StreamThunk with non-callable raises TypeError."""
        with pytest.raises(TypeError, match="StreamThunk requires a callable"):
            StreamThunk("not_a_function", name="test")

    def test_stream_thunk_creation_with_metadata(self):
        """Test creating a StreamThunk with metadata."""

        async def identity_processor(stream):
            async for item in stream:
                yield item

        metadata = {"version": "1.0", "description": "test thunk"}
        stream_thunk = StreamThunk(
            identity_processor, name="identity", metadata=metadata
        )
        assert stream_thunk.metadata == metadata

    def test_stream_thunk_name_fallback(self):
        """Test that StreamThunk names fall back appropriately."""

        async def identity_processor(stream):
            async for item in stream:
                yield item

        # With explicit name
        stream_thunk1 = StreamThunk(identity_processor, name="explicit")
        assert stream_thunk1.name == "explicit"

        # With empty name, should use function name
        stream_thunk2 = StreamThunk(identity_processor, name="")
        assert stream_thunk2.name == "identity_processor"

    @pytest.mark.asyncio
    async def test_stream_thunk_call(self):
        """Test calling a StreamThunk."""

        async def double_processor(stream):
            async for item in stream:
                yield item * 2

        stream_thunk = StreamThunk(double_processor, name="double")

        # Should return an async iterator
        input_stream = sync_stream_range(3)
        output_stream = stream_thunk(input_stream)
        assert hasattr(output_stream, "__aiter__")

        # Collect values
        values = []
        async for item in output_stream:
            values.append(item)
        assert values == [0, 2, 4]

    @pytest.mark.asyncio
    async def test_stream_thunk_with_async_stream(self):
        """Test StreamThunk with async input stream."""

        async def increment_processor(stream):
            async for item in stream:
                yield item + 1

        stream_thunk = StreamThunk(increment_processor, name="increment")

        input_stream = async_stream_range(3)
        output_stream = stream_thunk(input_stream)
        values = [item async for item in output_stream]
        assert values == [1, 2, 3]  # 0+1, 1+1, 2+1

    @pytest.mark.asyncio
    async def test_stream_thunk_empty_stream(self):
        """Test StreamThunk with empty input stream."""

        async def identity_processor(stream):
            async for item in stream:
                yield item

        stream_thunk = StreamThunk(identity_processor, name="identity")

        input_stream = async_empty_stream(5)
        output_stream = stream_thunk(input_stream)
        values = [item async for item in output_stream]
        assert values == []

    @pytest.mark.asyncio
    async def test_stream_thunk_exception_handling(self):
        """Test that exceptions from streams are properly propagated."""

        async def identity_processor(stream):
            async for item in stream:
                yield item

        stream_thunk = StreamThunk(identity_processor, name="identity")

        input_stream = async_exception_stream(5)
        output_stream = stream_thunk(input_stream)

        values = []
        with pytest.raises(ValueError, match="Exception at item 2"):
            async for item in output_stream:
                values.append(item)

        # Should have yielded values before the exception
        assert values == [0, 1]


class TestStreamThunkMap:
    """Test cases for StreamThunk.map method."""

    @pytest.mark.asyncio
    async def test_map_basic(self):
        """Test basic map functionality."""

        async def identity_processor(stream):
            async for item in stream:
                yield item

        stream_thunk = StreamThunk(identity_processor, name="identity")
        mapped_thunk = stream_thunk.map(sync_increment)

        assert mapped_thunk.name == "identity.map(sync_increment)"

        input_stream = sync_stream_range(3)
        output_stream = mapped_thunk(input_stream)
        values = [item async for item in output_stream]
        assert values == [1, 2, 3]  # 0+1, 1+1, 2+1

    @pytest.mark.asyncio
    async def test_map_with_lambda(self):
        """Test map with lambda function."""

        async def identity_processor(stream):
            async for item in stream:
                yield item

        stream_thunk = StreamThunk(identity_processor, name="identity")
        mapped_thunk = stream_thunk.map(lambda x: x * 10)

        assert mapped_thunk.name == "identity.map(<lambda>)"

        input_stream = sync_stream_range(3)
        output_stream = mapped_thunk(input_stream)
        values = [item async for item in output_stream]
        assert values == [0, 10, 20]

    @pytest.mark.asyncio
    async def test_map_type_transformation(self):
        """Test map that transforms types."""

        async def identity_processor(stream):
            async for item in stream:
                yield item

        stream_thunk = StreamThunk(identity_processor, name="identity")
        mapped_thunk = stream_thunk.map(sync_to_string)

        input_stream = sync_stream_range(3)
        output_stream = mapped_thunk(input_stream)
        values = [item async for item in output_stream]
        assert values == ["value_0", "value_1", "value_2"]

    @pytest.mark.asyncio
    async def test_map_chaining(self):
        """Test chaining multiple map operations."""

        async def identity_processor(stream):
            async for item in stream:
                yield item

        stream_thunk = StreamThunk(identity_processor, name="identity")
        chained_thunk = stream_thunk.map(sync_increment).map(sync_double)

        assert chained_thunk.name == "identity.map(sync_increment).map(sync_double)"

        input_stream = sync_stream_range(3)
        output_stream = chained_thunk(input_stream)
        values = [item async for item in output_stream]
        assert values == [2, 4, 6]  # (0+1)*2, (1+1)*2, (2+1)*2

    @pytest.mark.asyncio
    async def test_map_empty_stream(self):
        """Test map on empty stream."""

        async def identity_processor(stream):
            async for item in stream:
                yield item

        stream_thunk = StreamThunk(identity_processor, name="identity")
        mapped_thunk = stream_thunk.map(sync_increment)

        input_stream = async_empty_stream(3)
        output_stream = mapped_thunk(input_stream)
        values = [item async for item in output_stream]
        assert values == []


class TestStreamThunkFilter:
    """Test cases for StreamThunk.filter method."""

    @pytest.mark.asyncio
    async def test_filter_basic(self):
        """Test basic filter functionality."""

        async def identity_processor(stream):
            async for item in stream:
                yield item

        stream_thunk = StreamThunk(identity_processor, name="identity")
        filtered_thunk = stream_thunk.filter(is_even)

        assert filtered_thunk.name == "identity.filter(is_even)"

        input_stream = sync_stream_range(6)
        output_stream = filtered_thunk(input_stream)
        values = [item async for item in output_stream]
        assert values == [0, 2, 4]  # Even numbers from 0-5

    @pytest.mark.asyncio
    async def test_filter_with_lambda(self):
        """Test filter with lambda predicate."""

        async def identity_processor(stream):
            async for item in stream:
                yield item

        stream_thunk = StreamThunk(identity_processor, name="identity")
        filtered_thunk = stream_thunk.filter(lambda x: x > 2)

        assert filtered_thunk.name == "identity.filter(<lambda>)"

        input_stream = sync_stream_range(6)
        output_stream = filtered_thunk(input_stream)
        values = [item async for item in output_stream]
        assert values == [3, 4, 5]  # Numbers > 2

    @pytest.mark.asyncio
    async def test_filter_no_matches(self):
        """Test filter where no items match."""

        async def identity_processor(stream):
            async for item in stream:
                yield item

        stream_thunk = StreamThunk(identity_processor, name="identity")
        filtered_thunk = stream_thunk.filter(lambda x: x > 100)

        input_stream = sync_stream_range(5)
        output_stream = filtered_thunk(input_stream)
        values = [item async for item in output_stream]
        assert values == []

    @pytest.mark.asyncio
    async def test_filter_all_match(self):
        """Test filter where all items match."""

        async def identity_processor(stream):
            async for item in stream:
                yield item

        stream_thunk = StreamThunk(identity_processor, name="identity")
        filtered_thunk = stream_thunk.filter(lambda x: x >= 0)

        input_stream = sync_stream_range(3)
        output_stream = filtered_thunk(input_stream)
        values = [item async for item in output_stream]
        assert values == [0, 1, 2]

    @pytest.mark.asyncio
    async def test_filter_chaining(self):
        """Test chaining filter operations."""

        async def identity_processor(stream):
            async for item in stream:
                yield item

        stream_thunk = StreamThunk(identity_processor, name="identity")
        chained_thunk = stream_thunk.filter(is_even).filter(less_than_five)

        input_stream = sync_stream_range(10)
        output_stream = chained_thunk(input_stream)
        values = [item async for item in output_stream]
        assert values == [0, 2, 4]  # Even numbers less than 5


class TestStreamThunkFlatMap:
    """Test cases for StreamThunk.flat_map method."""

    @pytest.mark.asyncio
    async def test_flat_map_basic(self):
        """Test basic flat_map functionality."""

        async def identity_processor(stream):
            async for item in stream:
                yield item

        async def create_range_stream(n: int):
            """Create an async iterator that yields range(n)."""
            for i in range(n):
                yield i

        stream_thunk = StreamThunk(identity_processor, name="identity")
        flat_mapped = stream_thunk.flat_map(create_range_stream)

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

        async def create_repeat_stream(x: int):
            """Create a stream that repeats a value twice."""
            for _ in range(2):
                yield x

        stream_thunk = StreamThunk(identity_processor, name="identity")
        flat_mapped = stream_thunk.flat_map(create_repeat_stream)

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

        async def create_conditional_stream(x: int):
            """Create a stream that only yields for even numbers."""
            if x % 2 == 0:
                yield x * 10

        stream_thunk = StreamThunk(identity_processor, name="identity")
        flat_mapped = stream_thunk.flat_map(create_conditional_stream)

        input_stream = sync_stream_range(4)
        output_stream = flat_mapped(input_stream)
        values = [item async for item in output_stream]
        assert values == [0, 20]  # Only even numbers * 10


class TestStreamThunkPipe:
    """Test cases for StreamThunk.pipe method and composition."""

    @pytest.mark.asyncio
    async def test_pipe_basic(self):
        """Test basic pipe functionality."""

        async def increment_processor(stream):
            async for item in stream:
                yield item + 1

        async def double_processor(stream):
            async for item in stream:
                yield item * 2

        first_thunk = StreamThunk(increment_processor, name="increment")
        second_thunk = StreamThunk(double_processor, name="double")

        piped_thunk = first_thunk.pipe(second_thunk)
        assert piped_thunk.name == "increment | double"

        input_stream = sync_stream_range(3)
        output_stream = piped_thunk(input_stream)
        values = [item async for item in output_stream]
        assert values == [2, 4, 6]  # (0+1)*2, (1+1)*2, (2+1)*2

    @pytest.mark.asyncio
    async def test_rshift_operator(self):
        """Test >> operator for StreamThunk composition."""

        async def increment_processor(stream):
            async for item in stream:
                yield item + 1

        async def double_processor(stream):
            async for item in stream:
                yield item * 2

        first_thunk = StreamThunk(increment_processor, name="increment")
        second_thunk = StreamThunk(double_processor, name="double")

        composed = first_thunk >> second_thunk
        assert composed.name == "increment | double"

        input_stream = sync_stream_range(3)
        output_stream = composed(input_stream)
        values = [item async for item in output_stream]
        assert values == [2, 4, 6]  # (0+1)*2, (1+1)*2, (2+1)*2

    @pytest.mark.asyncio
    async def test_complex_pipe_chain(self):
        """Test complex chain of piped stream thunks."""

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

        increment_thunk = StreamThunk(increment_processor, name="increment")
        filter_thunk = StreamThunk(filter_even_processor, name="filter_even")
        double_thunk = StreamThunk(double_processor, name="double")

        # Build a complex pipeline
        complex_thunk = increment_thunk.pipe(filter_thunk).pipe(double_thunk)

        input_stream = sync_stream_range(6)
        output_stream = complex_thunk(input_stream)
        values = [item async for item in output_stream]
        # Original: [0,1,2,3,4,5]
        # After +1: [1,2,3,4,5,6]
        # After filter even: [2,4,6]
        # After *2: [4,8,12]
        assert values == [4, 8, 12]


class TestStreamThunkForEach:
    """Test cases for StreamThunk.for_each method."""

    def setup_method(self):
        """Clear side effects before each test."""
        side_effects.clear()

    @pytest.mark.asyncio
    async def test_for_each_basic(self):
        """Test basic for_each functionality."""

        async def identity_processor(stream):
            async for item in stream:
                yield item

        stream_thunk = StreamThunk(identity_processor, name="identity")
        for_each_fn = stream_thunk.for_each(async_side_effect)

        input_stream = sync_stream_range(3)
        await for_each_fn(input_stream)

        assert side_effects == ["side_effect: 0", "side_effect: 1", "side_effect: 2"]

    @pytest.mark.asyncio
    async def test_for_each_with_transformation(self):
        """Test for_each with stream transformation."""

        async def double_processor(stream):
            async for item in stream:
                yield item * 2

        stream_thunk = StreamThunk(double_processor, name="double")
        for_each_fn = stream_thunk.for_each(async_side_effect)

        input_stream = sync_stream_range(3)
        await for_each_fn(input_stream)

        assert side_effects == ["side_effect: 0", "side_effect: 2", "side_effect: 4"]

    @pytest.mark.asyncio
    async def test_for_each_empty_stream(self):
        """Test for_each with empty stream."""

        async def identity_processor(stream):
            async for item in stream:
                yield item

        stream_thunk = StreamThunk(identity_processor, name="identity")
        for_each_fn = stream_thunk.for_each(async_side_effect)

        input_stream = async_empty_stream(5)
        await for_each_fn(input_stream)

        assert side_effects == []


class TestStreamThunkToList:
    """Test cases for StreamThunk.to_list method."""

    @pytest.mark.asyncio
    async def test_to_list_basic(self):
        """Test basic to_list functionality."""

        async def identity_processor(stream):
            async for item in stream:
                yield item

        stream_thunk = StreamThunk(identity_processor, name="identity")
        to_list_fn = stream_thunk.to_list()

        input_stream = sync_stream_range(3)
        result = await to_list_fn(input_stream)
        assert result == [0, 1, 2]

    @pytest.mark.asyncio
    async def test_to_list_with_transformation(self):
        """Test to_list with stream transformation."""

        async def double_processor(stream):
            async for item in stream:
                yield item * 2

        stream_thunk = StreamThunk(double_processor, name="double")
        to_list_fn = stream_thunk.to_list()

        input_stream = sync_stream_range(3)
        result = await to_list_fn(input_stream)
        assert result == [0, 2, 4]

    @pytest.mark.asyncio
    async def test_to_list_empty_stream(self):
        """Test to_list with empty stream."""

        async def identity_processor(stream):
            async for item in stream:
                yield item

        stream_thunk = StreamThunk(identity_processor, name="identity")
        to_list_fn = stream_thunk.to_list()

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

        stream_thunk = StreamThunk(filter_even_processor, name="filter_even")
        to_list_fn = stream_thunk.to_list()

        input_stream = sync_stream_range(6)
        result = await to_list_fn(input_stream)
        assert result == [0, 2, 4]


class TestStreamThunkCollect:
    """Test cases for StreamThunk.collect method."""

    @pytest.mark.asyncio
    async def test_collect_basic(self):
        """Test collecting StreamThunk values into a list."""

        async def identity_processor(stream):
            async for item in stream:
                yield item

        stream_thunk = StreamThunk(identity_processor, name="identity")
        collected_thunk = stream_thunk.collect()

        assert collected_thunk.name == "identity.collect"
        assert isinstance(collected_thunk, Thunk)  # Should return a regular Thunk

        input_stream = sync_stream_range(3)
        result = await collected_thunk(input_stream)
        assert result == [0, 1, 2]

    @pytest.mark.asyncio
    async def test_collect_empty_stream(self):
        """Test collecting empty stream."""

        async def identity_processor(stream):
            async for item in stream:
                yield item

        stream_thunk = StreamThunk(identity_processor, name="identity")
        collected_thunk = stream_thunk.collect()

        input_stream = async_empty_stream(5)
        result = await collected_thunk(input_stream)
        assert result == []

    @pytest.mark.asyncio
    async def test_collect_with_transformations(self):
        """Test collect after transformations."""

        async def identity_processor(stream):
            async for item in stream:
                yield item

        stream_thunk = StreamThunk(identity_processor, name="identity")
        transformed_thunk = stream_thunk.map(sync_double).filter(lambda x: x < 6)
        collected_thunk = transformed_thunk.collect()

        input_stream = sync_stream_range(5)
        result = await collected_thunk(input_stream)
        # Original: [0,1,2,3,4] -> doubled: [0,2,4,6,8] -> filtered < 6: [0,2,4]
        assert result == [0, 2, 4]


class TestThunkStreamMethod:
    """Test cases for Thunk.stream() method that converts to StreamThunk."""

    @pytest.mark.asyncio
    async def test_thunk_stream_conversion(self):
        """Test converting regular Thunk to StreamThunk."""
        regular_thunk = Thunk(lambda x: x * 2, name="double")
        stream_thunk = regular_thunk.stream()

        assert isinstance(stream_thunk, StreamThunk)
        assert stream_thunk.name == "double"
        assert stream_thunk.metadata == regular_thunk.metadata

        # Should process each item in the stream
        input_stream = sync_stream_range(3)
        output_stream = stream_thunk(input_stream)
        values = [item async for item in output_stream]
        assert values == [0, 2, 4]  # 0*2, 1*2, 2*2

    @pytest.mark.asyncio
    async def test_thunk_stream_with_async_thunk(self):
        """Test converting async Thunk to StreamThunk."""

        async def async_multiply(x):
            await asyncio.sleep(0.01)
            return x * 3

        regular_thunk = Thunk(async_multiply, name="triple")
        stream_thunk = regular_thunk.stream()

        input_stream = sync_stream_range(3)
        output_stream = stream_thunk(input_stream)
        values = [item async for item in output_stream]
        assert values == [0, 3, 6]  # 0*3, 1*3, 2*3

    @pytest.mark.asyncio
    async def test_thunk_stream_preserves_metadata(self):
        """Test that converting to StreamThunk preserves metadata."""
        metadata = {"version": "1.0", "description": "test"}
        regular_thunk = Thunk(lambda x: x + 1, name="increment", metadata=metadata)
        stream_thunk = regular_thunk.stream()

        assert stream_thunk.metadata == metadata

    @pytest.mark.asyncio
    async def test_thunk_stream_with_complex_function(self):
        """Test stream conversion with complex function."""

        def complex_transform(x):
            if x % 2 == 0:
                return x * 10
            else:
                return x + 100

        regular_thunk = Thunk(complex_transform, name="complex")
        stream_thunk = regular_thunk.stream()

        input_stream = sync_stream_range(4)
        output_stream = stream_thunk(input_stream)
        values = [item async for item in output_stream]
        assert values == [0, 101, 20, 103]  # 0*10, 1+100, 2*10, 3+100

    @pytest.mark.asyncio
    async def test_thunk_stream_empty_input(self):
        """Test stream conversion with empty input stream."""
        regular_thunk = Thunk(lambda x: x * 2, name="double")
        stream_thunk = regular_thunk.stream()

        input_stream = async_empty_stream(5)
        output_stream = stream_thunk(input_stream)
        values = [item async for item in output_stream]
        assert values == []


class TestStreamThunkEdgeCases:
    """Test edge cases and error conditions for StreamThunk."""

    @pytest.mark.asyncio
    async def test_stream_thunk_with_none_values(self):
        """Test StreamThunk that processes None values."""

        async def none_processor(stream):
            async for item in stream:
                if item % 2 == 0:
                    yield None
                else:
                    yield item

        async def mixed_stream(n: int):
            for i in range(n):
                yield i

        stream_thunk = StreamThunk(none_processor, name="none_processor")
        input_stream = mixed_stream(4)
        output_stream = stream_thunk(input_stream)
        values = [item async for item in output_stream]
        assert values == [None, 1, None, 3]

    @pytest.mark.asyncio
    async def test_stream_thunk_with_complex_objects(self):
        """Test StreamThunk with complex object types."""

        async def dict_processor(stream):
            async for item in stream:
                yield {"id": item, "value": item * 2}

        stream_thunk = StreamThunk(dict_processor, name="dict_processor")
        input_stream = sync_stream_range(3)
        output_stream = stream_thunk(input_stream)
        values = [item async for item in output_stream]
        expected = [{"id": 0, "value": 0}, {"id": 1, "value": 2}, {"id": 2, "value": 4}]
        assert values == expected

    def test_stream_thunk_repr(self):
        """Test string representation of StreamThunk."""

        async def identity_processor(stream):
            async for item in stream:
                yield item

        metadata = {"test": "value"}
        stream_thunk = StreamThunk(
            identity_processor, name="test_thunk", metadata=metadata
        )

        # StreamThunk doesn't define __repr__ but inherits object's default
        repr_str = repr(stream_thunk)
        assert "StreamThunk" in repr_str


class TestStreamThunkIntegration:
    """Integration tests combining multiple StreamThunk operations."""

    @pytest.mark.asyncio
    async def test_complex_stream_pipeline(self):
        """Test complex pipeline with multiple operations."""

        async def identity_processor(stream):
            async for item in stream:
                yield item

        base_thunk = StreamThunk(identity_processor, name="base")

        # Build a complex pipeline
        complex_thunk = (
            base_thunk.map(sync_increment)  # Add 1 to each
            .filter(is_even)  # Keep only even results
            .map(lambda x: x * 10)  # Multiply by 10
        )

        input_stream = sync_stream_range(6)
        output_stream = complex_thunk(input_stream)
        values = [item async for item in output_stream]
        # Original: [0,1,2,3,4,5]
        # After +1: [1,2,3,4,5,6]
        # After filter even: [2,4,6]
        # After *10: [20,40,60]
        assert values == [20, 40, 60]

    @pytest.mark.asyncio
    async def test_stream_thunk_with_different_stream_types(self):
        """Test StreamThunk with different types of input streams."""

        async def type_processor(stream):
            async for item in stream:
                yield f"processed_{item}"

        stream_thunk = StreamThunk(type_processor, name="type_processor")

        # Test with string stream
        input_stream = async_string_stream(3)
        output_stream = stream_thunk(input_stream)
        values = [item async for item in output_stream]
        assert values == ["processed_item_0", "processed_item_1", "processed_item_2"]

    @pytest.mark.asyncio
    async def test_thunk_to_stream_to_thunk_conversion(self):
        """Test round-trip conversion: Thunk -> StreamThunk -> Thunk."""
        original_thunk = Thunk(lambda x: x * 2, name="double")
        stream_thunk = original_thunk.stream()
        collected_thunk = stream_thunk.collect()

        # Verify the round trip preserves functionality
        input_stream = sync_stream_range(3)
        result = await collected_thunk(input_stream)
        assert result == [0, 2, 4]
        assert collected_thunk.name == "double.collect"
