"""Tests for ContextFlowCombinators.transform_key method."""

from typing import Any, Callable

import pytest

from context_flow.integration import (
    ContextFlowCombinators,
    ContextTypeMismatchError,
    MissingRequiredKeyError,
    run_flow_with_input,
)
from flowengine.flow import Flow


class TestTransformKey:
    """Test cases for ContextFlowCombinators.transform_key method."""

    def test_transform_key_basic_functionality(self) -> None:
        """Test that transform_key applies transformation to a key value."""
        from context.key import ContextKey
        from context.main import Context

        # Create context key and context
        name_key: ContextKey[str] = ContextKey("name", str, "User's name")
        context = Context()
        context["name"] = "alice"

        # Create transformation function
        def capitalize_name(value: str) -> str:
            return value.capitalize()

        # Create and run the flow
        transform_flow = ContextFlowCombinators.transform_key(name_key, capitalize_name)
        result = run_flow_with_input(transform_flow, context)

        # Check that the value was transformed
        assert result["name"] == "Alice"
        assert isinstance(result, Context)

    def test_transform_key_with_different_types(self) -> None:
        """Test that transform_key works with different data types."""
        self._test_transform_key_with_integer_type()
        self._test_transform_key_with_string_to_int()
        self._test_transform_key_with_list_type()

    def _test_transform_key_with_integer_type(self) -> None:
        """Test transform_key with integer type."""
        from context.key import ContextKey
        from context.main import Context

        age_key: ContextKey[int] = ContextKey("age", int, "User's age")
        context = Context()
        context["age"] = 25

        def double_age(value: int) -> int:
            return value * 2

        transform_flow = ContextFlowCombinators.transform_key(age_key, double_age)
        result = run_flow_with_input(transform_flow, context)

        assert result["age"] == 50

    def _test_transform_key_with_string_to_int(self) -> None:
        """Test transform_key with type conversion."""
        from context.key import ContextKey
        from context.main import Context

        # Note: This uses type: ignore because we're intentionally testing
        # type transformation which violates static typing
        score_key: ContextKey[str] = ContextKey("score", str, "Score as string")
        context = Context()
        context["score"] = "100"

        def string_to_int(value: str) -> int:
            return int(value)

        transform_flow = ContextFlowCombinators.transform_key(score_key, string_to_int)
        result = run_flow_with_input(transform_flow, context)

        assert result["score"] == 100
        assert isinstance(result["score"], int)

    def _test_transform_key_with_list_type(self) -> None:
        """Test transform_key with list type."""
        from context.key import ContextKey
        from context.main import Context

        items_key: ContextKey[list[int]] = ContextKey("items", list, "List of items")
        context = Context()
        context["items"] = [1, 2, 3]

        def sort_reverse(value: list[int]) -> list[int]:
            return sorted(value, reverse=True)

        transform_flow = ContextFlowCombinators.transform_key(items_key, sort_reverse)
        result = run_flow_with_input(transform_flow, context)

        assert result["items"] == [3, 2, 1]

    def test_transform_key_with_missing_key(self) -> None:
        """Test that transform_key raises error when key is missing."""
        from context.key import ContextKey
        from context.main import Context

        # Create context key and empty context
        name_key: ContextKey[str] = ContextKey("name", str, "User's name")
        context = Context()

        def uppercase(value: str) -> str:
            return value.upper()

        # Create the flow
        transform_flow = ContextFlowCombinators.transform_key(name_key, uppercase)

        # Should raise MissingRequiredKeyError
        with pytest.raises(
            MissingRequiredKeyError, match="Required context key 'name' is missing"
        ):
            run_flow_with_input(transform_flow, context)

    def test_transform_key_with_lambda_function(self) -> None:
        """Test that transform_key works with lambda functions."""
        from context.key import ContextKey
        from context.main import Context

        # Create context key and context
        value_key: ContextKey[int] = ContextKey("value", int, "Numeric value")
        context = Context()
        context["value"] = 5

        # Create and run the flow with lambda
        transform_flow = ContextFlowCombinators.transform_key(value_key, lambda x: x**2)
        result = run_flow_with_input(transform_flow, context)

        assert result["value"] == 25

    def test_transform_key_with_complex_paths(self) -> None:
        """Test that transform_key works with complex key paths."""
        from context.key import ContextKey
        from context.main import Context

        # Create context key with complex path
        user_email_key: ContextKey[str] = ContextKey(
            "user.profile.email", str, "User email"
        )
        context = Context()
        context["user.profile.email"] = "ALICE@EXAMPLE.COM"

        def normalize_email(email: str) -> str:
            return email.lower().strip()

        # Create and run the flow
        transform_flow = ContextFlowCombinators.transform_key(
            user_email_key, normalize_email
        )
        result = run_flow_with_input(transform_flow, context)

        assert result["user.profile.email"] == "alice@example.com"

    def test_transform_key_flow_name(self) -> None:
        """Test that transform_key creates flows with descriptive names."""
        from context.key import ContextKey

        # Create context key
        name_key: ContextKey[str] = ContextKey("user.name", str, "User's name")

        def capitalize(value: str) -> str:
            return value.capitalize()

        # Create the flow
        transform_flow = ContextFlowCombinators.transform_key(name_key, capitalize)

        # Check that the flow has a descriptive name
        assert transform_flow.name == "transform_key(user.name)"

    def test_transform_key_with_custom_classes(self) -> None:
        """Test that transform_key works with custom class types."""
        from context.key import ContextKey
        from context.main import Context

        # Define custom classes
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

        class UserProfile:
            def __init__(self, user: User, bio: str):
                super().__init__()
                self.user = user
                self.bio = bio

            def __eq__(self, other: object) -> bool:
                return (
                    isinstance(other, UserProfile)
                    and self.user == other.user
                    and self.bio == other.bio
                )

        self._test_transform_key_custom_class_flow(User, UserProfile)

    def _test_transform_key_custom_class_flow(
        self, User: type[Any], UserProfile: type[Any]
    ) -> None:
        """Helper to test transform_key flow with custom classes."""
        from context.key import ContextKey
        from context.main import Context

        # Create context key for the custom class
        user_key: ContextKey[Any] = ContextKey("current_user", User, "Current user")
        context = Context()
        user_obj = User("Alice", 30)
        context["current_user"] = user_obj

        def user_to_profile(user: Any) -> Any:
            return UserProfile(user, f"Bio for {user.name}")

        # Create and run the flow
        transform_flow = ContextFlowCombinators.transform_key(user_key, user_to_profile)
        result = run_flow_with_input(transform_flow, context)

        assert isinstance(result["current_user"], UserProfile)
        assert result["current_user"].user == user_obj
        assert result["current_user"].bio == "Bio for Alice"

    def test_transform_key_preserves_other_context_data(self) -> None:
        """Test that transform_key preserves other data in the context."""
        from context.key import ContextKey
        from context.main import Context

        # Create context with multiple keys
        target_key: ContextKey[str] = ContextKey("target", str, "Target key")
        context = Context()
        context["target"] = "transform_me"
        context["keep1"] = "value1"
        context["keep2"] = 42
        context["keep3"] = [1, 2, 3]

        self._test_transform_with_data_preservation(target_key, context)

    def _test_transform_with_data_preservation(
        self, target_key: Any, context: Any
    ) -> None:
        """Test transform execution with data preservation."""

        def uppercase(value: str) -> str:
            return value.upper()

        # Create and run the flow
        transform_flow = ContextFlowCombinators.transform_key(target_key, uppercase)
        result = run_flow_with_input(transform_flow, context)

        # Check that transformation happened and all data preserved
        assert result["target"] == "TRANSFORM_ME"
        assert result["keep1"] == "value1"
        assert result["keep2"] == 42
        assert result["keep3"] == [1, 2, 3]

    def test_transform_key_flow_integration_with_chaining(self) -> None:
        """Test that transform_key flows can be chained with other flows."""
        from context.key import ContextKey
        from context.main import Context

        # Create context keys
        name_key: ContextKey[str] = ContextKey("name", str, "Name")
        backup_key: ContextKey[str] = ContextKey("backup_name", str, "Backup name")
        context = Context()
        context["name"] = "alice"

        self._test_chained_transform_and_copy_flow(name_key, backup_key, context)

    def _test_chained_transform_and_copy_flow(
        self, name_key: Any, backup_key: Any, context: Any
    ) -> None:
        """Test chained transform and copy flow execution."""

        def capitalize(value: str) -> str:
            return value.capitalize()

        # Create flows to chain transform with copy
        transform_flow = ContextFlowCombinators.transform_key(name_key, capitalize)
        copy_flow = ContextFlowCombinators.copy_key(name_key, backup_key)

        # Chain the flows
        chained_flow = transform_flow >> copy_flow

        # Run the chained flow
        result = run_flow_with_input(chained_flow, context)

        # Check that transformation and copy both happened
        assert result["name"] == "Alice"
        assert result["backup_name"] == "Alice"

    def test_transform_key_with_multiple_contexts(self) -> None:
        """Test that transform_key flow works with multiple context inputs."""
        from context.key import ContextKey
        from context.main import Context

        # Create context key
        score_key: ContextKey[int] = ContextKey("score", int, "Score")

        def double_score(value: int) -> int:
            return value * 2

        # Create the flow
        transform_flow = ContextFlowCombinators.transform_key(score_key, double_score)

        self._test_transform_key_context_one(transform_flow)
        self._test_transform_key_context_two(transform_flow)

    def _test_transform_key_context_one(self, transform_flow: Flow[Any, Any]) -> None:
        """Test transform_key with first context."""
        from context.main import Context

        context1 = Context()
        context1["score"] = 100
        result1 = run_flow_with_input(transform_flow, context1)
        assert result1["score"] == 200

    def _test_transform_key_context_two(self, transform_flow: Flow[Any, Any]) -> None:
        """Test transform_key with second context."""
        from context.main import Context

        context2 = Context()
        context2["score"] = 50
        result2 = run_flow_with_input(transform_flow, context2)
        assert result2["score"] == 100

    def test_transform_key_with_transformation_errors(self) -> None:
        """Test that transform_key properly handles transformation errors."""
        from context.key import ContextKey
        from context.main import Context

        # Create context key and context
        value_key: ContextKey[str] = ContextKey("value", str, "Value")
        context = Context()
        context["value"] = "not_a_number"

        def string_to_int(value: str) -> int:
            return int(value)  # Will raise ValueError

        # Create the flow
        transform_flow = ContextFlowCombinators.transform_key(value_key, string_to_int)

        # Should propagate the ValueError from transformation
        with pytest.raises(ValueError, match="invalid literal for int()"):
            run_flow_with_input(transform_flow, context)

    def test_transform_key_immutability(self) -> None:
        """Test that transform_key creates new contexts without modifying the original."""
        from context.key import ContextKey
        from context.main import Context

        # Create original context with some data
        target_key: ContextKey[str] = ContextKey("target_key", str, "Target key")
        original_context = Context()
        original_context["target_key"] = "original"
        original_context["other_key"] = "other_value"

        def uppercase(value: str) -> str:
            return value.upper()

        # Create and run the flow
        transform_flow = ContextFlowCombinators.transform_key(target_key, uppercase)
        result_context = run_flow_with_input(transform_flow, original_context)

        self._verify_original_unchanged_for_transform(original_context)
        self._verify_result_has_transformation(result_context)

    def _verify_original_unchanged_for_transform(self, original_context: Any) -> None:
        """Verify original context was not modified."""
        assert "target_key" in original_context
        assert original_context["target_key"] == "original"
        assert original_context["other_key"] == "other_value"

    def _verify_result_has_transformation(self, result_context: Any) -> None:
        """Verify result context has the transformation applied."""
        assert result_context["target_key"] == "ORIGINAL"
        assert result_context["other_key"] == "other_value"

    def test_transform_key_static_method_access(self) -> None:
        """Test that transform_key can be accessed as a static method."""
        from context.key import ContextKey

        # Create context key
        test_key: ContextKey[str] = ContextKey("test", str, "Test key")

        def identity(value: str) -> str:
            return value

        # Should be able to access as static method
        flow = ContextFlowCombinators.transform_key(test_key, identity)
        assert isinstance(flow, Flow)

        # Should also work through class instance (though not recommended)
        combinators = ContextFlowCombinators()
        flow2 = combinators.transform_key(test_key, identity)
        assert isinstance(flow2, Flow)

    def test_transform_key_with_none_values(self) -> None:
        """Test that transform_key handles None values correctly."""
        from context.key import ContextKey
        from context.main import Context

        # Create context key that has None value
        optional_key: ContextKey[object] = ContextKey("optional", object, "Optional")
        context = Context()
        context["optional"] = None

        def handle_none(value: object) -> str:
            return "was_none" if value is None else str(value)

        # Create and run the flow
        transform_flow = ContextFlowCombinators.transform_key(optional_key, handle_none)
        result = run_flow_with_input(transform_flow, context)

        assert result["optional"] == "was_none"

    def test_transform_key_with_side_effects(self) -> None:
        """Test that transform_key can work with functions that have side effects."""
        from context.key import ContextKey
        from context.main import Context

        # Create context key and context
        counter_key: ContextKey[int] = ContextKey("counter", int, "Counter")
        context = Context()
        context["counter"] = 5

        # Track side effects
        call_count = []

        def increment_with_logging(value: int) -> int:
            call_count.append(1)  # Side effect: logging call
            return value + 1

        # Create and run the flow
        transform_flow = ContextFlowCombinators.transform_key(
            counter_key, increment_with_logging
        )
        result = run_flow_with_input(transform_flow, context)

        assert result["counter"] == 6
        assert len(call_count) == 1  # Side effect occurred

    def test_transform_key_with_identity_transformation(self) -> None:
        """Test that transform_key works with identity transformations."""
        from context.key import ContextKey
        from context.main import Context

        # Create context key and context
        value_key: ContextKey[str] = ContextKey("value", str, "Value")
        context = Context()
        context["value"] = "unchanged"

        def identity(value: str) -> str:
            return value

        # Create and run the flow
        transform_flow = ContextFlowCombinators.transform_key(value_key, identity)
        result = run_flow_with_input(transform_flow, context)

        # Value should remain the same but context should be new instance
        assert result["value"] == "unchanged"
        assert result is not context  # New context instance

    def test_transform_key_composition_patterns(self) -> None:
        """Test transform_key with function composition patterns."""
        from context.key import ContextKey
        from context.main import Context

        # Create context key and context
        text_key: ContextKey[str] = ContextKey("text", str, "Text")
        context = Context()
        context["text"] = "  hello world  "

        # Create composed transformation
        def strip_and_title(value: str) -> str:
            return value.strip().title()

        # Create and run the flow
        transform_flow = ContextFlowCombinators.transform_key(text_key, strip_and_title)
        result = run_flow_with_input(transform_flow, context)

        assert result["text"] == "Hello World"
