"""Test Context.deep_diff method."""

from typing import Any

import pytest

from context.main import Context


def test_deep_diff_basic() -> None:
    """Test basic deep_diff functionality."""
    context1 = Context()
    context1["key1"] = "value1"
    context1["shared_key"] = "original_value"

    context2 = Context()
    context2["key2"] = "value2"
    context2["shared_key"] = "modified_value"

    # Get deep diff from context1 to context2
    diff_result = context1.deep_diff(context2)

    # Should contain additions, modifications, and removals
    assert "added" in diff_result
    assert "modified" in diff_result
    assert "removed" in diff_result

    assert diff_result["added"] == {"key2": "value2"}
    assert diff_result["modified"] == {
        "shared_key": {"old": "original_value", "new": "modified_value"}
    }
    assert diff_result["removed"] == {"key1": "value1"}


def _create_nested_dict_contexts() -> tuple[Context, Context]:
    """Helper function to create contexts with nested dict changes."""
    context1 = Context()
    context1["nested"] = {
        "level1": {
            "unchanged": "same",
            "modified": "old_value",
            "removed": "to_be_removed",
        },
        "top_level": "unchanged",
    }

    context2 = Context()
    context2["nested"] = {
        "level1": {"unchanged": "same", "modified": "new_value", "added": "new_item"},
        "top_level": "unchanged",
    }

    return context1, context2


def _verify_top_level_changes(diff_result: dict[str, Any]) -> dict[str, Any]:
    """Helper function to verify top-level changes."""
    assert diff_result["added"] == {}
    assert diff_result["removed"] == {}
    assert "nested" in diff_result["modified"]

    nested_diff = diff_result["modified"]["nested"]
    assert "old" in nested_diff
    assert "new" in nested_diff
    assert "deep_changes" in nested_diff
    return dict(nested_diff["deep_changes"])


def _verify_level1_changes(deep_changes: dict[str, Any]) -> None:
    """Helper function to verify level1 changes."""
    assert deep_changes["added"] == {}
    assert "level1" in deep_changes["modified"]
    assert deep_changes["removed"] == {}

    level1_changes = deep_changes["modified"]["level1"]["deep_changes"]
    assert level1_changes["added"] == {"added": "new_item"}
    assert level1_changes["modified"] == {
        "modified": {"old": "old_value", "new": "new_value"}
    }
    assert level1_changes["removed"] == {"removed": "to_be_removed"}


def _verify_nested_dict_changes(diff_result: dict[str, Any]) -> None:
    """Helper function to verify nested dict changes."""
    deep_changes = _verify_top_level_changes(diff_result)
    _verify_level1_changes(deep_changes)


def test_deep_diff_nested_dict_changes() -> None:
    """Test deep_diff with nested dictionary changes."""
    context1, context2 = _create_nested_dict_contexts()
    diff_result = context1.deep_diff(context2)
    _verify_nested_dict_changes(diff_result)


def test_deep_diff_nested_list_changes() -> None:
    """Test deep_diff with nested list changes."""
    context1 = Context()
    context1["list_data"] = [
        {"id": 1, "name": "item1", "data": "original"},
        {"id": 2, "name": "item2", "data": "unchanged"},
    ]

    context2 = Context()
    context2["list_data"] = [
        {"id": 1, "name": "item1", "data": "modified"},
        {"id": 3, "name": "item3", "data": "new"},
    ]

    diff_result = context1.deep_diff(context2)

    # Should detect list structure changes
    assert "list_data" in diff_result["modified"]
    list_diff = diff_result["modified"]["list_data"]
    assert "old" in list_diff
    assert "new" in list_diff
    assert "deep_changes" in list_diff


def test_deep_diff_identical_contexts() -> None:
    """Test deep_diff with identical contexts."""
    context1 = Context()
    context1["simple"] = "value"
    context1["nested"] = {"inner": {"deep": "value"}}

    context2 = Context()
    context2["simple"] = "value"
    context2["nested"] = {"inner": {"deep": "value"}}

    diff_result = context1.deep_diff(context2)

    # Should have no differences
    assert diff_result["added"] == {}
    assert diff_result["modified"] == {}
    assert diff_result["removed"] == {}


def test_deep_diff_complex_nested_structures() -> None:
    """Test deep_diff with complex nested structures."""
    context1 = Context()
    context1["complex"] = {
        "users": [
            {"name": "alice", "age": 30, "settings": {"theme": "dark"}},
            {"name": "bob", "age": 25, "settings": {"theme": "light"}},
        ],
        "config": {
            "database": {"host": "localhost", "port": 5432},
            "cache": {"enabled": True, "ttl": 300},
        },
    }

    context2 = Context()
    context2["complex"] = {
        "users": [
            {"name": "alice", "age": 31, "settings": {"theme": "dark"}},
            {"name": "charlie", "age": 28, "settings": {"theme": "auto"}},
        ],
        "config": {
            "database": {"host": "remote", "port": 5432},
            "cache": {"enabled": False, "ttl": 600},
        },
    }

    diff_result = context1.deep_diff(context2)

    # Should detect deep nested changes
    assert "complex" in diff_result["modified"]
    complex_diff = diff_result["modified"]["complex"]
    assert "deep_changes" in complex_diff


def test_deep_diff_with_none_values() -> None:
    """Test deep_diff with None values in nested structures."""
    context1 = Context()
    context1["data"] = {"nullable": None, "nested": {"inner": None, "value": "text"}}

    context2 = Context()
    context2["data"] = {
        "nullable": "not_null_anymore",
        "nested": {"inner": "now_has_value", "value": None},
    }

    diff_result = context1.deep_diff(context2)

    # Should handle None values properly
    assert "data" in diff_result["modified"]
    data_diff = diff_result["modified"]["data"]
    assert "deep_changes" in data_diff


def test_deep_diff_preserves_original_contexts() -> None:
    """Test that deep_diff does not modify the original contexts."""
    context1 = Context()
    context1["nested"] = {"inner": {"value": "original"}}

    context2 = Context()
    context2["nested"] = {"inner": {"value": "modified"}}

    # Store original states
    original_value1 = context1["nested"]["inner"]["value"]
    original_value2 = context2["nested"]["inner"]["value"]

    # Get deep diff
    context1.deep_diff(context2)

    # Contexts should be unchanged
    assert context1["nested"]["inner"]["value"] == original_value1
    assert context2["nested"]["inner"]["value"] == original_value2


def test_deep_diff_returns_proper_structure() -> None:
    """Test that deep_diff returns the expected data structure."""
    context1 = Context()
    context2 = Context()

    diff_result = context1.deep_diff(context2)

    # Should be a dictionary with three required keys
    assert isinstance(diff_result, dict)
    assert "added" in diff_result
    assert "modified" in diff_result
    assert "removed" in diff_result

    # Each section should be a dictionary
    assert isinstance(diff_result["added"], dict)
    assert isinstance(diff_result["modified"], dict)
    assert isinstance(diff_result["removed"], dict)


def test_deep_diff_with_mixed_types() -> None:
    """Test deep_diff with mixed data types."""
    context1 = Context()
    context1["mixed"] = {
        "string": "text",
        "number": 42,
        "boolean": True,
        "list": [1, 2, 3],
        "dict": {"key": "value"},
    }

    context2 = Context()
    context2["mixed"] = {
        "string": "changed_text",
        "number": 42,
        "boolean": False,
        "list": [1, 2, 4],
        "dict": {"key": "new_value"},
    }

    diff_result = context1.deep_diff(context2)

    # Should handle mixed types properly
    assert "mixed" in diff_result["modified"]
    mixed_diff = diff_result["modified"]["mixed"]
    assert "deep_changes" in mixed_diff


def test_deep_diff_max_depth_limit() -> None:
    """Test deep_diff with maximum depth limitation."""
    # Create deeply nested structure
    deep_nested: dict[str, Any] = {"level": 1}
    current = deep_nested
    for i in range(2, 15):  # Create 14 levels deep
        current["next"] = {"level": i}
        current = current["next"]

    context1 = Context()
    context1["deep"] = deep_nested

    context2 = Context()
    context2["deep"] = {"level": 999}

    # Should handle deep nesting without infinite recursion
    diff_result = context1.deep_diff(context2, max_depth=5)

    assert "deep" in diff_result["modified"]


def test_deep_diff_circular_reference_protection() -> None:
    """Test deep_diff handles circular references safely."""
    context1 = Context()
    circular1: dict[str, Any] = {"name": "circular"}
    circular1["self"] = circular1
    context1["circular"] = circular1

    context2 = Context()
    circular2: dict[str, Any] = {"name": "different"}
    circular2["self"] = circular2
    context2["circular"] = circular2

    # Should handle circular references without infinite recursion
    diff_result = context1.deep_diff(context2)

    assert "circular" in diff_result["modified"]


def test_deep_diff_with_custom_objects() -> None:
    """Test deep_diff with custom objects."""

    class CustomObj:
        def __init__(self, value: str) -> None:
            super().__init__()
            self.value = value

        def __eq__(self, other: object) -> bool:
            return isinstance(other, CustomObj) and self.value == other.value

    context1 = Context()
    context1["custom"] = {"obj": CustomObj("original")}

    context2 = Context()
    context2["custom"] = {"obj": CustomObj("modified")}

    diff_result = context1.deep_diff(context2)

    # Should handle custom objects
    assert "custom" in diff_result["modified"]
