"""Tests for ContextFlowCombinators.move_key method."""

from typing import Any

import pytest

from context_flow.integration import (
    ContextFlowCombinators,
    ContextTypeMismatchError,
    MissingRequiredKeyError,
    run_flow_with_input,
)
from flow.flow import Flow


class TestMoveKey:
    """Test cases for ContextFlowCombinators.move_key method."""

    def test_move_key_basic_functionality(self) -> None:
        """Test that move_key moves a value from one key to another."""
        from context.key import ContextKey
        from context.main import Context

        # Create context keys and context
        old_key: ContextKey[str] = ContextKey("old_name", str, "Old name key")
        new_key: ContextKey[str] = ContextKey("new_name", str, "New name key")
        context = Context()
        context["old_name"] = "Alice"

        # Create and run the flow
        move_name_flow = ContextFlowCombinators.move_key(old_key, new_key)
        result = run_flow_with_input(move_name_flow, context)

        # Check that the value was moved
        assert result["new_name"] == "Alice"
        assert "old_name" not in result
        assert isinstance(result, Context)

    def test_move_key_with_different_types(self) -> None:
        """Test that move_key works with different data types."""
        self._test_move_key_with_integer_type()
        self._test_move_key_with_boolean_type()
        self._test_move_key_with_list_type()

    def _test_move_key_with_integer_type(self) -> None:
        """Test move_key with integer type."""
        from context.key import ContextKey
        from context.main import Context

        old_key: ContextKey[int] = ContextKey("old_age", int, "Old age key")
        new_key: ContextKey[int] = ContextKey("new_age", int, "New age key")
        context = Context()
        context["old_age"] = 25

        move_age_flow = ContextFlowCombinators.move_key(old_key, new_key)
        result = run_flow_with_input(move_age_flow, context)

        assert result["new_age"] == 25
        assert "old_age" not in result

    def _test_move_key_with_boolean_type(self) -> None:
        """Test move_key with boolean type."""
        from context.key import ContextKey
        from context.main import Context

        old_key: ContextKey[bool] = ContextKey("old_active", bool, "Old active key")
        new_key: ContextKey[bool] = ContextKey("new_active", bool, "New active key")
        context = Context()
        context["old_active"] = True

        move_active_flow = ContextFlowCombinators.move_key(old_key, new_key)
        result = run_flow_with_input(move_active_flow, context)

        assert result["new_active"] is True
        assert "old_active" not in result

    def _test_move_key_with_list_type(self) -> None:
        """Test move_key with list type."""
        from context.key import ContextKey
        from context.main import Context

        old_key: ContextKey[list[Any]] = ContextKey("old_items", list, "Old items")
        new_key: ContextKey[list[Any]] = ContextKey("new_items", list, "New items")
        context = Context()
        context["old_items"] = [1, 2, 3]

        move_items_flow = ContextFlowCombinators.move_key(old_key, new_key)
        result = run_flow_with_input(move_items_flow, context)

        assert result["new_items"] == [1, 2, 3]
        assert "old_items" not in result

    def test_move_key_with_missing_source_key(self) -> None:
        """Test that move_key raises MissingRequiredKeyError when source key is missing."""
        from context.key import ContextKey
        from context.main import Context

        # Create context keys and empty context
        old_key: ContextKey[str] = ContextKey("old_name", str, "Old name key")
        new_key: ContextKey[str] = ContextKey("new_name", str, "New name key")
        context = Context()

        # Create the flow
        move_name_flow = ContextFlowCombinators.move_key(old_key, new_key)

        # Should raise MissingRequiredKeyError
        with pytest.raises(
            MissingRequiredKeyError, match="Required context key 'old_name' is missing"
        ):
            run_flow_with_input(move_name_flow, context)

    def test_move_key_with_type_mismatch_between_keys(self) -> None:
        """Test that move_key validates type compatibility between keys."""
        from context.key import ContextKey
        from context.main import Context

        # Create context keys with different types
        old_key: ContextKey[str] = ContextKey("old_value", str, "String value")
        new_key: ContextKey[int] = ContextKey("new_value", int, "Integer value")
        context = Context()
        context["old_value"] = "not_an_int"

        # Should raise ContextTypeMismatchError at flow creation or runtime
        move_flow = ContextFlowCombinators.move_key(old_key, new_key)  # type: ignore[misc]

        with pytest.raises(
            ContextTypeMismatchError,
            match="Context key 'new_value' expected int, got str",
        ):
            run_flow_with_input(move_flow, context)

    def test_move_key_with_existing_destination_key(self) -> None:
        """Test that move_key overwrites existing destination key."""
        from context.key import ContextKey
        from context.main import Context

        # Create context with both keys present
        old_key: ContextKey[str] = ContextKey("old_name", str, "Old name key")
        new_key: ContextKey[str] = ContextKey("new_name", str, "New name key")
        context = Context()
        context["old_name"] = "Alice"
        context["new_name"] = "Bob"

        # Create and run the flow
        move_name_flow = ContextFlowCombinators.move_key(old_key, new_key)
        result = run_flow_with_input(move_name_flow, context)

        # New key should have old value, old key should be removed
        assert result["new_name"] == "Alice"
        assert "old_name" not in result

    def test_move_key_with_complex_paths(self) -> None:
        """Test that move_key works with complex key paths."""
        from context.key import ContextKey
        from context.main import Context

        # Create context keys with complex paths
        old_key: ContextKey[str] = ContextKey("user.old.location", str, "Old location")
        new_key: ContextKey[str] = ContextKey("user.new.location", str, "New location")
        context = Context()
        context["user.old.location"] = "New York"

        # Create and run the flow
        move_location_flow = ContextFlowCombinators.move_key(old_key, new_key)
        result = run_flow_with_input(move_location_flow, context)

        assert result["user.new.location"] == "New York"
        assert "user.old.location" not in result

    def test_move_key_flow_name(self) -> None:
        """Test that move_key creates flows with descriptive names."""
        from context.key import ContextKey

        # Create context keys
        old_key: ContextKey[str] = ContextKey("old.path", str, "Old key")
        new_key: ContextKey[str] = ContextKey("new.path", str, "New key")

        # Create the flow
        move_flow = ContextFlowCombinators.move_key(old_key, new_key)

        # Check that the flow has a descriptive name
        assert move_flow.name == "move_key(old.path -> new.path)"

    def test_move_key_with_custom_classes(self) -> None:
        """Test that move_key works with custom class types."""
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

        self._test_move_key_custom_class_flow(User)

    def _test_move_key_custom_class_flow(self, User: type[Any]) -> None:
        """Helper to test move_key flow with custom class."""
        from context.key import ContextKey
        from context.main import Context

        # Create context keys for the custom class
        old_key: ContextKey[Any] = ContextKey("old_user", User, "Old user")
        new_key: ContextKey[Any] = ContextKey("new_user", User, "New user")
        context = Context()
        user_obj = User("Alice", 30)
        context["old_user"] = user_obj

        # Create and run the flow
        move_user_flow = ContextFlowCombinators.move_key(old_key, new_key)
        result = run_flow_with_input(move_user_flow, context)

        assert result["new_user"] == user_obj
        assert isinstance(result["new_user"], User)
        assert result["new_user"].name == "Alice"
        assert result["new_user"].age == 30
        assert "old_user" not in result

    def test_move_key_preserves_other_context_data(self) -> None:
        """Test that move_key preserves other data in the context."""
        from context.key import ContextKey
        from context.main import Context

        # Create context with multiple keys
        old_key: ContextKey[str] = ContextKey("old_name", str, "Old name key")
        new_key: ContextKey[str] = ContextKey("new_name", str, "New name key")
        context = Context()
        context["old_name"] = "Alice"
        context["other_data"] = "preserved"
        context["more_data"] = 42

        # Create and run the flow
        move_name_flow = ContextFlowCombinators.move_key(old_key, new_key)
        result = run_flow_with_input(move_name_flow, context)

        # Check that move happened and other data preserved
        assert result["new_name"] == "Alice"
        assert "old_name" not in result
        assert result["other_data"] == "preserved"
        assert result["more_data"] == 42

    def test_move_key_flow_integration_with_chaining(self) -> None:
        """Test that move_key flows can be chained with other flows."""
        from context.key import ContextKey
        from context.main import Context

        # Create context keys
        old_key: ContextKey[str] = ContextKey("old_name", str, "Old name")
        temp_key: ContextKey[str] = ContextKey("temp_name", str, "Temp name")
        final_key: ContextKey[str] = ContextKey("final_name", str, "Final name")
        context = Context()
        context["old_name"] = "alice"

        # Create flows to chain moves
        move_to_temp = ContextFlowCombinators.move_key(old_key, temp_key)
        move_to_final = ContextFlowCombinators.move_key(temp_key, final_key)

        # Chain the flows
        chained_flow = move_to_temp >> move_to_final

        # Run the chained flow
        result = run_flow_with_input(chained_flow, context)

        # Check final result
        assert result["final_name"] == "alice"
        assert "old_name" not in result
        assert "temp_name" not in result

    def test_move_key_with_multiple_contexts(self) -> None:
        """Test that move_key flow works with multiple context inputs."""
        from context.key import ContextKey
        from context.main import Context

        # Create context keys
        old_key: ContextKey[int] = ContextKey("old_score", int, "Old score")
        new_key: ContextKey[int] = ContextKey("new_score", int, "New score")

        # Create the flow
        move_score_flow = ContextFlowCombinators.move_key(old_key, new_key)

        self._test_move_key_context_one(move_score_flow)
        self._test_move_key_context_two(move_score_flow)

    def _test_move_key_context_one(self, move_score_flow: Flow[Any, Any]) -> None:
        """Test move_key with first context."""
        from context.main import Context

        context1 = Context()
        context1["old_score"] = 100
        result1 = run_flow_with_input(move_score_flow, context1)
        assert result1["new_score"] == 100
        assert "old_score" not in result1

    def _test_move_key_context_two(self, move_score_flow: Flow[Any, Any]) -> None:
        """Test move_key with second context."""
        from context.main import Context

        context2 = Context()
        context2["old_score"] = 200
        result2 = run_flow_with_input(move_score_flow, context2)
        assert result2["new_score"] == 200
        assert "old_score" not in result2

    def test_move_key_error_message_formatting(self) -> None:
        """Test that move_key produces well-formatted error messages."""
        from context.key import ContextKey
        from context.main import Context

        # Test missing key error message
        old_key: ContextKey[str] = ContextKey("user.old.email", str, "Old email")
        new_key: ContextKey[str] = ContextKey("user.new.email", str, "New email")
        context = Context()

        move_email_flow = ContextFlowCombinators.move_key(old_key, new_key)

        with pytest.raises(MissingRequiredKeyError) as exc_info:
            run_flow_with_input(move_email_flow, context)

        assert "Required context key 'user.old.email' is missing" in str(exc_info.value)

    def test_move_key_immutability(self) -> None:
        """Test that move_key creates new contexts without modifying the original."""
        from context.key import ContextKey
        from context.main import Context

        # Create original context with some data
        old_key: ContextKey[str] = ContextKey("old_key", str, "Old key")
        new_key: ContextKey[str] = ContextKey("new_key", str, "New key")
        original_context = Context()
        original_context["old_key"] = "value"
        original_context["other_key"] = "other_value"

        # Create and run the flow
        move_flow = ContextFlowCombinators.move_key(old_key, new_key)
        result_context = run_flow_with_input(move_flow, original_context)

        self._verify_original_unchanged(original_context)
        self._verify_result_modified(result_context)

    def _verify_original_unchanged(self, original_context: Any) -> None:
        """Verify original context was not modified."""
        assert "old_key" in original_context
        assert original_context["old_key"] == "value"
        assert "new_key" not in original_context

    def _verify_result_modified(self, result_context: Any) -> None:
        """Verify result context has the move applied."""
        assert "old_key" not in result_context
        assert result_context["new_key"] == "value"
        assert result_context["other_key"] == "other_value"

    def test_move_key_static_method_access(self) -> None:
        """Test that move_key can be accessed as a static method."""
        from context.key import ContextKey

        # Create context keys
        old_key: ContextKey[str] = ContextKey("old", str, "Old key")
        new_key: ContextKey[str] = ContextKey("new", str, "New key")

        # Should be able to access as static method
        flow = ContextFlowCombinators.move_key(old_key, new_key)
        assert isinstance(flow, Flow)

        # Should also work through class instance (though not recommended)
        combinators = ContextFlowCombinators()
        flow2 = combinators.move_key(old_key, new_key)
        assert isinstance(flow2, Flow)

    def test_move_key_with_none_value(self) -> None:
        """Test that move_key handles None values correctly."""
        from context.key import ContextKey
        from context.main import Context

        # Create context keys that can accept None
        old_key: ContextKey[object] = ContextKey("old_optional", object, "Old optional")
        new_key: ContextKey[object] = ContextKey("new_optional", object, "New optional")
        context = Context()
        context["old_optional"] = None

        # Create and run the flow
        move_optional_flow = ContextFlowCombinators.move_key(old_key, new_key)
        result = run_flow_with_input(move_optional_flow, context)

        assert result["new_optional"] is None
        assert "old_optional" not in result

    def test_move_key_with_same_source_and_destination(self) -> None:
        """Test that move_key with same source and destination is a no-op."""
        from context.key import ContextKey
        from context.main import Context

        # Create context key (same for source and destination)
        key: ContextKey[str] = ContextKey("name", str, "Name key")
        context = Context()
        context["name"] = "Alice"

        # Create and run the flow with same source and destination
        move_flow = ContextFlowCombinators.move_key(key, key)
        result = run_flow_with_input(move_flow, context)

        # Value should still be present (essentially a no-op)
        assert result["name"] == "Alice"
