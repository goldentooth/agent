"""Test Context.delete_snapshot method."""

import pytest

from context.main import Context


def test_delete_snapshot_basic() -> None:
    """Test basic snapshot deletion."""
    context = Context()
    context["key1"] = "value1"

    # Create snapshot
    context.create_snapshot("test_snapshot")

    # Verify snapshot exists
    snapshots_before = context.list_snapshots()
    assert "test_snapshot" in snapshots_before

    # Delete snapshot
    context.delete_snapshot("test_snapshot")

    # Verify snapshot is deleted
    snapshots_after = context.list_snapshots()
    assert "test_snapshot" not in snapshots_after
    assert len(snapshots_after) == 0


def test_delete_snapshot_nonexistent_raises_error() -> None:
    """Test that deleting non-existent snapshot raises KeyError."""
    context = Context()

    # Try to delete non-existent snapshot
    with pytest.raises(KeyError, match="Snapshot 'nonexistent' not found"):
        context.delete_snapshot("nonexistent")


def test_delete_snapshot_with_multiple_snapshots() -> None:
    """Test deleting one snapshot leaves others intact."""
    context = Context()
    context["key1"] = "value1"

    # Create multiple snapshots
    snapshot1 = context.create_snapshot("snapshot1")
    context["key2"] = "value2"
    snapshot2 = context.create_snapshot("snapshot2")
    context["key3"] = "value3"
    snapshot3 = context.create_snapshot("snapshot3")

    # Delete middle snapshot
    context.delete_snapshot("snapshot2")

    # Verify only snapshot2 is deleted
    snapshots = context.list_snapshots()
    assert len(snapshots) == 2
    assert (
        "snapshot1" in snapshots
        and "snapshot2" not in snapshots
        and "snapshot3" in snapshots
    )
    assert snapshots["snapshot1"] == snapshot1.timestamp
    assert snapshots["snapshot3"] == snapshot3.timestamp


def test_delete_snapshot_and_recreate() -> None:
    """Test deleting snapshot and recreating with same name."""
    context = Context()
    context["key1"] = "value1"

    # Create snapshot
    original_snapshot = context.create_snapshot("test_snapshot")
    original_timestamp = original_snapshot.timestamp

    # Delete snapshot
    context.delete_snapshot("test_snapshot")

    # Verify it's gone
    assert "test_snapshot" not in context.list_snapshots()

    # Recreate with same name
    context["key2"] = "value2"
    new_snapshot = context.create_snapshot("test_snapshot")

    # Verify new snapshot exists and has different timestamp
    snapshots = context.list_snapshots()
    assert "test_snapshot" in snapshots
    assert snapshots["test_snapshot"] == new_snapshot.timestamp
    assert new_snapshot.timestamp != original_timestamp


def test_delete_snapshot_error_message_format() -> None:
    """Test that error message follows expected format."""
    context = Context()

    # Test with various snapshot names
    test_names = ["simple", "with_underscore", "with-dash", "with123", "UPPERCASE"]

    for name in test_names:
        with pytest.raises(KeyError) as exc_info:
            context.delete_snapshot(name)

        assert f"Snapshot '{name}' not found" in str(exc_info.value)


def test_delete_snapshot_after_restore() -> None:
    """Test deleting snapshot after restoring from it."""
    context = Context()
    context["key1"] = "original"

    # Create snapshot
    context.create_snapshot("restore_test")

    # Modify context
    context["key1"] = "modified"

    # Restore snapshot
    context.restore_snapshot("restore_test")

    # Verify restoration worked
    assert context["key1"] == "original"

    # Delete the snapshot
    context.delete_snapshot("restore_test")

    # Verify snapshot is deleted
    assert "restore_test" not in context.list_snapshots()

    # Verify context state remains as restored
    assert context["key1"] == "original"


def test_delete_snapshot_with_complex_context() -> None:
    """Test deleting snapshot with complex context data."""
    context = Context()

    # Add complex data
    context["string"] = "test"
    context["number"] = 42
    context["list"] = [1, 2, 3]
    context["dict"] = {"nested": "value"}
    context["none"] = None

    # Create snapshot
    context.create_snapshot("complex_test")

    # Verify snapshot exists
    assert "complex_test" in context.list_snapshots()

    # Delete snapshot
    context.delete_snapshot("complex_test")

    # Verify snapshot is deleted
    assert "complex_test" not in context.list_snapshots()

    # Verify context data is unchanged
    assert context["string"] == "test" and context["number"] == 42
    assert context["list"] == [1, 2, 3] and context["dict"] == {"nested": "value"}
    assert context["none"] is None


def test_delete_snapshot_with_layers() -> None:
    """Test deleting snapshot with multiple context layers."""
    context = Context()

    # Add data to base layer
    context["base"] = "base_value"

    # Push layer and add more data
    context.push_layer()
    context["layer1"] = "layer1_value"

    # Push another layer
    context.push_layer()
    context["layer2"] = "layer2_value"

    # Create snapshot
    context.create_snapshot("layers_test")

    # Verify snapshot exists
    assert "layers_test" in context.list_snapshots()

    # Delete snapshot
    context.delete_snapshot("layers_test")

    # Verify snapshot is deleted
    assert "layers_test" not in context.list_snapshots()

    # Verify context layers remain intact
    assert context["base"] == "base_value"
    assert context["layer1"] == "layer1_value"
    assert context["layer2"] == "layer2_value"


def test_delete_snapshot_return_type() -> None:
    """Test that delete_snapshot returns None."""
    context = Context()
    context["key1"] = "value1"

    # Create snapshot
    context.create_snapshot("return_test")

    # Delete snapshot - method returns None
    context.delete_snapshot("return_test")

    # Verify snapshot is deleted
    assert "return_test" not in context.list_snapshots()


def test_delete_snapshot_empty_context() -> None:
    """Test deleting snapshot from empty context."""
    context = Context()

    # Create snapshot of empty context
    context.create_snapshot("empty_test")

    # Delete snapshot
    context.delete_snapshot("empty_test")

    # Verify snapshot is deleted
    assert "empty_test" not in context.list_snapshots()


def test_delete_snapshot_with_special_characters() -> None:
    """Test deleting snapshots with special characters in names."""
    context = Context()
    context["key1"] = "value1"

    # Test various special characters
    special_names = [
        "test space",
        "test.dot",
        "test@symbol",
        "test#hash",
        "test$dollar",
        "test%percent",
        "test^caret",
        "test&ampersand",
        "test*star",
        "test(paren)",
        "test[bracket]",
        "test{brace}",
        "test|pipe",
        "test\\backslash",
        "test/slash",
        "test:colon",
        "test;semicolon",
        'test"quote',
        "test'apostrophe",
        "test<less>",
        "test=equals",
        "test+plus",
        "test~tilde",
        "test`backtick",
    ]

    for name in special_names:
        # Create snapshot
        context.create_snapshot(name)

        # Verify it exists
        assert name in context.list_snapshots()

        # Delete snapshot
        context.delete_snapshot(name)

        # Verify it's deleted
        assert name not in context.list_snapshots()
