"""Tests for Context.query method."""

from context.main import Context


class TestContextQuery:
    """Test suite for Context.query method."""

    def test_query_empty_context(self) -> None:
        """Test query on empty context."""
        context = Context()

        result = context.query()

        assert isinstance(result, dict)
        assert len(result) == 0

    def test_query_no_filters(self) -> None:
        """Test query with no filters returns all data."""
        context = Context()

        # Add test data
        context["key1"] = "value1"
        context["key2"] = 42
        context["key3"] = [1, 2, 3]

        result = context.query()

        assert len(result) == 3
        assert result["key1"] == "value1"
        assert result["key2"] == 42
        assert result["key3"] == [1, 2, 3]

    def test_query_pattern_filter_basic(self) -> None:
        """Test query with regex pattern filter."""
        context = Context()

        # Add test data with various patterns
        context["user_name"] = "alice"
        context["user_age"] = 30
        context["data_value"] = "test"
        context["config_path"] = "/etc/config"

        # Query for keys starting with "user"
        result = context.query(pattern=r"^user")

        assert len(result) == 2
        assert "user_name" in result
        assert "user_age" in result
        assert "data_value" not in result
        assert "config_path" not in result

    def test_query_pattern_filter_complex(self) -> None:
        """Test query with complex regex patterns."""
        context = Context()

        # Add test data
        context["test1"] = "value1"
        context["test2"] = "value2"
        context["other"] = "value3"
        context["test_special"] = "value4"

        # Query for keys containing numbers
        result = context.query(pattern=r"\d")

        assert len(result) == 2
        assert result["test1"] == "value1"
        assert result["test2"] == "value2"

    def test_query_invalid_pattern(self) -> None:
        """Test query with invalid regex pattern."""
        context = Context()

        context["key"] = "value"

        # Use invalid regex pattern
        result = context.query(pattern="[invalid")

        assert len(result) == 0

    def test_query_key_filter(self) -> None:
        """Test query with key filter function."""
        context = Context()

        # Add test data
        context["short"] = "value1"
        context["medium_key"] = "value2"
        context["very_long_key_name"] = "value3"

        # Filter for keys with length > 5
        result = context.query(key_filter=lambda k: len(k) > 5)

        assert len(result) == 2
        assert "medium_key" in result
        assert "very_long_key_name" in result
        assert "short" not in result

    def test_query_value_filter(self) -> None:
        """Test query with value filter function."""
        context = Context()

        # Add test data with different types
        context["str_key"] = "hello"
        context["int_key"] = 42
        context["list_key"] = [1, 2, 3]
        context["none_key"] = None

        # Filter for string values
        result = context.query(value_filter=lambda v: isinstance(v, str))

        assert len(result) == 1
        assert result["str_key"] == "hello"

    def test_query_combined_filters(self) -> None:
        """Test query with multiple filters combined."""
        context = Context()

        # Add test data
        context["user_name"] = "alice"
        context["user_count"] = 5
        context["admin_name"] = "bob"
        context["admin_count"] = 3

        # Combine pattern and value filters
        result = context.query(
            pattern=r"_name$", value_filter=lambda v: len(str(v)) > 3
        )

        assert len(result) == 1
        assert result["user_name"] == "alice"

    def test_query_include_computed_true(self) -> None:
        """Test query including computed properties."""
        context = Context()

        # Add regular data
        context["base"] = 10

        # Add computed property
        context.add_computed_property("computed", lambda ctx: ctx.get("base", 0) * 2)

        result = context.query(include_computed=True)

        assert len(result) == 2
        assert result["base"] == 10
        assert result["computed"] == 20

    def test_query_include_computed_false(self) -> None:
        """Test query excluding computed properties."""
        context = Context()

        # Add regular data
        context["base"] = 10

        # Add computed property
        context.add_computed_property("computed", lambda ctx: ctx.get("base", 0) * 2)

        result = context.query(include_computed=False)

        assert len(result) == 1
        assert result["base"] == 10
        assert "computed" not in result

    def test_query_with_transformations(self) -> None:
        """Test query with transformed values."""
        context = Context()

        # Add transformation
        context.add_transformation("name", str.upper)

        # Set values
        context["name"] = "alice"
        context["other"] = "bob"

        result = context.query()

        # Note: transformations don't affect get() results in current implementation
        assert len(result) == 2
        assert result["name"] == "alice"  # Not transformed by get()
        assert result["other"] == "bob"

    def test_query_layered_context(self) -> None:
        """Test query with layered context frames."""
        context = Context()

        # Add base layer data
        context["key1"] = "base_value"
        context["key2"] = "shared"

        # Push new layer and override
        context.push_layer()
        context["key2"] = "layer_value"
        context["key3"] = "new_value"

        result = context.query()

        assert len(result) == 3
        assert result["key1"] == "base_value"
        assert result["key2"] == "layer_value"  # Layer override
        assert result["key3"] == "new_value"

    def test_query_error_handling(self) -> None:
        """Test query handles key access errors gracefully."""
        context = Context()

        # Add normal key
        context["normal"] = "value"

        # Add computed property that raises an exception
        context.add_computed_property("error_prop", lambda ctx: 1 / 0)

        # Query should handle the error gracefully
        result = context.query()

        # Should include normal key but skip the error property
        assert "normal" in result
        assert result["normal"] == "value"

    def test_query_pattern_matching_variations(self) -> None:
        """Test various regex pattern matching scenarios."""
        context = Context()

        # Add test data
        context["test"] = "value1"
        context["testing"] = "value2"
        context["contest"] = "value3"
        context["best"] = "value4"

        # Test exact match pattern
        exact_match = context.query(pattern=r"^test$")
        assert len(exact_match) == 1
        assert "test" in exact_match

        # Test starts with pattern
        starts_with = context.query(pattern=r"^test")
        assert len(starts_with) == 2
        assert "test" in starts_with and "testing" in starts_with

    def test_query_return_type(self) -> None:
        """Test that query returns correct type."""
        context = Context()

        context["key"] = "value"

        result = context.query()

        assert isinstance(result, dict)
        assert all(isinstance(k, str) for k in result.keys())
