"""Test Context.create_snapshot method."""

import pytest

from context.main import Context


def test_create_snapshot_basic():
    """Test basic create_snapshot functionality."""
    context = Context()
    context["key1"] = "value1"
    context["key2"] = "value2"

    # Create a snapshot
    snapshot = context.create_snapshot("test_snapshot")

    # Snapshot should exist and have correct properties
    assert snapshot is not None
    assert snapshot.name == "test_snapshot"
    assert len(snapshot.frames) == 1
    assert snapshot.frames[0]["key1"] == "value1"
    assert snapshot.frames[0]["key2"] == "value2"


def test_create_snapshot_with_multiple_frames():
    """Test create_snapshot with multiple context frames."""
    context = Context()
    context["base_key"] = "base_value"

    # Add layers
    context.push_layer()
    context["layer1_key"] = "layer1_value"
    context["base_key"] = "shadowed_value"

    context.push_layer()
    context["layer2_key"] = "layer2_value"

    # Create snapshot
    snapshot = context.create_snapshot("multi_frame_snapshot")

    # Should capture all frames
    assert len(snapshot.frames) == 3
    assert snapshot.frames[0]["base_key"] == "base_value"
    assert snapshot.frames[1]["layer1_key"] == "layer1_value"
    assert snapshot.frames[1]["base_key"] == "shadowed_value"
    assert snapshot.frames[2]["layer2_key"] == "layer2_value"


def test_create_snapshot_independence():
    """Test that snapshot is independent of original context."""
    context = Context()
    context["mutable_data"] = ["original", "list"]

    # Create snapshot
    snapshot = context.create_snapshot("independence_test")

    # Modify original context
    context["mutable_data"].append("modified")
    context["new_key"] = "new_value"

    # Snapshot should remain unchanged
    assert snapshot.frames[0]["mutable_data"] == ["original", "list"]
    assert "new_key" not in snapshot.frames[0]


def test_create_snapshot_empty_context():
    """Test create_snapshot with empty context."""
    context = Context()

    # Create snapshot of empty context
    snapshot = context.create_snapshot("empty_snapshot")

    # Should have one empty frame
    assert len(snapshot.frames) == 1
    assert len(snapshot.frames[0].data) == 0


def test_create_snapshot_returns_snapshot_object():
    """Test that create_snapshot returns proper ContextSnapshot object."""
    context = Context()
    context["test_key"] = "test_value"

    snapshot = context.create_snapshot("type_test")

    # Should be ContextSnapshot instance
    assert hasattr(snapshot, "name")
    assert hasattr(snapshot, "timestamp")
    assert hasattr(snapshot, "frames")
    assert hasattr(snapshot, "restore_to")


def test_create_snapshot_preserves_original_context():
    """Test that create_snapshot does not modify original context."""
    context = Context()
    context["key1"] = "value1"
    context["key2"] = "value2"

    original_frames_count = len(context.frames)
    original_key1 = context["key1"]

    # Create snapshot
    context.create_snapshot("preservation_test")

    # Original context should be unchanged
    assert len(context.frames) == original_frames_count
    assert context["key1"] == original_key1
    assert context["key2"] == "value2"


def test_create_snapshot_with_none_values():
    """Test create_snapshot with None values."""
    context = Context()
    context["none_key"] = None
    context["value_key"] = "value"

    snapshot = context.create_snapshot("none_test")

    # Should preserve None values
    assert snapshot.frames[0]["none_key"] is None
    assert snapshot.frames[0]["value_key"] == "value"


def test_create_snapshot_with_complex_data():
    """Test create_snapshot with complex data types."""
    context = Context()
    context["dict_data"] = {"nested": {"deep": "value"}}
    context["list_data"] = [1, 2, {"item": "value"}]

    snapshot = context.create_snapshot("complex_test")

    # Should preserve complex structures
    assert snapshot.frames[0]["dict_data"] == {"nested": {"deep": "value"}}
    assert snapshot.frames[0]["list_data"] == [1, 2, {"item": "value"}]


def test_create_snapshot_timestamp():
    """Test that snapshot has a valid timestamp."""
    context = Context()
    context["test_key"] = "test_value"

    import time

    before_time = time.time()
    snapshot = context.create_snapshot("timestamp_test")
    after_time = time.time()

    # Timestamp should be within reasonable range
    assert before_time <= snapshot.timestamp <= after_time


def test_create_snapshot_with_computed_properties():
    """Test create_snapshot behavior with computed properties."""
    context = Context()
    context["base_value"] = 10

    # TODO: This test will be enhanced when computed properties are implemented
    # For now, just verify snapshot creation works
    snapshot = context.create_snapshot("computed_test")

    assert snapshot.frames[0]["base_value"] == 10


def test_create_snapshot_multiple_snapshots():
    """Test creating multiple snapshots with different names."""
    context = Context()
    context["shared_key"] = "shared_value"

    # Create first snapshot
    snapshot1 = context.create_snapshot("snapshot_1")

    # Modify context
    context["new_key"] = "new_value"

    # Create second snapshot
    snapshot2 = context.create_snapshot("snapshot_2")

    # Snapshots should be different
    assert snapshot1.name == "snapshot_1"
    assert snapshot2.name == "snapshot_2"
    assert "new_key" not in snapshot1.frames[0]
    assert snapshot2.frames[0]["new_key"] == "new_value"


def test_create_snapshot_frame_deep_copy():
    """Test that snapshot creates deep copies of frames."""
    context = Context()
    nested_dict = {"level1": {"level2": "value"}}
    context["nested"] = nested_dict

    snapshot = context.create_snapshot("deep_copy_test")

    # Modify original nested structure
    nested_dict["level1"]["level2"] = "modified"
    context["nested"]["level1"]["new_key"] = "new"

    # Snapshot should have original values
    assert snapshot.frames[0]["nested"]["level1"]["level2"] == "value"
    assert "new_key" not in snapshot.frames[0]["nested"]["level1"]
