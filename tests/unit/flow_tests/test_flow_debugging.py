from __future__ import annotations

import pytest

from flow.flow import Flow


class TestFlowDebugging:
    """Test Flow debugging and representation improvements."""

    def test_flow_repr(self) -> None:
        """Test rich __repr__ for Flow."""
        flow: Flow[int, int] = Flow.from_sync_fn(lambda x: x + 1)
        repr_str = repr(flow)

        assert "<Flow name=" in repr_str
        assert "fn=" in repr_str
        assert "metadata=" in repr_str

    def test_flow_aiter_error(self) -> None:
        """Test that __aiter__ raises helpful error."""
        flow: Flow[int, int] = Flow.from_sync_fn(lambda x: x)

        with pytest.raises(TypeError, match="Flows must be called with a stream"):
            aiter(flow)
