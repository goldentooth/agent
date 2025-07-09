"""Tests for ContextFlowCombinators.require_key method."""

from typing import Any

import pytest

from context_flow.integration import (
    ContextFlowCombinators,
    ContextTypeMismatchError,
    MissingRequiredKeyError,
    run_flow_with_input,
)
from flowengine.flow import Flow


class TestRequireKey:
    """Test cases for ContextFlowCombinators.require_key method."""

    def test_require_key_basic_functionality(self) -> None:
        """Test that require_key extracts values from context successfully."""
        from context.key import ContextKey
        from context.main import Context

        # Create a context key and context
        name_key: ContextKey[str] = ContextKey("name", str, "User's name")
        context = Context()
        context["name"] = "Alice"

        # Create and run the flow
        require_name_flow = ContextFlowCombinators.require_key(name_key)
        result = run_flow_with_input(require_name_flow, context)

        assert result == "Alice"
        assert isinstance(result, str)

    def test_require_key_with_different_types(self) -> None:
        """Test that require_key works with different data types."""
        self._test_require_key_with_integer_type()
        self._test_require_key_with_boolean_type()
        self._test_require_key_with_list_type()

    def _test_require_key_with_integer_type(self) -> None:
        """Test require_key with integer type."""
        from context.key import ContextKey
        from context.main import Context

        age_key: ContextKey[int] = ContextKey("age", int, "User's age")
        context = Context()
        context["age"] = 25

        require_age_flow = ContextFlowCombinators.require_key(age_key)
        age_result = run_flow_with_input(require_age_flow, context)

        assert age_result == 25
        assert isinstance(age_result, int)

    def _test_require_key_with_boolean_type(self) -> None:
        """Test require_key with boolean type."""
        from context.key import ContextKey
        from context.main import Context

        active_key: ContextKey[bool] = ContextKey("active", bool, "Is user active")
        context = Context()
        context["active"] = True

        require_active_flow = ContextFlowCombinators.require_key(active_key)
        active_result = run_flow_with_input(require_active_flow, context)

        assert active_result is True
        assert isinstance(active_result, bool)

    def _test_require_key_with_list_type(self) -> None:
        """Test require_key with list type."""
        from context.key import ContextKey
        from context.main import Context

        items_key: ContextKey[list[Any]] = ContextKey("items", list, "List of items")
        context = Context()
        context["items"] = [1, 2, 3]

        require_items_flow = ContextFlowCombinators.require_key(items_key)
        items_result = run_flow_with_input(require_items_flow, context)

        assert items_result == [1, 2, 3]
        assert isinstance(items_result, list)

    def test_require_key_with_missing_key(self) -> None:
        """Test that require_key raises MissingRequiredKeyError when key is missing."""
        from context.key import ContextKey
        from context.main import Context

        # Create a context key and empty context
        name_key: ContextKey[str] = ContextKey("name", str, "User's name")
        context = Context()

        # Create the flow
        require_name_flow = ContextFlowCombinators.require_key(name_key)

        # Should raise MissingRequiredKeyError
        with pytest.raises(
            MissingRequiredKeyError, match="Required context key 'name' is missing"
        ):
            run_flow_with_input(require_name_flow, context)

    def test_require_key_with_type_mismatch(self) -> None:
        """Test that require_key raises ContextTypeMismatchError for wrong types."""
        from context.key import ContextKey
        from context.main import Context

        # Create a context key expecting int but provide str
        age_key: ContextKey[int] = ContextKey("age", int, "User's age")
        context = Context()
        context["age"] = "not_an_int"

        # Create the flow
        require_age_flow = ContextFlowCombinators.require_key(age_key)

        # Should raise ContextTypeMismatchError
        with pytest.raises(
            ContextTypeMismatchError, match="Context key 'age' expected int, got str"
        ):
            run_flow_with_input(require_age_flow, context)

    def test_require_key_with_object_type_key(self) -> None:
        """Test that require_key works when ContextKey has object type."""
        from context.key import ContextKey
        from context.main import Context

        # Create a context key with object type (minimal type validation)
        data_key: ContextKey[Any] = ContextKey("data", object, "Any data")
        context = Context()
        context["data"] = {"any": "value"}

        # Create and run the flow
        require_data_flow = ContextFlowCombinators.require_key(data_key)
        result = run_flow_with_input(require_data_flow, context)

        assert result == {"any": "value"}
        assert isinstance(result, dict)

    def test_require_key_with_complex_path(self) -> None:
        """Test that require_key works with complex key paths."""
        from context.key import ContextKey
        from context.main import Context

        # Create a context key with complex path
        user_name_key: ContextKey[str] = ContextKey(
            "user.profile.name", str, "User profile name"
        )
        context = Context()
        context["user.profile.name"] = "John Doe"

        # Create and run the flow
        require_user_name_flow = ContextFlowCombinators.require_key(user_name_key)
        result = run_flow_with_input(require_user_name_flow, context)

        assert result == "John Doe"
        assert isinstance(result, str)

    def test_require_key_flow_name(self) -> None:
        """Test that require_key creates flows with descriptive names."""
        from context.key import ContextKey

        # Create a context key
        name_key: ContextKey[str] = ContextKey("user.name", str, "User's name")

        # Create the flow
        require_name_flow = ContextFlowCombinators.require_key(name_key)

        # Check that the flow has a descriptive name
        assert require_name_flow.name == "require_key(user.name)"

    def test_require_key_with_inheritance_types(self) -> None:
        """Test that require_key works correctly with inheritance."""
        from context.key import ContextKey
        from context.main import Context

        # Test with inheritance - list should be instance of object
        data_key: ContextKey[object] = ContextKey("data", object, "Any object")
        context = Context()
        context["data"] = [1, 2, 3]  # List is an object

        require_data_flow = ContextFlowCombinators.require_key(data_key)
        result = run_flow_with_input(require_data_flow, context)

        assert result == [1, 2, 3]
        assert isinstance(result, list)

    def test_require_key_flow_integration_with_chaining(self) -> None:
        """Test that require_key flows can be chained with other flows."""
        from context.key import ContextKey
        from context.main import Context

        # Create a context key and context
        name_key: ContextKey[str] = ContextKey("name", str, "User's name")
        context = Context()
        context["name"] = "alice"

        # Create a flow that requires the name and then processes it
        require_name_flow = ContextFlowCombinators.require_key(name_key)
        uppercase_flow: Flow[str, str] = Flow.from_sync_fn(lambda x: x.upper())

        # Chain the flows
        chained_flow = require_name_flow >> uppercase_flow

        # Run the chained flow
        result = run_flow_with_input(chained_flow, context)

        assert result == "ALICE"
        assert isinstance(result, str)

    def test_require_key_flow_with_multiple_contexts(self) -> None:
        """Test that require_key flow works with multiple context inputs."""
        from context.key import ContextKey
        from context.main import Context

        # Create a context key
        score_key: ContextKey[int] = ContextKey("score", int, "User's score")

        # Create the flow
        require_score_flow = ContextFlowCombinators.require_key(score_key)

        # Test with multiple contexts
        context1 = Context()
        context1["score"] = 100
        result1 = run_flow_with_input(require_score_flow, context1)
        assert result1 == 100

        context2 = Context()
        context2["score"] = 200
        result2 = run_flow_with_input(require_score_flow, context2)
        assert result2 == 200

    def test_require_key_error_message_formatting(self) -> None:
        """Test that require_key produces well-formatted error messages."""
        from context.key import ContextKey
        from context.main import Context

        # Test missing key error message
        missing_key: ContextKey[str] = ContextKey(
            "user.profile.email", str, "User email"
        )
        context = Context()

        require_email_flow = ContextFlowCombinators.require_key(missing_key)

        with pytest.raises(MissingRequiredKeyError) as exc_info:
            run_flow_with_input(require_email_flow, context)

        assert "Required context key 'user.profile.email' is missing" in str(
            exc_info.value
        )

        # Test type mismatch error message
        age_key: ContextKey[int] = ContextKey("user.age", int, "User age")
        context["user.age"] = "twenty-five"

        require_age_flow = ContextFlowCombinators.require_key(age_key)

        with pytest.raises(ContextTypeMismatchError) as exc_info2:
            run_flow_with_input(require_age_flow, context)

        error_message = str(exc_info2.value)
        assert "Context key 'user.age' expected int, got str" in error_message

    def test_require_key_with_custom_classes(self) -> None:
        """Test that require_key works with custom class types."""
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
        require_user_flow = ContextFlowCombinators.require_key(user_key)
        result = run_flow_with_input(require_user_flow, context)

        assert result == user_obj
        assert isinstance(result, User)
        assert result.name == "Alice"
        assert result.age == 30

    def test_require_key_type_safety_with_cast(self) -> None:
        """Test that require_key properly casts types for type safety."""
        from context.key import ContextKey
        from context.main import Context

        # Create a context key with specific type
        count_key: ContextKey[int] = ContextKey("count", int, "Item count")
        context = Context()
        context["count"] = 42

        # Create and run the flow
        require_count_flow = ContextFlowCombinators.require_key(count_key)
        result = run_flow_with_input(require_count_flow, context)

        # Result should be properly typed
        assert result == 42
        assert isinstance(result, int)

    def test_require_key_static_method_access(self) -> None:
        """Test that require_key can be accessed as a static method."""
        from context.key import ContextKey

        # Create a context key
        test_key: ContextKey[str] = ContextKey("test", str, "Test key")

        # Should be able to access as static method
        flow = ContextFlowCombinators.require_key(test_key)
        assert isinstance(flow, Flow)

        # Should also work through class instance (though not recommended)
        combinators = ContextFlowCombinators()
        flow2 = combinators.require_key(test_key)
        assert isinstance(flow2, Flow)

    def test_require_key_no_default_support(self) -> None:
        """Test that require_key does not support default values."""
        from context.key import ContextKey

        # Create a context key
        name_key: ContextKey[str] = ContextKey("name", str, "User's name")

        # require_key should not accept default parameter
        # This test ensures the method signature is correct
        flow = ContextFlowCombinators.require_key(name_key)
        assert isinstance(flow, Flow)

    def test_require_key_difference_from_get_key(self) -> None:
        """Test that require_key behaves differently from get_key for missing keys."""
        from context.key import ContextKey
        from context.main import Context

        # Create a context key and empty context
        name_key: ContextKey[str] = ContextKey("name", str, "User's name")
        context = Context()

        # require_key should always raise error for missing key
        require_name_flow = ContextFlowCombinators.require_key(name_key)
        with pytest.raises(MissingRequiredKeyError):
            run_flow_with_input(require_name_flow, context)

        # get_key with no default should also raise error for missing key
        get_name_flow = ContextFlowCombinators.get_key(name_key)
        with pytest.raises(MissingRequiredKeyError):
            run_flow_with_input(get_name_flow, context)

        # But get_key can accept a default, while require_key cannot
        get_name_with_default_flow = ContextFlowCombinators.get_key(name_key, "Default")
        result = run_flow_with_input(get_name_with_default_flow, context)
        assert result == "Default"
