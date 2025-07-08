"""Test Context.get_snapshots method."""

from context.main import Context, ContextSnapshot


def test_get_snapshots_empty() -> None:
    """Test get_snapshots with no snapshots returns empty dict."""
    context = Context()

    snapshots = context.get_snapshots()

    assert snapshots == {}
    assert isinstance(snapshots, dict)


def test_get_snapshots_single_snapshot() -> None:
    """Test get_snapshots with single snapshot."""
    context = Context()
    context["key1"] = "value1"

    # Create snapshot
    created_snapshot = context.create_snapshot("test_snapshot")

    # Get snapshots
    snapshots = context.get_snapshots()

    assert len(snapshots) == 1
    assert "test_snapshot" in snapshots
    assert isinstance(snapshots["test_snapshot"], ContextSnapshot)
    assert snapshots["test_snapshot"].name == "test_snapshot"
    assert snapshots["test_snapshot"].timestamp == created_snapshot.timestamp


def test_get_snapshots_multiple_snapshots() -> None:
    """Test get_snapshots with multiple snapshots."""
    context = Context()
    context["key1"] = "value1"

    # Create first snapshot
    snapshot1 = context.create_snapshot("snapshot1")

    # Modify context
    context["key2"] = "value2"

    # Create second snapshot
    snapshot2 = context.create_snapshot("snapshot2")

    # Get snapshots
    snapshots = context.get_snapshots()

    assert len(snapshots) == 2
    assert "snapshot1" in snapshots
    assert "snapshot2" in snapshots
    assert snapshots["snapshot1"].name == "snapshot1"
    assert snapshots["snapshot2"].name == "snapshot2"
    assert snapshots["snapshot1"].timestamp == snapshot1.timestamp
    assert snapshots["snapshot2"].timestamp == snapshot2.timestamp


def test_get_snapshots_returns_snapshot_objects() -> None:
    """Test get_snapshots returns ContextSnapshot objects."""
    context = Context()
    context["test_key"] = "test_value"

    # Create snapshot
    context.create_snapshot("test_snapshot")

    # Get snapshots
    snapshots = context.get_snapshots()

    snapshot = snapshots["test_snapshot"]
    assert isinstance(snapshot, ContextSnapshot)
    assert hasattr(snapshot, "name")
    assert hasattr(snapshot, "timestamp")
    assert hasattr(snapshot, "frames")
    assert snapshot.name == "test_snapshot"


def test_get_snapshots_vs_list_snapshots() -> None:
    """Test get_snapshots vs list_snapshots return different types."""
    context = Context()
    context["key1"] = "value1"

    # Create snapshot
    context.create_snapshot("test_snapshot")

    # Get snapshots using both methods
    snapshots = context.get_snapshots()
    snapshot_list = context.list_snapshots()

    # list_snapshots returns dict[str, float]
    assert isinstance(snapshot_list["test_snapshot"], float)

    # get_snapshots returns dict[str, ContextSnapshot]
    assert isinstance(snapshots["test_snapshot"], ContextSnapshot)
    assert snapshots["test_snapshot"].timestamp == snapshot_list["test_snapshot"]


def test_get_snapshots_independence() -> None:
    """Test that get_snapshots returns independent dict."""
    context = Context()
    context["key1"] = "value1"

    # Create snapshot
    context.create_snapshot("test_snapshot")

    # Get snapshots multiple times
    snapshots1 = context.get_snapshots()
    snapshots2 = context.get_snapshots()

    # Should be independent objects
    assert snapshots1 is not snapshots2
    assert len(snapshots1) == len(snapshots2)
    assert "test_snapshot" in snapshots1
    assert "test_snapshot" in snapshots2

    # Modifying one should not affect the other
    # Create a dummy ContextSnapshot for testing independence
    dummy_snapshot = ContextSnapshot(context, "dummy")
    snapshots1["new_key"] = dummy_snapshot
    assert "new_key" not in snapshots2


def test_get_snapshots_with_complex_data() -> None:
    """Test get_snapshots with complex context data."""
    context = Context()

    # Add complex data
    context["string"] = "test"
    context["number"] = 42
    context["list"] = [1, 2, 3]
    context["dict"] = {"nested": "value"}

    # Create snapshot
    context.create_snapshot("complex_snapshot")

    # Get snapshots
    snapshots = context.get_snapshots()

    snapshot = snapshots["complex_snapshot"]
    assert snapshot.name == "complex_snapshot"
    assert isinstance(snapshot.frames, list)
    assert len(snapshot.frames) == 1

    # Verify frame contains the data
    frame = snapshot.frames[0]
    assert frame["string"] == "test" and frame["number"] == 42
    assert frame["list"] == [1, 2, 3] and frame["dict"] == {"nested": "value"}


def test_get_snapshots_with_layers() -> None:
    """Test get_snapshots with multiple context layers."""
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
    context.create_snapshot("layers_snapshot")

    # Get snapshots
    snapshots = context.get_snapshots()

    snapshot = snapshots["layers_snapshot"]
    assert len(snapshot.frames) == 3

    # Verify frames contain the layered data
    assert snapshot.frames[0]["base"] == "base_value"
    assert snapshot.frames[1]["layer1"] == "layer1_value"
    assert snapshot.frames[2]["layer2"] == "layer2_value"


def test_get_snapshots_after_deletion() -> None:
    """Test get_snapshots after deleting snapshots."""
    context = Context()
    context["key1"] = "value1"

    # Create multiple snapshots
    context.create_snapshot("keep_me")
    context.create_snapshot("delete_me")

    # Delete one snapshot
    context.delete_snapshot("delete_me")

    # Get snapshots
    snapshots = context.get_snapshots()

    assert len(snapshots) == 1
    assert "keep_me" in snapshots
    assert "delete_me" not in snapshots


def test_get_snapshots_after_restore() -> None:
    """Test get_snapshots after restoring snapshot."""
    context = Context()
    context["key1"] = "original"

    # Create snapshot
    context.create_snapshot("restore_test")

    # Modify context
    context["key1"] = "modified"

    # Get snapshots before restore
    snapshots_before = context.get_snapshots()

    # Restore snapshot
    context.restore_snapshot("restore_test")

    # Get snapshots after restore
    snapshots_after = context.get_snapshots()

    # Should be the same snapshots
    assert len(snapshots_before) == len(snapshots_after)
    assert "restore_test" in snapshots_after
    assert snapshots_after["restore_test"].name == "restore_test"


def test_get_snapshots_empty_context() -> None:
    """Test get_snapshots with empty context snapshot."""
    context = Context()

    # Create snapshot of empty context
    context.create_snapshot("empty_snapshot")

    # Get snapshots
    snapshots = context.get_snapshots()

    assert len(snapshots) == 1
    snapshot = snapshots["empty_snapshot"]
    assert snapshot.name == "empty_snapshot"
    assert len(snapshot.frames) == 1
    assert len(snapshot.frames[0].data) == 0


def test_get_snapshots_with_special_names() -> None:
    """Test get_snapshots with various snapshot names."""
    context = Context()
    context["key1"] = "value1"

    # Create snapshots with different name formats
    names = ["simple", "with_underscore", "with-dash", "with123numbers"]

    for name in names:
        context.create_snapshot(name)

    # Get snapshots
    snapshots = context.get_snapshots()

    assert len(snapshots) == len(names)
    for name in names:
        assert name in snapshots
        assert isinstance(snapshots[name], ContextSnapshot)
        assert snapshots[name].name == name


def test_get_snapshots_preserves_snapshot_data() -> None:
    """Test that get_snapshots preserves all snapshot data."""
    context = Context()
    context["key1"] = "value1"

    # Create snapshot
    original_snapshot = context.create_snapshot("data_test")

    # Get snapshots
    snapshots = context.get_snapshots()
    retrieved_snapshot = snapshots["data_test"]

    # Verify all data is preserved
    assert retrieved_snapshot.name == original_snapshot.name
    assert retrieved_snapshot.timestamp == original_snapshot.timestamp
    assert retrieved_snapshot.context_id == original_snapshot.context_id
    assert len(retrieved_snapshot.frames) == len(original_snapshot.frames)

    # Verify frame data is preserved
    for i, frame in enumerate(retrieved_snapshot.frames):
        assert frame.data == original_snapshot.frames[i].data
