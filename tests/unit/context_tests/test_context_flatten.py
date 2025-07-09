"""Tests for Context.flatten method."""

from context.main import Context


class TestContextFlatten:
    """Test suite for Context.flatten method."""

    def test_flatten_basic(self) -> None:
        """Test basic flattening functionality."""
        context = Context()

        context["simple"] = "value"
        context["nested"] = {"level1": {"level2": "deep_value"}, "other": "other_value"}

        flattened = context.flatten()

        assert flattened["simple"] == "value"
        assert flattened["nested.level1.level2"] == "deep_value"
        assert flattened["nested.other"] == "other_value"

    def test_flatten_empty_context(self) -> None:
        """Test flattening an empty context."""
        context = Context()

        flattened = context.flatten()

        assert flattened == {}

    def test_flatten_single_level(self) -> None:
        """Test flattening with no nested structures."""
        context = Context()

        context["key1"] = "value1"
        context["key2"] = 42
        context["key3"] = True

        flattened = context.flatten()

        assert flattened == {"key1": "value1", "key2": 42, "key3": True}

    def test_flatten_max_depth(self) -> None:
        """Test flattening with maximum depth limit."""
        context = Context()

        context["deep"] = {"level1": {"level2": {"level3": "value"}}}

        # Flatten with max depth 1
        flattened = context.flatten(max_depth=1)

        assert "deep.level1" in flattened
        assert isinstance(flattened["deep.level1"], dict)
        assert flattened["deep.level1"]["level2"]["level3"] == "value"

    def test_flatten_max_depth_zero(self) -> None:
        """Test flattening with max depth 0 (no flattening)."""
        context = Context()

        context["nested"] = {"level1": {"level2": "value"}}

        flattened = context.flatten(max_depth=0)

        assert flattened == {"nested": {"level1": {"level2": "value"}}}

    def test_flatten_custom_delimiter(self) -> None:
        """Test flattening with custom delimiter."""
        context = Context()

        context["nested"] = {"level1": {"level2": "value"}}

        flattened = context.flatten(delimiter="/")
        assert "nested/level1/level2" in flattened
        assert flattened["nested/level1/level2"] == "value"

    def test_flatten_different_delimiters(self) -> None:
        """Test flattening with various delimiters."""
        context = Context()

        context["a"] = {"b": {"c": "value"}}

        # Test with underscore
        flattened = context.flatten(delimiter="_")
        assert flattened == {"a_b_c": "value"}

        # Test with dash
        flattened = context.flatten(delimiter="-")
        assert flattened == {"a-b-c": "value"}

        # Test with double colon
        flattened = context.flatten(delimiter="::")
        assert flattened == {"a::b::c": "value"}

    def test_flatten_deeply_nested(self) -> None:
        """Test flattening deeply nested structures."""
        context = Context()

        context["level1"] = {"level2": {"level3": {"level4": {"level5": "deep_value"}}}}

        flattened = context.flatten()

        assert flattened["level1.level2.level3.level4.level5"] == "deep_value"

    def test_flatten_multiple_branches(self) -> None:
        """Test flattening with multiple nested branches."""
        context = Context()

        context["config"] = {
            "database": {"host": "localhost", "port": 5432},
            "cache": {"redis": {"host": "redis.local", "port": 6379}},
        }

        flattened = context.flatten()

        assert flattened["config.database.host"] == "localhost"
        assert flattened["config.database.port"] == 5432
        assert flattened["config.cache.redis.host"] == "redis.local"
        assert flattened["config.cache.redis.port"] == 6379

    def test_flatten_with_mixed_types(self) -> None:
        """Test flattening with various data types."""
        context = Context()

        context["data"] = {
            "string": "text",
            "number": 42,
            "float": 3.14,
            "boolean": True,
            "none": None,
            "list": [1, 2, 3],
            "nested": {"key": "value"},
        }

        flattened = context.flatten()

        assert flattened["data.string"] == "text"
        assert flattened["data.number"] == 42
        assert flattened["data.float"] == 3.14
        assert flattened["data.boolean"] is True
        assert flattened["data.none"] is None
        assert flattened["data.list"] == [1, 2, 3]
        assert flattened["data.nested.key"] == "value"

    def test_flatten_with_list_values(self) -> None:
        """Test flattening stops at list values."""
        context = Context()

        context["data"] = {
            "items": [{"id": 1, "name": "item1"}, {"id": 2, "name": "item2"}]
        }

        flattened = context.flatten()

        assert flattened["data.items"] == [
            {"id": 1, "name": "item1"},
            {"id": 2, "name": "item2"},
        ]

    def test_flatten_max_depth_multiple_levels(self) -> None:
        """Test max depth with various depth values."""
        context = Context()

        context["root"] = {"l1": {"l2": {"l3": {"l4": "value"}}}}

        # Max depth 1
        flattened = context.flatten(max_depth=1)
        assert "root.l1" in flattened
        assert isinstance(flattened["root.l1"], dict)

        # Max depth 2
        flattened = context.flatten(max_depth=2)
        assert "root.l1.l2" in flattened
        assert isinstance(flattened["root.l1.l2"], dict)

        # Max depth 3
        flattened = context.flatten(max_depth=3)
        assert "root.l1.l2.l3" in flattened
        assert isinstance(flattened["root.l1.l2.l3"], dict)

        # No max depth (full flatten)
        flattened = context.flatten()
        assert "root.l1.l2.l3.l4" in flattened
        assert flattened["root.l1.l2.l3.l4"] == "value"

    def test_flatten_with_empty_dicts(self) -> None:
        """Test flattening with empty dictionaries."""
        context = Context()

        context["config"] = {"empty": {}, "nested": {"also_empty": {}}}

        flattened = context.flatten()

        # Empty dicts should still be preserved
        assert flattened["config.empty"] == {}
        assert flattened["config.nested.also_empty"] == {}

    def test_flatten_with_special_keys(self) -> None:
        """Test flattening with special characters in keys."""
        context = Context()

        context["special"] = {
            "key-with-dashes": {"value": 1},
            "key_with_underscores": {"value": 2},
            "key with spaces": {"value": 3},
        }

        flattened = context.flatten()

        assert flattened["special.key-with-dashes.value"] == 1
        assert flattened["special.key_with_underscores.value"] == 2
        assert flattened["special.key with spaces.value"] == 3

    def test_flatten_excludes_computed_properties(self) -> None:
        """Test that flatten excludes computed properties."""
        context = Context()

        context["base"] = 10
        context["multiplier"] = 5

        def compute_result(ctx: Context) -> int:
            base = ctx["base"]
            multiplier = ctx["multiplier"]
            assert isinstance(base, int)
            assert isinstance(multiplier, int)
            return base * multiplier

        context.add_computed_property("result", compute_result)

        context["nested"] = {"data": "value"}

        flattened = context.flatten()

        # Should include regular values
        assert flattened["base"] == 10
        assert flattened["multiplier"] == 5
        assert flattened["nested.data"] == "value"

        # Should exclude computed property
        assert "result" not in flattened

    def test_flatten_with_layered_context(self) -> None:
        """Test flattening with layered context frames."""
        context = Context()

        # Base layer
        context["config"] = {"level": "base"}

        # Add layer with nested data
        context.push_layer()
        context["config"] = {"level": "override", "nested": {"key": "value"}}

        flattened = context.flatten()

        # Should use the top layer's value
        assert flattened["config.level"] == "override"
        assert flattened["config.nested.key"] == "value"

    def test_flatten_return_type(self) -> None:
        """Test that flatten returns a dictionary."""
        context = Context()

        context["nested"] = {"key": "value"}

        flattened = context.flatten()

        assert isinstance(flattened, dict)
        assert all(isinstance(k, str) for k in flattened.keys())

    def test_flatten_preserves_context_state(self) -> None:
        """Test that flatten doesn't modify context state."""
        context = Context()

        context["data"] = {"nested": {"value": 42}}

        # Store original reference
        original_data = context["data"]

        # Call flatten multiple times
        context.flatten()
        context.flatten(delimiter="/")
        context.flatten(max_depth=1)

        # Verify state is unchanged
        assert context["data"] is original_data
        assert context["data"]["nested"]["value"] == 42

    def test_flatten_handles_non_dict_values(self) -> None:
        """Test flattening with non-dictionary nested values."""
        context = Context()

        # Custom object (not a dict)
        class CustomObject:
            def __init__(self) -> None:  # pyright: ignore[reportMissingSuperCall]
                self.attr = "object_value"

        context["obj"] = CustomObject()
        context["string"] = "just a string"
        context["number"] = 123

        flattened = context.flatten()

        # Non-dict values should be included as-is
        assert isinstance(flattened["obj"], CustomObject)
        assert flattened["string"] == "just a string"
        assert flattened["number"] == 123

    def test_flatten_delimiter_in_keys(self) -> None:
        """Test flattening when keys contain the delimiter."""
        context = Context()

        # Keys containing dots
        context["key.with.dots"] = {"nested": "value"}
        context["normal"] = {"key.with.dots": "another_value"}

        flattened = context.flatten()

        # The flattened keys will have multiple dots
        assert flattened["key.with.dots.nested"] == "value"
        assert flattened["normal.key.with.dots"] == "another_value"
