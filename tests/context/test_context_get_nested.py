"""Tests for Context.get_nested method."""

import pytest

from context.main import Context


class TestContextGetNested:
    """Test suite for Context.get_nested method."""

    def test_get_nested_basic(self) -> None:
        """Test getting nested values with dot notation."""
        context = Context()

        context["user"] = {
            "profile": {"name": "Alice", "age": 30},
            "settings": {"theme": "dark"},
        }

        assert context.get_nested("user.profile.name") == "Alice"
        assert context.get_nested("user.profile.age") == 30
        assert context.get_nested("user.settings.theme") == "dark"

    def test_get_nested_single_level(self) -> None:
        """Test getting single-level values (no nesting)."""
        context = Context()

        context["simple_key"] = "simple_value"
        context["number"] = 42

        assert context.get_nested("simple_key") == "simple_value"
        assert context.get_nested("number") == 42

    def test_get_nested_custom_delimiter(self) -> None:
        """Test getting nested values with custom delimiter."""
        context = Context()

        context["data"] = {"level1": {"level2": "value"}}

        assert context.get_nested("data/level1/level2", delimiter="/") == "value"

    def test_get_nested_with_underscores(self) -> None:
        """Test getting nested values with underscore delimiter."""
        context = Context()

        context["config"] = {"database": {"host": "localhost", "port": 5432}}

        assert context.get_nested("config_database_host", delimiter="_") == "localhost"
        assert context.get_nested("config_database_port", delimiter="_") == 5432

    def test_get_nested_missing_top_level(self) -> None:
        """Test getting nested values with missing top-level key."""
        context = Context()

        context["user"] = {"name": "Alice"}

        with pytest.raises(KeyError, match="nonexistent"):
            context.get_nested("nonexistent.path")

    def test_get_nested_missing_nested_path(self) -> None:
        """Test getting nested values with missing nested paths."""
        context = Context()

        context["user"] = {"name": "Alice"}

        with pytest.raises(KeyError, match="Path 'user.profile.name' not found"):
            context.get_nested("user.profile.name")

    def test_get_nested_missing_intermediate_key(self) -> None:
        """Test getting nested values with missing intermediate key."""
        context = Context()

        context["user"] = {"profile": {"name": "Alice"}}

        with pytest.raises(KeyError, match="Path 'user.profile.age' not found"):
            context.get_nested("user.profile.age")

    def test_get_nested_empty_path(self) -> None:
        """Test getting nested values with empty path."""
        context = Context()

        context["test"] = "value"

        # Empty path should raise an error when split
        with pytest.raises(KeyError):
            context.get_nested("")

    def test_get_nested_deeply_nested(self) -> None:
        """Test getting deeply nested values."""
        context = Context()

        context["level1"] = {"level2": {"level3": {"level4": {"level5": "deep_value"}}}}

        assert context.get_nested("level1.level2.level3.level4.level5") == "deep_value"

    def test_get_nested_with_object_attributes(self) -> None:
        """Test getting nested values with object attributes."""

        class TestObject:
            def __init__(self) -> None:
                super().__init__()
                self.attribute = "object_value"
                self.nested_obj = TestNestedObject()

        class TestNestedObject:
            def __init__(self) -> None:
                super().__init__()
                self.value = 42

        context = Context()
        context["obj"] = TestObject()

        assert context.get_nested("obj.attribute") == "object_value"
        assert context.get_nested("obj.nested_obj.value") == 42

    def test_get_nested_with_missing_attribute(self) -> None:
        """Test getting nested values with missing object attributes."""

        class TestObject:
            def __init__(self) -> None:
                super().__init__()
                self.existing_attr = "value"

        context = Context()
        context["obj"] = TestObject()

        with pytest.raises(KeyError, match="Path 'obj.missing_attr' not found"):
            context.get_nested("obj.missing_attr")

    def test_get_nested_mixed_dict_and_object(self) -> None:
        """Test getting nested values mixing dictionaries and objects."""

        class UserProfile:
            def __init__(self) -> None:
                super().__init__()
                self.details = {"bio": "Software developer", "location": "NYC"}

        context = Context()
        context["user"] = {"name": "Alice", "profile": UserProfile()}

        assert context.get_nested("user.name") == "Alice"
        assert context.get_nested("user.profile.details") == {
            "bio": "Software developer",
            "location": "NYC",
        }

    def test_get_nested_with_list_values(self) -> None:
        """Test getting nested values that contain lists."""
        context = Context()

        context["data"] = {"items": [1, 2, 3], "nested": {"list": ["a", "b", "c"]}}

        assert context.get_nested("data.items") == [1, 2, 3]
        assert context.get_nested("data.nested.list") == ["a", "b", "c"]

    def test_get_nested_with_none_values(self) -> None:
        """Test getting nested values that contain None."""
        context = Context()

        context["data"] = {"value": None, "nested": {"none_value": None}}

        assert context.get_nested("data.value") is None
        assert context.get_nested("data.nested.none_value") is None

    def test_get_nested_with_computed_properties(self) -> None:
        """Test getting nested values that include computed properties."""
        context = Context()

        context["base_data"] = {"value": 10}

        def computed_nested(ctx: Context) -> dict[str, int]:
            base_val = ctx["base_data"]["value"]
            assert isinstance(base_val, int)
            return {"computed": base_val * 2}

        context.add_computed_property("computed_data", computed_nested)

        assert context.get_nested("computed_data.computed") == 20

    def test_get_nested_with_layered_context(self) -> None:
        """Test getting nested values in layered context."""
        context = Context()

        # Set up base layer
        context["config"] = {"database": {"host": "localhost"}}

        # Add layer and override
        context.push_layer()
        context["config"] = {"database": {"host": "remote_host", "port": 5432}}

        assert context.get_nested("config.database.host") == "remote_host"
        assert context.get_nested("config.database.port") == 5432

    def test_get_nested_return_types(self) -> None:
        """Test that get_nested returns correct types."""
        context = Context()

        context["data"] = {
            "string": "text",
            "integer": 42,
            "float": 3.14,
            "boolean": True,
            "list": [1, 2, 3],
            "dict": {"nested": "value"},
            "none": None,
        }

        assert isinstance(context.get_nested("data.string"), str)
        assert isinstance(context.get_nested("data.integer"), int)
        assert isinstance(context.get_nested("data.float"), float)
        assert isinstance(context.get_nested("data.boolean"), bool)
        assert isinstance(context.get_nested("data.list"), list)
        assert isinstance(context.get_nested("data.dict"), dict)
        assert context.get_nested("data.none") is None

    def test_get_nested_delimiter_in_path(self) -> None:
        """Test getting nested values when delimiter appears in keys."""
        context = Context()

        # Use underscore delimiter when keys contain dots
        context["file.txt"] = {"metadata": {"size": 1024}}

        assert context.get_nested("file.txt_metadata_size", delimiter="_") == 1024

    def test_get_nested_error_messages(self) -> None:
        """Test that get_nested provides helpful error messages."""
        context = Context()

        context["user"] = {"name": "Alice"}

        # Test missing nested key error message
        with pytest.raises(KeyError) as exc_info:
            context.get_nested("user.profile.name")

        assert "Path 'user.profile.name' not found" in str(exc_info.value)
        assert "missing 'profile'" in str(exc_info.value)

    def test_get_nested_with_numeric_string_keys(self) -> None:
        """Test getting nested values with numeric string keys."""
        context = Context()

        context["data"] = {"0": {"value": "first"}, "1": {"value": "second"}}

        assert context.get_nested("data.0.value") == "first"
        assert context.get_nested("data.1.value") == "second"

    def test_get_nested_with_special_characters(self) -> None:
        """Test getting nested values with special characters in keys."""
        context = Context()

        context["config"] = {
            "key-with-dashes": {"value": "test1"},
            "key_with_underscores": {"value": "test2"},
        }

        assert context.get_nested("config.key-with-dashes.value") == "test1"
        assert context.get_nested("config.key_with_underscores.value") == "test2"
