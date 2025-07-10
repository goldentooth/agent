"""Tests for ContextFlowCombinators.get_key method."""

from typing import Any

import pytest

from context_flow.integration import (
    ContextFlowCombinators,
    ContextTypeMismatchError,
    MissingRequiredKeyError,
    run_flow_with_input,
)
from flowengine.flow import Flow


class TestGetKey:
    """Test cases for ContextFlowCombinators.get_key method."""

    def test_get_key_basic_functionality(self) -> None:
        """Test that get_key extracts values from context successfully."""
        from context.key import ContextKey
        from context.main import Context

        # Create a context key and context
        name_key: ContextKey[str] = ContextKey("name", str, "User's name")
        context = Context()
        context["name"] = "Alice"

        # Create and run the flow
        get_name_flow = ContextFlowCombinators.get_key(name_key)
        result = run_flow_with_input(get_name_flow, context)

        assert result == "Alice"
        assert isinstance(result, str)

    def test_get_key_with_different_types(self) -> None:
        """Test that get_key works with different data types."""
        from context.key import ContextKey
        from context.main import Context

        self._test_get_key_with_integer()
        self._test_get_key_with_boolean()
        self._test_get_key_with_list()

    def _test_get_key_with_integer(self) -> None:
        """Test get_key with integer type."""
        from context.key import ContextKey
        from context.main import Context

        age_key: ContextKey[int] = ContextKey("age", int, "User's age")
        context = Context()
        context["age"] = 25

        get_age_flow = ContextFlowCombinators.get_key(age_key)
        age_result = run_flow_with_input(get_age_flow, context)

        assert age_result == 25
        assert isinstance(age_result, int)

    def _test_get_key_with_boolean(self) -> None:
        """Test get_key with boolean type."""
        from context.key import ContextKey
        from context.main import Context

        active_key: ContextKey[bool] = ContextKey("active", bool, "Is user active")
        context = Context()
        context["active"] = True

        get_active_flow = ContextFlowCombinators.get_key(active_key)
        active_result = run_flow_with_input(get_active_flow, context)

        assert active_result is True
        assert isinstance(active_result, bool)

    def _test_get_key_with_list(self) -> None:
        """Test get_key with list type."""
        from context.key import ContextKey
        from context.main import Context

        items_key: ContextKey[list[Any]] = ContextKey("items", list, "List of items")
        context = Context()
        context["items"] = [1, 2, 3]

        get_items_flow = ContextFlowCombinators.get_key(items_key)
        items_result = run_flow_with_input(get_items_flow, context)

        assert items_result == [1, 2, 3]
        assert isinstance(items_result, list)

    def test_get_key_with_missing_key_no_default(self) -> None:
        """Test that get_key raises MissingRequiredKeyError when key is missing and no default."""
        from context.key import ContextKey
        from context.main import Context

        # Create a context key and empty context
        name_key: ContextKey[str] = ContextKey("name", str, "User's name")
        context = Context()

        # Create the flow
        get_name_flow = ContextFlowCombinators.get_key(name_key)

        # Should raise MissingRequiredKeyError
        with pytest.raises(
            MissingRequiredKeyError, match="Required context key 'name' is missing"
        ):
            run_flow_with_input(get_name_flow, context)

    def test_get_key_with_missing_key_with_default(self) -> None:
        """Test that get_key returns default value when key is missing."""
        from context.key import ContextKey
        from context.main import Context

        # Create a context key and empty context
        name_key: ContextKey[str] = ContextKey("name", str, "User's name")
        context = Context()

        # Create the flow with default value
        get_name_flow = ContextFlowCombinators.get_key(name_key, "Anonymous")
        result = run_flow_with_input(get_name_flow, context)

        assert result == "Anonymous"
        assert isinstance(result, str)

    def test_get_key_with_type_mismatch(self) -> None:
        """Test that get_key raises ContextTypeMismatchError when value has wrong type."""
        from context.key import ContextKey
        from context.main import Context

        # Create a context key expecting int but provide str
        age_key: ContextKey[int] = ContextKey("age", int, "User's age")
        context = Context()
        context["age"] = "not_an_int"

        # Create the flow
        get_age_flow = ContextFlowCombinators.get_key(age_key)

        # Should raise ContextTypeMismatchError
        with pytest.raises(
            ContextTypeMismatchError, match="Context key 'age' expected int, got str"
        ):
            run_flow_with_input(get_age_flow, context)

    def test_get_key_with_object_type_key(self) -> None:
        """Test that get_key works when ContextKey has object type specification."""
        from context.key import ContextKey
        from context.main import Context

        # Create a context key with object type (minimal type validation)
        data_key: ContextKey[Any] = ContextKey("data", object, "Any data")
        context = Context()
        context["data"] = {"any": "value"}

        # Create and run the flow
        get_data_flow = ContextFlowCombinators.get_key(data_key)
        result = run_flow_with_input(get_data_flow, context)

        assert result == {"any": "value"}
        assert isinstance(result, dict)

    def test_get_key_with_complex_path(self) -> None:
        """Test that get_key works with complex key paths."""
        from context.key import ContextKey
        from context.main import Context

        # Create a context key with complex path
        user_name_key: ContextKey[str] = ContextKey(
            "user.profile.name", str, "User profile name"
        )
        context = Context()
        context["user.profile.name"] = "John Doe"

        # Create and run the flow
        get_user_name_flow = ContextFlowCombinators.get_key(user_name_key)
        result = run_flow_with_input(get_user_name_flow, context)

        assert result == "John Doe"
        assert isinstance(result, str)

    def test_get_key_flow_name(self) -> None:
        """Test that get_key creates flows with descriptive names."""
        from context.key import ContextKey

        # Create a context key
        name_key: ContextKey[str] = ContextKey("user.name", str, "User's name")

        # Create the flow
        get_name_flow = ContextFlowCombinators.get_key(name_key)

        # Check that the flow has a descriptive name
        assert get_name_flow.name == "get_key(user.name)"

    def test_get_key_with_inheritance_types(self) -> None:
        """Test that get_key works correctly with inheritance and isinstance checks."""
        from context.key import ContextKey
        from context.main import Context

        # Test with inheritance - list should be instance of object
        data_key: ContextKey[object] = ContextKey("data", object, "Any object")
        context = Context()
        context["data"] = [1, 2, 3]  # List is an object

        get_data_flow = ContextFlowCombinators.get_key(data_key)
        result = run_flow_with_input(get_data_flow, context)

        assert result == [1, 2, 3]
        assert isinstance(result, list)

    def test_get_key_with_none_default_value(self) -> None:
        """Test that get_key works when default value is explicitly None."""
        from context.key import ContextKey
        from context.main import Context

        # Create a context key with None default
        optional_key: ContextKey[str] = ContextKey("optional", str, "Optional value")
        context = Context()

        # Create the flow with None default
        get_optional_flow = ContextFlowCombinators.get_key(optional_key, None)
        result = run_flow_with_input(get_optional_flow, context)

        assert result is None

    def test_get_key_with_different_default_types(self) -> None:
        """Test that get_key works with different default value types."""
        from context.main import Context

        context = Context()
        self._test_string_default(context)
        self._test_int_default(context)
        self._test_list_default(context)

    def _test_string_default(self, context: Any) -> None:
        """Test get_key with string default."""
        from context.key import ContextKey

        name_key: ContextKey[str] = ContextKey("name", str, "User's name")
        get_name_flow = ContextFlowCombinators.get_key(name_key, "Default Name")
        name_result = run_flow_with_input(get_name_flow, context)
        assert name_result == "Default Name"

    def _test_int_default(self, context: Any) -> None:
        """Test get_key with int default."""
        from context.key import ContextKey

        age_key: ContextKey[int] = ContextKey("age", int, "User's age")
        get_age_flow = ContextFlowCombinators.get_key(age_key, 0)
        age_result = run_flow_with_input(get_age_flow, context)
        assert age_result == 0

    def _test_list_default(self, context: Any) -> None:
        """Test get_key with list default."""
        from context.key import ContextKey

        items_key: ContextKey[list[Any]] = ContextKey("items", list, "List of items")
        get_items_flow = ContextFlowCombinators.get_key(items_key, [])
        items_result = run_flow_with_input(get_items_flow, context)
        assert items_result == []

    def test_get_key_flow_integration_with_chaining(self) -> None:
        """Test that get_key flows can be chained with other flows."""
        from context.key import ContextKey
        from context.main import Context

        # Create a context key and context
        name_key: ContextKey[str] = ContextKey("name", str, "User's name")
        context = Context()
        context["name"] = "alice"

        # Create a flow that gets the name and then processes it
        get_name_flow = ContextFlowCombinators.get_key(name_key)
        uppercase_flow: Flow[str | None, str] = Flow.from_sync_fn(
            lambda x: x.upper() if x else ""
        )

        # Chain the flows
        chained_flow = get_name_flow >> uppercase_flow

        # Run the chained flow
        result = run_flow_with_input(chained_flow, context)

        assert result == "ALICE"
        assert isinstance(result, str)

    def test_get_key_flow_with_multiple_contexts(self) -> None:
        """Test that get_key flow works with multiple context inputs."""
        from context.key import ContextKey
        from context.main import Context

        # Create a context key
        score_key: ContextKey[int] = ContextKey("score", int, "User's score")

        # Create the flow
        get_score_flow = ContextFlowCombinators.get_key(score_key)

        # Test with multiple contexts
        context1 = Context()
        context1["score"] = 100
        result1 = run_flow_with_input(get_score_flow, context1)
        assert result1 == 100

        context2 = Context()
        context2["score"] = 200
        result2 = run_flow_with_input(get_score_flow, context2)
        assert result2 == 200

    def test_get_key_error_message_formatting(self) -> None:
        """Test that get_key produces well-formatted error messages."""
        from context.key import ContextKey
        from context.main import Context

        # Test missing key error message
        missing_key: ContextKey[str] = ContextKey(
            "user.profile.email", str, "User email"
        )
        context = Context()

        get_email_flow = ContextFlowCombinators.get_key(missing_key)

        with pytest.raises(MissingRequiredKeyError) as exc_info:
            run_flow_with_input(get_email_flow, context)

        assert "Required context key 'user.profile.email' is missing" in str(
            exc_info.value
        )

        # Test type mismatch error message
        age_key: ContextKey[int] = ContextKey("user.age", int, "User age")
        context["user.age"] = "twenty-five"

        get_age_flow = ContextFlowCombinators.get_key(age_key)

        with pytest.raises(ContextTypeMismatchError) as exc_info2:
            run_flow_with_input(get_age_flow, context)

        error_message = str(exc_info2.value)
        assert "Context key 'user.age' expected int, got str" in error_message

    def test_get_key_with_custom_classes(self) -> None:
        """Test that get_key works with custom class types."""
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
        get_user_flow = ContextFlowCombinators.get_key(user_key)
        result = run_flow_with_input(get_user_flow, context)

        assert result == user_obj
        assert isinstance(result, User)
        assert result.name == "Alice"
        assert result.age == 30

    def test_get_key_type_safety_with_cast(self) -> None:
        """Test that get_key properly casts types for type safety."""
        from context.key import ContextKey
        from context.main import Context

        # Create a context key with specific type
        count_key: ContextKey[int] = ContextKey("count", int, "Item count")
        context = Context()
        context["count"] = 42

        # Create and run the flow
        get_count_flow = ContextFlowCombinators.get_key(count_key)
        result = run_flow_with_input(get_count_flow, context)

        # Result should be properly typed
        assert result == 42
        assert isinstance(result, int)

    def test_get_key_static_method_access(self) -> None:
        """Test that get_key can be accessed as a static method."""
        from context.key import ContextKey

        # Create a context key
        test_key: ContextKey[str] = ContextKey("test", str, "Test key")

        # Should be able to access as static method
        flow = ContextFlowCombinators.get_key(test_key)
        assert isinstance(flow, Flow)

        # Should also work through class instance (though not recommended)
        combinators = ContextFlowCombinators()
        flow2 = combinators.get_key(test_key)
        assert isinstance(flow2, Flow)
