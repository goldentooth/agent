"""Tests for ContextFlowCombinators.set_key method."""

from typing import Any

import pytest

from context_flow.integration import (
    ContextFlowCombinators,
    ContextTypeMismatchError,
    run_flow_with_input,
)
from flowengine.flow import Flow


class TestSetKey:
    """Test cases for ContextFlowCombinators.set_key method."""

    def test_set_key_basic_functionality(self) -> None:
        """Test that set_key creates a new context with the key set."""
        from context.key import ContextKey
        from context.main import Context

        # Create a context key and context
        name_key: ContextKey[str] = ContextKey("name", str, "User's name")
        context = Context()

        # Create and run the flow
        set_name_flow = ContextFlowCombinators.set_key(name_key, "Alice")
        result = run_flow_with_input(set_name_flow, context)

        # Check that the result is a new context with the key set
        assert result["name"] == "Alice"
        assert isinstance(result, Context)
        # Original context should be unchanged
        assert "name" not in context

    def test_set_key_with_different_types(self) -> None:
        """Test that set_key works with different data types."""
        self._test_set_key_with_integer_type()
        self._test_set_key_with_boolean_type()
        self._test_set_key_with_list_type()

    def _test_set_key_with_integer_type(self) -> None:
        """Test set_key with integer type."""
        from context.key import ContextKey
        from context.main import Context

        age_key: ContextKey[int] = ContextKey("age", int, "User's age")
        context = Context()

        set_age_flow = ContextFlowCombinators.set_key(age_key, 25)
        result = run_flow_with_input(set_age_flow, context)

        assert result["age"] == 25
        assert isinstance(result["age"], int)

    def _test_set_key_with_boolean_type(self) -> None:
        """Test set_key with boolean type."""
        from context.key import ContextKey
        from context.main import Context

        active_key: ContextKey[bool] = ContextKey("active", bool, "Is user active")
        context = Context()

        set_active_flow = ContextFlowCombinators.set_key(active_key, True)
        result = run_flow_with_input(set_active_flow, context)

        assert result["active"] is True
        assert isinstance(result["active"], bool)

    def _test_set_key_with_list_type(self) -> None:
        """Test set_key with list type."""
        from context.key import ContextKey
        from context.main import Context

        items_key: ContextKey[list[Any]] = ContextKey("items", list, "List of items")
        context = Context()

        set_items_flow = ContextFlowCombinators.set_key(items_key, [1, 2, 3])
        result = run_flow_with_input(set_items_flow, context)

        assert result["items"] == [1, 2, 3]
        assert isinstance(result["items"], list)

    def test_set_key_with_type_mismatch(self) -> None:
        """Test that set_key raises ContextTypeMismatchError for wrong types."""
        from context.key import ContextKey
        from context.main import Context

        # Create a context key expecting int but try to set str
        age_key: ContextKey[int] = ContextKey("age", int, "User's age")
        context = Context()

        # Should raise ContextTypeMismatchError
        with pytest.raises(
            ContextTypeMismatchError,
            match="Value for context key 'age' expected int, got str",
        ):
            set_age_flow = ContextFlowCombinators.set_key(age_key, "not_an_int")  # type: ignore[misc]
            run_flow_with_input(set_age_flow, context)

    def test_set_key_with_existing_context_data(self) -> None:
        """Test that set_key preserves existing context data."""
        from context.key import ContextKey
        from context.main import Context

        # Create context with existing data
        context = Context()
        context["existing_key"] = "existing_value"

        # Create and run the flow to set a new key
        name_key: ContextKey[str] = ContextKey("name", str, "User's name")
        set_name_flow = ContextFlowCombinators.set_key(name_key, "Alice")
        result = run_flow_with_input(set_name_flow, context)

        # Both keys should be present in the result
        assert result["name"] == "Alice"
        assert result["existing_key"] == "existing_value"

    def test_set_key_with_complex_path(self) -> None:
        """Test that set_key works with complex key paths."""
        from context.key import ContextKey
        from context.main import Context

        # Create a context key with complex path
        user_name_key: ContextKey[str] = ContextKey(
            "user.profile.name", str, "User profile name"
        )
        context = Context()

        # Create and run the flow
        set_user_name_flow = ContextFlowCombinators.set_key(user_name_key, "John Doe")
        result = run_flow_with_input(set_user_name_flow, context)

        assert result["user.profile.name"] == "John Doe"
        assert isinstance(result["user.profile.name"], str)

    def test_set_key_flow_name(self) -> None:
        """Test that set_key creates flows with descriptive names."""
        from context.key import ContextKey

        # Create a context key
        name_key: ContextKey[str] = ContextKey("user.name", str, "User's name")

        # Create the flow
        set_name_flow = ContextFlowCombinators.set_key(name_key, "Alice")

        # Check that the flow has a descriptive name
        assert set_name_flow.name == "set_key(user.name)"

    def test_set_key_with_none_value(self) -> None:
        """Test that set_key handles None values correctly."""
        from context.key import ContextKey
        from context.main import Context

        # Create a context key that can accept None (union type)
        optional_key: ContextKey[str | None] = ContextKey(
            "optional", str, "Optional value"
        )
        context = Context()

        # Create and run the flow with None value
        set_optional_flow = ContextFlowCombinators.set_key(optional_key, None)
        result = run_flow_with_input(set_optional_flow, context)

        assert result["optional"] is None

    def test_set_key_flow_integration_with_chaining(self) -> None:
        """Test that set_key flows can be chained with other flows."""
        from context.key import ContextKey
        from context.main import Context

        # Create context keys
        name_key: ContextKey[str] = ContextKey("name", str, "User's name")
        age_key: ContextKey[int] = ContextKey("age", int, "User's age")
        context = Context()

        # Create flows to set multiple keys
        set_name_flow = ContextFlowCombinators.set_key(name_key, "Alice")
        set_age_flow = ContextFlowCombinators.set_key(age_key, 30)

        # Chain the flows
        chained_flow = set_name_flow >> set_age_flow

        # Run the chained flow
        result = run_flow_with_input(chained_flow, context)

        # Both keys should be set in the result
        assert result["name"] == "Alice"
        assert result["age"] == 30

    def test_set_key_with_custom_classes(self) -> None:
        """Test that set_key works with custom class types."""
        from context.key import ContextKey
        from context.main import Context

        # Define a custom class
        class User:
            def __init__(self, name: str, age: int):
                super().__init__()
                self.name = name
                self.age = age

            def __eq__(self, other: object) -> bool:
                return (
                    isinstance(other, User)
                    and self.name == other.name
                    and self.age == other.age
                )

        # Create a context key for the custom class
        user_key: ContextKey[User] = ContextKey(
            "current_user", User, "Current user object"
        )
        context = Context()
        user_obj = User("Alice", 30)

        # Create and run the flow
        set_user_flow = ContextFlowCombinators.set_key(user_key, user_obj)
        result = run_flow_with_input(set_user_flow, context)

        assert result["current_user"] == user_obj
        assert isinstance(result["current_user"], User)
        assert result["current_user"].name == "Alice"
        assert result["current_user"].age == 30

    def test_set_key_immutability(self) -> None:
        """Test that set_key creates new contexts without modifying the original."""
        from context.key import ContextKey
        from context.main import Context

        # Create original context with some data
        original_context = Context()
        original_context["original_key"] = "original_value"

        # Create a new key to set
        new_key: ContextKey[str] = ContextKey("new_key", str, "New key")

        # Create and run the flow
        set_new_key_flow = ContextFlowCombinators.set_key(new_key, "new_value")
        result_context = run_flow_with_input(set_new_key_flow, original_context)

        # Original context should be unchanged
        assert "new_key" not in original_context
        assert original_context["original_key"] == "original_value"

        # Result context should have both keys
        assert result_context["new_key"] == "new_value"
        assert result_context["original_key"] == "original_value"

    def test_set_key_static_method_access(self) -> None:
        """Test that set_key can be accessed as a static method."""
        from context.key import ContextKey

        # Create a context key
        test_key: ContextKey[str] = ContextKey("test", str, "Test key")

        # Should be able to access as static method
        flow = ContextFlowCombinators.set_key(test_key, "test_value")
        assert isinstance(flow, Flow)

        # Should also work through class instance (though not recommended)
        combinators = ContextFlowCombinators()
        flow2 = combinators.set_key(test_key, "test_value")
        assert isinstance(flow2, Flow)

    def test_set_key_with_overwrite_existing_key(self) -> None:
        """Test that set_key overwrites existing keys properly."""
        from context.key import ContextKey
        from context.main import Context

        # Create context with existing key
        context = Context()
        context["name"] = "Original Name"

        # Create flow to overwrite the key
        name_key: ContextKey[str] = ContextKey("name", str, "User's name")
        set_name_flow = ContextFlowCombinators.set_key(name_key, "New Name")
        result = run_flow_with_input(set_name_flow, context)

        # Key should be overwritten in result
        assert result["name"] == "New Name"
        # Original context should be unchanged
        assert context["name"] == "Original Name"
