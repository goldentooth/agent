"""Tests for ContextSnapshot.restore_to method."""

from typing import Any

from context.main import ContextSnapshot


class MockFrame:
    """Mock ContextFrame for testing."""

    def __init__(self, data: dict[str, str] | None = None) -> None:
        super().__init__()
        self.data = data or {}

    def copy(self) -> "MockFrame":
        """Create a copy of this frame."""
        return MockFrame(self.data.copy())

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MockFrame):
            return False
        return self.data == other.data


class MockContext:
    """Mock Context class for testing purposes."""

    def __init__(self, data: dict[str, str] | None = None) -> None:
        super().__init__()
        self.data = data or {}
        self.frames: list[MockFrame] = []
        self._computed_properties: dict[str, Any] = {}
        self._transformations: dict[str, list[Any]] = {}
        self._dependency_graph: dict[str, Any] = {}
        self._sync_events: dict[str, Any] = {}
        self._async_events: dict[str, Any] = {}

    def clear(self) -> None:
        """Clear all context state for testing."""
        self.frames.clear()
        self._computed_properties.clear()
        self._transformations.clear()
        self._dependency_graph.clear()
        self._sync_events.clear()
        self._async_events.clear()

    def add_computed_property(
        self, key: str, func: Any, dependencies: set[str]
    ) -> None:
        """Mock method to add computed property."""
        self._computed_properties[key] = {"func": func, "dependencies": dependencies}

    def add_transformation(self, key: str, func: Any) -> None:
        """Mock method to add transformation."""
        if key not in self._transformations:
            self._transformations[key] = []
        self._transformations[key].append(func)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MockContext):
            return False
        return self.data == other.data


class MockComputedProperty:
    """Mock computed property for testing."""

    def __init__(self, func: Any, dependencies: set[str] | None = None) -> None:
        super().__init__()
        self.func = func
        self.dependencies = dependencies or set()


class MockTransformation:
    """Mock transformation for testing."""

    def __init__(self, func: Any) -> None:
        super().__init__()
        self.func = func


class TestContextSnapshotRestoreTo:
    """Test suite for ContextSnapshot.restore_to method."""

    def test_restore_to_basic(self) -> None:
        """Test basic snapshot restoration functionality."""
        # Create source context with data
        source_context = MockContext({"original": "data"})
        source_context.frames = [MockFrame({"frame": "data"})]

        # Create snapshot
        snapshot = ContextSnapshot(source_context, "test_snapshot")

        # Create target context with different data
        target_context = MockContext({"different": "data"})
        target_context.frames = [MockFrame({"other": "frame"})]

        # Restore snapshot to target
        snapshot.restore_to(target_context)

        # Target should now have source's frame data
        assert len(target_context.frames) == 1
        assert target_context.frames[0].data == {"frame": "data"}

    def test_restore_to_clears_existing_state(self) -> None:
        """Test that restore_to clears existing context state."""
        # Create source context and snapshot
        source_context = MockContext({"source": "data"})
        snapshot = ContextSnapshot(source_context, "clear_test")

        # Create target context with existing state
        target_context = MockContext({"target": "data"})
        target_context.frames = [MockFrame({"existing": "frame"})]
        target_context._computed_properties = {
            "existing": {"func": lambda: "test", "dependencies": set()}
        }
        target_context._transformations = {"existing": [lambda x: x]}
        target_context._dependency_graph = {"existing": "data"}
        target_context._sync_events = {"existing": "event"}
        target_context._async_events = {"existing": "async_event"}

        # Restore snapshot
        snapshot.restore_to(target_context)

        # Verify all existing state cleared
        assert len(target_context.frames) == 0  # Source had no frames
        collections_to_check = [
            target_context._computed_properties,
            target_context._transformations,
            target_context._dependency_graph,
            target_context._sync_events,
            target_context._async_events,
        ]
        assert all(len(collection) == 0 for collection in collections_to_check)

    def test_restore_to_with_frames(self) -> None:
        """Test restoring snapshot with multiple frames."""
        # Create source context with multiple frames
        source_context = MockContext({"source": "data"})
        source_context.frames = [
            MockFrame({"frame1": "data1"}),
            MockFrame({"frame2": "data2"}),
            MockFrame({"frame3": "data3"}),
        ]

        # Create snapshot
        snapshot = ContextSnapshot(source_context, "frames_test")

        # Create target context
        target_context = MockContext({"target": "data"})

        # Restore snapshot
        snapshot.restore_to(target_context)

        # Target should have all frames from source
        assert len(target_context.frames) == 3
        assert target_context.frames[0].data == {"frame1": "data1"}
        assert target_context.frames[1].data == {"frame2": "data2"}
        assert target_context.frames[2].data == {"frame3": "data3"}

        # Frames should be copies, not references
        assert target_context.frames[0] is not source_context.frames[0]
        assert target_context.frames[1] is not source_context.frames[1]
        assert target_context.frames[2] is not source_context.frames[2]

    def test_restore_to_with_computed_properties(self) -> None:
        """Test restoring snapshot with computed properties."""
        # Create source context with computed properties
        source_context = MockContext({"source": "data"})

        def compute_func1() -> str:
            return "computed1"

        def compute_func2() -> str:
            return "computed2"

        # Setup computed properties and create snapshot
        props = {
            "prop1": MockComputedProperty(compute_func1, {"dep1", "dep2"}),
            "prop2": MockComputedProperty(compute_func2, {"dep3"}),
        }
        source_context._computed_properties = props
        snapshot = ContextSnapshot(source_context, "computed_test")

        # Create target context, restore, and verify
        target_context = MockContext({"target": "data"})
        snapshot.restore_to(target_context)
        props_data = target_context._computed_properties
        assert len(props_data) == 2 and list(props_data.keys()) == ["prop1", "prop2"]
        assert props_data["prop1"]["func"] is compute_func1 and props_data["prop1"][
            "dependencies"
        ] == {"dep1", "dep2"}
        assert props_data["prop2"]["func"] is compute_func2 and props_data["prop2"][
            "dependencies"
        ] == {"dep3"}

    def test_restore_to_with_transformations(self) -> None:
        """Test restoring snapshot with transformations."""
        # Create source context with transformations
        source_context = MockContext({"source": "data"})

        def transform1(x: Any) -> Any:
            return x.upper()

        def transform2(x: Any) -> Any:
            return x.lower()

        # Setup transformations and create snapshot
        trans1, trans2 = MockTransformation(transform1), MockTransformation(transform2)
        source_context._transformations = {"key1": [trans1], "key2": [trans1, trans2]}
        snapshot = ContextSnapshot(source_context, "transform_test")

        # Create target context and restore
        target_context = MockContext({"target": "data"})
        snapshot.restore_to(target_context)

        # Verify transformations structure
        expected_structure = {"key1": 1, "key2": 2}  # key -> length mapping
        actual_structure = {
            k: len(v) for k, v in target_context._transformations.items()
        }
        assert (
            len(target_context._transformations) == 2
            and actual_structure == expected_structure
        )

        # Verify function references
        transforms = target_context._transformations
        assert transforms["key1"][0] is transform1 and transforms["key2"] == [
            transform1,
            transform2,
        ]

    def test_restore_to_empty_snapshot(self) -> None:
        """Test restoring empty snapshot clears target context."""
        # Create empty source context
        source_context = MockContext()

        # Create snapshot
        snapshot = ContextSnapshot(source_context, "empty_test")

        # Create target context with existing state
        target_context = MockContext({"target": "data"})
        target_context.frames = [MockFrame({"existing": "data"})]
        target_context._computed_properties = {
            "existing": {"func": lambda: "test", "dependencies": set()}
        }
        target_context._transformations = {"existing": [lambda x: x]}

        # Restore snapshot
        snapshot.restore_to(target_context)

        # Target should be empty
        assert len(target_context.frames) == 0
        assert len(target_context._computed_properties) == 0
        assert len(target_context._transformations) == 0

    def test_restore_to_returns_none(self) -> None:
        """Test that restore_to returns None."""
        source_context = MockContext({"source": "data"})
        snapshot = ContextSnapshot(source_context, "return_test")
        target_context = MockContext({"target": "data"})

        snapshot.restore_to(target_context)

    def test_restore_to_preserves_snapshot_state(self) -> None:
        """Test that restore_to does not modify the snapshot."""
        # Create source context
        source_context = MockContext({"source": "data"})
        source_context.frames = [MockFrame({"original": "frame"})]

        # Create snapshot
        snapshot = ContextSnapshot(source_context, "preserve_test")
        original_frames = snapshot.frames.copy()
        original_computed = snapshot.computed_properties.copy()
        original_transforms = snapshot.transformations.copy()

        # Create target context
        target_context = MockContext({"target": "data"})

        # Restore snapshot
        snapshot.restore_to(target_context)

        # Snapshot should be unchanged
        assert snapshot.frames == original_frames
        assert snapshot.computed_properties == original_computed
        assert snapshot.transformations == original_transforms

    def test_restore_to_handles_missing_attributes(self) -> None:
        """Test restore_to handles contexts with missing attributes gracefully."""
        # Create minimal source context
        source_context = MockContext({"source": "data"})

        # Create snapshot
        snapshot = ContextSnapshot(source_context, "missing_attrs_test")

        # Create target context without some attributes
        target_context = MockContext({"target": "data"})
        delattr(target_context, "_dependency_graph")
        delattr(target_context, "_sync_events")
        delattr(target_context, "_async_events")

        # Restore should work without errors
        snapshot.restore_to(target_context)

        # Basic state should be restored
        assert len(target_context.frames) == 0
        assert len(target_context._computed_properties) == 0
        assert len(target_context._transformations) == 0

    def test_restore_to_complex_snapshot(self) -> None:
        """Test restoring complex snapshot with all components."""
        # Create complex source context
        source_context = MockContext({"complex": "data"})
        source_context.frames = [
            MockFrame({"frame1": "data1"}),
            MockFrame({"frame2": "data2"}),
        ]

        def compute_func() -> str:
            return "computed"

        def transform_func(x: Any) -> Any:
            return x

        # Setup source context properties and create snapshot
        source_context._computed_properties = {
            "computed": MockComputedProperty(compute_func, {"dependency"})
        }
        source_context._transformations = {
            "transform": [MockTransformation(transform_func)]
        }
        snapshot = ContextSnapshot(source_context, "complex_test")

        # Create target context, restore, and verify all components
        target_context = MockContext({"target": "data"})
        snapshot.restore_to(target_context)
        expected_frame_data = [{"frame1": "data1"}, {"frame2": "data2"}]
        actual_frame_data = [frame.data for frame in target_context.frames]
        assert (
            len(target_context.frames) == 2 and actual_frame_data == expected_frame_data
        )
        assert (
            len(target_context._computed_properties) == 1
            and "computed" in target_context._computed_properties
            and len(target_context._transformations) == 1
            and "transform" in target_context._transformations
        )

    def test_restore_to_multiple_restorations(self) -> None:
        """Test multiple restorations work correctly."""
        # Create source context
        source_context = MockContext({"source": "data"})
        source_context.frames = [MockFrame({"consistent": "data"})]

        # Create snapshot
        snapshot = ContextSnapshot(source_context, "multiple_test")

        # Create multiple target contexts
        target1 = MockContext({"target1": "data"})
        target2 = MockContext({"target2": "data"})
        target3 = MockContext({"target3": "data"})

        # Restore to all targets
        snapshot.restore_to(target1)
        snapshot.restore_to(target2)
        snapshot.restore_to(target3)

        # All targets should have same restored state
        for target in [target1, target2, target3]:
            assert len(target.frames) == 1
            assert target.frames[0].data == {"consistent": "data"}

    def test_restore_to_independence(self) -> None:
        """Test that restored contexts are independent from snapshot and each other."""
        # Create source context
        source_context = MockContext({"source": "data"})
        source_context.frames = [MockFrame({"original": "data"})]

        # Create snapshot
        snapshot = ContextSnapshot(source_context, "independence_test")

        # Create target contexts
        target1 = MockContext({"target1": "data"})
        target2 = MockContext({"target2": "data"})

        # Restore to both targets
        snapshot.restore_to(target1)
        snapshot.restore_to(target2)

        # Modify one target's frames
        target1.frames[0].data["modified"] = "by_target1"

        # Other target and snapshot should be unaffected
        assert "modified" not in target2.frames[0].data
        assert "modified" not in snapshot.frames[0].data
        assert target2.frames[0].data == {"original": "data"}
        assert snapshot.frames[0].data == {"original": "data"}
