"""Tests for Context.filter_by_type method."""

from context.main import Context


class TestContextFilterByType:
    """Test suite for Context.filter_by_type method."""

    def test_filter_by_type_empty_context(self) -> None:
        """Test filter_by_type on empty context."""
        context = Context()

        result = context.filter_by_type(str)

        assert isinstance(result, dict)
        assert len(result) == 0

    def test_filter_by_type_no_matches(self) -> None:
        """Test filter_by_type with type that matches no values."""
        context = Context()

        # Add test data with different types
        context["key1"] = "value1"
        context["key2"] = 42
        context["key3"] = [1, 2, 3]

        result = context.filter_by_type(tuple)

        assert isinstance(result, dict)
        assert len(result) == 0

    def test_filter_by_type_string(self) -> None:
        """Test filter_by_type with string type."""
        context = Context()

        # Add test data with different types
        context["str_key1"] = "hello"
        context["str_key2"] = "world"
        context["int_key"] = 42
        context["list_key"] = [1, 2, 3]
        context["dict_key"] = {"a": 1}

        result = context.filter_by_type(str)

        assert len(result) == 2
        assert result["str_key1"] == "hello"
        assert result["str_key2"] == "world"
        assert "int_key" not in result
        assert "list_key" not in result
        assert "dict_key" not in result

    def test_filter_by_type_int(self) -> None:
        """Test filter_by_type with int type."""
        context = Context()

        # Add test data with different types
        context["int_key1"] = 42
        context["int_key2"] = 100
        context["str_key"] = "hello"
        context["float_key"] = 3.14
        context["bool_key"] = True  # Note: bool is subclass of int

        result = context.filter_by_type(int)

        assert len(result) == 3  # Includes bool since bool is subclass of int
        assert result["int_key1"] == 42
        assert result["int_key2"] == 100
        assert result["bool_key"] is True
        assert "str_key" not in result
        assert "float_key" not in result

    def test_filter_by_type_float(self) -> None:
        """Test filter_by_type with float type."""
        context = Context()

        # Add test data with different types
        context["float_key1"] = 3.14
        context["float_key2"] = 2.71
        context["int_key"] = 42
        context["str_key"] = "hello"

        result = context.filter_by_type(float)

        assert len(result) == 2
        assert result["float_key1"] == 3.14
        assert result["float_key2"] == 2.71
        assert "int_key" not in result
        assert "str_key" not in result

    def test_filter_by_type_bool(self) -> None:
        """Test filter_by_type with bool type."""
        context = Context()

        # Add test data with different types
        context["bool_key1"] = True
        context["bool_key2"] = False
        context["int_key"] = 42
        context["str_key"] = "hello"

        result = context.filter_by_type(bool)

        assert len(result) == 2
        assert result["bool_key1"] is True
        assert result["bool_key2"] is False
        assert "int_key" not in result
        assert "str_key" not in result

    def test_filter_by_type_list(self) -> None:
        """Test filter_by_type with list type."""
        context = Context()

        # Add test data with different types
        context["list_key1"] = [1, 2, 3]
        context["list_key2"] = ["a", "b", "c"]
        context["tuple_key"] = (1, 2, 3)
        context["str_key"] = "hello"

        result = context.filter_by_type(list)

        assert len(result) == 2
        assert result["list_key1"] == [1, 2, 3]
        assert result["list_key2"] == ["a", "b", "c"]
        assert "tuple_key" not in result
        assert "str_key" not in result

    def test_filter_by_type_dict(self) -> None:
        """Test filter_by_type with dict type."""
        context = Context()

        # Add test data with different types
        context["dict_key1"] = {"a": 1, "b": 2}
        context["dict_key2"] = {"name": "John", "age": 30}
        context["list_key"] = [1, 2, 3]
        context["str_key"] = "hello"

        result = context.filter_by_type(dict)

        assert len(result) == 2
        assert result["dict_key1"] == {"a": 1, "b": 2}
        assert result["dict_key2"] == {"name": "John", "age": 30}
        assert "list_key" not in result
        assert "str_key" not in result

    def test_filter_by_type_tuple(self) -> None:
        """Test filter_by_type with tuple type."""
        context = Context()

        # Add test data with different types
        context["tuple_key1"] = (1, 2, 3)
        context["tuple_key2"] = ("a", "b", "c")
        context["list_key"] = [1, 2, 3]
        context["str_key"] = "hello"

        result = context.filter_by_type(tuple)

        assert len(result) == 2
        assert result["tuple_key1"] == (1, 2, 3)
        assert result["tuple_key2"] == ("a", "b", "c")
        assert "list_key" not in result
        assert "str_key" not in result

    def test_filter_by_type_none(self) -> None:
        """Test filter_by_type with NoneType."""
        context = Context()

        # Add test data with different types
        context["none_key1"] = None
        context["none_key2"] = None
        context["str_key"] = "hello"
        context["int_key"] = 42

        result = context.filter_by_type(type(None))

        assert len(result) == 2
        assert result["none_key1"] is None
        assert result["none_key2"] is None
        assert "str_key" not in result
        assert "int_key" not in result

    def test_filter_by_type_with_computed_properties(self) -> None:
        """Test filter_by_type includes computed properties."""
        context = Context()

        # Add regular data
        context["regular_str"] = "regular"
        context["regular_int"] = 42

        # Add computed properties
        context.add_computed_property("computed_str", lambda ctx: "computed")
        context.add_computed_property("computed_int", lambda ctx: 100)

        result = context.filter_by_type(str)

        assert len(result) == 2
        assert result["regular_str"] == "regular"
        assert result["computed_str"] == "computed"
        assert "regular_int" not in result
        assert "computed_int" not in result

    def test_filter_by_type_layered_context(self) -> None:
        """Test filter_by_type with layered context."""
        context = Context()

        # Add base layer
        context["base_str"] = "base"
        context["base_int"] = 10
        context["shared_key"] = "base_value"

        # Add new layer
        context.push_layer()
        context["layer_str"] = "layer"
        context["layer_int"] = 20
        context["shared_key"] = 30  # Override with different type

        result = context.filter_by_type(str)

        # Should find all string values (layer overrides base)
        assert len(result) == 2
        assert result["base_str"] == "base"
        assert result["layer_str"] == "layer"
        assert "shared_key" not in result  # Now an int

    def test_filter_by_type_multiple_types(self) -> None:
        """Test filter_by_type with union of types."""
        context = Context()

        # Add test data with different types
        context["int_key"] = 42
        context["float_key"] = 3.14
        context["str_key"] = "hello"
        context["list_key"] = [1, 2, 3]

        # Filter by multiple types using tuple
        result = context.filter_by_type((int, float))

        assert len(result) == 2
        assert result["int_key"] == 42
        assert result["float_key"] == 3.14
        assert "str_key" not in result
        assert "list_key" not in result

    def test_filter_by_type_custom_class(self) -> None:
        """Test filter_by_type with custom class."""
        context = Context()

        class CustomClass:
            def __init__(self, value: str) -> None:
                super().__init__()
                self.value = value

        # Add test data with different types
        custom_obj1 = CustomClass("test1")
        custom_obj2 = CustomClass("test2")

        context["custom_key1"] = custom_obj1
        context["custom_key2"] = custom_obj2
        context["str_key"] = "hello"
        context["int_key"] = 42

        result = context.filter_by_type(CustomClass)

        assert len(result) == 2
        assert result["custom_key1"] is custom_obj1
        assert result["custom_key2"] is custom_obj2
        assert "str_key" not in result
        assert "int_key" not in result

    def test_filter_by_type_inheritance(self) -> None:
        """Test filter_by_type with inheritance."""
        context = Context()

        class BaseClass:
            def __init__(self) -> None:
                super().__init__()

        class DerivedClass(BaseClass):
            def __init__(self) -> None:
                super().__init__()

        # Add test data
        base_obj = BaseClass()
        derived_obj = DerivedClass()

        context["base_key"] = base_obj
        context["derived_key"] = derived_obj
        context["str_key"] = "hello"

        # Filter by base class should include derived instances
        result = context.filter_by_type(BaseClass)

        assert len(result) == 2
        assert result["base_key"] is base_obj
        assert result["derived_key"] is derived_obj
        assert "str_key" not in result

    def test_filter_by_type_all_match(self) -> None:
        """Test filter_by_type when all values match."""
        context = Context()

        # Add test data of same type
        context["str1"] = "hello"
        context["str2"] = "world"
        context["str3"] = "test"

        result = context.filter_by_type(str)

        assert len(result) == 3
        assert result["str1"] == "hello"
        assert result["str2"] == "world"
        assert result["str3"] == "test"

    def test_filter_by_type_return_type(self) -> None:
        """Test that filter_by_type returns correct type."""
        context = Context()

        context["key"] = "value"

        result = context.filter_by_type(str)

        assert isinstance(result, dict)
        assert all(isinstance(k, str) for k in result.keys())

    def test_filter_by_type_with_transformation(self) -> None:
        """Test filter_by_type with transformed values."""
        context = Context()

        # Add transformation
        context.add_transformation("name", str.upper)

        # Set values
        context["name"] = "alice"
        context["age"] = 30

        result = context.filter_by_type(str)

        # Note: transformations don't affect get() results in current implementation
        assert len(result) == 1
        assert result["name"] == "alice"  # Not transformed by get()
        assert "age" not in result

    def test_filter_by_type_mixed_types(self) -> None:
        """Test filter_by_type with mixed data types."""
        context = Context()

        # Add various types
        context["string"] = "hello"
        context["integer"] = 42
        context["float_val"] = 3.14
        context["boolean"] = True
        context["list_val"] = [1, 2, 3]
        context["dict_val"] = {"key": "value"}

        # Test string type
        str_result = context.filter_by_type(str)
        assert len(str_result) == 1
        assert "string" in str_result

        # Test int type (includes bool)
        int_result = context.filter_by_type(int)
        assert len(int_result) == 2
        assert "integer" in int_result
        assert "boolean" in int_result
