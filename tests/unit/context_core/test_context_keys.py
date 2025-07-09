"""Test Context.keys() method implementation."""

from __future__ import annotations

import pytest

from context.frame import ContextFrame
from context.main import Context


class TestContextKeys:
    """Test Context.keys() method functionality."""

    def test_keys_empty_context(self) -> None:
        """Test keys() returns empty iterator for empty context."""
        context = Context()
        keys = list(context.keys())
        assert keys == []

    def test_keys_single_frame(self) -> None:
        """Test keys() returns keys from single frame."""
        context = Context()
        context["key1"] = "value1"
        context["key2"] = "value2"

        keys = list(context.keys())
        assert set(keys) == {"key1", "key2"}

    def test_keys_multiple_frames(self) -> None:
        """Test keys() returns unique keys from multiple frames."""
        context = Context()
        context["base_key"] = "base_value"

        context.push_layer()
        context["layer_key"] = "layer_value"

        keys = list(context.keys())
        assert set(keys) == {"base_key", "layer_key"}

    def test_keys_shadowing_unique_keys(self) -> None:
        """Test keys() returns unique keys even with shadowing."""
        context = Context()
        context["shared_key"] = "base_value"

        context.push_layer()
        context["shared_key"] = "layer_value"

        keys = list(context.keys())
        assert keys == ["shared_key"]

    def test_keys_with_computed_properties(self) -> None:
        """Test keys() includes computed properties."""
        context = Context()
        context["regular_key"] = "regular_value"

        # Since add_computed_property is not implemented yet, we'll simulate
        # by directly adding to _computed_properties
        from context.computed import ComputedProperty

        computed_prop = ComputedProperty(lambda ctx: "computed_value")
        context._computed_properties["computed_key"] = computed_prop

        keys = list(context.keys())
        assert set(keys) == {"computed_key", "regular_key"}

    def test_keys_order_computed_first(self) -> None:
        """Test keys() yields computed properties first."""
        context = Context()
        context["frame_key"] = "frame_value"

        from context.computed import ComputedProperty

        computed_prop = ComputedProperty(lambda ctx: "computed_value")
        context._computed_properties["computed_key"] = computed_prop

        keys = list(context.keys())
        assert keys[0] == "computed_key"
        assert keys[1] == "frame_key"

    def test_keys_no_duplicates(self) -> None:
        """Test keys() returns no duplicates."""
        context = Context()
        context["key1"] = "value1"
        context["key2"] = "value2"

        context.push_layer()
        context["key1"] = "shadowed_value"
        context["key3"] = "value3"

        keys = list(context.keys())
        assert len(keys) == 3
        assert set(keys) == {"key1", "key2", "key3"}

    def test_keys_iterator_behavior(self) -> None:
        """Test keys() returns iterator that can be consumed."""
        context = Context()
        context["test_key"] = "test_value"

        keys_iter = context.keys()
        assert next(keys_iter) == "test_key"

        # Iterator should be exhausted
        with pytest.raises(StopIteration):
            next(keys_iter)

    def test_keys_with_multiple_layers(self) -> None:
        """Test keys() with multiple layers and shadowing."""
        context = Context()
        context["base"] = "base_value"

        context.push_layer()
        context["layer1"] = "layer1_value"
        context["base"] = "shadowed_base"

        context.push_layer()
        context["layer2"] = "layer2_value"

        keys = list(context.keys())
        assert set(keys) == {"base", "layer1", "layer2"}

    def test_keys_frame_order(self) -> None:
        """Test keys() processes frames in correct order."""
        context = Context()
        context["first"] = "first_value"

        context.push_layer()
        context["second"] = "second_value"

        context.push_layer()
        context["third"] = "third_value"

        keys = list(context.keys())

        # Keys from later frames should appear first
        assert keys.index("third") < keys.index("second")
        assert keys.index("second") < keys.index("first")

    def test_keys_empty_frames(self) -> None:
        """Test keys() handles empty frames correctly."""
        frame1 = ContextFrame()
        frame2 = ContextFrame()
        frame3 = ContextFrame()

        context = Context([frame1, frame2, frame3])
        keys = list(context.keys())
        assert keys == []

    def test_keys_mixed_empty_and_populated(self) -> None:
        """Test keys() with mix of empty and populated frames."""
        frame1 = ContextFrame()
        frame1["key1"] = "value1"

        frame2 = ContextFrame()  # Empty

        frame3 = ContextFrame()
        frame3["key2"] = "value2"

        context = Context([frame1, frame2, frame3])
        keys = list(context.keys())
        assert set(keys) == {"key1", "key2"}
