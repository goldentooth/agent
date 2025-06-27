"""Basic tests for Context class ensuring backward compatibility."""

from __future__ import annotations

import pytest

from goldentooth_agent.core.context import Context, ContextFrame


class TestContextBasicFunctionality:
    """Test suite for basic Context functionality and backward compatibility."""

    def test_context_initialization(self) -> None:
        """Test Context initializes with default frame."""
        context = Context()
        assert len(context.frames) == 1
        assert isinstance(context.frames[0], ContextFrame)

    def test_context_initialization_with_frames(self) -> None:
        """Test Context initializes with provided frames."""
        frame1 = ContextFrame()
        frame1["key1"] = "value1"

        frame2 = ContextFrame()
        frame2["key2"] = "value2"

        context = Context([frame1, frame2])
        assert len(context.frames) == 2
        assert context["key1"] == "value1"
        assert context["key2"] == "value2"

    def test_basic_get_and_set(self) -> None:
        """Test basic get/set operations."""
        context = Context()

        # Test setting and getting values
        context["test_key"] = "test_value"
        assert context["test_key"] == "test_value"
        assert context.get("test_key") == "test_value"

    def test_get_with_default(self) -> None:
        """Test get() with default values."""
        context = Context()

        # Non-existent key should return default
        assert context.get("nonexistent") is None
        assert context.get("nonexistent", "default") == "default"

        # Existing key should return actual value
        context["existing"] = "value"
        assert context.get("existing", "default") == "value"

    def test_contains_operator(self) -> None:
        """Test __contains__ operator (in keyword)."""
        context = Context()

        assert "test_key" not in context

        context["test_key"] = "test_value"
        assert "test_key" in context

    def test_keyerror_on_missing_key(self) -> None:
        """Test that accessing missing key raises KeyError."""
        context = Context()

        with pytest.raises(KeyError, match="Context key 'missing' not found"):
            _ = context["missing"]

    def test_layer_operations(self) -> None:
        """Test push_layer and pop_layer operations."""
        context = Context()

        # Set value in base layer
        context["base_key"] = "base_value"
        assert len(context.frames) == 1

        # Push new layer
        context.push_layer()
        assert len(context.frames) == 2

        # Value should still be accessible
        assert context["base_key"] == "base_value"

        # Set value in new layer
        context["layer_key"] = "layer_value"
        assert context["layer_key"] == "layer_value"

        # Pop layer
        context.pop_layer()
        assert len(context.frames) == 1
        assert context["base_key"] == "base_value"
        assert "layer_key" not in context

    def test_layer_shadowing(self) -> None:
        """Test that upper layers shadow lower layers."""
        context = Context()

        # Set value in base layer
        context["shared_key"] = "base_value"

        # Push new layer and override
        context.push_layer()
        context["shared_key"] = "layer_value"

        # Should return layer value
        assert context["shared_key"] == "layer_value"

        # Pop layer - should return base value
        context.pop_layer()
        assert context["shared_key"] == "base_value"

    def test_cannot_pop_root_frame(self) -> None:
        """Test that popping the root frame raises error."""
        context = Context()

        with pytest.raises(IndexError, match="Cannot pop root context frame"):
            context.pop_layer()

    def test_fork_creates_independent_copy(self) -> None:
        """Test that fork() creates independent context copy."""
        original = Context()
        original["shared_key"] = "original_value"
        original["unique_key"] = "unique_value"

        forked = original.fork()

        # Forked should have same data initially
        assert forked["shared_key"] == "original_value"
        assert forked["unique_key"] == "unique_value"

        # Changes should be independent
        original["shared_key"] = "modified_original"
        forked["shared_key"] = "modified_forked"

        assert original["shared_key"] == "modified_original"
        assert forked["shared_key"] == "modified_forked"

    def test_merge_combines_contexts(self) -> None:
        """Test that merge() properly combines contexts."""
        context1 = Context()
        context1["key1"] = "value1"
        context1["shared"] = "context1_value"

        context2 = Context()
        context2["key2"] = "value2"
        context2["shared"] = "context2_value"

        merged = context1.merge(context2)

        # Should have keys from both contexts
        assert merged["key1"] == "value1"
        assert merged["key2"] == "value2"

        # Second context should override shared keys
        assert merged["shared"] == "context2_value"

        # Original contexts should be unchanged
        assert context1["shared"] == "context1_value"
        assert context2["shared"] == "context2_value"

    def test_diff_computes_differences(self) -> None:
        """Test that diff() correctly computes context differences."""
        context1 = Context()
        context1["same_key"] = "same_value"
        context1["different_key"] = "context1_value"
        context1["unique1"] = "unique_to_1"

        context2 = Context()
        context2["same_key"] = "same_value"
        context2["different_key"] = "context2_value"
        context2["unique2"] = "unique_to_2"

        diffs = context1.diff(context2)

        # Should not include same_key (same in both)
        assert "same_key" not in diffs

        # Should include different values
        assert diffs["different_key"] == ("context1_value", "context2_value")
        assert diffs["unique1"] == ("unique_to_1", None)
        assert diffs["unique2"] == (None, "unique_to_2")

    def test_keys_iteration(self) -> None:
        """Test keys() method returns all unique keys."""
        context = Context()

        # Empty context
        assert list(context.keys()) == []

        # Single layer
        context["key1"] = "value1"
        context["key2"] = "value2"
        assert set(context.keys()) == {"key1", "key2"}

        # Multiple layers with shadowing
        context.push_layer()
        context["key3"] = "value3"
        context["key1"] = "shadowed_value"  # Shadow key1

        # Should return all unique keys, with most recent first
        all_keys = list(context.keys())
        assert set(all_keys) == {"key1", "key2", "key3"}
        # key1 and key3 should come first (from top layer)
        assert all_keys.index("key1") < all_keys.index("key2")
        assert all_keys.index("key3") < all_keys.index("key2")

    def test_dump_produces_valid_json(self) -> None:
        """Test that dump() produces valid JSON."""
        context = Context()

        # Add various data types
        context["string"] = "test"
        context["number"] = 42
        context["boolean"] = True
        context["null"] = None
        context["list"] = [1, 2, 3]
        context["dict"] = {"nested": "value"}

        # Push layer and add more data
        context.push_layer()
        context["layer_data"] = "layer_value"
        context["string"] = "overridden"  # Shadow original

        dump_str = context.dump()

        # Should be valid JSON
        import json

        parsed = json.loads(dump_str)

        # Should merge all layers (latest values win)
        assert parsed["string"] == "overridden"
        assert parsed["number"] == 42
        assert parsed["layer_data"] == "layer_value"
        assert parsed["dict"]["nested"] == "value"

    def test_repr_shows_basic_info(self) -> None:
        """Test that __repr__ shows useful information."""
        context = Context()
        context["key1"] = "value1"
        context["key2"] = "value2"

        repr_str = repr(context)

        assert "Context" in repr_str
        assert "frames=1" in repr_str
        # Keys might be in any order
        assert "key1" in repr_str
        assert "key2" in repr_str

    def test_complex_nested_data(self) -> None:
        """Test handling of complex nested data structures."""
        context = Context()

        complex_data = {
            "users": [
                {"id": 1, "name": "Alice", "settings": {"theme": "dark"}},
                {"id": 2, "name": "Bob", "settings": {"theme": "light"}},
            ],
            "config": {
                "database": {"host": "localhost", "port": 5432},
                "cache": {"ttl": 3600},
            },
        }

        context["app_data"] = complex_data

        # Should be able to retrieve and work with complex data
        retrieved = context["app_data"]
        assert retrieved["users"][0]["name"] == "Alice"
        assert retrieved["config"]["database"]["host"] == "localhost"

        # Should work with dump
        dump_str = context.dump()
        import json

        parsed = json.loads(dump_str)
        assert parsed["app_data"]["users"][1]["settings"]["theme"] == "light"
