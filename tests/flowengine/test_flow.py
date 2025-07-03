from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from flowengine.flow import Flow


def get_mock_flow(overrides: dict[str, Any] | None = None) -> Flow[int, str]:
    """Factory for creating test flows."""
    base_metadata = {"test": True}

    async def default_fn(stream: AsyncIterator[int]) -> AsyncIterator[str]:
        async for item in stream:
            yield str(item)

    fn = default_fn
    name = "test_flow"
    metadata = base_metadata

    if overrides:
        fn = overrides.get("fn", default_fn)
        name = overrides.get("name", "test_flow")
        metadata = overrides.get("metadata", base_metadata)

    return Flow(fn, name, metadata)


class TestFlowInit:
    """Tests for Flow.__init__ method."""

    def test_init_with_function_only(self) -> None:
        """Test Flow initialization with just a function."""

        async def test_fn(stream: AsyncIterator[int]) -> AsyncIterator[str]:
            async for item in stream:
                yield str(item)

        flow = Flow(test_fn)

        assert flow.fn is test_fn
        assert flow.name == "<anonymous>"
        assert flow.metadata == {}
        assert flow.__name__ == "<anonymous>"

    def test_init_with_name(self) -> None:
        """Test Flow initialization with a name."""

        async def test_fn(stream: AsyncIterator[int]) -> AsyncIterator[str]:
            async for item in stream:
                yield str(item)

        flow = Flow(test_fn, name="my_flow")

        assert flow.fn is test_fn
        assert flow.name == "my_flow"
        assert flow.metadata == {}
        assert flow.__name__ == "my_flow"

    def test_init_with_metadata(self) -> None:
        """Test Flow initialization with metadata."""

        async def test_fn(stream: AsyncIterator[int]) -> AsyncIterator[str]:
            async for item in stream:
                yield str(item)

        metadata = {"key": "value", "number": 42}
        flow = Flow(test_fn, metadata=metadata)

        assert flow.fn is test_fn
        assert flow.name == "<anonymous>"
        assert flow.metadata == metadata
        assert flow.__name__ == "<anonymous>"

    def test_init_with_none_metadata(self) -> None:
        """Test Flow initialization with explicit None metadata."""

        async def test_fn(stream: AsyncIterator[int]) -> AsyncIterator[str]:
            async for item in stream:
                yield str(item)

        flow = Flow(test_fn, metadata=None)

        assert flow.fn is test_fn
        assert flow.name == "<anonymous>"
        assert flow.metadata == {}
        assert flow.__name__ == "<anonymous>"

    def test_init_with_all_parameters(self) -> None:
        """Test Flow initialization with all parameters."""

        async def test_fn(stream: AsyncIterator[int]) -> AsyncIterator[str]:
            async for item in stream:
                yield str(item)

        metadata = {"description": "test flow", "version": 1}
        flow = Flow(test_fn, name="complete_flow", metadata=metadata)

        assert flow.fn is test_fn
        assert flow.name == "complete_flow"
        assert flow.metadata == metadata
        assert flow.__name__ == "complete_flow"
