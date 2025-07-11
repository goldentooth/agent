"""Tests for ContextFlowCombinators.forget_key method."""

from typing import Any

import pytest

from context_flow.integration import ContextFlowCombinators, run_flow_with_input
from flow.flow import Flow


class TestForgetKey:
    """Test cases for ContextFlowCombinators.forget_key method."""

    def test_forget_key_basic_functionality(self) -> None:
        """Test that forget_key removes a key from the context."""
        from context.key import ContextKey
        from context.main import Context

        # Create context key and context
        name_key: ContextKey[str] = ContextKey("name", str, "User's name")
        context = Context()
        context["name"] = "Alice"
        context["other_data"] = "preserved"

        # Create and run the flow
        forget_name_flow = ContextFlowCombinators.forget_key(name_key)
        result = run_flow_with_input(forget_name_flow, context)

        # Check that the key was removed but other data preserved
        assert "name" not in result
        assert result["other_data"] == "preserved"
        assert isinstance(result, Context)

    def test_forget_key_with_different_types(self) -> None:
        """Test that forget_key works with different data types."""
        self._test_forget_key_with_integer_type()
        self._test_forget_key_with_boolean_type()
        self._test_forget_key_with_list_type()

    def _test_forget_key_with_integer_type(self) -> None:
        """Test forget_key with integer type."""
        from context.key import ContextKey
        from context.main import Context

        age_key: ContextKey[int] = ContextKey("age", int, "User's age")
        context = Context()
        context["age"] = 25
        context["name"] = "Alice"

        forget_age_flow = ContextFlowCombinators.forget_key(age_key)
        result = run_flow_with_input(forget_age_flow, context)

        assert "age" not in result
        assert result["name"] == "Alice"  # Other data preserved

    def _test_forget_key_with_boolean_type(self) -> None:
        """Test forget_key with boolean type."""
        from context.key import ContextKey
        from context.main import Context

        active_key: ContextKey[bool] = ContextKey("active", bool, "Is user active")
        context = Context()
        context["active"] = True
        context["name"] = "Bob"

        forget_active_flow = ContextFlowCombinators.forget_key(active_key)
        result = run_flow_with_input(forget_active_flow, context)

        assert "active" not in result
        assert result["name"] == "Bob"  # Other data preserved

    def _test_forget_key_with_list_type(self) -> None:
        """Test forget_key with list type."""
        from context.key import ContextKey
        from context.main import Context

        items_key: ContextKey[list[Any]] = ContextKey("items", list, "List of items")
        context = Context()
        context["items"] = [1, 2, 3]
        context["count"] = 3

        forget_items_flow = ContextFlowCombinators.forget_key(items_key)
        result = run_flow_with_input(forget_items_flow, context)

        assert "items" not in result
        assert result["count"] == 3  # Other data preserved

    def test_forget_key_with_missing_key(self) -> None:
        """Test that forget_key is a no-op when key is missing."""
        from context.key import ContextKey
        from context.main import Context

        # Create context key and context without that key
        name_key: ContextKey[str] = ContextKey("name", str, "User's name")
        context = Context()
        context["other_data"] = "preserved"

        # Create and run the flow
        forget_name_flow = ContextFlowCombinators.forget_key(name_key)
        result = run_flow_with_input(forget_name_flow, context)

        # Should be a no-op - nothing removed, other data preserved
        assert "name" not in result  # Still not there
        assert result["other_data"] == "preserved"

    def test_forget_key_with_complex_paths(self) -> None:
        """Test that forget_key works with complex key paths."""
        from context.key import ContextKey
        from context.main import Context

        # Create context key with complex path
        user_email_key: ContextKey[str] = ContextKey(
            "user.profile.email", str, "User email"
        )
        context = Context()
        context["user.profile.email"] = "alice@example.com"
        context["user.profile.name"] = "Alice"

        # Create and run the flow
        forget_email_flow = ContextFlowCombinators.forget_key(user_email_key)
        result = run_flow_with_input(forget_email_flow, context)

        assert "user.profile.email" not in result
        assert result["user.profile.name"] == "Alice"  # Other data preserved

    def test_forget_key_flow_name(self) -> None:
        """Test that forget_key creates flows with descriptive names."""
        from context.key import ContextKey

        # Create context key
        name_key: ContextKey[str] = ContextKey("user.name", str, "User's name")

        # Create the flow
        forget_name_flow = ContextFlowCombinators.forget_key(name_key)

        # Check that the flow has a descriptive name
        assert forget_name_flow.name == "forget_key(user.name)"

    def test_forget_key_with_custom_classes(self) -> None:
        """Test that forget_key works with custom class types."""
        from context.key import ContextKey
        from context.main import Context

        # Define a custom class
        class User:
            def __init__(self, name: str, age: int):
                super().__init__()
                self.name = name
                self.age = age

        self._test_forget_key_custom_class_flow(User)

    def _test_forget_key_custom_class_flow(self, User: type[Any]) -> None:
        """Helper to test forget_key flow with custom class."""
        from context.key import ContextKey
        from context.main import Context

        # Create context key for the custom class
        user_key: ContextKey[Any] = ContextKey("current_user", User, "Current user")
        context = Context()
        user_obj = User("Alice", 30)
        context["current_user"] = user_obj
        context["session_id"] = "abc123"

        # Create and run the flow
        forget_user_flow = ContextFlowCombinators.forget_key(user_key)
        result = run_flow_with_input(forget_user_flow, context)

        assert "current_user" not in result
        assert result["session_id"] == "abc123"  # Other data preserved

    def test_forget_key_preserves_other_context_data(self) -> None:
        """Test that forget_key preserves all other data in the context."""
        from context.key import ContextKey
        from context.main import Context

        # Create context with multiple keys
        target_key: ContextKey[str] = ContextKey("target", str, "Target key")
        context = Context()
        context["target"] = "remove_me"
        context["keep1"] = "value1"
        context["keep2"] = 42
        context["keep3"] = [1, 2, 3]

        # Create and run the flow
        forget_target_flow = ContextFlowCombinators.forget_key(target_key)
        result = run_flow_with_input(forget_target_flow, context)

        # Check that only target was removed
        assert "target" not in result
        assert result["keep1"] == "value1"
        assert result["keep2"] == 42
        assert result["keep3"] == [1, 2, 3]

    def test_forget_key_flow_integration_with_chaining(self) -> None:
        """Test that forget_key flows can be chained with other flows."""
        from context.key import ContextKey
        from context.main import Context

        # Create context keys
        temp1_key: ContextKey[str] = ContextKey("temp1", str, "Temporary key 1")
        temp2_key: ContextKey[str] = ContextKey("temp2", str, "Temporary key 2")
        context = Context()
        context["temp1"] = "value1"
        context["temp2"] = "value2"
        context["permanent"] = "keep_me"

        self._test_chained_forget_flow(temp1_key, temp2_key, context)

    def _test_chained_forget_flow(
        self, temp1_key: Any, temp2_key: Any, context: Any
    ) -> None:
        """Test chained forget flow execution."""
        # Create flows to chain forgets
        forget_temp1 = ContextFlowCombinators.forget_key(temp1_key)
        forget_temp2 = ContextFlowCombinators.forget_key(temp2_key)

        # Chain the flows
        chained_flow = forget_temp1 >> forget_temp2

        # Run the chained flow
        result = run_flow_with_input(chained_flow, context)

        # Check that both temp keys were removed
        assert "temp1" not in result
        assert "temp2" not in result
        assert result["permanent"] == "keep_me"

    def test_forget_key_with_multiple_contexts(self) -> None:
        """Test that forget_key flow works with multiple context inputs."""
        from context.key import ContextKey
        from context.main import Context

        # Create context key
        score_key: ContextKey[int] = ContextKey("score", int, "User's score")

        # Create the flow
        forget_score_flow = ContextFlowCombinators.forget_key(score_key)

        self._test_forget_key_context_one(forget_score_flow)
        self._test_forget_key_context_two(forget_score_flow)

    def _test_forget_key_context_one(self, forget_score_flow: Flow[Any, Any]) -> None:
        """Test forget_key with first context."""
        from context.main import Context

        context1 = Context()
        context1["score"] = 100
        context1["name"] = "Alice"
        result1 = run_flow_with_input(forget_score_flow, context1)
        assert "score" not in result1
        assert result1["name"] == "Alice"

    def _test_forget_key_context_two(self, forget_score_flow: Flow[Any, Any]) -> None:
        """Test forget_key with second context."""
        from context.main import Context

        context2 = Context()
        context2["score"] = 200
        context2["level"] = "expert"
        result2 = run_flow_with_input(forget_score_flow, context2)
        assert "score" not in result2
        assert result2["level"] == "expert"

    def test_forget_key_immutability(self) -> None:
        """Test that forget_key creates new contexts without modifying the original."""
        from context.key import ContextKey
        from context.main import Context

        # Create original context with some data
        target_key: ContextKey[str] = ContextKey("target_key", str, "Target key")
        original_context = Context()
        original_context["target_key"] = "value"
        original_context["other_key"] = "other_value"

        # Create and run the flow
        forget_flow = ContextFlowCombinators.forget_key(target_key)
        result_context = run_flow_with_input(forget_flow, original_context)

        self._verify_original_unchanged_for_forget(original_context)
        self._verify_result_has_key_removed(result_context)

    def _verify_original_unchanged_for_forget(self, original_context: Any) -> None:
        """Verify original context was not modified."""
        assert "target_key" in original_context
        assert original_context["target_key"] == "value"
        assert original_context["other_key"] == "other_value"

    def _verify_result_has_key_removed(self, result_context: Any) -> None:
        """Verify result context has the key removed."""
        assert "target_key" not in result_context
        assert result_context["other_key"] == "other_value"

    def test_forget_key_static_method_access(self) -> None:
        """Test that forget_key can be accessed as a static method."""
        from context.key import ContextKey

        # Create context key
        test_key: ContextKey[str] = ContextKey("test", str, "Test key")

        # Should be able to access as static method
        flow = ContextFlowCombinators.forget_key(test_key)
        assert isinstance(flow, Flow)

        # Should also work through class instance (though not recommended)
        combinators = ContextFlowCombinators()
        flow2 = combinators.forget_key(test_key)
        assert isinstance(flow2, Flow)

    def test_forget_key_with_none_value(self) -> None:
        """Test that forget_key works when the value being removed is None."""
        from context.key import ContextKey
        from context.main import Context

        # Create context key that has None value
        optional_key: ContextKey[object] = ContextKey("optional", object, "Optional")
        context = Context()
        context["optional"] = None
        context["other"] = "data"

        # Create and run the flow
        forget_optional_flow = ContextFlowCombinators.forget_key(optional_key)
        result = run_flow_with_input(forget_optional_flow, context)

        assert "optional" not in result
        assert result["other"] == "data"

    def test_forget_key_cleanup_pattern(self) -> None:
        """Test forget_key as part of cleanup patterns."""
        from context.key import ContextKey
        from context.main import Context

        # Create temporary keys that need cleanup
        temp_data_key: ContextKey[str] = ContextKey("temp_data", str, "Temporary data")
        temp_calc_key: ContextKey[int] = ContextKey(
            "temp_calc", int, "Temp calculation"
        )

        context = Context()
        context["temp_data"] = "processing"
        context["temp_calc"] = 42
        context["final_result"] = "success"
        context["user_id"] = "user123"

        self._test_cleanup_flow_execution(temp_data_key, temp_calc_key, context)

    def _test_cleanup_flow_execution(
        self, temp_data_key: Any, temp_calc_key: Any, context: Any
    ) -> None:
        """Execute cleanup flow and verify results."""
        # Create cleanup flow that removes all temporary data
        cleanup_data = ContextFlowCombinators.forget_key(temp_data_key)
        cleanup_calc = ContextFlowCombinators.forget_key(temp_calc_key)
        cleanup_flow = cleanup_data >> cleanup_calc

        # Run cleanup
        result = run_flow_with_input(cleanup_flow, context)

        # Only permanent data should remain
        assert "temp_data" not in result
        assert "temp_calc" not in result
        assert result["final_result"] == "success"
        assert result["user_id"] == "user123"

    def test_forget_key_idempotent(self) -> None:
        """Test that forget_key is idempotent - can be applied multiple times."""
        from context.key import ContextKey
        from context.main import Context

        # Create context with key to forget
        name_key: ContextKey[str] = ContextKey("name", str, "Name")
        context = Context()
        context["name"] = "Alice"
        context["age"] = 25

        # Create the forget flow
        forget_name_flow = ContextFlowCombinators.forget_key(name_key)

        self._test_forget_key_first_application(forget_name_flow, context)

    def _test_forget_key_first_application(
        self, forget_name_flow: Any, context: Any
    ) -> None:
        """Test first application of forget flow."""
        # Apply forget once
        result1 = run_flow_with_input(forget_name_flow, context)
        assert "name" not in result1
        assert result1["age"] == 25

        # Apply forget again to the result - should be no-op
        result2 = run_flow_with_input(forget_name_flow, result1)
        self._verify_idempotent_results(result1, result2)

    def _verify_idempotent_results(self, result1: Any, result2: Any) -> None:
        """Verify that forget operations are idempotent."""
        assert "name" not in result2
        assert result2["age"] == 25

        # Results should be equivalent - check keys and values
        assert set(result1.keys()) == set(result2.keys())
        for key in result1.keys():
            assert result1[key] == result2[key]

    def test_forget_key_vs_other_key_operations(self) -> None:
        """Test forget_key in combination with other key operations."""
        from context.key import ContextKey
        from context.main import Context

        # Create context keys
        source_key: ContextKey[str] = ContextKey("source", str, "Source")
        dest_key: ContextKey[str] = ContextKey("dest", str, "Destination")
        temp_key: ContextKey[str] = ContextKey("temp", str, "Temporary")

        context = Context()
        context["source"] = "data"
        context["temp"] = "cleanup_me"

        self._test_combined_copy_and_forget_flow(
            source_key, dest_key, temp_key, context
        )

    def _test_combined_copy_and_forget_flow(
        self, source_key: Any, dest_key: Any, temp_key: Any, context: Any
    ) -> None:
        """Test combined copy and forget flow operations."""
        # Create a complex flow: copy source to dest, then forget temp
        copy_flow = ContextFlowCombinators.copy_key(source_key, dest_key)
        forget_flow = ContextFlowCombinators.forget_key(temp_key)
        combined_flow = copy_flow >> forget_flow

        result = run_flow_with_input(combined_flow, context)

        # Should have copied data and removed temp
        assert result["source"] == "data"  # Original remains
        assert result["dest"] == "data"  # Copy created
        assert "temp" not in result  # Temp removed
