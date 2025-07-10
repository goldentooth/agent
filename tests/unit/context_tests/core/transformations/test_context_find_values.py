"""Tests for Context.find_values method."""

from context.main import Context


class TestContextFindValues:
    """Test suite for Context.find_values method."""

    def test_find_values_empty_context(self) -> None:
        """Test find_values on empty context."""
        context = Context()

        result = context.find_values(lambda v: True)

        assert isinstance(result, dict)
        assert len(result) == 0

    def test_find_values_no_matches(self) -> None:
        """Test find_values with predicate that matches no values."""
        context = Context()

        # Add test data
        context["key1"] = "value1"
        context["key2"] = "value2"
        context["key3"] = "value3"

        result = context.find_values(lambda v: v == "nonexistent")

        assert isinstance(result, dict)
        assert len(result) == 0

    def test_find_values_string_type(self) -> None:
        """Test find_values with string type predicate."""
        context = Context()

        # Add test data with different types
        context["str_key"] = "hello"
        context["int_key"] = 42
        context["list_key"] = [1, 2, 3]
        context["str_key2"] = "world"

        result = context.find_values(lambda v: isinstance(v, str))

        assert len(result) == 2
        assert result["str_key"] == "hello"
        assert result["str_key2"] == "world"
        assert "int_key" not in result
        assert "list_key" not in result

    def test_find_values_numeric_type(self) -> None:
        """Test find_values with numeric type predicate."""
        context = Context()

        # Add test data with different types
        context["int_key"] = 42
        context["float_key"] = 3.14
        context["str_key"] = "hello"
        context["bool_key"] = True

        result = context.find_values(
            lambda v: isinstance(v, (int, float)) and not isinstance(v, bool)
        )

        assert len(result) == 2
        assert result["int_key"] == 42
        assert result["float_key"] == 3.14
        assert "str_key" not in result
        assert "bool_key" not in result

    def test_find_values_value_range(self) -> None:
        """Test find_values with value range predicate."""
        context = Context()

        # Add test data
        context["small"] = 5
        context["medium"] = 15
        context["large"] = 25
        context["string"] = "not a number"

        result = context.find_values(lambda v: isinstance(v, int) and 10 <= v <= 20)

        assert len(result) == 1
        assert result["medium"] == 15

    def test_find_values_string_content(self) -> None:
        """Test find_values with string content predicate."""
        context = Context()

        # Add test data
        context["email"] = "user@example.com"
        context["name"] = "John Doe"
        context["address"] = "123 Main St"
        context["phone"] = "555-1234"

        result = context.find_values(lambda v: isinstance(v, str) and "@" in v)

        assert len(result) == 1
        assert result["email"] == "user@example.com"

    def test_find_values_list_length(self) -> None:
        """Test find_values with list length predicate."""
        context = Context()

        # Add test data
        context["short"] = [1, 2]
        context["medium"] = [1, 2, 3, 4]
        context["long"] = [1, 2, 3, 4, 5, 6]
        context["string"] = "not a list"

        result = context.find_values(lambda v: isinstance(v, list) and len(v) > 3)

        assert len(result) == 2
        assert result["medium"] == [1, 2, 3, 4]
        assert result["long"] == [1, 2, 3, 4, 5, 6]

    def test_find_values_none_values(self) -> None:
        """Test find_values with None values."""
        context = Context()

        # Add test data
        context["has_value"] = "value"
        context["is_none"] = None
        context["is_empty"] = ""
        context["is_zero"] = 0

        result = context.find_values(lambda v: v is None)

        assert len(result) == 1
        assert result["is_none"] is None

    def test_find_values_truthy_values(self) -> None:
        """Test find_values with truthy predicate."""
        context = Context()

        # Add test data
        context["truthy_str"] = "hello"
        context["truthy_int"] = 42
        context["truthy_list"] = [1, 2, 3]
        context["falsy_str"] = ""
        context["falsy_int"] = 0
        context["falsy_list"] = []
        context["falsy_none"] = None

        result = context.find_values(lambda v: bool(v))

        assert len(result) == 3
        assert result["truthy_str"] == "hello"
        assert result["truthy_int"] == 42
        assert result["truthy_list"] == [1, 2, 3]

    def test_find_values_with_computed_properties(self) -> None:
        """Test find_values includes computed properties."""
        context = Context()

        # Add regular data
        context["regular_str"] = "regular"
        context["regular_int"] = 42

        # Add computed property
        context.add_computed_property("computed_str", lambda ctx: "computed")
        context.add_computed_property("computed_int", lambda ctx: 100)

        result = context.find_values(lambda v: isinstance(v, str))

        assert len(result) == 2
        assert result["regular_str"] == "regular"
        assert result["computed_str"] == "computed"

    def test_find_values_layered_context(self) -> None:
        """Test find_values with layered context."""
        context = Context()

        # Add base layer
        context["base_str"] = "base"
        context["shared_key"] = "base_value"

        # Add new layer
        context.push_layer()
        context["layer_str"] = "layer"
        context["shared_key"] = "layer_value"  # Override

        result = context.find_values(lambda v: isinstance(v, str))

        # Should find all string values with layer overrides
        assert len(result) == 3
        assert result["base_str"] == "base"
        assert result["layer_str"] == "layer"
        assert result["shared_key"] == "layer_value"  # Layer override

    def test_find_values_complex_predicate(self) -> None:
        """Test find_values with complex predicate."""
        context = Context()

        # Add test data
        context["user1"] = {"name": "Alice", "age": 25}
        context["user2"] = {"name": "Bob", "age": 30}
        context["user3"] = {"name": "Charlie", "age": 17}
        context["not_user"] = "not a dict"

        result = context.find_values(
            lambda v: isinstance(v, dict)
            and "age" in v
            and isinstance(v["age"], int)
            and v["age"] >= 18
        )

        assert len(result) == 2
        assert result["user1"]["name"] == "Alice"
        assert result["user2"]["name"] == "Bob"
        assert "user3" not in result

    def test_find_values_exception_handling(self) -> None:
        """Test find_values handles predicate exceptions gracefully."""
        context = Context()

        # Add test data
        context["good_key"] = "good_value"
        context["bad_key"] = "bad_value"

        def risky_predicate(value: str) -> bool:
            if value == "bad_value":
                raise ValueError("Test exception")
            return value == "good_value"

        result = context.find_values(risky_predicate)

        # Should handle exception gracefully and continue
        assert len(result) == 1
        assert result["good_key"] == "good_value"

    def test_find_values_all_match(self) -> None:
        """Test find_values when all values match."""
        context = Context()

        # Add test data
        context["str1"] = "hello"
        context["str2"] = "world"
        context["str3"] = "test"

        result = context.find_values(lambda v: isinstance(v, str))

        assert len(result) == 3
        assert result["str1"] == "hello"
        assert result["str2"] == "world"
        assert result["str3"] == "test"

    def test_find_values_return_type(self) -> None:
        """Test that find_values returns correct type."""
        context = Context()

        context["key"] = "value"

        result = context.find_values(lambda v: True)

        assert isinstance(result, dict)
        assert all(isinstance(k, str) for k in result.keys())

    def test_find_values_empty_predicate_result(self) -> None:
        """Test find_values with predicate that never returns True."""
        context = Context()

        # Add test data
        context["key1"] = "value1"
        context["key2"] = "value2"

        result = context.find_values(lambda v: False)

        assert isinstance(result, dict)
        assert len(result) == 0

    def test_find_values_excludes_computed_false(self) -> None:
        """Test find_values with include_computed=False."""
        context = Context()

        # Add regular data
        context["regular"] = "regular_value"

        # Add computed property
        context.add_computed_property("computed", lambda ctx: "computed_value")

        # Note: find_values uses query with default include_computed=True
        # This test verifies the default behavior
        result = context.find_values(lambda v: isinstance(v, str))

        assert len(result) == 2
        assert result["regular"] == "regular_value"
        assert result["computed"] == "computed_value"

    def test_find_values_with_transformation(self) -> None:
        """Test find_values with transformed values."""
        context = Context()

        # Add transformation
        context.add_transformation("name", str.upper)

        # Set values
        context["name"] = "alice"
        context["other"] = "bob"

        result = context.find_values(lambda v: isinstance(v, str))

        # Transformations are now applied to get() results
        assert len(result) == 2
        assert result["name"] == "ALICE"  # Transformed by get()
        assert result["other"] == "bob"
