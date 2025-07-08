from typing import Any, AsyncGenerator

import pytest

from flowengine.flow import Flow


class TestFlowCreation:
    """Tests for Flow creation patterns and factory methods."""

    @pytest.mark.asyncio
    async def test_factory_method_pure(self) -> None:
        """Test Flow.pure() factory method."""

        async def source_stream() -> AsyncGenerator[int, None]:
            yield 1
            yield 2
            yield 3

        flow = Flow.pure("hello")
        result = [item async for item in flow(source_stream())]

        assert result == ["hello"]

    @pytest.mark.asyncio
    async def test_factory_method_identity(self) -> None:
        """Test Flow.identity() factory method."""

        async def source_stream() -> AsyncGenerator[str, None]:
            yield "hello"
            yield "world"

        flow: Flow[str, str] = Flow.identity()
        result: list[str] = [item async for item in flow(source_stream())]

        assert result == ["hello", "world"]

    @pytest.mark.asyncio
    async def test_factory_method_from_iterable(self) -> None:
        """Test Flow.from_iterable() factory method."""

        async def source_stream() -> AsyncGenerator[None, None]:
            return
            yield  # pragma: no cover

        flow = Flow.from_iterable([1, 2, 3, 4, 5])
        result = [item async for item in flow(source_stream())]

        assert result == [1, 2, 3, 4, 5]

    @pytest.mark.asyncio
    async def test_factory_method_from_value_fn(self) -> None:
        """Test Flow.from_value_fn() factory method."""

        async def async_double(x: int) -> int:
            return x * 2

        flow = Flow.from_value_fn(async_double)

        async def source_stream() -> AsyncGenerator[int, None]:
            yield 5
            yield 10

        result = [item async for item in flow(source_stream())]

        assert result == [10, 20]

    @pytest.mark.asyncio
    async def test_factory_method_from_sync_fn(self) -> None:
        """Test Flow.from_sync_fn() factory method."""

        def sync_square(x: int) -> int:
            return x * x

        flow = Flow.from_sync_fn(sync_square)

        async def source_stream() -> AsyncGenerator[int, None]:
            yield 3
            yield 4

        result = [item async for item in flow(source_stream())]

        assert result == [9, 16]

    @pytest.mark.asyncio
    async def test_factory_method_from_event_fn(self) -> None:
        """Test Flow.from_event_fn() factory method."""

        async def async_range(n: int) -> AsyncGenerator[int, None]:
            for i in range(n):
                yield i

        flow = Flow.from_event_fn(async_range)

        async def source_stream() -> AsyncGenerator[int, None]:
            yield 3
            yield 2

        result = [item async for item in flow(source_stream())]

        assert result == [0, 1, 2, 0, 1]

    @pytest.mark.asyncio
    async def test_decorator_patterns_value_fn(self) -> None:
        """Test decorator pattern with from_value_fn."""

        @Flow.from_value_fn
        async def process_value(x: int) -> str:
            return f"processed_{x}"

        async def source_stream() -> AsyncGenerator[int, None]:
            yield 1
            yield 2

        result = [item async for item in process_value(source_stream())]

        assert result == ["processed_1", "processed_2"]

    @pytest.mark.asyncio
    async def test_decorator_patterns_sync_fn(self) -> None:
        """Test decorator pattern with from_sync_fn."""

        @Flow.from_sync_fn
        def transform_sync(x: int) -> str:
            return f"sync_{x}"

        async def source_stream() -> AsyncGenerator[int, None]:
            yield 7
            yield 8

        result = [item async for item in transform_sync(source_stream())]

        assert result == ["sync_7", "sync_8"]

    @pytest.mark.asyncio
    async def test_decorator_patterns_event_fn(self) -> None:
        """Test decorator pattern with from_event_fn."""

        @Flow.from_event_fn
        async def generate_events(x: int) -> AsyncGenerator[str, None]:
            for i in range(x):
                yield f"event_{i}"

        async def source_stream() -> AsyncGenerator[int, None]:
            yield 2
            yield 1

        result = [item async for item in generate_events(source_stream())]

        assert result == ["event_0", "event_1", "event_0"]

    @pytest.mark.asyncio
    async def test_lambda_flows(self) -> None:
        """Test creating flows from lambda expressions."""

        async def source_stream() -> AsyncGenerator[None, None]:
            return
            yield  # pragma: no cover

        # Create a flow from a lambda that generates values
        flow = Flow.from_iterable([1, 2, 3]).map(lambda x: x * 3)
        result = [item async for item in flow(source_stream())]

        assert result == [3, 6, 9]

    @pytest.mark.asyncio
    async def test_factory_method_composition(self) -> None:
        """Test composing factory methods."""

        async def source_stream() -> AsyncGenerator[None, None]:
            return
            yield  # pragma: no cover

        # Compose multiple factory methods
        flow = Flow.from_iterable([1, 2, 3]).map(lambda x: x * 2) >> Flow.from_sync_fn(
            lambda x: f"value_{x}"
        )

        result = [item async for item in flow(source_stream())]

        assert result == ["value_2", "value_4", "value_6"]

    @pytest.mark.asyncio
    async def test_factory_method_metadata(self) -> None:
        """Test that factory methods preserve metadata."""

        flow = Flow.pure(42)
        assert flow.name == "pure(42)"
        assert isinstance(flow.metadata, dict)

        identity_flow: Flow[Any, Any] = Flow.identity()
        assert identity_flow.name == "identity"

        iterable_flow = Flow.from_iterable([1, 2, 3])
        assert iterable_flow.name == "from_iterable"
        assert isinstance(iterable_flow.metadata, dict)

    @pytest.mark.asyncio
    async def test_emitter_pattern_creation(self) -> None:
        """Test Flow.from_emitter() creation pattern."""

        async def emitter_fn(emit: Any) -> None:
            emit("hello")
            emit("world")

        flow: Flow[None, str] = Flow.from_emitter(emitter_fn)

        async def source_stream() -> AsyncGenerator[None, None]:
            yield None

        result: list[str] = [item async for item in flow(source_stream())]

        assert result == ["hello", "world"]
