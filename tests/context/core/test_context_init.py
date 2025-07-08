"""Tests for Context.__init__ method."""

from typing import Any

from context.frame import ContextFrame
from context.main import Context


class TestContextInit:
    """Test suite for Context.__init__ method."""

    def test_init_basic(self) -> None:
        """Test basic Context initialization."""

        context = Context()

        # Should have frames attribute
        assert hasattr(context, "frames")
        assert isinstance(context.frames, list)
        assert len(context.frames) == 1
        assert isinstance(context.frames[0], ContextFrame)

    def test_init_with_default_frame(self) -> None:
        """Test initialization creates default frame when no frames provided."""

        context = Context()

        # Should create a single default frame
        assert len(context.frames) == 1
        assert isinstance(context.frames[0], ContextFrame)
        # Default frame should be empty
        assert len(context.frames[0].data) == 0

    def test_init_with_none_frames(self) -> None:
        """Test initialization with explicit None frames parameter."""

        context = Context(frames=None)

        # Should create a single default frame
        assert len(context.frames) == 1
        assert isinstance(context.frames[0], ContextFrame)

    def test_init_with_provided_frames(self) -> None:
        """Test initialization with provided frames."""

        frame1 = ContextFrame()
        frame1["key1"] = "value1"
        frame2 = ContextFrame()
        frame2["key2"] = "value2"
        frames = [frame1, frame2]

        context = Context(frames=frames)

        # Should use provided frames
        assert len(context.frames) == 2
        assert context.frames[0] is frame1
        assert context.frames[1] is frame2

    def test_init_with_single_frame(self) -> None:
        """Test initialization with single provided frame."""

        frame = ContextFrame()
        frame["test"] = "data"
        context = Context(frames=[frame])

        assert len(context.frames) == 1
        assert context.frames[0] is frame
        assert context.frames[0]["test"] == "data"

    def test_init_with_empty_frames_list(self) -> None:
        """Test initialization with empty frames list."""

        context = Context(frames=[])

        # Should create default frame since empty list provided
        assert len(context.frames) == 1
        assert isinstance(context.frames[0], ContextFrame)

    def test_init_computed_properties_dict(self) -> None:
        """Test initialization creates computed properties dict."""

        context = Context()

        assert hasattr(context, "_computed_properties")
        assert isinstance(context._computed_properties, dict)
        assert len(context._computed_properties) == 0

    def test_init_transformations_dict(self) -> None:
        """Test initialization creates transformations dict."""

        context = Context()

        assert hasattr(context, "_transformations")
        assert isinstance(context._transformations, dict)
        assert len(context._transformations) == 0

    def test_init_snapshot_manager(self) -> None:
        """Test initialization creates snapshot manager."""

        context = Context()

        assert hasattr(context, "_snapshot_manager")
        # Should be a SnapshotManager instance
        from context.snapshot_manager import SnapshotManager

        assert isinstance(context._snapshot_manager, SnapshotManager)

    def test_init_multiple_contexts_independent(self) -> None:
        """Test that multiple contexts are independent."""

        context1 = Context()
        context2 = Context()

        # Should have different frames lists
        assert context1.frames is not context2.frames

        # Should have different computed properties dicts
        assert context1._computed_properties is not context2._computed_properties

        # Should have different transformations dicts
        assert context1._transformations is not context2._transformations

        # Should have different snapshot managers
        assert context1._snapshot_manager is not context2._snapshot_manager

    def test_init_frames_reference_preservation(self) -> None:
        """Test that provided frames list reference is preserved."""

        frame1 = ContextFrame()
        frame1["a"] = 1
        frame2 = ContextFrame()
        frame2["b"] = 2
        frames = [frame1, frame2]
        context = Context(frames=frames)

        # Should use the exact same list object
        assert context.frames is frames

        # Modifications to original list should affect context
        frame3 = ContextFrame()
        frame3["c"] = 3
        frames.append(frame3)
        assert len(context.frames) == 3

    def test_init_with_complex_frame_data(self) -> None:
        """Test initialization with frames containing complex data."""

        complex_data = {
            "string": "value",
            "number": 42,
            "float": 3.14,
            "boolean": True,
            "none": None,
            "list": [1, 2, 3],
            "dict": {"nested": "data"},
            "tuple": (1, 2, 3),
        }

        frame = ContextFrame()
        for key, value in complex_data.items():
            frame[key] = value
        context = Context(frames=[frame])

        assert len(context.frames) == 1
        assert context.frames[0] is frame
        # Verify all data is preserved
        for key, value in complex_data.items():
            assert context.frames[0][key] == value
