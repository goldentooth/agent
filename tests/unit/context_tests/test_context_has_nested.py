"""Tests for Context.has_nested method."""

from context.main import Context


class TestContextHasNested:
    """Test suite for Context.has_nested method."""

    def test_has_nested_basic(self) -> None:
        """Test basic has_nested functionality."""
        context = Context()

        context["user"] = {"profile": {"name": "Alice"}}

        assert context.has_nested("user.profile.name")
        assert context.has_nested("user.profile")
        assert context.has_nested("user")
        assert not context.has_nested("user.profile.age")
        assert not context.has_nested("missing.path")

    def test_has_nested_empty_context(self) -> None:
        """Test has_nested on empty context."""
        context = Context()

        assert not context.has_nested("anything")
        assert not context.has_nested("nested.path")

    def test_has_nested_single_level(self) -> None:
        """Test has_nested with single-level keys."""
        context = Context()

        context["simple_key"] = "simple_value"
        context["number"] = 42

        assert context.has_nested("simple_key")
        assert context.has_nested("number")
        assert not context.has_nested("missing")

    def test_has_nested_custom_delimiter(self) -> None:
        """Test has_nested with custom delimiter."""
        context = Context()

        context["data"] = {"level1": {"level2": "value"}}

        assert context.has_nested("data/level1/level2", delimiter="/")
        assert context.has_nested("data/level1", delimiter="/")
        assert not context.has_nested("data/missing", delimiter="/")

    def test_has_nested_deeply_nested(self) -> None:
        """Test has_nested with deeply nested structures."""
        context = Context()

        context["level1"] = {"level2": {"level3": {"level4": {"level5": "deep_value"}}}}

        assert context.has_nested("level1.level2.level3.level4.level5")
        assert context.has_nested("level1.level2.level3.level4")
        assert context.has_nested("level1.level2.level3")
        assert context.has_nested("level1.level2")
        assert context.has_nested("level1")
        assert not context.has_nested("level1.level2.level3.level4.level6")
        assert not context.has_nested("level1.level2.level3.missing")

    def test_has_nested_with_object_attributes(self) -> None:
        """Test has_nested with object attributes."""

        class TestObject:
            def __init__(self) -> None:  # pyright: ignore[reportMissingSuperCall]
                self.attribute = "object_value"
                self.nested_obj = TestNestedObject()

        class TestNestedObject:
            def __init__(self) -> None:  # pyright: ignore[reportMissingSuperCall]
                self.value = 42

        context = Context()
        context["obj"] = TestObject()

        assert context.has_nested("obj.attribute")
        assert context.has_nested("obj.nested_obj.value")
        assert context.has_nested("obj.nested_obj")
        assert not context.has_nested("obj.missing_attr")
        assert not context.has_nested("obj.nested_obj.missing")

    def test_has_nested_mixed_dict_and_object(self) -> None:
        """Test has_nested with mixed dictionaries and objects."""

        class UserProfile:
            def __init__(self) -> None:  # pyright: ignore[reportMissingSuperCall]
                self.details = {"bio": "Software developer", "location": "NYC"}

        context = Context()
        context["user"] = {"name": "Alice", "profile": UserProfile()}

        assert context.has_nested("user.name")
        assert context.has_nested("user.profile.details")
        assert context.has_nested("user.profile")
        assert not context.has_nested("user.age")
        assert not context.has_nested("user.profile.settings")

    def test_has_nested_with_none_values(self) -> None:
        """Test has_nested with None values."""
        context = Context()

        context["data"] = {"value": None, "nested": {"none_value": None}}

        assert context.has_nested("data.value")
        assert context.has_nested("data.nested.none_value")
        assert context.has_nested("data.nested")
        assert not context.has_nested("data.missing")

    def test_has_nested_with_computed_properties(self) -> None:
        """Test has_nested with computed properties."""
        context = Context()

        context["base_data"] = {"value": 10}

        def computed_nested(ctx: Context) -> dict[str, int]:
            base_val = ctx["base_data"]["value"]
            assert isinstance(base_val, int)
            return {"computed": base_val * 2}

        context.add_computed_property("computed_data", computed_nested)

        assert context.has_nested("computed_data.computed")
        assert context.has_nested("computed_data")
        assert context.has_nested("base_data.value")
        assert not context.has_nested("computed_data.missing")

    def test_has_nested_with_layered_context(self) -> None:
        """Test has_nested with layered context."""
        context = Context()

        # Set up base layer
        context["config"] = {"database": {"host": "localhost"}}

        # Add layer and override
        context.push_layer()
        context["config"] = {"database": {"host": "remote_host", "port": 5432}}

        assert context.has_nested("config.database.host")
        assert context.has_nested("config.database.port")
        assert context.has_nested("config.database")
        assert not context.has_nested("config.app")

    def test_has_nested_with_list_values(self) -> None:
        """Test has_nested with list values."""
        context = Context()

        context["data"] = {"items": [1, 2, 3], "nested": {"list": ["a", "b", "c"]}}

        assert context.has_nested("data.items")
        assert context.has_nested("data.nested.list")
        assert context.has_nested("data.nested")
        assert not context.has_nested("data.missing")

    def test_has_nested_with_different_types(self) -> None:
        """Test has_nested with various data types."""
        context = Context()

        context["data"] = {
            "string": "text",
            "integer": 42,
            "float": 3.14,
            "boolean": True,
            "list": [1, 2, 3],
            "dict": {"nested": "value"},
        }

        assert context.has_nested("data.string")
        assert context.has_nested("data.integer")
        assert context.has_nested("data.float")
        assert context.has_nested("data.boolean")
        assert context.has_nested("data.list")
        assert context.has_nested("data.dict")
        assert context.has_nested("data.dict.nested")
        assert not context.has_nested("data.missing")

    def test_has_nested_return_type(self) -> None:
        """Test that has_nested returns boolean."""
        context = Context()

        context["test"] = {"key": "value"}

        result_true = context.has_nested("test.key")
        result_false = context.has_nested("test.missing")

        assert isinstance(result_true, bool)
        assert isinstance(result_false, bool)
        assert result_true is True
        assert result_false is False

    def test_has_nested_empty_path(self) -> None:
        """Test has_nested with empty path."""
        context = Context()

        context[""] = "empty_key_value"

        assert context.has_nested("")
        assert not context.has_nested("missing")

    def test_has_nested_with_special_characters(self) -> None:
        """Test has_nested with special characters in keys."""
        context = Context()

        context["config"] = {
            "key-with-dashes": {"value": "test1"},
            "key_with_underscores": {"value": "test2"},
            "key with spaces": {"value": "test3"},
        }

        assert context.has_nested("config.key-with-dashes.value")
        assert context.has_nested("config.key_with_underscores.value")
        assert context.has_nested("config.key with spaces.value")
        assert not context.has_nested("config.missing-key.value")

    def test_has_nested_with_numeric_string_keys(self) -> None:
        """Test has_nested with numeric string keys."""
        context = Context()

        context["data"] = {"0": {"value": "first"}, "1": {"value": "second"}}

        assert context.has_nested("data.0.value")
        assert context.has_nested("data.1.value")
        assert context.has_nested("data.0")
        assert not context.has_nested("data.2")

    def test_has_nested_with_custom_delimiter_complex(self) -> None:
        """Test has_nested with various custom delimiters."""
        context = Context()

        context["a"] = {"b": {"c": "slash_value"}}
        context["x"] = {"y": {"z": "underscore_value"}}
        context["m"] = {"n": {"o": "pipe_value"}}

        assert context.has_nested("a/b/c", delimiter="/")
        assert context.has_nested("x_y_z", delimiter="_")
        assert context.has_nested("m|n|o", delimiter="|")
        assert not context.has_nested("a/b/missing", delimiter="/")

    def test_has_nested_integration_with_get_nested(self) -> None:
        """Test that has_nested is consistent with get_nested."""
        context = Context()

        # Test various paths
        test_paths = [
            "simple",
            "nested.path",
            "deep.very.deep.path",
            "config.settings.enabled",
            "missing.path",
            "user.profile.missing",
        ]

        # Set up some test data
        context["simple"] = "value"
        context["nested"] = {"path": "nested_value"}
        context["deep"] = {"very": {"deep": {"path": 42}}}
        context["config"] = {"settings": {"enabled": True}}
        context["user"] = {"profile": {"name": "Alice"}}

        for path in test_paths:
            has_result = context.has_nested(path)

            try:
                context.get_nested(path)
                get_result = True
            except KeyError:
                get_result = False

            assert has_result == get_result, f"Inconsistency for path '{path}'"

    def test_has_nested_with_transformation(self) -> None:
        """Test has_nested with transformations."""
        context = Context()

        # Add transformation
        context.add_transformation("name", str.upper)

        # Set nested value
        context["user"] = {"name": "alice"}

        # has_nested should work regardless of transformations
        assert context.has_nested("user.name")
        assert not context.has_nested("user.age")

    def test_has_nested_preserves_context_state(self) -> None:
        """Test that has_nested doesn't modify context state."""
        context = Context()

        context["test"] = {"key": "value"}

        # Store original state
        original_value = context.get_nested("test.key")

        # Call has_nested multiple times
        context.has_nested("test.key")
        context.has_nested("test.missing")
        context.has_nested("missing.path")

        # Verify state is unchanged
        assert context.get_nested("test.key") == original_value
        assert len(list(context.keys())) == 1
