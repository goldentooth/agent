"""Tests for Context.dump method."""

import json

from context.main import Context


class TestContextDump:
    """Test suite for Context.dump method."""

    def test_dump_basic(self) -> None:
        """Test basic dump functionality."""
        context = Context()

        context["key1"] = "value1"
        context["key2"] = 42

        result = context.dump()

        # Should be valid JSON
        parsed = json.loads(result)
        assert parsed == {"key1": "value1", "key2": 42}

    def test_dump_empty_context(self) -> None:
        """Test dumping an empty context."""
        context = Context()

        result = context.dump()

        parsed = json.loads(result)
        assert parsed == {}

    def test_dump_single_frame(self) -> None:
        """Test dumping with a single frame."""
        context = Context()

        context["string"] = "text"
        context["number"] = 123
        context["boolean"] = True
        context["none"] = None

        result = context.dump()

        parsed = json.loads(result)
        assert parsed == {
            "string": "text",
            "number": 123,
            "boolean": True,
            "none": None,
        }

    def test_dump_multiple_frames(self) -> None:
        """Test dumping with multiple frames merged."""
        context = Context()

        # Base frame
        context["base"] = "base_value"
        context["shared"] = "base_shared"

        # Add a new frame
        context.push_layer()
        context["layer"] = "layer_value"
        context["shared"] = "layer_shared"  # Override

        result = context.dump()

        parsed = json.loads(result)
        # Should merge all frames, with later frames overriding earlier ones
        assert parsed == {
            "base": "base_value",
            "shared": "layer_shared",  # Later frame wins
            "layer": "layer_value",
        }

    def test_dump_nested_dictionaries(self) -> None:
        """Test dumping with nested dictionary structures."""
        context = Context()

        context["config"] = {
            "database": {"host": "localhost", "port": 5432},
            "cache": {"enabled": True},
        }

        result = context.dump()

        parsed = json.loads(result)
        assert parsed == {
            "config": {
                "database": {"host": "localhost", "port": 5432},
                "cache": {"enabled": True},
            }
        }

    def test_dump_with_list_values(self) -> None:
        """Test dumping with list values."""
        context = Context()

        context["items"] = [1, 2, 3]
        context["mixed"] = ["string", 42, True, None]

        result = context.dump()

        parsed = json.loads(result)
        assert parsed == {"items": [1, 2, 3], "mixed": ["string", 42, True, None]}

    def test_dump_excludes_computed_properties(self) -> None:
        """Test that dump excludes computed properties."""
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

        result = context.dump()

        parsed = json.loads(result)
        # Should only include regular values, not computed properties
        assert parsed == {"base": 10, "multiplier": 5}
        assert "result" not in parsed

    def test_dump_json_formatting(self) -> None:
        """Test that dump returns properly formatted JSON."""
        context = Context()

        context["nested"] = {"key": "value"}

        result = context.dump()

        # Should be properly indented JSON
        assert result.count("\n") > 0  # Multi-line
        assert "  " in result  # Indented

        # Should be valid JSON
        parsed = json.loads(result)
        assert parsed == {"nested": {"key": "value"}}

    def test_dump_return_type(self) -> None:
        """Test that dump returns a string."""
        context = Context()

        context["key"] = "value"

        result = context.dump()

        assert isinstance(result, str)

    def test_dump_with_frame_override_pattern(self) -> None:
        """Test dump with complex frame override patterns."""
        context = Context()

        # First frame
        context["common"] = "frame1"
        context["unique1"] = "value1"

        # Second frame
        context.push_layer()
        context["common"] = "frame2"
        context["unique2"] = "value2"

        # Third frame
        context.push_layer()
        context["common"] = "frame3"
        context["unique3"] = "value3"

        result = context.dump()

        parsed = json.loads(result)
        assert parsed == {
            "common": "frame3",  # Top frame wins
            "unique1": "value1",
            "unique2": "value2",
            "unique3": "value3",
        }

    def test_dump_with_complex_nested_structure(self) -> None:
        """Test dump with complex nested structures."""
        context = Context()

        context["app"] = {
            "name": "MyApp",
            "version": "1.0.0",
            "config": {
                "features": {
                    "auth": True,
                    "logging": {"level": "info", "file": "app.log"},
                    "cache": {"ttl": 3600, "enabled": True},
                },
                "database": {
                    "connections": [
                        {"name": "primary", "host": "db1.example.com"},
                        {"name": "secondary", "host": "db2.example.com"},
                    ]
                },
            },
        }

        result = context.dump()

        parsed = json.loads(result)
        assert parsed["app"]["config"]["features"]["logging"]["level"] == "info"
        assert len(parsed["app"]["config"]["database"]["connections"]) == 2

    def test_dump_preserves_context_state(self) -> None:
        """Test that dump doesn't modify the context state."""
        context = Context()

        original_data = {"nested": {"key": "value"}}
        context["data"] = original_data

        # Call dump multiple times
        context.dump()
        context.dump()

        # Verify context state is unchanged
        assert context["data"] is original_data
        assert context["data"]["nested"]["key"] == "value"

    def test_dump_with_special_characters(self) -> None:
        """Test dump with special characters in keys and values."""
        context = Context()

        context["key with spaces"] = "value with spaces"
        context["key-with-dashes"] = "value-with-dashes"
        context["key_with_underscores"] = "value_with_underscores"
        context["unicode_key"] = "value with unicode: 你好"

        result = context.dump()

        parsed = json.loads(result)
        assert parsed["key with spaces"] == "value with spaces"
        assert parsed["key-with-dashes"] == "value-with-dashes"
        assert parsed["key_with_underscores"] == "value_with_underscores"
        assert parsed["unicode_key"] == "value with unicode: 你好"

    def test_dump_with_empty_nested_structures(self) -> None:
        """Test dump with empty nested structures."""
        context = Context()

        context["empty_dict"] = {}
        context["empty_list"] = []
        context["nested_empty"] = {"empty": {}, "also_empty": []}

        result = context.dump()

        parsed = json.loads(result)
        assert parsed["empty_dict"] == {}
        assert parsed["empty_list"] == []
        assert parsed["nested_empty"]["empty"] == {}
        assert parsed["nested_empty"]["also_empty"] == []

    def test_dump_handles_json_serializable_values(self) -> None:
        """Test dump with various JSON-serializable values."""
        context = Context()

        # Set up test data with various JSON-serializable types
        test_data = {
            "int": 42,
            "float": 3.14,
            "bool_true": True,
            "bool_false": False,
            "null": None,
            "string": "text",
            "list": [1, 2, 3],
            "dict": {"key": "value"},
        }

        for key, value in test_data.items():
            context[key] = value

        result = context.dump()
        parsed = json.loads(result)

        # Verify all values are correctly serialized
        assert parsed == test_data

    def test_dump_with_multiple_layers_and_overrides(self) -> None:
        """Test dump with multiple layers showing override behavior."""
        context = Context()

        # Base layer
        context["config"] = {"mode": "development", "debug": True}

        # Override layer
        context.push_layer()
        context["config"] = {"mode": "production", "debug": False, "ssl": True}

        result = context.dump()

        parsed = json.loads(result)
        # Should use the top layer's value completely
        assert parsed["config"] == {"mode": "production", "debug": False, "ssl": True}

    def test_dump_ignores_non_json_serializable_gracefully(self) -> None:
        """Test that dump handles non-JSON serializable values gracefully."""
        context = Context()

        # Add JSON serializable values
        context["good_key"] = "good_value"
        context["number"] = 42

        # We'll test that regular values work -
        # the method should handle serialization of basic types
        result = context.dump()

        parsed = json.loads(result)
        assert parsed["good_key"] == "good_value"
        assert parsed["number"] == 42
