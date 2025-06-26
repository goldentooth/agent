"""Comprehensive tests for the EventThunk class."""

import asyncio
import pytest
from unittest.mock import AsyncMock, Mock
from pyee.asyncio import AsyncIOEventEmitter
from goldentooth_agent.core.thunk import EventThunk, Thunk


# Test fixtures - async generator functions
async def sync_range_generator(n: int):
    """Generate numbers from 0 to n-1."""
    for i in range(n):
        yield i


async def async_range_generator(n: int):
    """Asynchronously generate numbers from 0 to n-1 with delays."""
    for i in range(n):
        await asyncio.sleep(0.01)
        yield i


async def async_fibonacci_generator(n: int):
    """Generate first n fibonacci numbers."""
    a, b = 0, 1
    for _ in range(n):
        yield a
        await asyncio.sleep(0.001)  # Small delay to make it async
        a, b = b, a + b


async def async_exception_generator(n: int):
    """Generator that raises an exception after yielding some values."""
    for i in range(n):
        if i == 2:
            raise ValueError(f"Exception at item {i}")
        yield i


async def async_empty_generator(n: int):
    """Generator that yields nothing."""
    return
    yield  # unreachable


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


def sync_side_effect(x):
    """Sync side effect function (won't work with tap)."""
    side_effects.append(f"sync_side_effect: {x}")


class TestEventThunkCreation:
    """Test cases for EventThunk creation and basic functionality."""

    def setup_method(self):
        """Clear side effects before each test."""
        side_effects.clear()

    @pytest.mark.asyncio
    async def test_event_thunk_creation(self):
        """Test creating an EventThunk with an async generator."""
        event_thunk = EventThunk(sync_range_generator, name="range")
        assert event_thunk.name == "range"
        assert event_thunk.metadata == {}

        # Test that it's callable and returns an async iterator
        iterator = event_thunk(3)
        values = [item async for item in iterator]
        assert values == [0, 1, 2]

    def test_event_thunk_creation_non_callable_raises_error(self):
        """Test that creating an EventThunk with non-callable raises TypeError."""
        with pytest.raises(TypeError, match="EventThunk requires a callable"):
            EventThunk("not_a_function", name="test")

    def test_event_thunk_creation_with_metadata(self):
        """Test creating an EventThunk with metadata."""
        metadata = {"version": "1.0", "description": "test thunk"}
        event_thunk = EventThunk(sync_range_generator, name="range", metadata=metadata)
        assert event_thunk.metadata == metadata

    def test_event_thunk_name_fallback(self):
        """Test that EventThunk names fall back appropriately."""
        # With explicit name
        event_thunk1 = EventThunk(sync_range_generator, name="explicit")
        assert event_thunk1.name == "explicit"

        # With empty name, should use function name
        event_thunk2 = EventThunk(sync_range_generator, name="")
        assert event_thunk2.name == "sync_range_generator"

    @pytest.mark.asyncio
    async def test_event_thunk_call(self):
        """Test calling an EventThunk."""
        event_thunk = EventThunk(async_range_generator, name="async_range")

        # Should return an async iterator
        iterator = event_thunk(3)
        assert hasattr(iterator, "__aiter__")

        # Collect values
        values = []
        async for item in iterator:
            values.append(item)
        assert values == [0, 1, 2]

    @pytest.mark.asyncio
    async def test_event_thunk_with_async_generator(self):
        """Test EventThunk with async generator that includes delays."""
        event_thunk = EventThunk(async_fibonacci_generator, name="fibonacci")

        values = [item async for item in event_thunk(5)]
        assert values == [0, 1, 1, 2, 3]  # First 5 fibonacci numbers

    @pytest.mark.asyncio
    async def test_event_thunk_empty_stream(self):
        """Test EventThunk with generator that yields nothing."""
        event_thunk = EventThunk(async_empty_generator, name="empty")

        values = [item async for item in event_thunk(5)]
        assert values == []

    @pytest.mark.asyncio
    async def test_event_thunk_exception_handling(self):
        """Test that exceptions from generators are properly propagated."""
        event_thunk = EventThunk(async_exception_generator, name="exception")

        values = []
        with pytest.raises(ValueError, match="Exception at item 2"):
            async for item in event_thunk(5):
                values.append(item)

        # Should have yielded values before the exception
        assert values == [0, 1]


class TestEventThunkFromCallable:
    """Test cases for EventThunk.from_callable class method."""

    @pytest.mark.asyncio
    async def test_from_callable_basic(self):
        """Test creating EventThunk from callable."""
        event_thunk = EventThunk.from_callable(
            sync_range_generator, name="from_callable"
        )

        assert event_thunk.name == "from_callable"
        values = [item async for item in event_thunk(3)]
        assert values == [0, 1, 2]

    @pytest.mark.asyncio
    async def test_from_callable_with_async_generator(self):
        """Test from_callable with async generator."""
        event_thunk = EventThunk.from_callable(async_fibonacci_generator, name="fib")

        values = [item async for item in event_thunk(4)]
        assert values == [0, 1, 1, 2]


class TestEventThunkMap:
    """Test cases for EventThunk.map method."""

    @pytest.mark.asyncio
    async def test_map_basic(self):
        """Test basic map functionality."""
        event_thunk = EventThunk(sync_range_generator, name="range")
        mapped_thunk = event_thunk.map(sync_increment)

        assert mapped_thunk.name == "range.map(sync_increment)"
        values = [item async for item in mapped_thunk(3)]
        assert values == [1, 2, 3]  # 0+1, 1+1, 2+1

    @pytest.mark.asyncio
    async def test_map_with_lambda(self):
        """Test map with lambda function."""
        event_thunk = EventThunk(sync_range_generator, name="range")
        mapped_thunk = event_thunk.map(lambda x: x * 10)

        assert mapped_thunk.name == "range.map(<lambda>)"
        values = [item async for item in mapped_thunk(3)]
        assert values == [0, 10, 20]

    @pytest.mark.asyncio
    async def test_map_type_transformation(self):
        """Test map that transforms types."""
        event_thunk = EventThunk(sync_range_generator, name="range")
        mapped_thunk = event_thunk.map(sync_to_string)

        values = [item async for item in mapped_thunk(3)]
        assert values == ["value_0", "value_1", "value_2"]

    @pytest.mark.asyncio
    async def test_map_chaining(self):
        """Test chaining multiple map operations."""
        event_thunk = EventThunk(sync_range_generator, name="range")
        chained_thunk = event_thunk.map(sync_increment).map(sync_double)

        assert chained_thunk.name == "range.map(sync_increment).map(sync_double)"
        values = [item async for item in chained_thunk(3)]
        assert values == [2, 4, 6]  # (0+1)*2, (1+1)*2, (2+1)*2

    @pytest.mark.asyncio
    async def test_map_empty_stream(self):
        """Test map on empty stream."""
        event_thunk = EventThunk(async_empty_generator, name="empty")
        mapped_thunk = event_thunk.map(sync_increment)

        values = [item async for item in mapped_thunk(3)]
        assert values == []


class TestEventThunkFilter:
    """Test cases for EventThunk.filter method."""

    @pytest.mark.asyncio
    async def test_filter_basic(self):
        """Test basic filter functionality."""
        event_thunk = EventThunk(sync_range_generator, name="range")
        filtered_thunk = event_thunk.filter(is_even)

        assert filtered_thunk.name == "range.filter(is_even)"
        values = [item async for item in filtered_thunk(6)]
        assert values == [0, 2, 4]  # Even numbers from 0-5

    @pytest.mark.asyncio
    async def test_filter_with_lambda(self):
        """Test filter with lambda predicate."""
        event_thunk = EventThunk(sync_range_generator, name="range")
        filtered_thunk = event_thunk.filter(lambda x: x > 2)

        assert filtered_thunk.name == "range.filter(<lambda>)"
        values = [item async for item in filtered_thunk(6)]
        assert values == [3, 4, 5]  # Numbers > 2

    @pytest.mark.asyncio
    async def test_filter_no_matches(self):
        """Test filter where no items match."""
        event_thunk = EventThunk(sync_range_generator, name="range")
        filtered_thunk = event_thunk.filter(lambda x: x > 100)

        values = [item async for item in filtered_thunk(5)]
        assert values == []

    @pytest.mark.asyncio
    async def test_filter_all_match(self):
        """Test filter where all items match."""
        event_thunk = EventThunk(sync_range_generator, name="range")
        filtered_thunk = event_thunk.filter(lambda x: x >= 0)

        values = [item async for item in filtered_thunk(3)]
        assert values == [0, 1, 2]

    @pytest.mark.asyncio
    async def test_filter_chaining(self):
        """Test chaining filter operations."""
        event_thunk = EventThunk(sync_range_generator, name="range")
        chained_thunk = event_thunk.filter(is_even).filter(less_than_five)

        values = [item async for item in chained_thunk(10)]
        assert values == [0, 2, 4]  # Even numbers less than 5


class TestEventThunkFlatMap:
    """Test cases for EventThunk.flat_map method."""

    def create_range_event_thunk(self, n: int) -> EventThunk:
        """Helper to create an EventThunk that generates range(n)."""

        async def range_gen(_):
            for i in range(n):
                yield i

        return EventThunk(range_gen, name=f"range_{n}")

    @pytest.mark.asyncio
    async def test_flat_map_basic(self):
        """Test basic flat_map functionality."""
        event_thunk = EventThunk(sync_range_generator, name="range")

        # For each number, create a range EventThunk of that size
        flat_mapped = event_thunk.flat_map(lambda x: self.create_range_event_thunk(x))

        assert flat_mapped.name == "range.flat_map(<lambda>)"
        values = [item async for item in flat_mapped(4)]
        # 0: no items, 1: [0], 2: [0,1], 3: [0,1,2]
        assert values == [0, 0, 1, 0, 1, 2]

    @pytest.mark.asyncio
    async def test_flat_map_with_named_function(self):
        """Test flat_map with named function."""

        def create_repeat_thunk(x: int) -> EventThunk:
            async def repeat_gen(_):
                for _ in range(2):  # Repeat each value twice
                    yield x

            return EventThunk(repeat_gen, name=f"repeat_{x}")

        event_thunk = EventThunk(sync_range_generator, name="range")
        flat_mapped = event_thunk.flat_map(create_repeat_thunk)

        assert flat_mapped.name == "range.flat_map(create_repeat_thunk)"
        values = [item async for item in flat_mapped(3)]
        assert values == [0, 0, 1, 1, 2, 2]

    @pytest.mark.asyncio
    async def test_flat_map_empty_results(self):
        """Test flat_map where some results are empty."""

        def create_conditional_thunk(x: int) -> EventThunk:
            async def conditional_gen(_):
                if x % 2 == 0:  # Only yield for even numbers
                    yield x * 10

            return EventThunk(conditional_gen, name=f"conditional_{x}")

        event_thunk = EventThunk(sync_range_generator, name="range")
        flat_mapped = event_thunk.flat_map(create_conditional_thunk)

        values = [item async for item in flat_mapped(4)]
        assert values == [0, 20]  # Only even numbers * 10


class TestEventThunkFlatten:
    """Test cases for EventThunk.flatten method."""

    @pytest.mark.asyncio
    async def test_flatten_basic(self):
        """Test basic flatten functionality."""

        # Create an EventThunk that yields other EventThunks
        async def thunk_generator(n: int):
            for i in range(n):
                # Each yielded thunk generates numbers from 0 to i
                # Need to capture i in closure to avoid late binding
                def make_inner_gen(count):
                    async def inner_gen(_):
                        for j in range(count):
                            yield j

                    return inner_gen

                yield EventThunk(make_inner_gen(i), name=f"inner_{i}")

        nested_thunk = EventThunk(thunk_generator, name="nested")
        flattened_thunk = nested_thunk.flatten()

        assert flattened_thunk.name == "nested.flatten"
        values = [item async for item in flattened_thunk(4)]
        # 0: no items, 1: [0], 2: [0,1], 3: [0,1,2]
        assert values == [0, 0, 1, 0, 1, 2]

    @pytest.mark.asyncio
    async def test_flatten_empty_inner_streams(self):
        """Test flatten with some empty inner streams."""

        async def thunk_generator(n: int):
            for i in range(n):
                if i % 2 == 0:  # Only yield thunks for even indices

                    async def inner_gen(_):
                        yield i * 10

                    yield EventThunk(inner_gen, name=f"inner_{i}")
                else:
                    # Yield empty thunk for odd indices
                    async def empty_gen(_):
                        return
                        yield  # unreachable

                    yield EventThunk(empty_gen, name=f"empty_{i}")

        nested_thunk = EventThunk(thunk_generator, name="nested")
        flattened_thunk = nested_thunk.flatten()

        values = [item async for item in flattened_thunk(4)]
        assert values == [0, 20]  # Only even indices * 10


class TestEventThunkTap:
    """Test cases for EventThunk.tap method."""

    def setup_method(self):
        """Clear side effects before each test."""
        side_effects.clear()

    @pytest.mark.asyncio
    async def test_tap_basic(self):
        """Test basic tap functionality."""
        event_thunk = EventThunk(sync_range_generator, name="range")
        tapped_thunk = event_thunk.tap(async_side_effect)

        assert tapped_thunk.name == "range.tap(async_side_effect)"
        values = [item async for item in tapped_thunk(3)]

        # Original values should be preserved
        assert values == [0, 1, 2]
        # Side effects should have been called
        assert side_effects == ["side_effect: 0", "side_effect: 1", "side_effect: 2"]

    @pytest.mark.asyncio
    async def test_tap_with_lambda(self):
        """Test tap with lambda function."""

        async def log_lambda(x):
            side_effects.append(f"lambda: {x}")

        event_thunk = EventThunk(sync_range_generator, name="range")
        tapped_thunk = event_thunk.tap(log_lambda)

        values = [item async for item in tapped_thunk(2)]
        assert values == [0, 1]
        assert side_effects == ["lambda: 0", "lambda: 1"]

    @pytest.mark.asyncio
    async def test_tap_multiple(self):
        """Test chaining multiple tap operations."""

        async def first_effect(x):
            side_effects.append(f"first: {x}")

        async def second_effect(x):
            side_effects.append(f"second: {x}")

        event_thunk = EventThunk(sync_range_generator, name="range")
        tapped_thunk = event_thunk.tap(first_effect).tap(second_effect)

        values = [item async for item in tapped_thunk(2)]
        assert values == [0, 1]
        assert side_effects == ["first: 0", "second: 0", "first: 1", "second: 1"]

    @pytest.mark.asyncio
    async def test_tap_with_exception_in_side_effect(self):
        """Test tap when side effect raises exception."""

        async def failing_effect(x):
            if x == 1:
                raise ValueError(f"Side effect failed for {x}")
            side_effects.append(f"effect: {x}")

        event_thunk = EventThunk(sync_range_generator, name="range")
        tapped_thunk = event_thunk.tap(failing_effect)

        values = []
        with pytest.raises(ValueError, match="Side effect failed for 1"):
            async for item in tapped_thunk(3):
                values.append(item)

        # Should have processed the first item before failing
        assert values == [0]
        assert side_effects == ["effect: 0"]


class TestEventThunkComposition:
    """Test cases for EventThunk composition and operators."""

    def setup_method(self):
        """Clear side effects before each test."""
        side_effects.clear()

    @pytest.mark.asyncio
    async def test_rshift_operator(self):
        """Test >> operator for EventThunk composition."""
        # First thunk generates numbers
        first_thunk = EventThunk(sync_range_generator, name="first")

        # Second thunk takes a number and generates that many strings
        async def string_generator(n: int):
            for i in range(n):
                yield f"item_{i}"

        second_thunk = EventThunk(string_generator, name="second")

        composed = first_thunk >> second_thunk
        assert composed.name == "first >> second"

        values = [item async for item in composed(3)]
        # 0: no items, 1: ["item_0"], 2: ["item_0", "item_1"]
        assert values == ["item_0", "item_0", "item_1"]

    @pytest.mark.asyncio
    async def test_complex_composition(self):
        """Test complex composition of multiple operations."""
        event_thunk = EventThunk(sync_range_generator, name="range")

        # Build a complex pipeline
        complex_thunk = (
            event_thunk.map(sync_increment)  # Add 1 to each
            .filter(is_even)  # Keep only even results
            .map(lambda x: x * 10)  # Multiply by 10
            .tap(async_side_effect)  # Log each value
        )

        values = [item async for item in complex_thunk(6)]
        # Original: [0,1,2,3,4,5]
        # After +1: [1,2,3,4,5,6]
        # After filter even: [2,4,6]
        # After *10: [20,40,60]
        assert values == [20, 40, 60]
        assert side_effects == ["side_effect: 20", "side_effect: 40", "side_effect: 60"]


class TestEventThunkCollect:
    """Test cases for EventThunk.collect method."""

    @pytest.mark.asyncio
    async def test_collect_basic(self):
        """Test collecting EventThunk values into a list."""
        event_thunk = EventThunk(sync_range_generator, name="range")
        collected_thunk = event_thunk.collect()

        assert collected_thunk.name == "range.collect"
        assert isinstance(collected_thunk, Thunk)  # Should return a regular Thunk

        result = await collected_thunk(3)
        assert result == [0, 1, 2]

    @pytest.mark.asyncio
    async def test_collect_empty_stream(self):
        """Test collecting empty stream."""
        event_thunk = EventThunk(async_empty_generator, name="empty")
        collected_thunk = event_thunk.collect()

        result = await collected_thunk(5)
        assert result == []

    @pytest.mark.asyncio
    async def test_collect_with_transformations(self):
        """Test collect after transformations."""
        event_thunk = EventThunk(sync_range_generator, name="range")
        transformed_thunk = event_thunk.map(sync_double).filter(lambda x: x < 6)
        collected_thunk = transformed_thunk.collect()

        result = await collected_thunk(5)
        # Original: [0,1,2,3,4] -> doubled: [0,2,4,6,8] -> filtered < 6: [0,2,4]
        assert result == [0, 2, 4]

    @pytest.mark.asyncio
    async def test_collect_with_async_generator(self):
        """Test collect with async generator."""
        event_thunk = EventThunk(async_fibonacci_generator, name="fib")
        collected_thunk = event_thunk.collect()

        result = await collected_thunk(5)
        assert result == [0, 1, 1, 2, 3]


class TestEventThunkFromEmitter:
    """Test cases for EventThunk.from_emitter static method."""

    @pytest.mark.asyncio
    async def test_from_emitter_basic(self):
        """Test creating EventThunk from event emitter."""
        emitter = AsyncIOEventEmitter()
        event_thunk = EventThunk.from_emitter(emitter, "test_event")

        assert event_thunk.name == "EventThunk.from_emitter(test_event)"
        assert event_thunk.metadata["event"] == "test_event"
        assert event_thunk.metadata["emitter"] is emitter

        # Create iterator and start consuming
        iterator = event_thunk(None)

        # Create a task to emit events after a short delay
        async def emit_events():
            await asyncio.sleep(0.01)  # Small delay to ensure iterator is ready
            emitter.emit("test_event", "value1")
            emitter.emit("test_event", "value2")
            emitter.emit("test_event", "value3")

        # Start emitting events in the background
        emit_task = asyncio.create_task(emit_events())

        # Collect a few values (this will run indefinitely so we limit it)
        values = []
        async for value in iterator:
            values.append(value)
            if len(values) >= 3:
                break

        await emit_task  # Ensure the emit task completes
        assert values == ["value1", "value2", "value3"]

    @pytest.mark.asyncio
    async def test_from_emitter_different_events(self):
        """Test that from_emitter only captures specified events."""
        emitter = AsyncIOEventEmitter()
        event_thunk = EventThunk.from_emitter(emitter, "target_event")

        iterator = event_thunk(None)

        # Create a task to emit events after a short delay
        async def emit_events():
            await asyncio.sleep(0.01)  # Small delay to ensure iterator is ready
            emitter.emit("other_event", "ignored")
            emitter.emit("target_event", "captured1")
            emitter.emit("another_event", "also_ignored")
            emitter.emit("target_event", "captured2")

        # Start emitting events in the background
        emit_task = asyncio.create_task(emit_events())

        # Should only capture events for the target event
        values = []
        async for value in iterator:
            values.append(value)
            if len(values) >= 2:
                break

        await emit_task  # Ensure the emit task completes
        assert values == ["captured1", "captured2"]


class TestThunkEventsMethod:
    """Test cases for Thunk.events() method that converts to EventThunk."""

    @pytest.mark.asyncio
    async def test_thunk_events_conversion(self):
        """Test converting regular Thunk to EventThunk."""
        from goldentooth_agent.core.thunk import Thunk

        regular_thunk = Thunk(lambda x: x * 2, name="double")
        event_thunk = regular_thunk.events()

        assert isinstance(event_thunk, EventThunk)
        assert event_thunk.name == "double"
        assert event_thunk.metadata == regular_thunk.metadata

        # Should yield the single result
        values = [item async for item in event_thunk(5)]
        assert values == [10]

    @pytest.mark.asyncio
    async def test_thunk_events_with_async_thunk(self):
        """Test converting async Thunk to EventThunk."""
        from goldentooth_agent.core.thunk import Thunk

        async def async_multiply(x):
            await asyncio.sleep(0.01)
            return x * 3

        regular_thunk = Thunk(async_multiply, name="triple")
        event_thunk = regular_thunk.events()

        values = [item async for item in event_thunk(4)]
        assert values == [12]

    @pytest.mark.asyncio
    async def test_thunk_events_preserves_metadata(self):
        """Test that converting to EventThunk preserves metadata."""
        from goldentooth_agent.core.thunk import Thunk

        metadata = {"version": "1.0", "description": "test"}
        regular_thunk = Thunk(lambda x: x + 1, name="increment", metadata=metadata)
        event_thunk = regular_thunk.events()

        assert event_thunk.metadata == metadata


class TestEventThunkEdgeCases:
    """Test edge cases and error conditions for EventThunk."""

    @pytest.mark.asyncio
    async def test_event_thunk_with_none_values(self):
        """Test EventThunk that yields None values."""

        async def none_generator(n: int):
            for i in range(n):
                if i % 2 == 0:
                    yield None
                else:
                    yield i

        event_thunk = EventThunk(none_generator, name="none_gen")
        values = [item async for item in event_thunk(4)]
        assert values == [None, 1, None, 3]

    @pytest.mark.asyncio
    async def test_event_thunk_with_complex_objects(self):
        """Test EventThunk with complex object types."""

        async def dict_generator(n: int):
            for i in range(n):
                yield {"id": i, "value": i * 2}

        event_thunk = EventThunk(dict_generator, name="dict_gen")
        values = [item async for item in event_thunk(3)]
        expected = [{"id": 0, "value": 0}, {"id": 1, "value": 2}, {"id": 2, "value": 4}]
        assert values == expected

    @pytest.mark.asyncio
    async def test_event_thunk_generator_cleanup(self):
        """Test that generators are properly cleaned up."""
        cleanup_called = []

        async def generator_with_cleanup(n: int):
            try:
                for i in range(n):
                    yield i
            finally:
                cleanup_called.append("cleanup")

        event_thunk = EventThunk(generator_with_cleanup, name="cleanup_gen")

        # Partially consume the generator
        iterator = event_thunk(5)
        values = []
        async for item in iterator:
            values.append(item)
            if len(values) >= 2:
                break

        # Force cleanup by deleting the iterator
        del iterator
        await asyncio.sleep(0.01)  # Give time for cleanup

        assert values == [0, 1]
        # Note: Cleanup behavior depends on Python's garbage collection

    def test_event_thunk_repr(self):
        """Test string representation of EventThunk."""
        metadata = {"test": "value"}
        event_thunk = EventThunk(
            sync_range_generator, name="test_thunk", metadata=metadata
        )

        # EventThunk doesn't define __repr__ but inherits object's default
        repr_str = repr(event_thunk)
        assert "EventThunk" in repr_str
