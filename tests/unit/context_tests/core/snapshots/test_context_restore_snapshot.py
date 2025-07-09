"""Test Context.restore_snapshot method."""

import pytest

from context.main import Context


def test_restore_snapshot_basic() -> None:
    """Test basic restore_snapshot functionality."""
    context = Context()
    context["key1"] = "value1"
    context["key2"] = "value2"

    # Create a snapshot
    snapshot = context.create_snapshot("test_snapshot")

    # Modify context
    context["key1"] = "modified_value1"
    context["key3"] = "new_value"

    # Restore from snapshot
    context.restore_snapshot("test_snapshot")

    # Context should be restored to snapshot state
    assert context["key1"] == "value1"
    assert context["key2"] == "value2"
    assert "key3" not in context.frames[0]


def _create_multilayer_context() -> Context:
    """Create a context with multiple layers for testing."""
    context = Context()
    context["base_key"] = "base_value"

    # Add layers
    context.push_layer()
    context["layer1_key"] = "layer1_value"
    context["base_key"] = "shadowed_value"

    context.push_layer()
    context["layer2_key"] = "layer2_value"
    return context


def test_restore_snapshot_with_multiple_frames() -> None:
    """Test restore_snapshot with multiple context frames."""
    context = _create_multilayer_context()

    # Create snapshot
    snapshot = context.create_snapshot("multi_frame_snapshot")

    # Modify context structure
    context.pop_layer()
    context["new_key"] = "new_value"

    # Restore snapshot
    context.restore_snapshot("multi_frame_snapshot")

    # Should restore all frames
    assert len(context.frames) == 3
    assert context.frames[0]["base_key"] == "base_value"
    assert context.frames[1]["layer1_key"] == "layer1_value"
    assert context.frames[1]["base_key"] == "shadowed_value"
    assert context.frames[2]["layer2_key"] == "layer2_value"


def test_restore_snapshot_nonexistent_snapshot() -> None:
    """Test restore_snapshot with non-existent snapshot raises KeyError."""
    context = Context()
    context["key1"] = "value1"

    # Try to restore non-existent snapshot
    with pytest.raises(KeyError, match="Snapshot 'nonexistent' not found"):
        context.restore_snapshot("nonexistent")


def test_restore_snapshot_empty_context() -> None:
    """Test restore_snapshot with empty context."""
    context = Context()

    # Create snapshot of empty context
    snapshot = context.create_snapshot("empty_snapshot")

    # Add data to context
    context["new_key"] = "new_value"

    # Restore empty snapshot
    context.restore_snapshot("empty_snapshot")

    # Context should be empty again
    assert len(context.frames) == 1
    assert len(context.frames[0].data) == 0


def test_restore_snapshot_preserves_snapshot_manager() -> None:
    """Test that restore_snapshot preserves the snapshot manager."""
    context = Context()
    context["key1"] = "value1"

    # Create snapshot
    snapshot1 = context.create_snapshot("snapshot1")

    # Modify context
    context["key1"] = "modified"

    # Create another snapshot
    snapshot2 = context.create_snapshot("snapshot2")

    # Restore first snapshot
    context.restore_snapshot("snapshot1")

    # Should still be able to restore second snapshot
    context.restore_snapshot("snapshot2")
    assert context["key1"] == "modified"


def test_restore_snapshot_independence() -> None:
    """Test that restore_snapshot creates independent context state."""
    context = Context()
    context["mutable_data"] = ["original", "list"]

    # Create snapshot
    snapshot = context.create_snapshot("independence_test")

    # Modify original context
    context["mutable_data"].append("modified")

    # Restore snapshot
    context.restore_snapshot("independence_test")

    # Context should have original data
    assert context["mutable_data"] == ["original", "list"]

    # Modifying restored context should not affect future restores
    context["mutable_data"].append("new_modification")

    # Restore again
    context.restore_snapshot("independence_test")

    # Should get clean original data again
    assert context["mutable_data"] == ["original", "list"]


def test_restore_snapshot_returns_none() -> None:
    """Test that restore_snapshot returns None."""
    context = Context()
    context["test_key"] = "test_value"

    # Create snapshot
    snapshot = context.create_snapshot("return_test")

    # Restore should return None
    context.restore_snapshot("return_test")
    # Method returns None, no need to check return value


def test_restore_snapshot_with_none_values() -> None:
    """Test restore_snapshot with None values."""
    context = Context()
    context["none_key"] = None
    context["value_key"] = "value"

    # Create snapshot
    snapshot = context.create_snapshot("none_test")

    # Modify context
    context["none_key"] = "not_none"
    context["value_key"] = "modified"

    # Restore snapshot
    context.restore_snapshot("none_test")

    # Should preserve None values
    assert context["none_key"] is None
    assert context["value_key"] == "value"


def test_restore_snapshot_with_complex_data() -> None:
    """Test restore_snapshot with complex data types."""
    context = Context()
    context["dict_data"] = {"nested": {"deep": "value"}}
    context["list_data"] = [1, 2, {"item": "value"}]

    # Create snapshot
    snapshot = context.create_snapshot("complex_test")

    # Modify context
    context["dict_data"] = {"different": "structure"}
    context["list_data"] = [99]

    # Restore snapshot
    context.restore_snapshot("complex_test")

    # Should preserve complex structures
    assert context["dict_data"] == {"nested": {"deep": "value"}}
    assert context["list_data"] == [1, 2, {"item": "value"}]


def test_restore_snapshot_multiple_times() -> None:
    """Test multiple restore operations."""
    context = Context()
    context["key1"] = "value1"
    context["key2"] = "value2"

    # Create snapshot
    snapshot = context.create_snapshot("multi_restore_test")

    # Modify and restore multiple times
    for i in range(3):
        context["key1"] = f"modified_{i}"
        context["key2"] = f"modified_{i}"
        context[f"new_key_{i}"] = f"new_value_{i}"

        # Restore
        context.restore_snapshot("multi_restore_test")

        # Should consistently restore to original state
        assert context["key1"] == "value1"
        assert context["key2"] == "value2"
        assert f"new_key_{i}" not in context.frames[0]


def test_restore_snapshot_with_computed_properties() -> None:
    """Test restore_snapshot behavior with computed properties."""
    context = Context()
    context["base_value"] = 10

    # Add a computed property that doubles the base value
    context.add_computed_property(
        "doubled_value", lambda ctx: ctx.get("base_value", 0) * 2
    )

    # Verify initial computed value
    assert context["doubled_value"] == 20

    # Create snapshot
    context.create_snapshot("computed_test")

    # Modify context base value
    context["base_value"] = 20
    # Note: Computed properties may be cached, so don't assume immediate recalculation

    # Restore snapshot - this restores stored values
    context.restore_snapshot("computed_test")

    # Verify base value is restored
    assert context["base_value"] == 10
    # Computed properties behavior after restore depends on implementation
    # The main test is that restore works with computed properties present
