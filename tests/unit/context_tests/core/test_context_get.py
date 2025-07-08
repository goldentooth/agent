"""Tests for Context.get method."""

from typing import Any, TypeVar

from context.frame import ContextFrame
from context.main import Context

T = TypeVar("T")


class TestContextGet:
    """Test suite for Context.get method."""

    def test_get_basic_functionality(self) -> None:
        """Test basic get functionality."""

        context = Context()
        context.frames[0]["key1"] = "value1"

        result = context.get("key1")
        assert result == "value1"

    def test_get_with_default_value(self) -> None:
        """Test get with default value when key not found."""

        context = Context()

        result = context.get("nonexistent", "default_value")
        assert result == "default_value"

    def test_get_with_none_default(self) -> None:
        """Test get with None as default value."""

        context = Context()

        result = context.get("nonexistent", None)
        assert result is None

    def test_get_without_default_returns_none(self) -> None:
        """Test get without default returns None when key not found."""

        context = Context()

        result = context.get("nonexistent")
        assert result is None

    def test_get_searches_frames_in_reverse_order(self) -> None:
        """Test get searches frames from top to bottom (reverse order)."""

        frame1 = ContextFrame()
        frame1["key"] = "frame1_value"
        frame2 = ContextFrame()
        frame2["key"] = "frame2_value"
        frame3 = ContextFrame()
        frame3["key"] = "frame3_value"

        context = Context(frames=[frame1, frame2, frame3])

        # Should return value from the last frame (frame3)
        result = context.get("key")
        assert result == "frame3_value"

    def test_get_finds_key_in_earlier_frame_if_not_in_later(self) -> None:
        """Test get finds key in earlier frame when not in later frames."""

        frame1 = ContextFrame()
        frame1["key1"] = "value1"
        frame1["key2"] = "value2"
        frame2 = ContextFrame()
        frame2["key2"] = "overridden_value2"
        frame3 = ContextFrame()
        # frame3 doesn't have either key

        context = Context(frames=[frame1, frame2, frame3])

        # key1 only in frame1
        assert context.get("key1") == "value1"
        # key2 in frame1 and frame2, should get frame2's value
        assert context.get("key2") == "overridden_value2"

    def test_get_with_multiple_frame_layers(self) -> None:
        """Test get with multiple frame layers and various key distributions."""

        frame1 = ContextFrame()
        frame1["base"] = "base_value"
        frame1["shared"] = "frame1_shared"

        frame2 = ContextFrame()
        frame2["middle"] = "middle_value"
        frame2["shared"] = "frame2_shared"

        frame3 = ContextFrame()
        frame3["top"] = "top_value"

        context = Context(frames=[frame1, frame2, frame3])

        assert context.get("base") == "base_value"  # Only in frame1
        assert context.get("middle") == "middle_value"  # Only in frame2
        assert context.get("top") == "top_value"  # Only in frame3
        assert (
            context.get("shared") == "frame2_shared"
        )  # In frame1 and frame2, frame2 wins

    def test_get_with_different_value_types(self) -> None:
        """Test get with different value types."""

        context = Context()
        test_values = {
            "string": "text",
            "integer": 42,
            "float": 3.14,
            "boolean": True,
            "none_value": None,
            "list": [1, 2, 3],
            "dict": {"nested": "value"},
            "tuple": (1, 2, 3),
        }

        # Set all values
        for key, value in test_values.items():
            context.frames[0][key] = value

        # Verify all values
        for key, expected in test_values.items():
            if key == "boolean":
                assert context.get(key) is expected
            else:
                assert context.get(key) == expected

    def test_get_computed_properties_take_precedence(self) -> None:
        """Test get checks computed properties before frames."""

        context = Context()
        context.frames[0]["key"] = "frame_value"

        # Add a computed property with same key
        def compute_func(ctx: Any) -> str:
            return "computed_value"

        from context.main import ComputedProperty

        context._computed_properties["key"] = ComputedProperty(compute_func)

        # Should return computed value, not frame value
        result = context.get("key")
        assert result == "computed_value"

    def test_get_computed_property_only(self) -> None:
        """Test get with computed property that has no frame equivalent."""

        context = Context()

        def compute_func(ctx: Any) -> int:
            return 100

        from context.main import ComputedProperty

        context._computed_properties["computed_key"] = ComputedProperty(compute_func)

        result = context.get("computed_key")
        assert result == 100

    def test_get_preserves_type_information(self) -> None:
        """Test get preserves type information for type checking."""

        context = Context()
        context.frames[0]["typed_value"] = "string_value"

        # Test type preservation (this is more for static type checking)
        result: str | None = context.get("typed_value")
        assert result == "string_value"
        assert isinstance(result, str)

    def test_get_with_empty_context(self) -> None:
        """Test get with completely empty context."""

        context = Context()

        result = context.get("any_key")
        assert result is None

        result_with_default = context.get("any_key", "default")
        assert result_with_default == "default"

    def test_get_key_case_sensitivity(self) -> None:
        """Test get is case sensitive for keys."""

        context = Context()
        context.frames[0]["Key"] = "value1"
        context.frames[0]["key"] = "value2"
        context.frames[0]["KEY"] = "value3"

        assert context.get("Key") == "value1"
        assert context.get("key") == "value2"
        assert context.get("KEY") == "value3"
        assert context.get("kEy") is None

    def test_get_with_complex_nested_data(self) -> None:
        """Test get with complex nested data structures."""

        context = Context()
        complex_data = {
            "users": [
                {"id": 1, "name": "Alice", "profile": {"age": 30, "city": "NYC"}},
                {"id": 2, "name": "Bob", "profile": {"age": 25, "city": "LA"}},
            ],
            "settings": {
                "theme": "dark",
                "notifications": {"email": True, "push": False},
            },
        }
        context.frames[0]["data"] = complex_data

        result = context.get("data")
        assert result == complex_data
        assert result is complex_data  # Should be same object reference

    def test_get_default_with_different_types(self) -> None:
        """Test get with different default value types."""

        context = Context()

        assert context.get("missing", "string_default") == "string_default"
        assert context.get("missing", 42) == 42
        assert context.get("missing", [1, 2, 3]) == [1, 2, 3]
        assert context.get("missing", {"key": "value"}) == {"key": "value"}
        assert context.get("missing", None) is None

    def test_get_performance_with_many_frames(self) -> None:
        """Test get performance with many frames."""

        frames: list[ContextFrame] = []
        for i in range(100):
            frame = ContextFrame()
            frame[f"key_{i}"] = f"value_{i}"
            frames.append(frame)

        context = Context(frames=frames)

        # Test getting keys from various frame positions
        assert context.get("key_0") == "value_0"  # First frame
        assert context.get("key_50") == "value_50"  # Middle frame
        assert context.get("key_99") == "value_99"  # Last frame
        assert context.get("nonexistent") is None

    def test_get_with_frame_modifications_after_creation(self) -> None:
        """Test get behavior when frames are modified after context creation."""

        frame1 = ContextFrame()
        frame1["original"] = "value"

        context = Context(frames=[frame1])

        # Verify original value
        assert context.get("original") == "value"

        # Modify the frame
        frame1["new_key"] = "new_value"
        frame1["original"] = "modified_value"

        # Context should see the modifications
        assert context.get("new_key") == "new_value"
        assert context.get("original") == "modified_value"

    def test_get_computed_property_caching_behavior(self) -> None:
        """Test get behavior with computed property caching."""

        context = Context()
        call_count = 0

        def counting_compute(ctx: Any) -> int:
            nonlocal call_count
            call_count += 1
            return call_count * 10

        from context.main import ComputedProperty

        computed_prop = ComputedProperty(counting_compute)
        context._computed_properties["computed"] = computed_prop

        # First call should compute
        result1 = context.get("computed")
        assert result1 == 10
        assert call_count == 1

        # Second call should use cache
        result2 = context.get("computed")
        assert result2 == 10
        assert call_count == 1  # Should not increment

    def test_get_none_values_vs_missing_keys(self) -> None:
        """Test get distinguishes between None values and missing keys."""

        context = Context()
        context.frames[0]["explicit_none"] = None

        # Key with None value should return None
        result_none = context.get("explicit_none")
        assert result_none is None

        # Missing key with default should return default
        result_missing = context.get("missing_key", "default")
        assert result_missing == "default"

        # Missing key without default should return None
        result_missing_no_default = context.get("missing_key")
        assert result_missing_no_default is None
