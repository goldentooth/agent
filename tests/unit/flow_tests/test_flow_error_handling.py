from typing import AsyncGenerator

import pytest

from flow.flow import Flow


class TestFlowErrorHandling:
    """Test Flow error handling improvements."""

    @pytest.mark.asyncio
    async def test_with_fallback_empty_stream(self) -> None:
        """Test with_fallback when stream is empty."""
        # Create an empty flow
        empty_flow: Flow[None, str] = Flow.from_iterable([])
        fallback_flow = empty_flow.with_fallback("fallback_value")

        async def input_stream() -> AsyncGenerator[None, None]:
            yield None

        result = await fallback_flow.collect()(input_stream())

        assert result == ["fallback_value"]

    @pytest.mark.asyncio
    async def test_with_fallback_non_empty_stream(self) -> None:
        """Test with_fallback when stream has items."""
        # Create a non-empty flow
        flow: Flow[None, str] = Flow.from_iterable(["a", "b"])
        fallback_flow = flow.with_fallback("fallback_value")

        async def input_stream() -> AsyncGenerator[None, None]:
            yield None

        result = await fallback_flow.collect()(input_stream())

        # Should not include fallback since stream wasn't empty
        assert result == ["a", "b"]
