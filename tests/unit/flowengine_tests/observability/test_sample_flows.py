"""Test the sample_flows fixture."""

from collections.abc import AsyncGenerator

import pytest

from flowengine.flow import Flow


@pytest.mark.asyncio
async def test_sample_flows_fixture(sample_flows: dict[str, Flow[int, int]]) -> None:
    """Test sample_flows fixture provides test flows."""
    assert "identity" in sample_flows
    assert "double" in sample_flows
    assert "filter_even" in sample_flows

    # Test identity flow
    identity_flow = sample_flows["identity"]
    assert identity_flow.name == "identity"
    assert isinstance(identity_flow, Flow)


@pytest.mark.asyncio
async def test_sample_flows_execution(sample_flows: dict[str, Flow[int, int]]) -> None:
    """Test sample flows execute correctly."""

    async def test_stream() -> AsyncGenerator[int, None]:
        for i in range(5):
            yield i

    # Test identity flow
    identity_flow = sample_flows["identity"]
    result: list[int] = []
    async for item in identity_flow(test_stream()):
        result.append(item)
    assert result == [0, 1, 2, 3, 4]

    # Test double flow
    double_flow = sample_flows["double"]
    result = []
    async for item in double_flow(test_stream()):
        result.append(item)
    assert result == [0, 2, 4, 6, 8]

    # Test filter_even flow
    filter_even_flow = sample_flows["filter_even"]
    result = []
    async for item in filter_even_flow(test_stream()):
        result.append(item)
    assert result == [0, 2, 4]
