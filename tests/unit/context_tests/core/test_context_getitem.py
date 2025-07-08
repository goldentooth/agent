"""Tests for Context.__getitem__ method."""

from typing import Any

import pytest

from context.frame import ContextFrame
from context.main import Context


class TestContextGetitem:
    """Test suite for Context.__getitem__ method."""

    def test_getitem_basic_functionality(self) -> None:
        """Test basic __getitem__ functionality."""

        context = Context()
        context.frames[0]["key1"] = "value1"

        result = context["key1"]
        assert result == "value1"

    def test_getitem_raises_keyerror_for_missing_key(self) -> None:
        """Test __getitem__ raises KeyError when key not found."""

        context = Context()

        with pytest.raises(KeyError, match="Context key 'nonexistent' not found"):
            _ = context["nonexistent"]

    def test_getitem_searches_frames_in_reverse_order(self) -> None:
        """Test __getitem__ searches frames from top to bottom (reverse order)."""

        frame1 = ContextFrame()
        frame1["key"] = "frame1_value"
        frame2 = ContextFrame()
        frame2["key"] = "frame2_value"
        frame3 = ContextFrame()
        frame3["key"] = "frame3_value"

        context = Context(frames=[frame1, frame2, frame3])

        # Should return value from the last frame (frame3)
        result = context["key"]
        assert result == "frame3_value"

    def test_getitem_finds_key_in_earlier_frame(self) -> None:
        """Test __getitem__ finds key in earlier frame when not in later frames."""

        frame1 = ContextFrame()
        frame1["key1"] = "value1"
        frame1["key2"] = "value2"
        frame2 = ContextFrame()
        frame2["key2"] = "overridden_value2"
        frame3 = ContextFrame()
        # frame3 doesn't have either key

        context = Context(frames=[frame1, frame2, frame3])

        # key1 only in frame1
        assert context["key1"] == "value1"
        # key2 in frame1 and frame2, should get frame2's value
        assert context["key2"] == "overridden_value2"

    def test_getitem_with_multiple_frame_layers(self) -> None:
        """Test __getitem__ with multiple frame layers and various key distributions."""

        frame1 = ContextFrame()
        frame1["base"] = "base_value"
        frame1["shared"] = "frame1_shared"

        frame2 = ContextFrame()
        frame2["middle"] = "middle_value"
        frame2["shared"] = "frame2_shared"

        frame3 = ContextFrame()
        frame3["top"] = "top_value"

        context = Context(frames=[frame1, frame2, frame3])

        assert context["base"] == "base_value"  # Only in frame1
        assert context["middle"] == "middle_value"  # Only in frame2
        assert context["top"] == "top_value"  # Only in frame3
        assert context["shared"] == "frame2_shared"  # In frame1 and frame2, frame2 wins

    def test_getitem_with_different_value_types(self) -> None:
        """Test __getitem__ with different value types."""

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
                assert context[key] is expected
            else:
                assert context[key] == expected

    def test_getitem_computed_properties_take_precedence(self) -> None:
        """Test __getitem__ checks computed properties before frames."""

        context = Context()
        context.frames[0]["key"] = "frame_value"

        # Add a computed property with same key
        def compute_func(ctx: Any) -> str:
            return "computed_value"

        from context.main import ComputedProperty

        context._computed_properties["key"] = ComputedProperty(compute_func)

        # Should return computed value, not frame value
        result = context["key"]
        assert result == "computed_value"

    def test_getitem_computed_property_only(self) -> None:
        """Test __getitem__ with computed property that has no frame equivalent."""

        context = Context()

        def compute_func(ctx: Any) -> int:
            return 100

        from context.main import ComputedProperty

        context._computed_properties["computed_key"] = ComputedProperty(compute_func)

        result = context["computed_key"]
        assert result == 100

    def test_getitem_preserves_type_information(self) -> None:
        """Test __getitem__ preserves type information."""

        context = Context()
        context.frames[0]["typed_value"] = "string_value"

        result = context["typed_value"]
        assert result == "string_value"
        assert isinstance(result, str)

    def test_getitem_with_empty_context_raises_keyerror(self) -> None:
        """Test __getitem__ with completely empty context raises KeyError."""

        context = Context()

        with pytest.raises(KeyError, match="Context key 'any_key' not found"):
            _ = context["any_key"]

    def test_getitem_key_case_sensitivity(self) -> None:
        """Test __getitem__ is case sensitive for keys."""

        context = Context()
        context.frames[0]["Key"] = "value1"
        context.frames[0]["key"] = "value2"
        context.frames[0]["KEY"] = "value3"

        assert context["Key"] == "value1"
        assert context["key"] == "value2"
        assert context["KEY"] == "value3"

        with pytest.raises(KeyError, match="Context key 'kEy' not found"):
            _ = context["kEy"]

    def test_getitem_with_complex_nested_data(self) -> None:
        """Test __getitem__ with complex nested data structures."""

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

        result = context["data"]
        assert result == complex_data
        assert result is complex_data  # Should be same object reference

    def test_getitem_performance_with_many_frames(self) -> None:
        """Test __getitem__ performance with many frames."""

        frames: list[ContextFrame] = []
        for i in range(100):
            frame = ContextFrame()
            frame[f"key_{i}"] = f"value_{i}"
            frames.append(frame)

        context = Context(frames=frames)

        # Test getting keys from various frame positions
        assert context["key_0"] == "value_0"  # First frame
        assert context["key_50"] == "value_50"  # Middle frame
        assert context["key_99"] == "value_99"  # Last frame

        with pytest.raises(KeyError, match="Context key 'nonexistent' not found"):
            _ = context["nonexistent"]

    def test_getitem_with_frame_modifications_after_creation(self) -> None:
        """Test __getitem__ behavior when frames are modified after context creation."""

        frame1 = ContextFrame()
        frame1["original"] = "value"

        context = Context(frames=[frame1])

        # Verify original value
        assert context["original"] == "value"

        # Modify the frame
        frame1["new_key"] = "new_value"
        frame1["original"] = "modified_value"

        # Context should see the modifications
        assert context["new_key"] == "new_value"
        assert context["original"] == "modified_value"

    def test_getitem_computed_property_caching_behavior(self) -> None:
        """Test __getitem__ behavior with computed property caching."""

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
        result1 = context["computed"]
        assert result1 == 10
        assert call_count == 1

        # Second call should use cache
        result2 = context["computed"]
        assert result2 == 10
        assert call_count == 1  # Should not increment

    def test_getitem_none_values_retrieved_successfully(self) -> None:
        """Test __getitem__ can retrieve None values without error."""

        context = Context()
        context.frames[0]["explicit_none"] = None

        # Key with None value should return None (not raise KeyError)
        result_none = context["explicit_none"]
        assert result_none is None

    def test_getitem_error_message_format(self) -> None:
        """Test __getitem__ error message format is correct."""

        context = Context()

        with pytest.raises(KeyError) as exc_info:
            _ = context["test_key"]

        error_message = str(exc_info.value)
        assert "Context key 'test_key' not found" in error_message

    def test_getitem_vs_get_behavior_difference(self) -> None:
        """Test __getitem__ raises KeyError while get returns None/default."""

        context = Context()

        # get method returns None for missing keys
        assert context.get("missing") is None
        assert context.get("missing", "default") == "default"

        # __getitem__ raises KeyError for missing keys
        with pytest.raises(KeyError, match="Context key 'missing' not found"):
            _ = context["missing"]

    def test_getitem_supports_dict_like_access_patterns(self) -> None:
        """Test __getitem__ supports standard dict-like access patterns."""

        context = Context()
        context.frames[0]["key1"] = "value1"
        context.frames[0]["key2"] = "value2"

        # Direct access
        assert context["key1"] == "value1"

        # Access in expressions
        result = f"The value is: {context['key1']}"
        assert result == "The value is: value1"

        # Access in conditional
        if context["key2"] == "value2":
            assert True
        else:
            assert False, "Should not reach here"

    def test_getitem_with_special_key_characters(self) -> None:
        """Test __getitem__ with special characters in keys."""

        context = Context()
        special_keys = {
            "key with spaces": "value1",
            "key_with_underscores": "value2",
            "key-with-dashes": "value3",
            "key.with.dots": "value4",
            "key123": "value5",
            "123key": "value6",
            "": "empty_key_value",  # Empty string key
        }

        # Set all special keys
        for key, value in special_keys.items():
            context.frames[0][key] = value

        # Verify all special keys can be retrieved
        for key, expected in special_keys.items():
            assert context[key] == expected

    def test_getitem_thread_safety_simulation(self) -> None:
        """Test __getitem__ behavior under simulated concurrent access."""

        context = Context()

        # Simulate concurrent modifications and reads
        for i in range(50):
            context.frames[0][f"key_{i}"] = f"value_{i}"

            # Read immediately after write
            assert context[f"key_{i}"] == f"value_{i}"

        # Verify all keys are still accessible
        for i in range(50):
            assert context[f"key_{i}"] == f"value_{i}"
