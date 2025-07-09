"""Test Context.list_snapshots method."""

from context.main import Context


def test_list_snapshots_empty() -> None:
    """Test list_snapshots with no snapshots returns empty dict."""
    context = Context()

    snapshots = context.list_snapshots()

    assert snapshots == {}
    assert isinstance(snapshots, dict)


def test_list_snapshots_single_snapshot() -> None:
    """Test list_snapshots with single snapshot."""
    context = Context()
    context["key1"] = "value1"

    # Create snapshot
    snapshot = context.create_snapshot("test_snapshot")

    # List snapshots
    snapshots = context.list_snapshots()

    assert len(snapshots) == 1
    assert "test_snapshot" in snapshots
    assert isinstance(snapshots["test_snapshot"], float)
    assert snapshots["test_snapshot"] == snapshot.timestamp


def test_list_snapshots_multiple_snapshots() -> None:
    """Test list_snapshots with multiple snapshots."""
    context = Context()
    context["key1"] = "value1"

    # Create first snapshot
    snapshot1 = context.create_snapshot("snapshot1")

    # Modify context
    context["key2"] = "value2"

    # Create second snapshot
    snapshot2 = context.create_snapshot("snapshot2")

    # List snapshots
    snapshots = context.list_snapshots()

    assert len(snapshots) == 2
    assert "snapshot1" in snapshots
    assert "snapshot2" in snapshots
    assert snapshots["snapshot1"] == snapshot1.timestamp
    assert snapshots["snapshot2"] == snapshot2.timestamp


def test_list_snapshots_return_type() -> None:
    """Test list_snapshots returns dict[str, float]."""
    context = Context()
    context["test_key"] = "test_value"

    # Create snapshot
    snapshot = context.create_snapshot("type_test")

    # List snapshots
    snapshots = context.list_snapshots()

    # Check return type
    assert isinstance(snapshots, dict)
    assert isinstance(list(snapshots.keys())[0], str)
    assert isinstance(list(snapshots.values())[0], float)


def test_list_snapshots_after_restore() -> None:
    """Test list_snapshots after restoring snapshot."""
    context = Context()
    context["key1"] = "value1"

    # Create snapshot
    snapshot = context.create_snapshot("restore_test")

    # Modify context
    context["key1"] = "modified"

    # List snapshots before restore
    snapshots_before = context.list_snapshots()

    # Restore snapshot
    context.restore_snapshot("restore_test")

    # List snapshots after restore
    snapshots_after = context.list_snapshots()

    # Should be the same
    assert snapshots_before == snapshots_after
    assert "restore_test" in snapshots_after


def test_list_snapshots_independence() -> None:
    """Test that list_snapshots returns independent dict."""
    context = Context()
    context["key1"] = "value1"

    # Create snapshot
    snapshot = context.create_snapshot("independence_test")

    # Get snapshots list
    snapshots1 = context.list_snapshots()
    snapshots2 = context.list_snapshots()

    # Should be independent objects
    assert snapshots1 is not snapshots2
    assert snapshots1 == snapshots2

    # Modifying one should not affect the other
    snapshots1["new_key"] = 123.0
    assert "new_key" not in snapshots2


def test_list_snapshots_with_empty_context() -> None:
    """Test list_snapshots with empty context snapshot."""
    context = Context()

    # Create snapshot of empty context
    snapshot = context.create_snapshot("empty_test")

    # List snapshots
    snapshots = context.list_snapshots()

    assert len(snapshots) == 1
    assert "empty_test" in snapshots
    assert snapshots["empty_test"] == snapshot.timestamp


def test_list_snapshots_timestamp_order() -> None:
    """Test that timestamps reflect creation order."""
    context = Context()
    context["key1"] = "value1"

    # Create first snapshot
    snapshot1 = context.create_snapshot("first")

    # Small delay to ensure different timestamps
    import time

    time.sleep(0.01)

    # Create second snapshot
    snapshot2 = context.create_snapshot("second")

    # List snapshots
    snapshots = context.list_snapshots()

    # Second snapshot should have later timestamp
    assert snapshots["second"] > snapshots["first"]
    assert snapshots["first"] == snapshot1.timestamp
    assert snapshots["second"] == snapshot2.timestamp


def test_list_snapshots_with_complex_names() -> None:
    """Test list_snapshots with various snapshot names."""
    context = Context()
    context["key1"] = "value1"

    # Create snapshots with different name formats
    names = ["simple", "with_underscore", "with-dash", "with123numbers", "UPPERCASE"]

    for name in names:
        context.create_snapshot(name)

    # List snapshots
    snapshots = context.list_snapshots()

    assert len(snapshots) == len(names)
    for name in names:
        assert name in snapshots
        assert isinstance(snapshots[name], float)


def test_list_snapshots_after_deletion() -> None:
    """Test list_snapshots after deleting snapshots."""
    context = Context()
    context["key1"] = "value1"

    # Create multiple snapshots
    snapshot1 = context.create_snapshot("keep_me")
    snapshot2 = context.create_snapshot("delete_me")

    # Delete one snapshot
    context._snapshot_manager.delete_snapshot("delete_me")

    # List snapshots
    snapshots = context.list_snapshots()

    assert len(snapshots) == 1
    assert "keep_me" in snapshots
    assert "delete_me" not in snapshots
    assert snapshots["keep_me"] == snapshot1.timestamp
