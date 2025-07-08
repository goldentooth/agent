from typing import Any, AsyncGenerator

import pytest

from flowengine.flow import Flow


class TestFlowChaining:
    """Tests for Flow method chaining ergonomics (fluent API)."""

    @pytest.mark.asyncio
    async def test_fluent_api_collect(self) -> None:
        """Test that collect() provides ergonomic data collection."""

        async def source_stream() -> AsyncGenerator[None, None]:
            return
            yield  # pragma: no cover

        flow = Flow.from_iterable([1, 2, 3, 4, 5])
        collector = flow.collect()
        result = await collector(source_stream())

        assert result == [1, 2, 3, 4, 5]

    @pytest.mark.asyncio
    async def test_fluent_api_preview(self) -> None:
        """Test that preview() provides REPL development helper."""

        async def source_stream() -> AsyncGenerator[None, None]:
            return
            yield  # pragma: no cover

        flow = Flow.from_iterable([1, 2, 3, 4, 5])
        result = await flow.preview(source_stream())

        assert result == [1, 2, 3, 4, 5]

    @pytest.mark.asyncio
    async def test_fluent_api_preview_with_limit(self) -> None:
        """Test that preview() respects item limits."""

        async def source_stream() -> AsyncGenerator[None, None]:
            return
            yield  # pragma: no cover

        flow = Flow.from_iterable([1, 2, 3, 4, 5])
        result = await flow.preview(source_stream(), limit=3)

        assert result == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_method_composition(self) -> None:
        """Test method chaining for readable compositions."""

        async def source_stream() -> AsyncGenerator[None, None]:
            return
            yield  # pragma: no cover

        flow = (
            Flow.from_iterable([1, 2, 3, 4, 5])
            .map(lambda x: x * 2)
            .filter(lambda x: x > 4)
            .collect()
        )
        result = await flow(source_stream())

        assert result == [6, 8, 10]

    @pytest.mark.asyncio
    async def test_readable_chains(self) -> None:
        """Test that method chains are readable and discoverable."""

        async def source_stream() -> AsyncGenerator[None, None]:
            return
            yield  # pragma: no cover

        # Test that Flow methods return Flow instances for chaining
        flow = Flow.from_iterable([1, 2, 3])
        mapped_flow = flow.map(lambda x: x * 2)
        filtered_flow = mapped_flow.filter(lambda x: x > 2)
        labeled_flow = filtered_flow.label("test-chain")

        assert isinstance(mapped_flow, Flow)
        assert isinstance(filtered_flow, Flow)
        assert isinstance(labeled_flow, Flow)

        # Test terminal operation
        terminal_flow = labeled_flow.collect()
        result = await terminal_flow(source_stream())
        assert result == [4, 6]

    @pytest.mark.asyncio
    async def test_chaining_with_fallback(self) -> None:
        """Test that error handling methods chain naturally."""

        async def source_stream() -> AsyncGenerator[None, None]:
            return
            yield  # pragma: no cover

        # Test empty stream with fallback
        async def empty_source() -> AsyncGenerator[int, None]:
            return
            yield  # pragma: no cover

        empty_flow: Flow[Any, int] = Flow(lambda _: empty_source(), name="empty-source")
        flow_with_fallback: Flow[Any, int] = empty_flow.with_fallback(42)
        flow = flow_with_fallback.collect()

        result = await flow(source_stream())
        assert result == [42]

    @pytest.mark.asyncio
    async def test_chaining_with_print_debugging(self) -> None:
        """Test that print() method chains for debugging."""

        async def source_stream() -> AsyncGenerator[None, None]:
            return
            yield  # pragma: no cover

        flow = (
            Flow.from_iterable([1, 2, 3])
            .map(lambda x: x * 2)
            .print()  # Should not break the chain
            .filter(lambda x: x > 2)
            .collect()
        )

        result = await flow(source_stream())
        assert result == [4, 6]

    @pytest.mark.asyncio
    async def test_chaining_preserves_types(self) -> None:
        """Test that method chaining preserves type information."""

        async def source_stream() -> AsyncGenerator[None, None]:
            return
            yield  # pragma: no cover

        # This should type-check correctly
        flow: Flow[None, str] = (
            Flow.from_iterable([1, 2, 3])
            .map(lambda x: str(x))
            .filter(lambda x: len(x) > 0)
        )

        terminal_flow = flow.collect()
        result = await terminal_flow(source_stream())
        assert result == ["1", "2", "3"]
