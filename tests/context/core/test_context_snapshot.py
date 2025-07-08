"""Tests for ContextSnapshot.__init__ method."""

import time
from typing import Any

from context.main import ContextSnapshot


class MockContext:
    """Mock Context class for testing purposes."""

    def __init__(self, data: dict[str, str] | None = None) -> None:
        super().__init__()
        self.data = data or {}
        self.frames: list[MockFrame] = []
        self._computed_properties: dict[str, object] = {}
        self._transformations: dict[str, object] = {}

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MockContext):
            return False
        return self.data == other.data


class MockFrame:
    """Mock ContextFrame for testing."""

    def __init__(self, data: dict[str, str] | None = None) -> None:
        super().__init__()
        self.data = data or {}

    def copy(self) -> "MockFrame":
        """Create a copy of this frame."""
        return MockFrame(self.data.copy())


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


class TestContextSnapshotInit:
    """Test suite for ContextSnapshot.__init__ method."""

    def test_context_snapshot_init_basic(self) -> None:
        """Test basic ContextSnapshot initialization."""
        context = MockContext({"key": "value"})
        name = "test_snapshot"

        # Create snapshot
        snapshot = ContextSnapshot(context, name)

        # Verify basic attributes
        assert snapshot.name == name
        assert isinstance(snapshot.timestamp, float)
        assert snapshot.context_id == id(context)

    def test_context_snapshot_init_with_frames(self) -> None:
        """Test ContextSnapshot initialization with frames."""
        context = MockContext({"key": "value"})
        frame1 = MockFrame({"frame1": "data1"})
        frame2 = MockFrame({"frame2": "data2"})
        context.frames = [frame1, frame2]
        name = "frames_snapshot"

        # Create snapshot
        snapshot = ContextSnapshot(context, name)

        # Verify frames are copied
        assert len(snapshot.frames) == 2
        assert snapshot.frames[0] is not frame1  # Should be copy, not reference
        assert snapshot.frames[1] is not frame2  # Should be copy, not reference
        assert snapshot.frames[0].data == {"frame1": "data1"}
        assert snapshot.frames[1].data == {"frame2": "data2"}

    def test_context_snapshot_init_without_frames(self) -> None:
        """Test ContextSnapshot initialization without frames attribute."""
        context = MockContext({"key": "value"})
        # Don't set frames attribute
        delattr(context, "frames")
        name = "no_frames_snapshot"

        # Create snapshot
        snapshot = ContextSnapshot(context, name)

        # Should default to empty list
        assert snapshot.frames == []

    def test_context_snapshot_init_with_computed_properties(self) -> None:
        """Test ContextSnapshot initialization with computed properties."""
        context = MockContext({"key": "value"})

        def test_func() -> str:
            return "computed"

        prop1 = MockComputedProperty(test_func, {"dep1", "dep2"})
        prop2 = MockComputedProperty(lambda: "lambda", {"dep3"})
        context._computed_properties = {"prop1": prop1, "prop2": prop2}  # type: ignore[reportPrivateUsage]
        name = "computed_snapshot"

        # Create snapshot
        snapshot = ContextSnapshot(context, name)

        # Verify computed properties are stored
        assert len(snapshot.computed_properties) == 2
        assert "prop1" in snapshot.computed_properties
        assert "prop2" in snapshot.computed_properties
        assert snapshot.computed_properties["prop1"]["func"] is test_func
        assert snapshot.computed_properties["prop1"]["dependencies"] == {"dep1", "dep2"}
        assert snapshot.computed_properties["prop2"]["dependencies"] == {"dep3"}

    def test_context_snapshot_init_without_computed_properties(self) -> None:
        """Test ContextSnapshot initialization without computed properties."""
        context = MockContext({"key": "value"})
        # Don't set _computed_properties attribute
        delattr(context, "_computed_properties")
        name = "no_computed_snapshot"

        # Create snapshot
        snapshot = ContextSnapshot(context, name)

        # Should default to empty dict
        assert snapshot.computed_properties == {}

    def test_context_snapshot_init_with_transformations(self) -> None:
        """Test ContextSnapshot initialization with transformations."""
        context = MockContext({"key": "value"})

        def transform1(x: Any) -> Any:
            return x.upper()

        def transform2(x: Any) -> Any:
            return x.lower()

        trans1, trans2 = MockTransformation(transform1), MockTransformation(transform2)
        context._transformations = {"key1": [trans1], "key2": [trans1, trans2]}  # type: ignore[reportPrivateUsage]

        # Create snapshot
        snapshot = ContextSnapshot(context, "transformations_snapshot")

        # Verify transformations are stored
        assert len(snapshot.transformations) == 2
        assert all(key in snapshot.transformations for key in ["key1", "key2"])
        assert (
            len(snapshot.transformations["key1"]) == 1
            and len(snapshot.transformations["key2"]) == 2
        )
        assert snapshot.transformations["key1"][0] is transform1
        assert all(
            snapshot.transformations["key2"][i] is func
            for i, func in enumerate([transform1, transform2])
        )

    def test_context_snapshot_init_without_transformations(self) -> None:
        """Test ContextSnapshot initialization without transformations."""
        context = MockContext({"key": "value"})
        # Don't set _transformations attribute
        delattr(context, "_transformations")
        name = "no_transformations_snapshot"

        # Create snapshot
        snapshot = ContextSnapshot(context, name)

        # Should default to empty dict
        assert snapshot.transformations == {}

    def test_context_snapshot_init_timestamp_uniqueness(self) -> None:
        """Test that snapshots have unique timestamps."""
        context = MockContext({"key": "value"})

        # Create snapshots with small delay
        snapshot1 = ContextSnapshot(context, "snapshot1")
        time.sleep(0.001)  # Small delay to ensure different timestamps
        snapshot2 = ContextSnapshot(context, "snapshot2")

        # Timestamps should be different
        assert snapshot1.timestamp != snapshot2.timestamp
        assert snapshot2.timestamp > snapshot1.timestamp

    def test_context_snapshot_init_context_id_preservation(self) -> None:
        """Test that context ID is correctly preserved."""
        context1 = MockContext({"key1": "value1"})
        context2 = MockContext({"key2": "value2"})

        snapshot1 = ContextSnapshot(context1, "snapshot1")
        snapshot2 = ContextSnapshot(context2, "snapshot2")

        # Context IDs should match their respective contexts
        assert snapshot1.context_id == id(context1)
        assert snapshot2.context_id == id(context2)
        assert snapshot1.context_id != snapshot2.context_id

    def test_context_snapshot_init_name_preservation(self) -> None:
        """Test that snapshot names are correctly preserved."""
        context = MockContext({"key": "value"})
        names = [
            "simple",
            "with_underscore",
            "with-dash",
            "with.dot",
            "with spaces",
            "",
            "123numeric",
        ]

        for name in names:
            snapshot = ContextSnapshot(context, name)
            assert snapshot.name == name

    def test_context_snapshot_init_complex_context(self) -> None:
        """Test ContextSnapshot initialization with complex context."""
        context = MockContext({"complex": "data", "nested": "structure"})

        # Add all components to context
        context.frames = [MockFrame({"frame": "data"})]

        def compute_func() -> str:
            return "result"

        def transform_func(x: Any) -> Any:
            return x

        context._computed_properties = {"computed": MockComputedProperty(compute_func, {"dependency"})}  # type: ignore[reportPrivateUsage]
        context._transformations = {"transform": [MockTransformation(transform_func)]}  # type: ignore[reportPrivateUsage]

        # Create snapshot
        snapshot = ContextSnapshot(context, "complex_snapshot")

        # Verify all components are preserved
        expected_lengths = [1, 1, 1]  # frames, computed_properties, transformations
        actual_lengths = [
            len(snapshot.frames),
            len(snapshot.computed_properties),
            len(snapshot.transformations),
        ]
        assert (
            snapshot.name == "complex_snapshot" and actual_lengths == expected_lengths
        )
        assert snapshot.context_id == id(context) and isinstance(
            snapshot.timestamp, float
        )

    def test_context_snapshot_init_empty_context(self) -> None:
        """Test ContextSnapshot initialization with minimal context."""
        context = MockContext()  # Empty context
        name = "empty_snapshot"

        # Create snapshot
        snapshot = ContextSnapshot(context, name)

        # Verify defaults
        assert snapshot.name == name
        assert snapshot.frames == []
        assert snapshot.computed_properties == {}
        assert snapshot.transformations == {}
        assert snapshot.context_id == id(context)
        assert isinstance(snapshot.timestamp, float)
