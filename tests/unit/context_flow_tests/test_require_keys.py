"""Tests for ContextFlowCombinators.require_keys method."""

from typing import Any

import pytest

from context_flow.integration import (
    ContextFlowCombinators,
    MissingRequiredKeyError,
    run_flow_with_input,
)
from flowengine.flow import Flow


class TestRequireKeys:
    """Test cases for ContextFlowCombinators.require_keys method."""

    def test_require_keys_basic_functionality(self) -> None:
        """Test that require_keys validates multiple keys exist in context."""
        from context.key import ContextKey
        from context.main import Context

        # Create context keys and context with all required keys
        name_key: ContextKey[str] = ContextKey("name", str, "User's name")
        age_key: ContextKey[int] = ContextKey("age", int, "User's age")
        context = Context()
        context["name"] = "Alice"
        context["age"] = 30

        # Create and run the flow
        require_keys_flow = ContextFlowCombinators.require_keys([name_key, age_key])
        result = run_flow_with_input(require_keys_flow, context)

        # Should return the original context unchanged
        assert result is context or (result["name"] == "Alice" and result["age"] == 30)
        assert isinstance(result, Context)

    def test_require_keys_with_single_key(self) -> None:
        """Test that require_keys works with a single key."""
        from context.key import ContextKey
        from context.main import Context

        # Create context key and context
        email_key: ContextKey[str] = ContextKey("email", str, "User's email")
        context = Context()
        context["email"] = "alice@example.com"

        # Create and run the flow
        require_keys_flow = ContextFlowCombinators.require_keys([email_key])
        result = run_flow_with_input(require_keys_flow, context)

        # Should pass validation and return context
        assert result["email"] == "alice@example.com"

    def test_require_keys_with_missing_key(self) -> None:
        """Test that require_keys raises error when required key is missing."""
        from context.key import ContextKey
        from context.main import Context

        # Create context keys but only provide one in context
        name_key: ContextKey[str] = ContextKey("name", str, "User's name")
        age_key: ContextKey[int] = ContextKey("age", int, "User's age")
        context = Context()
        context["name"] = "Alice"
        # age is missing

        # Create the flow
        require_keys_flow = ContextFlowCombinators.require_keys([name_key, age_key])

        # Should raise MissingRequiredKeyError
        with pytest.raises(
            MissingRequiredKeyError, match="Required context key 'age' is missing"
        ):
            run_flow_with_input(require_keys_flow, context)

    def test_require_keys_with_all_missing_keys(self) -> None:
        """Test that require_keys raises error for first missing key."""
        from context.key import ContextKey
        from context.main import Context

        # Create context keys but provide none in context
        name_key: ContextKey[str] = ContextKey("name", str, "User's name")
        age_key: ContextKey[int] = ContextKey("age", int, "User's age")
        context = Context()

        # Create the flow
        require_keys_flow = ContextFlowCombinators.require_keys([name_key, age_key])

        # Should raise MissingRequiredKeyError for first missing key
        with pytest.raises(
            MissingRequiredKeyError, match="Required context key 'name' is missing"
        ):
            run_flow_with_input(require_keys_flow, context)

    def test_require_keys_with_empty_list(self) -> None:
        """Test that require_keys works with empty key list."""
        from context.main import Context

        # Create context
        context = Context()
        context["data"] = "value"

        # Create and run flow with empty key list
        require_keys_flow = ContextFlowCombinators.require_keys([])
        result = run_flow_with_input(require_keys_flow, context)

        # Should pass validation and return context unchanged
        assert result["data"] == "value"

    def test_require_keys_with_different_types(self) -> None:
        """Test that require_keys works with different key types."""
        self._test_require_keys_with_string_and_int()
        self._test_require_keys_with_bool_and_list()

    def _test_require_keys_with_string_and_int(self) -> None:
        """Test require_keys with string and int types."""
        from context.key import ContextKey
        from context.main import Context

        name_key: ContextKey[str] = ContextKey("name", str, "Name")
        count_key: ContextKey[int] = ContextKey("count", int, "Count")
        context = Context()
        context["name"] = "test"
        context["count"] = 42

        require_keys_flow = ContextFlowCombinators.require_keys([name_key, count_key])
        result = run_flow_with_input(require_keys_flow, context)

        assert result["name"] == "test"
        assert result["count"] == 42

    def _test_require_keys_with_bool_and_list(self) -> None:
        """Test require_keys with bool and list types."""
        from context.key import ContextKey
        from context.main import Context

        active_key: ContextKey[bool] = ContextKey("active", bool, "Active")
        items_key: ContextKey[list[Any]] = ContextKey("items", list, "Items")
        context = Context()
        context["active"] = True
        context["items"] = [1, 2, 3]

        require_keys_flow = ContextFlowCombinators.require_keys([active_key, items_key])
        result = run_flow_with_input(require_keys_flow, context)

        assert result["active"] is True
        assert result["items"] == [1, 2, 3]

    def test_require_keys_with_complex_paths(self) -> None:
        """Test that require_keys works with complex key paths."""
        from context.key import ContextKey
        from context.main import Context

        # Create context keys with complex paths
        user_name_key: ContextKey[str] = ContextKey("user.profile.name", str, "Name")
        user_email_key: ContextKey[str] = ContextKey("user.profile.email", str, "Email")
        context = Context()
        context["user.profile.name"] = "Alice"
        context["user.profile.email"] = "alice@example.com"

        # Create and run the flow
        require_keys_flow = ContextFlowCombinators.require_keys(
            [user_name_key, user_email_key]
        )
        result = run_flow_with_input(require_keys_flow, context)

        assert result["user.profile.name"] == "Alice"
        assert result["user.profile.email"] == "alice@example.com"

    def test_require_keys_flow_name(self) -> None:
        """Test that require_keys creates flows with descriptive names."""
        from context.key import ContextKey

        # Create context keys
        name_key: ContextKey[str] = ContextKey("name", str, "Name")
        age_key: ContextKey[int] = ContextKey("age", int, "Age")

        # Create the flow
        require_keys_flow = ContextFlowCombinators.require_keys([name_key, age_key])

        # Check that the flow has a descriptive name
        assert require_keys_flow.name == "require_keys([name, age])"

    def test_require_keys_flow_name_with_single_key(self) -> None:
        """Test flow name with single key."""
        from context.key import ContextKey

        # Create context key
        email_key: ContextKey[str] = ContextKey("email", str, "Email")

        # Create the flow
        require_keys_flow = ContextFlowCombinators.require_keys([email_key])

        # Check that the flow has a descriptive name
        assert require_keys_flow.name == "require_keys([email])"

    def test_require_keys_flow_name_with_empty_list(self) -> None:
        """Test flow name with empty key list."""
        # Create the flow
        require_keys_flow = ContextFlowCombinators.require_keys([])

        # Check that the flow has a descriptive name
        assert require_keys_flow.name == "require_keys([])"

    def test_require_keys_with_custom_classes(self) -> None:
        """Test that require_keys works with custom class types."""
        from context.key import ContextKey
        from context.main import Context

        # Define a custom class
        class User:
            def __init__(self, name: str, age: int):
                super().__init__()
                self.name = name
                self.age = age

        self._test_require_keys_custom_class_flow(User)

    def _test_require_keys_custom_class_flow(self, User: type[Any]) -> None:
        """Helper to test require_keys flow with custom class."""
        from context.key import ContextKey
        from context.main import Context

        # Create context keys for the custom class
        user_key: ContextKey[Any] = ContextKey("current_user", User, "Current user")
        session_key: ContextKey[str] = ContextKey("session_id", str, "Session ID")
        context = Context()
        user_obj = User("Alice", 30)
        context["current_user"] = user_obj
        context["session_id"] = "abc123"

        # Create and run the flow
        require_keys_flow = ContextFlowCombinators.require_keys([user_key, session_key])
        result = run_flow_with_input(require_keys_flow, context)

        assert result["current_user"] == user_obj
        assert result["session_id"] == "abc123"

    def test_require_keys_preserves_other_context_data(self) -> None:
        """Test that require_keys preserves all context data."""
        from context.key import ContextKey
        from context.main import Context

        # Create context with required and extra keys
        name_key: ContextKey[str] = ContextKey("name", str, "Name")
        context = Context()
        context["name"] = "Alice"
        context["extra1"] = "value1"
        context["extra2"] = 42
        context["extra3"] = [1, 2, 3]

        # Create and run the flow
        require_keys_flow = ContextFlowCombinators.require_keys([name_key])
        result = run_flow_with_input(require_keys_flow, context)

        # Check that all data is preserved
        assert result["name"] == "Alice"
        assert result["extra1"] == "value1"
        assert result["extra2"] == 42
        assert result["extra3"] == [1, 2, 3]

    def test_require_keys_flow_integration_with_chaining(self) -> None:
        """Test that require_keys flows can be chained with other flows."""
        from context.key import ContextKey
        from context.main import Context

        # Create context keys
        name_key: ContextKey[str] = ContextKey("name", str, "Name")
        age_key: ContextKey[int] = ContextKey("age", int, "Age")
        backup_name_key: ContextKey[str] = ContextKey("backup_name", str, "Backup name")

        context = Context()
        context["name"] = "Alice"
        context["age"] = 30

        self._test_chained_require_and_copy_flow(
            name_key, age_key, backup_name_key, context
        )

    def _test_chained_require_and_copy_flow(
        self, name_key: Any, age_key: Any, backup_name_key: Any, context: Any
    ) -> None:
        """Test chained require and copy flow execution."""
        # Create flows to chain require with copy
        require_flow = ContextFlowCombinators.require_keys([name_key, age_key])
        copy_flow = ContextFlowCombinators.copy_key(name_key, backup_name_key)

        # Chain the flows
        chained_flow = require_flow >> copy_flow

        # Run the chained flow
        result = run_flow_with_input(chained_flow, context)

        # Check that requirements were validated and copy happened
        assert result["name"] == "Alice"
        assert result["age"] == 30
        assert result["backup_name"] == "Alice"

    def test_require_keys_with_multiple_contexts(self) -> None:
        """Test that require_keys flow works with multiple context inputs."""
        from context.key import ContextKey
        from context.main import Context

        # Create context keys
        score_key: ContextKey[int] = ContextKey("score", int, "Score")
        level_key: ContextKey[str] = ContextKey("level", str, "Level")

        # Create the flow
        require_keys_flow = ContextFlowCombinators.require_keys([score_key, level_key])

        self._test_require_keys_context_one(require_keys_flow)
        self._test_require_keys_context_two(require_keys_flow)

    def _test_require_keys_context_one(self, require_keys_flow: Flow[Any, Any]) -> None:
        """Test require_keys with first context."""
        from context.main import Context

        context1 = Context()
        context1["score"] = 100
        context1["level"] = "beginner"
        result1 = run_flow_with_input(require_keys_flow, context1)
        assert result1["score"] == 100
        assert result1["level"] == "beginner"

    def _test_require_keys_context_two(self, require_keys_flow: Flow[Any, Any]) -> None:
        """Test require_keys with second context."""
        from context.main import Context

        context2 = Context()
        context2["score"] = 200
        context2["level"] = "expert"
        result2 = run_flow_with_input(require_keys_flow, context2)
        assert result2["score"] == 200
        assert result2["level"] == "expert"

    def test_require_keys_error_message_formatting(self) -> None:
        """Test that require_keys produces well-formatted error messages."""
        from context.key import ContextKey
        from context.main import Context

        # Test missing key error message
        user_name_key: ContextKey[str] = ContextKey("user.profile.name", str, "Name")
        user_email_key: ContextKey[str] = ContextKey("user.profile.email", str, "Email")
        context = Context()
        context["user.profile.name"] = "Alice"
        # user.profile.email is missing

        require_keys_flow = ContextFlowCombinators.require_keys(
            [user_name_key, user_email_key]
        )

        with pytest.raises(MissingRequiredKeyError) as exc_info:
            run_flow_with_input(require_keys_flow, context)

        assert "Required context key 'user.profile.email' is missing" in str(
            exc_info.value
        )

    def test_require_keys_static_method_access(self) -> None:
        """Test that require_keys can be accessed as a static method."""
        from context.key import ContextKey

        # Create context keys
        name_key: ContextKey[str] = ContextKey("name", str, "Name")
        age_key: ContextKey[int] = ContextKey("age", int, "Age")

        # Should be able to access as static method
        flow = ContextFlowCombinators.require_keys([name_key, age_key])
        assert isinstance(flow, Flow)

        # Should also work through class instance (though not recommended)
        combinators = ContextFlowCombinators()
        flow2 = combinators.require_keys([name_key, age_key])
        assert isinstance(flow2, Flow)

    def test_require_keys_with_none_values(self) -> None:
        """Test that require_keys accepts None values for optional key types."""
        from context.key import ContextKey
        from context.main import Context

        # Create context keys that can accept None
        optional_key: ContextKey[object] = ContextKey("optional", object, "Optional")
        required_key: ContextKey[str] = ContextKey("required", str, "Required")
        context = Context()
        context["optional"] = None
        context["required"] = "value"

        # Create and run the flow
        require_keys_flow = ContextFlowCombinators.require_keys(
            [optional_key, required_key]
        )
        result = run_flow_with_input(require_keys_flow, context)

        assert result["optional"] is None
        assert result["required"] == "value"

    def test_require_keys_ordering_independence(self) -> None:
        """Test that require_keys validation order doesn't affect results."""
        from context.key import ContextKey
        from context.main import Context

        # Create context keys
        key1: ContextKey[str] = ContextKey("key1", str, "Key 1")
        key2: ContextKey[str] = ContextKey("key2", str, "Key 2")
        key3: ContextKey[str] = ContextKey("key3", str, "Key 3")

        context = Context()
        context["key1"] = "value1"
        context["key2"] = "value2"
        context["key3"] = "value3"

        self._test_different_key_orderings(key1, key2, key3, context)

    def _test_different_key_orderings(
        self, key1: Any, key2: Any, key3: Any, context: Any
    ) -> None:
        """Test different key orderings produce equivalent results."""
        # Test different orderings
        flow1 = ContextFlowCombinators.require_keys([key1, key2, key3])
        flow2 = ContextFlowCombinators.require_keys([key3, key1, key2])
        flow3 = ContextFlowCombinators.require_keys([key2, key3, key1])

        result1 = run_flow_with_input(flow1, context)
        result2 = run_flow_with_input(flow2, context)
        result3 = run_flow_with_input(flow3, context)

        # All should produce equivalent results
        assert result1["key1"] == result2["key1"] == result3["key1"] == "value1"
        assert result1["key2"] == result2["key2"] == result3["key2"] == "value2"
        assert result1["key3"] == result2["key3"] == result3["key3"] == "value3"

    def test_require_keys_vs_require_key_single_behavior(self) -> None:
        """Test that require_keys with single key behaves like require_key."""
        from context.key import ContextKey
        from context.main import Context

        # Create context key and context
        name_key: ContextKey[str] = ContextKey("name", str, "Name")
        context = Context()
        context["name"] = "Alice"

        # Compare single require_key vs require_keys with one key
        require_key_flow = ContextFlowCombinators.require_key(name_key)
        require_keys_flow = ContextFlowCombinators.require_keys([name_key])

        # require_key extracts the value
        single_result = run_flow_with_input(require_key_flow, context)
        assert single_result == "Alice"

        # require_keys validates and returns the context
        multiple_result = run_flow_with_input(require_keys_flow, context)
        assert multiple_result["name"] == "Alice"
        assert isinstance(multiple_result, Context)
