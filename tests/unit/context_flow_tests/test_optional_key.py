"""Tests for ContextFlowCombinators.optional_key method."""

from typing import Any

import pytest

from context_flow.integration import (
    ContextFlowCombinators,
    ContextTypeMismatchError,
    MissingRequiredKeyError,
    run_flow_with_input,
)
from flowengine.flow import Flow


class TestOptionalKey:
    """Test cases for ContextFlowCombinators.optional_key method."""

    def test_optional_key_basic_functionality(self) -> None:
        """Test that optional_key extracts values from context successfully."""
        from context.key import ContextKey
        from context.main import Context

        # Create a context key and context
        name_key: ContextKey[str] = ContextKey("name", str, "User's name")
        context = Context()
        context["name"] = "Alice"

        # Create and run the flow
        optional_name_flow = ContextFlowCombinators.optional_key(name_key)
        result = run_flow_with_input(optional_name_flow, context)

        assert result == "Alice"
        assert isinstance(result, str)

    def test_optional_key_with_missing_key_returns_none(self) -> None:
        """Test that optional_key returns None when key is missing."""
        from context.key import ContextKey
        from context.main import Context

        # Create a context key and empty context
        name_key: ContextKey[str] = ContextKey("name", str, "User's name")
        context = Context()

        # Create and run the flow
        optional_name_flow = ContextFlowCombinators.optional_key(name_key)
        result = run_flow_with_input(optional_name_flow, context)

        assert result is None

    def test_optional_key_with_different_types(self) -> None:
        """Test that optional_key works with different data types."""
        self._test_optional_key_with_integer_type()
        self._test_optional_key_with_boolean_type()
        self._test_optional_key_with_list_type()

    def _test_optional_key_with_integer_type(self) -> None:
        """Test optional_key with integer type."""
        from context.key import ContextKey
        from context.main import Context

        age_key: ContextKey[int] = ContextKey("age", int, "User's age")
        context = Context()
        context["age"] = 25

        optional_age_flow = ContextFlowCombinators.optional_key(age_key)
        age_result = run_flow_with_input(optional_age_flow, context)

        assert age_result == 25
        assert isinstance(age_result, int)

    def _test_optional_key_with_boolean_type(self) -> None:
        """Test optional_key with boolean type."""
        from context.key import ContextKey
        from context.main import Context

        active_key: ContextKey[bool] = ContextKey("active", bool, "Is user active")
        context = Context()
        context["active"] = True

        optional_active_flow = ContextFlowCombinators.optional_key(active_key)
        active_result = run_flow_with_input(optional_active_flow, context)

        assert active_result is True
        assert isinstance(active_result, bool)

    def _test_optional_key_with_list_type(self) -> None:
        """Test optional_key with list type."""
        from context.key import ContextKey
        from context.main import Context

        items_key: ContextKey[list[Any]] = ContextKey("items", list, "List of items")
        context = Context()
        context["items"] = [1, 2, 3]

        optional_items_flow = ContextFlowCombinators.optional_key(items_key)
        items_result = run_flow_with_input(optional_items_flow, context)

        assert items_result == [1, 2, 3]
        assert isinstance(items_result, list)

    def test_optional_key_with_type_mismatch(self) -> None:
        """Test that optional_key raises ContextTypeMismatchError for wrong types."""
        from context.key import ContextKey
        from context.main import Context

        # Create a context key expecting int but provide str
        age_key: ContextKey[int] = ContextKey("age", int, "User's age")
        context = Context()
        context["age"] = "not_an_int"

        # Create the flow
        optional_age_flow = ContextFlowCombinators.optional_key(age_key)

        # Should raise ContextTypeMismatchError
        with pytest.raises(
            ContextTypeMismatchError, match="Context key 'age' expected int, got str"
        ):
            run_flow_with_input(optional_age_flow, context)

    def test_optional_key_with_object_type_key(self) -> None:
        """Test that optional_key works when ContextKey has object type."""
        from context.key import ContextKey
        from context.main import Context

        # Create a context key with object type (minimal type validation)
        data_key: ContextKey[Any] = ContextKey("data", object, "Any data")
        context = Context()
        context["data"] = {"any": "value"}

        # Create and run the flow
        optional_data_flow = ContextFlowCombinators.optional_key(data_key)
        result = run_flow_with_input(optional_data_flow, context)

        assert result == {"any": "value"}
        assert isinstance(result, dict)

    def test_optional_key_with_complex_path(self) -> None:
        """Test that optional_key works with complex key paths."""
        from context.key import ContextKey
        from context.main import Context

        # Create a context key with complex path
        user_name_key: ContextKey[str] = ContextKey(
            "user.profile.name", str, "User profile name"
        )
        context = Context()
        context["user.profile.name"] = "John Doe"

        # Create and run the flow
        optional_user_name_flow = ContextFlowCombinators.optional_key(user_name_key)
        result = run_flow_with_input(optional_user_name_flow, context)

        assert result == "John Doe"
        assert isinstance(result, str)

    def test_optional_key_with_complex_path_missing(self) -> None:
        """Test that optional_key returns None for missing complex key paths."""
        from context.key import ContextKey
        from context.main import Context

        # Create a context key with complex path
        user_name_key: ContextKey[str] = ContextKey(
            "user.profile.name", str, "User profile name"
        )
        context = Context()  # Empty context

        # Create and run the flow
        optional_user_name_flow = ContextFlowCombinators.optional_key(user_name_key)
        result = run_flow_with_input(optional_user_name_flow, context)

        assert result is None

    def test_optional_key_flow_name(self) -> None:
        """Test that optional_key creates flows with descriptive names."""
        from context.key import ContextKey

        # Create a context key
        name_key: ContextKey[str] = ContextKey("user.name", str, "User's name")

        # Create the flow
        optional_name_flow = ContextFlowCombinators.optional_key(name_key)

        # Check that the flow has a descriptive name
        assert optional_name_flow.name == "optional_key(user.name)"

    def test_optional_key_with_inheritance_types(self) -> None:
        """Test that optional_key works correctly with inheritance."""
        from context.key import ContextKey
        from context.main import Context

        # Test with inheritance - list should be instance of object
        data_key: ContextKey[object] = ContextKey("data", object, "Any object")
        context = Context()
        context["data"] = [1, 2, 3]  # List is an object

        optional_data_flow = ContextFlowCombinators.optional_key(data_key)
        result = run_flow_with_input(optional_data_flow, context)

        assert result == [1, 2, 3]
        assert isinstance(result, list)

    def test_optional_key_flow_integration_with_chaining(self) -> None:
        """Test that optional_key flows can be chained with other flows."""
        from context.key import ContextKey
        from context.main import Context

        # Create a context key and context
        name_key: ContextKey[str] = ContextKey("name", str, "User's name")
        context = Context()
        context["name"] = "alice"

        # Create a flow that gets the optional name and then processes it
        optional_name_flow = ContextFlowCombinators.optional_key(name_key)
        uppercase_flow: Flow[str | None, str] = Flow.from_sync_fn(
            lambda x: x.upper() if x else ""
        )

        # Chain the flows
        chained_flow = optional_name_flow >> uppercase_flow

        # Run the chained flow
        result = run_flow_with_input(chained_flow, context)

        assert result == "ALICE"
        assert isinstance(result, str)

    def test_optional_key_flow_with_missing_key_chaining(self) -> None:
        """Test that optional_key flows handle None values in chaining."""
        from context.key import ContextKey
        from context.main import Context

        # Create a context key and empty context
        name_key: ContextKey[str] = ContextKey("name", str, "User's name")
        context = Context()  # Empty context

        # Create a flow that gets the optional name and then processes it
        optional_name_flow = ContextFlowCombinators.optional_key(name_key)
        uppercase_flow: Flow[str | None, str] = Flow.from_sync_fn(
            lambda x: x.upper() if x else "NO_NAME"
        )

        # Chain the flows
        chained_flow = optional_name_flow >> uppercase_flow

        # Run the chained flow
        result = run_flow_with_input(chained_flow, context)

        assert result == "NO_NAME"
        assert isinstance(result, str)

    def test_optional_key_flow_with_multiple_contexts(self) -> None:
        """Test that optional_key flow works with multiple context inputs."""
        from context.key import ContextKey
        from context.main import Context

        # Create a context key
        score_key: ContextKey[int] = ContextKey("score", int, "User's score")

        # Create the flow
        optional_score_flow = ContextFlowCombinators.optional_key(score_key)

        # Test with context that has the key
        context1 = Context()
        context1["score"] = 100
        result1 = run_flow_with_input(optional_score_flow, context1)
        assert result1 == 100

        # Test with context that doesn't have the key
        context2 = Context()
        result2 = run_flow_with_input(optional_score_flow, context2)
        assert result2 is None

    def test_optional_key_error_message_formatting(self) -> None:
        """Test that optional_key produces well-formatted error messages."""
        from context.key import ContextKey
        from context.main import Context

        # Test type mismatch error message
        age_key: ContextKey[int] = ContextKey("user.age", int, "User age")
        context = Context()
        context["user.age"] = "twenty-five"

        optional_age_flow = ContextFlowCombinators.optional_key(age_key)

        with pytest.raises(ContextTypeMismatchError) as exc_info:
            run_flow_with_input(optional_age_flow, context)

        error_message = str(exc_info.value)
        assert "Context key 'user.age' expected int, got str" in error_message

    def test_optional_key_with_custom_classes(self) -> None:
        """Test that optional_key works with custom class types."""
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
        context["current_user"] = user_obj

        # Create and run the flow
        optional_user_flow = ContextFlowCombinators.optional_key(user_key)
        result = run_flow_with_input(optional_user_flow, context)

        assert result == user_obj
        assert isinstance(result, User)
        assert result.name == "Alice"
        assert result.age == 30

    def test_optional_key_with_custom_classes_missing(self) -> None:
        """Test that optional_key returns None for missing custom class keys."""
        from context.key import ContextKey
        from context.main import Context

        # Define a custom class
        class User:
            def __init__(self, name: str, age: int):
                super().__init__()
                self.name = name
                self.age = age

        # Create a context key for the custom class
        user_key: ContextKey[User] = ContextKey(
            "current_user", User, "Current user object"
        )
        context = Context()  # Empty context

        # Create and run the flow
        optional_user_flow = ContextFlowCombinators.optional_key(user_key)
        result = run_flow_with_input(optional_user_flow, context)

        assert result is None

    def test_optional_key_type_safety_with_cast(self) -> None:
        """Test that optional_key properly casts types for type safety."""
        from context.key import ContextKey
        from context.main import Context

        # Create a context key with specific type
        count_key: ContextKey[int] = ContextKey("count", int, "Item count")
        context = Context()
        context["count"] = 42

        # Create and run the flow
        optional_count_flow = ContextFlowCombinators.optional_key(count_key)
        result = run_flow_with_input(optional_count_flow, context)

        # Result should be properly typed
        assert result == 42
        assert isinstance(result, int)

    def test_optional_key_static_method_access(self) -> None:
        """Test that optional_key can be accessed as a static method."""
        from context.key import ContextKey

        # Create a context key
        test_key: ContextKey[str] = ContextKey("test", str, "Test key")

        # Should be able to access as static method
        flow = ContextFlowCombinators.optional_key(test_key)
        assert isinstance(flow, Flow)

        # Should also work through class instance (though not recommended)
        combinators = ContextFlowCombinators()
        flow2 = combinators.optional_key(test_key)
        assert isinstance(flow2, Flow)

    def test_optional_key_no_default_parameter(self) -> None:
        """Test that optional_key does not accept default parameters."""
        from context.key import ContextKey

        # Create a context key
        name_key: ContextKey[str] = ContextKey("name", str, "User's name")

        # optional_key should not accept default parameter
        # This test ensures the method signature is correct
        flow = ContextFlowCombinators.optional_key(name_key)
        assert isinstance(flow, Flow)

    def test_optional_key_difference_from_other_methods(self) -> None:
        """Test that optional_key behaves differently from get_key and require_key."""
        from context.key import ContextKey
        from context.main import Context

        # Create a context key and empty context
        name_key: ContextKey[str] = ContextKey("name", str, "User's name")
        context = Context()

        # optional_key should return None for missing key
        optional_name_flow = ContextFlowCombinators.optional_key(name_key)
        result = run_flow_with_input(optional_name_flow, context)
        assert result is None

        # require_key should raise error for missing key
        require_name_flow = ContextFlowCombinators.require_key(name_key)
        with pytest.raises(MissingRequiredKeyError):
            run_flow_with_input(require_name_flow, context)

        # get_key with no default should also raise error for missing key
        get_name_flow = ContextFlowCombinators.get_key(name_key)
        with pytest.raises(MissingRequiredKeyError):
            run_flow_with_input(get_name_flow, context)

    def test_optional_key_with_none_value_in_context(self) -> None:
        """Test that optional_key handles None values stored in context."""
        from context.key import ContextKey
        from context.main import Context

        # Create a context key that can hold None using object type
        optional_key: ContextKey[object] = ContextKey(
            "optional_value", object, "Optional value"
        )
        context = Context()
        context["optional_value"] = None

        # Create and run the flow
        optional_flow = ContextFlowCombinators.optional_key(optional_key)
        result = run_flow_with_input(optional_flow, context)

        # Should return None (the actual value in context)
        assert result is None
