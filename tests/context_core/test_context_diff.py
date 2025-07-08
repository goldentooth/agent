"""Test Context.diff method."""

import pytest

from context.main import Context


def test_diff_basic() -> None:
    """Test basic diff functionality."""
    context1 = Context()
    context1["key1"] = "value1"
    context1["shared_key"] = "original_value"

    context2 = Context()
    context2["key2"] = "value2"
    context2["shared_key"] = "modified_value"

    # Get diff from context1 to context2
    diff_result = context1.diff(context2)

    # Should contain additions, modifications, and removals
    assert "added" in diff_result
    assert "modified" in diff_result
    assert "removed" in diff_result

    assert diff_result["added"] == {"key2": "value2"}
    assert diff_result["modified"] == {
        "shared_key": {"old": "original_value", "new": "modified_value"}
    }
    assert diff_result["removed"] == {"key1": "value1"}


def test_diff_identical_contexts() -> None:
    """Test diff with identical contexts."""
    context1 = Context()
    context1["key1"] = "value1"
    context1["key2"] = "value2"

    context2 = Context()
    context2["key1"] = "value1"
    context2["key2"] = "value2"

    # Get diff
    diff_result = context1.diff(context2)

    # Should have no differences
    assert diff_result["added"] == {}
    assert diff_result["modified"] == {}
    assert diff_result["removed"] == {}


def test_diff_empty_contexts() -> None:
    """Test diff with empty contexts."""
    context1 = Context()
    context2 = Context()

    # Get diff
    diff_result = context1.diff(context2)

    # Should have no differences
    assert diff_result["added"] == {}
    assert diff_result["modified"] == {}
    assert diff_result["removed"] == {}


def test_diff_one_empty_context() -> None:
    """Test diff where one context is empty."""
    context1 = Context()
    context1["key1"] = "value1"
    context1["key2"] = "value2"

    context2 = Context()

    # Diff from populated to empty
    diff_result = context1.diff(context2)

    assert diff_result["added"] == {}
    assert diff_result["modified"] == {}
    assert diff_result["removed"] == {"key1": "value1", "key2": "value2"}

    # Diff from empty to populated
    diff_result = context2.diff(context1)

    assert diff_result["added"] == {"key1": "value1", "key2": "value2"}
    assert diff_result["modified"] == {}
    assert diff_result["removed"] == {}


def test_diff_with_none_values() -> None:
    """Test diff with None values."""
    context1 = Context()
    context1["none_key"] = None
    context1["value_key"] = "value"

    context2 = Context()
    context2["none_key"] = "changed_from_none"
    context2["value_key"] = None

    # Get diff
    diff_result = context1.diff(context2)

    assert diff_result["added"] == {}
    assert diff_result["modified"] == {
        "none_key": {"old": None, "new": "changed_from_none"},
        "value_key": {"old": "value", "new": None},
    }
    assert diff_result["removed"] == {}


def test_diff_with_complex_data_types() -> None:
    """Test diff with complex data types."""
    context1 = Context()
    context1["list_key"] = ["original", "list"]
    context1["dict_key"] = {"original": "dict"}

    context2 = Context()
    context2["list_key"] = ["modified", "list"]
    context2["dict_key"] = {"modified": "dict"}

    # Get diff
    diff_result = context1.diff(context2)

    assert diff_result["added"] == {}
    assert diff_result["modified"] == {
        "list_key": {"old": ["original", "list"], "new": ["modified", "list"]},
        "dict_key": {"old": {"original": "dict"}, "new": {"modified": "dict"}},
    }
    assert diff_result["removed"] == {}


def test_diff_with_multiple_frames() -> None:
    """Test diff with contexts that have multiple frames."""
    context1 = Context()
    context1["base_key"] = "base_value"
    context1.push_layer()
    context1["layer_key"] = "layer_value"
    context1["base_key"] = "shadowed_value"

    context2 = Context()
    context2["base_key"] = "different_base"
    context2.push_layer()
    context2["layer_key"] = "different_layer"
    context2["base_key"] = "different_shadowed"

    # Get diff
    diff_result = context1.diff(context2)

    # Should compare the effective values (top-level access)
    assert diff_result["added"] == {}
    assert diff_result["modified"] == {
        "base_key": {"old": "shadowed_value", "new": "different_shadowed"},
        "layer_key": {"old": "layer_value", "new": "different_layer"},
    }
    assert diff_result["removed"] == {}


def test_diff_preserves_original_contexts() -> None:
    """Test that diff does not modify the original contexts."""
    context1 = Context()
    context1["key1"] = "value1"

    context2 = Context()
    context2["key2"] = "value2"

    # Store original states
    original_context1_keys = set(context1.get(key, None) for key in ["key1"])
    original_context2_keys = set(context2.get(key, None) for key in ["key2"])

    # Get diff
    context1.diff(context2)

    # Contexts should be unchanged
    assert context1.get("key1") == "value1"
    assert context2.get("key2") == "value2"

    # No new keys should have been added
    with pytest.raises(KeyError):
        _ = context1["key2"]
    with pytest.raises(KeyError):
        _ = context2["key1"]


def test_diff_returns_proper_structure() -> None:
    """Test that diff returns the expected data structure."""
    context1 = Context()
    context2 = Context()

    diff_result = context1.diff(context2)

    # Should be a dictionary with three required keys
    assert isinstance(diff_result, dict)
    assert "added" in diff_result
    assert "modified" in diff_result
    assert "removed" in diff_result

    # Each section should be a dictionary
    assert isinstance(diff_result["added"], dict)
    assert isinstance(diff_result["modified"], dict)
    assert isinstance(diff_result["removed"], dict)


def test_diff_asymmetric() -> None:
    """Test that diff is asymmetric (order matters)."""
    context1 = Context()
    context1["key1"] = "value1"

    context2 = Context()
    context2["key2"] = "value2"

    # Diff from context1 to context2
    diff_1_to_2 = context1.diff(context2)

    # Diff from context2 to context1
    diff_2_to_1 = context2.diff(context1)

    # Should be inverses of each other
    assert diff_1_to_2["added"] == diff_2_to_1["removed"]
    assert diff_1_to_2["removed"] == diff_2_to_1["added"]

    # Both should have empty modified since no shared keys
    assert diff_1_to_2["modified"] == {}
    assert diff_2_to_1["modified"] == {}


def test_diff_only_additions() -> None:
    """Test diff when only additions are present."""
    context1 = Context()
    context1["existing_key"] = "existing_value"

    context2 = Context()
    context2["existing_key"] = "existing_value"
    context2["new_key"] = "new_value"

    diff_result = context1.diff(context2)

    assert diff_result["added"] == {"new_key": "new_value"}
    assert diff_result["modified"] == {}
    assert diff_result["removed"] == {}


def test_diff_only_removals() -> None:
    """Test diff when only removals are present."""
    context1 = Context()
    context1["existing_key"] = "existing_value"
    context1["removed_key"] = "removed_value"

    context2 = Context()
    context2["existing_key"] = "existing_value"

    diff_result = context1.diff(context2)

    assert diff_result["added"] == {}
    assert diff_result["modified"] == {}
    assert diff_result["removed"] == {"removed_key": "removed_value"}


def test_diff_only_modifications() -> None:
    """Test diff when only modifications are present."""
    context1 = Context()
    context1["modified_key"] = "original_value"
    context1["unchanged_key"] = "same_value"

    context2 = Context()
    context2["modified_key"] = "new_value"
    context2["unchanged_key"] = "same_value"

    diff_result = context1.diff(context2)

    assert diff_result["added"] == {}
    assert diff_result["modified"] == {
        "modified_key": {"old": "original_value", "new": "new_value"}
    }
    assert diff_result["removed"] == {}
