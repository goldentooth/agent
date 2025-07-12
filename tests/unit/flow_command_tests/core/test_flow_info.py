"""Tests for FlowInfo data structure."""

from __future__ import annotations

import pytest

from flow_command.core.flow_info import FlowInfo


class TestFlowInfo:
    """Test suite for FlowInfo."""

    def test_flow_info_creation_minimal(self) -> None:
        """FlowInfo should be creatable with just a name."""
        flow_info = FlowInfo(name="test_flow")

        assert flow_info.name == "test_flow"
        assert flow_info.category is None
        assert flow_info.tags is None
        assert flow_info.metadata is None

    def test_flow_info_creation_full(self) -> None:
        """FlowInfo should be creatable with all fields."""
        flow_info = FlowInfo(
            name="test_flow",
            category="text",
            tags=["transform", "case"],
            metadata={"description": "A test flow"},
        )

        assert flow_info.name == "test_flow"
        assert flow_info.category == "text"
        assert flow_info.tags == ["transform", "case"]
        assert flow_info.metadata == {"description": "A test flow"}

    def test_tags_display_empty(self) -> None:
        """tags_display should return empty string when no tags."""
        flow_info = FlowInfo(name="test_flow")
        assert flow_info.tags_display == ""

    def test_tags_display_none(self) -> None:
        """tags_display should return empty string when tags is None."""
        flow_info = FlowInfo(name="test_flow", tags=None)
        assert flow_info.tags_display == ""

    def test_tags_display_single(self) -> None:
        """tags_display should return single tag."""
        flow_info = FlowInfo(name="test_flow", tags=["transform"])
        assert flow_info.tags_display == "transform"

    def test_tags_display_multiple(self) -> None:
        """tags_display should return comma-separated tags."""
        flow_info = FlowInfo(name="test_flow", tags=["transform", "case", "text"])
        assert flow_info.tags_display == "transform, case, text"

    def test_category_display_none(self) -> None:
        """category_display should return empty string when category is None."""
        flow_info = FlowInfo(name="test_flow")
        assert flow_info.category_display == ""

    def test_category_display_present(self) -> None:
        """category_display should return category when present."""
        flow_info = FlowInfo(name="test_flow", category="text")
        assert flow_info.category_display == "text"

    def test_str_representation(self) -> None:
        """String representation should show flow name."""
        flow_info = FlowInfo(
            name="test_flow",
            category="text",
            tags=["transform"],
            metadata={"description": "Test"},
        )
        assert str(flow_info) == "test_flow"

    def test_flow_info_immutable(self) -> None:
        """FlowInfo should be immutable (frozen dataclass)."""
        flow_info = FlowInfo(name="test_flow")

        with pytest.raises(AttributeError):
            flow_info.name = "new_name"  # type: ignore[misc]

    def test_to_dict_minimal(self) -> None:
        """to_dict should convert FlowInfo to dictionary with minimal data."""
        flow_info = FlowInfo(name="test_flow")
        result = flow_info.to_dict()

        expected = {
            "name": "test_flow",
            "category": None,
            "tags": None,
            "metadata": None,
        }
        assert result == expected

    def test_to_dict_full(self) -> None:
        """to_dict should convert FlowInfo to dictionary with full data."""
        flow_info = FlowInfo(
            name="test_flow",
            category="text",
            tags=["transform", "case"],
            metadata={"description": "A test flow"},
        )
        result = flow_info.to_dict()

        expected = {
            "name": "test_flow",
            "category": "text",
            "tags": ["transform", "case"],
            "metadata": {"description": "A test flow"},
        }
        assert result == expected
