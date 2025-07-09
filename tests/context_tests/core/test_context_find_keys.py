"""Tests for Context.find_keys method."""

from context.main import Context


class TestContextFindKeys:
    """Test suite for Context.find_keys method."""

    def test_find_keys_empty_context(self) -> None:
        """Test find_keys on empty context."""
        context = Context()

        result = context.find_keys("test")

        assert isinstance(result, list)
        assert len(result) == 0

    def test_find_keys_no_matches(self) -> None:
        """Test find_keys with pattern that matches no keys."""
        context = Context()

        # Add test data
        context["key1"] = "value1"
        context["key2"] = "value2"
        context["key3"] = "value3"

        result = context.find_keys("nonexistent")

        assert isinstance(result, list)
        assert len(result) == 0

    def test_find_keys_exact_match(self) -> None:
        """Test find_keys with exact match pattern."""
        context = Context()

        # Add test data
        context["test"] = "value1"
        context["testing"] = "value2"
        context["other"] = "value3"

        result = context.find_keys("^test$")

        assert len(result) == 1
        assert "test" in result

    def test_find_keys_partial_match(self) -> None:
        """Test find_keys with partial match pattern."""
        context = Context()

        # Add test data
        context["user_name"] = "alice"
        context["user_age"] = 30
        context["admin_name"] = "bob"
        context["config_path"] = "/etc/config"

        result = context.find_keys("user")

        assert len(result) == 2
        assert "user_name" in result
        assert "user_age" in result
        assert "admin_name" not in result
        assert "config_path" not in result

    def test_find_keys_starts_with(self) -> None:
        """Test find_keys with starts with pattern."""
        context = Context()

        # Add test data
        context["prefix_one"] = "value1"
        context["prefix_two"] = "value2"
        context["other_prefix"] = "value3"
        context["suffix"] = "value4"

        result = context.find_keys("^prefix")

        assert len(result) == 2
        assert "prefix_one" in result
        assert "prefix_two" in result

    def test_find_keys_ends_with(self) -> None:
        """Test find_keys with ends with pattern."""
        context = Context()

        # Add test data
        context["test_suffix"] = "value1"
        context["other_suffix"] = "value2"
        context["prefix_suffix"] = "value3"
        context["different"] = "value4"

        result = context.find_keys("suffix$")

        assert len(result) == 3
        assert "test_suffix" in result
        assert "other_suffix" in result
        assert "prefix_suffix" in result
        assert "different" not in result

    def test_find_keys_contains_pattern(self) -> None:
        """Test find_keys with contains pattern."""
        context = Context()

        # Add test data
        context["before_middle_after"] = "value1"
        context["middle_section"] = "value2"
        context["test_middle"] = "value3"
        context["different"] = "value4"

        result = context.find_keys("middle")

        assert len(result) == 3
        assert "before_middle_after" in result
        assert "middle_section" in result
        assert "test_middle" in result
        assert "different" not in result

    def test_find_keys_special_characters(self) -> None:
        """Test find_keys with special characters in pattern."""
        context = Context()

        # Add test data
        context["test.config"] = "value1"
        context["other-config"] = "value2"
        context["config_file"] = "value3"
        context["normal"] = "value4"

        # Test dot pattern
        result = context.find_keys(r"\.")
        assert len(result) == 1
        assert "test.config" in result

        # Test dash pattern
        result = context.find_keys(r"-")
        assert len(result) == 1
        assert "other-config" in result

        # Test underscore pattern
        result = context.find_keys(r"_")
        assert len(result) == 1
        assert "config_file" in result

    def test_find_keys_numeric_pattern(self) -> None:
        """Test find_keys with numeric patterns."""
        context = Context()

        # Add test data
        context["item1"] = "value1"
        context["item2"] = "value2"
        context["test123"] = "value3"
        context["nonumber"] = "value4"

        result = context.find_keys(r"\d")

        assert len(result) == 3
        assert "item1" in result
        assert "item2" in result
        assert "test123" in result
        assert "nonumber" not in result

    def test_find_keys_case_sensitive(self) -> None:
        """Test find_keys is case sensitive."""
        context = Context()

        # Add test data
        context["Test"] = "value1"
        context["test"] = "value2"
        context["TEST"] = "value3"
        context["other"] = "value4"

        result = context.find_keys("test")

        assert len(result) == 1
        assert "test" in result
        assert "Test" not in result
        assert "TEST" not in result

    def test_find_keys_case_insensitive(self) -> None:
        """Test find_keys with case insensitive pattern."""
        context = Context()

        # Add test data
        context["Test"] = "value1"
        context["test"] = "value2"
        context["TEST"] = "value3"
        context["other"] = "value4"

        result = context.find_keys("(?i)test")

        assert len(result) == 3
        assert "Test" in result
        assert "test" in result
        assert "TEST" in result
        assert "other" not in result

    def test_find_keys_with_computed_properties(self) -> None:
        """Test find_keys includes computed properties."""
        context = Context()

        # Add regular data
        context["regular_key"] = "value"

        # Add computed property
        context.add_computed_property("computed_key", lambda ctx: "computed_value")

        result = context.find_keys("key")

        assert len(result) == 2
        assert "regular_key" in result
        assert "computed_key" in result

    def test_find_keys_layered_context(self) -> None:
        """Test find_keys with layered context."""
        context = Context()

        # Add base layer
        context["base_key"] = "base_value"
        context["shared_key"] = "base_shared"

        # Add new layer
        context.push_layer()
        context["layer_key"] = "layer_value"
        context["shared_key"] = "layer_shared"  # Override

        result = context.find_keys("key")

        # Should find all unique keys
        assert len(result) == 3
        assert "base_key" in result
        assert "layer_key" in result
        assert "shared_key" in result

    def test_find_keys_invalid_regex(self) -> None:
        """Test find_keys with invalid regex pattern."""
        context = Context()

        # Add test data
        context["test_key"] = "value"

        # Use invalid regex pattern
        result = context.find_keys("[invalid")

        assert isinstance(result, list)
        assert len(result) == 0

    def test_find_keys_complex_pattern(self) -> None:
        """Test find_keys with complex regex pattern."""
        context = Context()

        # Add test data
        context["config_1"] = "value1"
        context["config_2"] = "value2"
        context["config_test"] = "value3"
        context["other_config"] = "value4"
        context["configurable"] = "value5"

        # Pattern for config followed by underscore and digit
        result = context.find_keys(r"^config_\d+$")

        assert len(result) == 2
        assert "config_1" in result
        assert "config_2" in result
        assert "config_test" not in result
        assert "other_config" not in result
        assert "configurable" not in result

    def test_find_keys_empty_pattern(self) -> None:
        """Test find_keys with empty pattern."""
        context = Context()

        # Add test data
        context["key1"] = "value1"
        context["key2"] = "value2"

        result = context.find_keys("")

        # Empty pattern should match all keys
        assert len(result) == 2
        assert "key1" in result
        assert "key2" in result

    def test_find_keys_return_order(self) -> None:
        """Test find_keys returns keys in consistent order."""
        context = Context()

        # Add test data in specific order
        context["key_3"] = "value3"
        context["key_1"] = "value1"
        context["key_2"] = "value2"

        result = context.find_keys("key_")

        # Should return all keys
        assert len(result) == 3
        assert set(result) == {"key_1", "key_2", "key_3"}

    def test_find_keys_all_match(self) -> None:
        """Test find_keys when all keys match."""
        context = Context()

        # Add test data with common pattern
        context["test_one"] = "value1"
        context["test_two"] = "value2"
        context["test_three"] = "value3"

        result = context.find_keys("test_")

        assert len(result) == 3
        assert "test_one" in result
        assert "test_two" in result
        assert "test_three" in result
