"""Tests for Context.set_nested method."""

import pytest

from context.main import Context


class TestContextSetNested:
    """Test suite for Context.set_nested method."""

    def test_set_nested_basic(self) -> None:
        """Test setting nested values."""
        context = Context()

        context["user"] = {}
        context.set_nested("user.profile.name", "Alice")

        assert context["user"]["profile"]["name"] == "Alice"
        assert context.get_nested("user.profile.name") == "Alice"

    def test_set_nested_single_level(self) -> None:
        """Test setting single-level values (no nesting)."""
        context = Context()

        context.set_nested("simple_key", "simple_value")

        assert context["simple_key"] == "simple_value"
        assert context.get_nested("simple_key") == "simple_value"

    def test_set_nested_create_missing(self) -> None:
        """Test setting nested values with missing intermediate paths."""
        context = Context()

        # Should create missing structure by default
        context.set_nested("deep.nested.path.value", "test")

        assert context["deep"]["nested"]["path"]["value"] == "test"
        assert context.get_nested("deep.nested.path.value") == "test"

    def test_set_nested_no_create_missing(self) -> None:
        """Test setting nested values without creating missing paths."""
        context = Context()

        with pytest.raises(KeyError, match="does not exist"):
            context.set_nested("missing.path", "value", create_missing=False)

    def test_set_nested_no_create_missing_intermediate(self) -> None:
        """Test error when intermediate path doesn't exist and create_missing=False."""
        context = Context()

        context["user"] = {}

        with pytest.raises(KeyError, match="does not exist"):
            context.set_nested("user.profile.name", "Alice", create_missing=False)

    def test_set_nested_custom_delimiter(self) -> None:
        """Test setting nested values with custom delimiter."""
        context = Context()

        context.set_nested("data/level1/level2", "value", delimiter="/")

        assert context["data"]["level1"]["level2"] == "value"
        assert context.get_nested("data/level1/level2", delimiter="/") == "value"

    def test_set_nested_override_existing(self) -> None:
        """Test overriding existing nested values."""
        context = Context()

        # Set initial value
        context.set_nested("user.profile.name", "Alice")
        assert context.get_nested("user.profile.name") == "Alice"

        # Override with new value
        context.set_nested("user.profile.name", "Bob")
        assert context.get_nested("user.profile.name") == "Bob"

    def test_set_nested_different_types_basic(self) -> None:
        """Test setting nested values with basic data types."""
        context = Context()

        context.set_nested("data.string", "text")
        context.set_nested("data.integer", 42)
        context.set_nested("data.float", 3.14)
        context.set_nested("data.boolean", True)

        assert context.get_nested("data.string") == "text"
        assert context.get_nested("data.integer") == 42
        assert context.get_nested("data.float") == 3.14
        assert context.get_nested("data.boolean") is True

    def test_set_nested_different_types_complex(self) -> None:
        """Test setting nested values with complex data types."""
        context = Context()

        context.set_nested("data.list", [1, 2, 3])
        context.set_nested("data.dict", {"nested": "value"})
        context.set_nested("data.none", None)

        assert context.get_nested("data.list") == [1, 2, 3]
        assert context.get_nested("data.dict") == {"nested": "value"}
        assert context.get_nested("data.none") is None

    def test_set_nested_replace_dict_structure(self) -> None:
        """Test replacing entire dictionary structures."""
        context = Context()

        # Set initial nested structure
        context.set_nested("user.profile", {"name": "Alice", "age": 30})
        assert context.get_nested("user.profile.name") == "Alice"

        # Replace entire profile with new structure
        context.set_nested("user.profile", {"email": "alice@example.com"})
        assert context.get_nested("user.profile.email") == "alice@example.com"

        # Original name should no longer exist
        with pytest.raises(KeyError):
            context.get_nested("user.profile.name")

    def test_set_nested_parent_not_dict_error(self) -> None:
        """Test error when trying to set nested value on non-dict parent."""
        context = Context()

        context["user"] = "not_a_dict"

        with pytest.raises(KeyError, match="parent is not a dictionary"):
            context.set_nested("user.profile.name", "Alice")

    def test_set_nested_intermediate_not_dict_error(self) -> None:
        """Test error when intermediate value is not a dictionary."""
        context = Context()

        context["user"] = {"profile": "not_a_dict"}

        with pytest.raises(KeyError, match="parent is not a dictionary"):
            context.set_nested("user.profile.name", "Alice")

    def test_set_nested_deep_structure(self) -> None:
        """Test setting values in deeply nested structures."""
        context = Context()

        context.set_nested("level1.level2.level3.level4.level5", "deep_value")

        assert context.get_nested("level1.level2.level3.level4.level5") == "deep_value"

        # Verify intermediate levels were created
        assert isinstance(context["level1"], dict)
        assert isinstance(context["level1"]["level2"], dict)
        assert isinstance(context["level1"]["level2"]["level3"], dict)
        assert isinstance(context["level1"]["level2"]["level3"]["level4"], dict)

    def test_set_nested_with_existing_structure(self) -> None:
        """Test setting nested values in existing structure."""
        context = Context()

        # Create initial structure
        context["config"] = {
            "database": {"host": "localhost"},
            "app": {"name": "test_app"},
        }

        # Add new value to existing structure
        context.set_nested("config.database.port", 5432)
        context.set_nested("config.app.version", "1.0.0")

        assert context.get_nested("config.database.host") == "localhost"
        assert context.get_nested("config.database.port") == 5432
        assert context.get_nested("config.app.name") == "test_app"
        assert context.get_nested("config.app.version") == "1.0.0"

    def test_set_nested_empty_path(self) -> None:
        """Test setting nested values with empty path."""
        context = Context()

        # Empty path should be treated as single key
        context.set_nested("", "empty_key_value")

        assert context[""] == "empty_key_value"

    def test_set_nested_with_special_characters(self) -> None:
        """Test setting nested values with special characters in keys."""
        context = Context()

        context.set_nested("config.key-with-dashes", "value1")
        context.set_nested("config.key_with_underscores", "value2")
        context.set_nested("config.key with spaces", "value3")

        assert context.get_nested("config.key-with-dashes") == "value1"
        assert context.get_nested("config.key_with_underscores") == "value2"
        assert context.get_nested("config.key with spaces") == "value3"

    def test_set_nested_with_numeric_string_keys(self) -> None:
        """Test setting nested values with numeric string keys."""
        context = Context()

        context.set_nested("data.0.value", "first")
        context.set_nested("data.1.value", "second")

        assert context.get_nested("data.0.value") == "first"
        assert context.get_nested("data.1.value") == "second"

    def test_set_nested_return_none(self) -> None:
        """Test that set_nested returns None."""
        context = Context()

        # set_nested should return None (no return value)
        context.set_nested("test.key", "value")
        assert context.get_nested("test.key") == "value"

    def test_set_nested_with_layered_context(self) -> None:
        """Test setting nested values in layered context."""
        context = Context()

        # Set up base layer
        context["config"] = {"database": {"host": "localhost"}}

        # Add layer and set nested value
        context.push_layer()
        context.set_nested("config.database.port", 5432)

        assert context.get_nested("config.database.host") == "localhost"
        assert context.get_nested("config.database.port") == 5432

    def test_set_nested_integration_with_get_nested(self) -> None:
        """Test that set_nested works perfectly with get_nested."""
        context = Context()

        # Test various combinations
        test_cases = [
            ("simple", "value"),
            ("nested.path", "nested_value"),
            ("deep.very.deep.path", 42),
            ("config.settings.enabled", True),
            ("data.items", [1, 2, 3]),
            ("metadata.info", {"key": "value"}),
        ]

        for path, value in test_cases:
            context.set_nested(path, value)
            assert context.get_nested(path) == value

    def test_set_nested_with_custom_delimiter_complex(self) -> None:
        """Test setting nested values with various custom delimiters."""
        context = Context()

        # Test different delimiters
        context.set_nested("a/b/c", "slash_value", delimiter="/")
        context.set_nested("x_y_z", "underscore_value", delimiter="_")
        context.set_nested("m|n|o", "pipe_value", delimiter="|")

        assert context.get_nested("a/b/c", delimiter="/") == "slash_value"
        assert context.get_nested("x_y_z", delimiter="_") == "underscore_value"
        assert context.get_nested("m|n|o", delimiter="|") == "pipe_value"

    def test_set_nested_error_messages(self) -> None:
        """Test that set_nested provides helpful error messages."""
        context = Context()

        # Test error when parent is not a dict
        context["not_dict"] = "string_value"

        with pytest.raises(KeyError) as exc_info:
            context.set_nested("not_dict.child", "value")

        assert "parent is not a dictionary" in str(exc_info.value)

        # Test error when create_missing=False
        with pytest.raises(KeyError) as exc_info:
            context.set_nested("missing.path", "value", create_missing=False)

        assert "does not exist" in str(exc_info.value)

    def test_set_nested_preserves_existing_siblings(self) -> None:
        """Test that setting nested values preserves existing sibling values."""
        context = Context()

        # Create initial structure
        context.set_nested("user.profile.name", "Alice")
        context.set_nested("user.profile.age", 30)
        context.set_nested("user.settings.theme", "dark")

        # Add new value - should preserve existing siblings
        context.set_nested("user.profile.email", "alice@example.com")

        # All original values should still exist
        assert context.get_nested("user.profile.name") == "Alice"
        assert context.get_nested("user.profile.age") == 30
        assert context.get_nested("user.settings.theme") == "dark"
        assert context.get_nested("user.profile.email") == "alice@example.com"

    def test_set_nested_with_computed_properties(self) -> None:
        """Test setting nested values when computed properties exist."""
        context = Context()

        # Set base value
        context.set_nested("config.base_value", 10)

        # Add computed property
        def computed_double(ctx: Context) -> dict[str, int]:
            base_val = ctx.get_nested("config.base_value")
            assert isinstance(base_val, int)
            return {"doubled": base_val * 2}

        context.add_computed_property("computed_data", computed_double)

        # Set another nested value - should not interfere with computed property
        context.set_nested("config.other_value", "test")

        assert context.get_nested("config.base_value") == 10
        assert context.get_nested("config.other_value") == "test"
        assert context.get_nested("computed_data.doubled") == 20
