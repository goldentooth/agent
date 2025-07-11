import asyncio
from typing import Any, AsyncGenerator, Callable

import pytest

from flow.flow import Flow


class TestFlowFromEmitter:
    """Tests for Flow.from_emitter static method."""

    @pytest.mark.asyncio
    async def test_from_emitter_creates_flow_from_callback_system(self) -> None:
        """Test that from_emitter creates a flow from callback-based system."""

        def register_callback(callback: Callable[[str], None]) -> None:
            # Simulate emitting some values
            callback("event1")
            callback("event2")
            callback("event3")

        flow: Flow[Any, str] = Flow.from_emitter(register_callback)

        async def empty_stream() -> AsyncGenerator[None, None]:
            yield None

        result = flow(empty_stream())
        items: list[str] = [item async for item in result]

        assert items == ["event1", "event2", "event3"]

    @pytest.mark.asyncio
    async def test_from_emitter_with_async_registration(self) -> None:
        """Test that from_emitter works with async callback registration."""

        async def register_callback(callback: Callable[[int], None]) -> None:
            # Simulate async setup
            await asyncio.sleep(0.001)
            callback(100)
            callback(200)
            callback(300)

        flow: Flow[Any, int] = Flow.from_emitter(register_callback)

        async def empty_stream() -> AsyncGenerator[None, None]:
            yield None

        result = flow(empty_stream())
        items: list[int] = [item async for item in result]

        assert items == [100, 200, 300]

    @pytest.mark.asyncio
    async def test_from_emitter_with_no_emissions(self) -> None:
        """Test that from_emitter works when no values are emitted."""

        def register_callback(callback: Callable[[str], None]) -> None:
            # Don't call the callback at all
            pass

        flow: Flow[Any, str] = Flow.from_emitter(register_callback)

        async def empty_stream() -> AsyncGenerator[None, None]:
            yield None

        result = flow(empty_stream())
        items: list[str] = [item async for item in result]

        assert items == []

    @pytest.mark.asyncio
    async def test_from_emitter_with_single_emission(self) -> None:
        """Test that from_emitter works with single value emission."""

        def register_callback(callback: Callable[[str], None]) -> None:
            callback("single_value")

        flow: Flow[Any, str] = Flow.from_emitter(register_callback)

        async def empty_stream() -> AsyncGenerator[None, None]:
            yield None

        result = flow(empty_stream())
        items: list[str] = [item async for item in result]

        assert items == ["single_value"]

    def test_from_emitter_sets_descriptive_name(self) -> None:
        """Test that from_emitter sets a descriptive flow name."""

        def register_callback(callback: Callable[[str], None]) -> None:
            callback("test")

        flow: Flow[Any, str] = Flow.from_emitter(register_callback)

        assert flow.name == "from_emitter"

    @pytest.mark.asyncio
    async def test_from_emitter_preserves_types(self) -> None:
        """Test that from_emitter preserves the type of emitted values."""

        def register_callback(callback: Callable[[int], None]) -> None:
            callback(42)
            callback(99)
            callback(123)

        flow: Flow[Any, int] = Flow.from_emitter(register_callback)

        async def empty_stream() -> AsyncGenerator[None, None]:
            yield None

        result = flow(empty_stream())
        items: list[int] = [item async for item in result]

        assert items == [42, 99, 123]
        assert all(isinstance(item, int) for item in items)

    @pytest.mark.asyncio
    async def test_from_emitter_chaining_with_other_operations(self) -> None:
        """Test that flows from from_emitter can be chained."""

        def register_callback(callback: Callable[[int], None]) -> None:
            for i in [1, 2, 3, 4, 5]:
                callback(i)

        def is_even(x: int) -> bool:
            return x % 2 == 0

        def square(x: int) -> int:
            return x * x

        flow = Flow.from_emitter(register_callback).filter(is_even).map(square)

        async def empty_stream() -> AsyncGenerator[None, None]:
            yield None

        result = flow(empty_stream())
        items: list[int] = [item async for item in result]

        assert items == [4, 16]  # 2^2, 4^2

    @pytest.mark.asyncio
    async def test_from_emitter_ignores_input_stream(self) -> None:
        """Test that from_emitter ignores the input stream completely."""

        def register_callback(callback: Callable[[str], None]) -> None:
            callback("emitter_value")

        flow: Flow[Any, str] = Flow.from_emitter(register_callback)

        # Input stream with different data
        async def input_stream() -> AsyncGenerator[str, None]:
            yield "input_value"

        result = flow(input_stream())
        items: list[str] = [item async for item in result]

        # Should get the emitted data, not the input stream data
        assert items == ["emitter_value"]

    @pytest.mark.asyncio
    async def test_from_emitter_with_delayed_emissions(self) -> None:
        """Test that from_emitter works with delayed callback emissions."""

        async def register_callback(callback: Callable[[str], None]) -> None:
            await asyncio.sleep(0.001)
            callback("delayed1")
            await asyncio.sleep(0.001)
            callback("delayed2")

        flow: Flow[Any, str] = Flow.from_emitter(register_callback)

        async def empty_stream() -> AsyncGenerator[None, None]:
            yield None

        result = flow(empty_stream())
        items: list[str] = [item async for item in result]

        assert items == ["delayed1", "delayed2"]

    @pytest.mark.asyncio
    async def test_from_emitter_multiple_input_calls(self) -> None:
        """Test that from_emitter produces the same output for multiple calls."""

        def register_callback(callback: Callable[[str], None]) -> None:
            callback("value1")
            callback("value2")

        flow: Flow[Any, str] = Flow.from_emitter(register_callback)

        async def stream1() -> AsyncGenerator[None, None]:
            yield None

        async def stream2() -> AsyncGenerator[str, None]:
            yield "ignored"

        result1 = flow(stream1())
        items1: list[str] = [item async for item in result1]

        result2 = flow(stream2())
        items2: list[str] = [item async for item in result2]

        assert items1 == items2 == ["value1", "value2"]

    @pytest.mark.asyncio
    async def test_from_emitter_with_complex_emitter_system(self) -> None:
        """Test from_emitter with more complex emitter pattern."""

        class EventEmitter:
            def __init__(self) -> None:
                super().__init__()
                self.callbacks: list[Callable[[dict[str, Any]], None]] = []

            def register(self, callback: Callable[[dict[str, Any]], None]) -> None:
                self.callbacks.append(callback)
                # Simulate some events being emitted
                callback({"type": "start", "data": 1})
                callback({"type": "data", "data": 2})
                callback({"type": "end", "data": 3})

        emitter = EventEmitter()

        flow: Flow[Any, dict[str, Any]] = Flow.from_emitter(emitter.register)

        async def empty_stream() -> AsyncGenerator[None, None]:
            yield None

        result = flow(empty_stream())
        items: list[dict[str, Any]] = [item async for item in result]

        expected = [
            {"type": "start", "data": 1},
            {"type": "data", "data": 2},
            {"type": "end", "data": 3},
        ]
        assert items == expected
