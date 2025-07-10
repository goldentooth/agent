"""Tests for ContextFlowCombinators.copy_key method."""

from typing import Any

import pytest

from context_flow.integration import (
    ContextFlowCombinators,
    ContextTypeMismatchError,
    MissingRequiredKeyError,
    run_flow_with_input,
)
from flow.flow import Flow


class TestCopyKey:
    """Test cases for ContextFlowCombinators.copy_key method."""

    def test_copy_key_basic_functionality(self) -> None:
        """Test that copy_key copies a value from one key to another."""
        from context.key import ContextKey
        from context.main import Context

        # Create context keys and context
        source_key: ContextKey[str] = ContextKey("source_name", str, "Source name key")
        dest_key: ContextKey[str] = ContextKey("dest_name", str, "Destination name key")
        context = Context()
        context["source_name"] = "Alice"

        # Create and run the flow
        copy_name_flow = ContextFlowCombinators.copy_key(source_key, dest_key)
        result = run_flow_with_input(copy_name_flow, context)

        # Check that the value was copied (source still exists)
        assert result["dest_name"] == "Alice"
        assert result["source_name"] == "Alice"  # Source key should still exist
        assert isinstance(result, Context)

    def test_copy_key_with_different_types(self) -> None:
        """Test that copy_key works with different data types."""
        self._test_copy_key_with_integer_type()
        self._test_copy_key_with_boolean_type()
        self._test_copy_key_with_list_type()

    def _test_copy_key_with_integer_type(self) -> None:
        """Test copy_key with integer type."""
        from context.key import ContextKey
        from context.main import Context

        source_key: ContextKey[int] = ContextKey("source_age", int, "Source age key")
        dest_key: ContextKey[int] = ContextKey("dest_age", int, "Destination age key")
        context = Context()
        context["source_age"] = 25

        copy_age_flow = ContextFlowCombinators.copy_key(source_key, dest_key)
        result = run_flow_with_input(copy_age_flow, context)

        assert result["dest_age"] == 25
        assert result["source_age"] == 25  # Source still exists

    def _test_copy_key_with_boolean_type(self) -> None:
        """Test copy_key with boolean type."""
        from context.key import ContextKey
        from context.main import Context

        source_key: ContextKey[bool] = ContextKey(
            "source_active", bool, "Source active"
        )
        dest_key: ContextKey[bool] = ContextKey("dest_active", bool, "Dest active")
        context = Context()
        context["source_active"] = True

        copy_active_flow = ContextFlowCombinators.copy_key(source_key, dest_key)
        result = run_flow_with_input(copy_active_flow, context)

        assert result["dest_active"] is True
        assert result["source_active"] is True  # Source still exists

    def _test_copy_key_with_list_type(self) -> None:
        """Test copy_key with list type."""
        from context.key import ContextKey
        from context.main import Context

        source_key: ContextKey[list[Any]] = ContextKey(
            "source_items", list, "Source items"
        )
        dest_key: ContextKey[list[Any]] = ContextKey("dest_items", list, "Dest items")
        context = Context()
        context["source_items"] = [1, 2, 3]

        copy_items_flow = ContextFlowCombinators.copy_key(source_key, dest_key)
        result = run_flow_with_input(copy_items_flow, context)

        assert result["dest_items"] == [1, 2, 3]
        assert result["source_items"] == [1, 2, 3]  # Source still exists

    def test_copy_key_with_missing_source_key(self) -> None:
        """Test that copy_key raises MissingRequiredKeyError when source key is missing."""
        from context.key import ContextKey
        from context.main import Context

        # Create context keys and empty context
        source_key: ContextKey[str] = ContextKey("source_name", str, "Source name key")
        dest_key: ContextKey[str] = ContextKey("dest_name", str, "Destination name key")
        context = Context()

        # Create the flow
        copy_name_flow = ContextFlowCombinators.copy_key(source_key, dest_key)

        # Should raise MissingRequiredKeyError
        with pytest.raises(
            MissingRequiredKeyError,
            match="Required context key 'source_name' is missing",
        ):
            run_flow_with_input(copy_name_flow, context)

    def test_copy_key_with_type_mismatch_between_keys(self) -> None:
        """Test that copy_key validates type compatibility between keys."""
        from context.key import ContextKey
        from context.main import Context

        # Create context keys with different types
        source_key: ContextKey[str] = ContextKey("source_value", str, "String value")
        dest_key: ContextKey[int] = ContextKey("dest_value", int, "Integer value")
        context = Context()
        context["source_value"] = "not_an_int"

        # Should raise ContextTypeMismatchError at runtime
        copy_flow = ContextFlowCombinators.copy_key(source_key, dest_key)  # type: ignore[misc]

        with pytest.raises(
            ContextTypeMismatchError,
            match="Context key 'dest_value' expected int, got str",
        ):
            run_flow_with_input(copy_flow, context)

    def test_copy_key_with_existing_destination_key(self) -> None:
        """Test that copy_key overwrites existing destination key."""
        from context.key import ContextKey
        from context.main import Context

        # Create context with both keys present
        source_key: ContextKey[str] = ContextKey("source_name", str, "Source name key")
        dest_key: ContextKey[str] = ContextKey("dest_name", str, "Destination name key")
        context = Context()
        context["source_name"] = "Alice"
        context["dest_name"] = "Bob"

        # Create and run the flow
        copy_name_flow = ContextFlowCombinators.copy_key(source_key, dest_key)
        result = run_flow_with_input(copy_name_flow, context)

        # Destination should have source value, source should still exist
        assert result["dest_name"] == "Alice"
        assert result["source_name"] == "Alice"

    def test_copy_key_with_complex_paths(self) -> None:
        """Test that copy_key works with complex key paths."""
        from context.key import ContextKey
        from context.main import Context

        # Create context keys with complex paths
        source_key: ContextKey[str] = ContextKey(
            "user.source.location", str, "Source location"
        )
        dest_key: ContextKey[str] = ContextKey(
            "user.dest.location", str, "Destination location"
        )
        context = Context()
        context["user.source.location"] = "New York"

        # Create and run the flow
        copy_location_flow = ContextFlowCombinators.copy_key(source_key, dest_key)
        result = run_flow_with_input(copy_location_flow, context)

        assert result["user.dest.location"] == "New York"
        assert result["user.source.location"] == "New York"  # Source still exists

    def test_copy_key_flow_name(self) -> None:
        """Test that copy_key creates flows with descriptive names."""
        from context.key import ContextKey

        # Create context keys
        source_key: ContextKey[str] = ContextKey("source.path", str, "Source key")
        dest_key: ContextKey[str] = ContextKey("dest.path", str, "Destination key")

        # Create the flow
        copy_flow = ContextFlowCombinators.copy_key(source_key, dest_key)

        # Check that the flow has a descriptive name
        assert copy_flow.name == "copy_key(source.path -> dest.path)"

    def test_copy_key_with_custom_classes(self) -> None:
        """Test that copy_key works with custom class types."""
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

        self._test_copy_key_custom_class_flow(User)

    def _test_copy_key_custom_class_flow(self, User: type[Any]) -> None:
        """Helper to test copy_key flow with custom class."""
        from context.key import ContextKey
        from context.main import Context

        # Create context keys for the custom class
        source_key: ContextKey[Any] = ContextKey("source_user", User, "Source user")
        dest_key: ContextKey[Any] = ContextKey("dest_user", User, "Destination user")
        context = Context()
        user_obj = User("Alice", 30)
        context["source_user"] = user_obj

        # Create and run the flow
        copy_user_flow = ContextFlowCombinators.copy_key(source_key, dest_key)
        result = run_flow_with_input(copy_user_flow, context)

        assert result["dest_user"] == user_obj
        assert result["source_user"] == user_obj  # Source still exists
        assert isinstance(result["dest_user"], User)
        assert result["dest_user"].name == "Alice"
        assert result["dest_user"].age == 30

    def test_copy_key_preserves_other_context_data(self) -> None:
        """Test that copy_key preserves other data in the context."""
        from context.key import ContextKey
        from context.main import Context

        # Create context with multiple keys
        source_key: ContextKey[str] = ContextKey("source_name", str, "Source name key")
        dest_key: ContextKey[str] = ContextKey("dest_name", str, "Destination name key")
        context = Context()
        context["source_name"] = "Alice"
        context["other_data"] = "preserved"
        context["more_data"] = 42

        # Create and run the flow
        copy_name_flow = ContextFlowCombinators.copy_key(source_key, dest_key)
        result = run_flow_with_input(copy_name_flow, context)

        # Check that copy happened and all data preserved
        assert result["dest_name"] == "Alice"
        assert result["source_name"] == "Alice"  # Source still exists
        assert result["other_data"] == "preserved"
        assert result["more_data"] == 42

    def test_copy_key_flow_integration_with_chaining(self) -> None:
        """Test that copy_key flows can be chained with other flows."""
        from context.key import ContextKey
        from context.main import Context

        # Create context keys
        source_key: ContextKey[str] = ContextKey("original", str, "Original")
        copy1_key: ContextKey[str] = ContextKey("copy1", str, "First copy")
        copy2_key: ContextKey[str] = ContextKey("copy2", str, "Second copy")
        context = Context()
        context["original"] = "value"

        # Create flows to chain copies
        copy_to_1 = ContextFlowCombinators.copy_key(source_key, copy1_key)
        copy_to_2 = ContextFlowCombinators.copy_key(copy1_key, copy2_key)

        # Chain the flows
        chained_flow = copy_to_1 >> copy_to_2

        # Run the chained flow
        result = run_flow_with_input(chained_flow, context)

        # Check all copies exist
        assert result["original"] == "value"
        assert result["copy1"] == "value"
        assert result["copy2"] == "value"

    def test_copy_key_with_multiple_contexts(self) -> None:
        """Test that copy_key flow works with multiple context inputs."""
        from context.key import ContextKey
        from context.main import Context

        # Create context keys
        source_key: ContextKey[int] = ContextKey("source_score", int, "Source score")
        dest_key: ContextKey[int] = ContextKey("dest_score", int, "Destination score")

        # Create the flow
        copy_score_flow = ContextFlowCombinators.copy_key(source_key, dest_key)

        self._test_copy_key_context_one(copy_score_flow)
        self._test_copy_key_context_two(copy_score_flow)

    def _test_copy_key_context_one(self, copy_score_flow: Flow[Any, Any]) -> None:
        """Test copy_key with first context."""
        from context.main import Context

        context1 = Context()
        context1["source_score"] = 100
        result1 = run_flow_with_input(copy_score_flow, context1)
        assert result1["dest_score"] == 100
        assert result1["source_score"] == 100  # Source still exists

    def _test_copy_key_context_two(self, copy_score_flow: Flow[Any, Any]) -> None:
        """Test copy_key with second context."""
        from context.main import Context

        context2 = Context()
        context2["source_score"] = 200
        result2 = run_flow_with_input(copy_score_flow, context2)
        assert result2["dest_score"] == 200
        assert result2["source_score"] == 200  # Source still exists

    def test_copy_key_error_message_formatting(self) -> None:
        """Test that copy_key produces well-formatted error messages."""
        from context.key import ContextKey
        from context.main import Context

        # Test missing key error message
        source_key: ContextKey[str] = ContextKey(
            "user.source.email", str, "Source email"
        )
        dest_key: ContextKey[str] = ContextKey(
            "user.dest.email", str, "Destination email"
        )
        context = Context()

        copy_email_flow = ContextFlowCombinators.copy_key(source_key, dest_key)

        with pytest.raises(MissingRequiredKeyError) as exc_info:
            run_flow_with_input(copy_email_flow, context)

        assert "Required context key 'user.source.email' is missing" in str(
            exc_info.value
        )

    def test_copy_key_immutability(self) -> None:
        """Test that copy_key creates new contexts without modifying the original."""
        from context.key import ContextKey
        from context.main import Context

        # Create original context with some data
        source_key: ContextKey[str] = ContextKey("source_key", str, "Source key")
        dest_key: ContextKey[str] = ContextKey("dest_key", str, "Destination key")
        original_context = Context()
        original_context["source_key"] = "value"
        original_context["other_key"] = "other_value"

        # Create and run the flow
        copy_flow = ContextFlowCombinators.copy_key(source_key, dest_key)
        result_context = run_flow_with_input(copy_flow, original_context)

        self._verify_original_unchanged_for_copy(original_context)
        self._verify_result_has_copy(result_context)

    def _verify_original_unchanged_for_copy(self, original_context: Any) -> None:
        """Verify original context was not modified."""
        assert "source_key" in original_context
        assert original_context["source_key"] == "value"
        assert "dest_key" not in original_context

    def _verify_result_has_copy(self, result_context: Any) -> None:
        """Verify result context has the copy."""
        assert result_context["source_key"] == "value"  # Source still exists
        assert result_context["dest_key"] == "value"
        assert result_context["other_key"] == "other_value"

    def test_copy_key_static_method_access(self) -> None:
        """Test that copy_key can be accessed as a static method."""
        from context.key import ContextKey

        # Create context keys
        source_key: ContextKey[str] = ContextKey("source", str, "Source key")
        dest_key: ContextKey[str] = ContextKey("dest", str, "Destination key")

        # Should be able to access as static method
        flow = ContextFlowCombinators.copy_key(source_key, dest_key)
        assert isinstance(flow, Flow)

        # Should also work through class instance (though not recommended)
        combinators = ContextFlowCombinators()
        flow2 = combinators.copy_key(source_key, dest_key)
        assert isinstance(flow2, Flow)

    def test_copy_key_with_none_value(self) -> None:
        """Test that copy_key handles None values correctly."""
        from context.key import ContextKey
        from context.main import Context

        # Create context keys that can accept None
        source_key: ContextKey[object] = ContextKey(
            "source_optional", object, "Source opt"
        )
        dest_key: ContextKey[object] = ContextKey("dest_optional", object, "Dest opt")
        context = Context()
        context["source_optional"] = None

        # Create and run the flow
        copy_optional_flow = ContextFlowCombinators.copy_key(source_key, dest_key)
        result = run_flow_with_input(copy_optional_flow, context)

        assert result["dest_optional"] is None
        assert result["source_optional"] is None  # Source still exists

    def test_copy_key_with_same_source_and_destination(self) -> None:
        """Test that copy_key with same source and destination is effectively a no-op."""
        from context.key import ContextKey
        from context.main import Context

        # Create context key (same for source and destination)
        key: ContextKey[str] = ContextKey("name", str, "Name key")
        context = Context()
        context["name"] = "Alice"

        # Create and run the flow with same source and destination
        copy_flow = ContextFlowCombinators.copy_key(key, key)
        result = run_flow_with_input(copy_flow, context)

        # Value should still be present (essentially overwrites itself)
        assert result["name"] == "Alice"

    def test_copy_key_vs_move_key_difference(self) -> None:
        """Test that copy_key leaves source key intact unlike move_key."""
        from context.key import ContextKey
        from context.main import Context

        # Create context keys and context
        source_key: ContextKey[str] = ContextKey("from_here", str, "Source")
        dest_key: ContextKey[str] = ContextKey("to_here", str, "Destination")
        context = Context()
        context["from_here"] = "data"

        self._test_copy_key_behavior(source_key, dest_key, context)
        self._test_move_key_behavior(source_key, dest_key, context)

    def _test_copy_key_behavior(
        self, source_key: Any, dest_key: Any, context: Any
    ) -> None:
        """Test copy_key behavior - source remains."""
        copy_flow = ContextFlowCombinators.copy_key(source_key, dest_key)
        copy_result = run_flow_with_input(copy_flow, context)

        # With copy_key, source should still exist
        assert "from_here" in copy_result
        assert copy_result["from_here"] == "data"
        assert copy_result["to_here"] == "data"

    def _test_move_key_behavior(
        self, source_key: Any, dest_key: Any, context: Any
    ) -> None:
        """Test move_key behavior - source removed."""
        move_flow = ContextFlowCombinators.move_key(source_key, dest_key)
        move_result = run_flow_with_input(move_flow, context)

        # With move_key, source should be removed
        assert "from_here" not in move_result
        assert move_result["to_here"] == "data"
