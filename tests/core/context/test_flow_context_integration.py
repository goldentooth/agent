"""Tests for Flow-Context integration with type-safe keys and dependency declarations."""

import pytest

from goldentooth_agent.core.context import (
    Context,
    ContextKey,
    ContextTypeMismatchError,
    MissingRequiredKeyError,
    context_flow,
)
from goldentooth_agent.core.flow import Flow


class TestContextKeySystem:
    """Test the type-safe ContextKey system for Flow dependencies."""

    def test_context_key_creation(self):
        """Test creating typed context keys."""
        # Create type-safe keys
        name_key = ContextKey.create("user_name", str, "User's name")
        age_key = ContextKey.create("user_age", int, "User's age")

        assert name_key.path == "user_name"
        assert name_key.type_ is str
        assert age_key.path == "user_age"
        assert age_key.type_ is int

    def test_context_key_equality(self):
        """Test context key equality and hashing."""
        key1 = ContextKey.create("test", str, "")
        key2 = ContextKey.create("test", str, "")
        key3 = ContextKey.create("different", str, "")

        assert key1 == key2  # Same name
        assert key1 != key3  # Different name
        assert hash(key1) == hash(key2)
        assert hash(key1) != hash(key3)

    def test_context_key_representation(self):
        """Test string representation of context keys."""
        key = ContextKey.create("test_key", int, "Test key")

        assert str(key) == "test_key"
        assert repr(key) == "ContextKey(test_key<int>)"


class TestFlowContextBasics:
    """Test basic Flow-Context integration patterns."""

    def test_flow_reads_context_key(self):
        """Test Flow that reads a specific context key."""
        name_key = ContextKey.create("name", str, "User's name")

        # Create flow that gets a context key
        get_name_flow = Flow.get_key(name_key)

        context = Context()
        context["name"] = "Alice"

        result = get_name_flow.run(context)
        assert result == "Alice"

    def test_flow_writes_context_key(self):
        """Test Flow that writes a specific context key."""
        name_key = ContextKey.create("name", str, "User's name")

        # Create flow that sets a context key
        set_name_flow = Flow.set_key(name_key, "Bob")

        context = Context()
        result_context = set_name_flow.run(context)

        assert result_context["name"] == "Bob"

    def test_flow_requires_context_keys(self):
        """Test Flow that requires certain context keys to be present."""
        name_key = ContextKey.create("name", str, "User's name")
        age_key = ContextKey.create("age", int, "User's age")

        # Create flow that requires multiple keys
        require_flow = Flow.require_keys(name_key, age_key)

        context = Context()
        context["name"] = "Alice"
        context["age"] = 30

        # Should return the same context if all keys are present
        result = require_flow.run(context)
        assert result["name"] == "Alice"
        assert result["age"] == 30

    def test_flow_optional_context_keys(self):
        """Test Flow that handles optional context keys gracefully."""
        nickname_key = ContextKey.create("nickname", str, "User's nickname")

        # Create flow that gets optional key with default
        get_nickname_flow = Flow.optional_key(nickname_key, "Unknown")

        context = Context()
        # nickname not set - should use default

        result = get_nickname_flow.run(context)
        assert result == "Unknown"


class TestFlowContextCombinators:
    """Test Flow combinators for context manipulation."""

    def test_move_context_key(self):
        """Test moving a value from one context key to another."""
        source_key = ContextKey.create("temp_name", str, "Temporary name")
        dest_key = ContextKey.create("final_name", str, "Final name")

        move_flow = Flow.move_key(source_key, dest_key)

        context = Context()
        context["temp_name"] = "Alice"

        result_context = move_flow.run(context)
        assert "temp_name" not in result_context
        assert result_context["final_name"] == "Alice"

    def test_copy_context_key(self):
        """Test copying a value from one context key to another."""
        source_key = ContextKey.create("name", str, "Original name")
        dest_key = ContextKey.create("display_name", str, "Display name")

        copy_flow = Flow.copy_key(source_key, dest_key)

        context = Context()
        context["name"] = "Alice"

        result_context = copy_flow.run(context)
        assert result_context["name"] == "Alice"
        assert result_context["display_name"] == "Alice"

    def test_forget_context_key(self):
        """Test removing a key from context."""
        key_to_forget = ContextKey.create("temp_data", str, "Temporary data")

        forget_flow = Flow.forget_key(key_to_forget)

        context = Context()
        context["temp_data"] = "temporary"
        context["keep_data"] = "permanent"

        result_context = forget_flow.run(context)
        assert "temp_data" not in result_context
        assert result_context["keep_data"] == "permanent"

    def test_set_context_key(self):
        """Test setting a context key to a specific value."""
        key = ContextKey.create("status", str, "Status")

        set_flow = Flow.set_key(key, "active")

        context = Context()

        result_context = set_flow.run(context)
        assert result_context["status"] == "active"


class TestFlowContextComposition:
    """Test composing Flows with context dependencies."""

    def test_flow_composition_with_dependencies(self):
        """Test composing multiple Flows with clear dependency chains."""

        # Create a flow that processes input data
        def process_input(ctx: Context) -> Context:
            value = ctx["input"].upper()
            new_ctx = ctx.fork()
            new_ctx["processed"] = value
            return new_ctx

        process_flow = Flow.from_sync_fn(process_input)

        context = Context()
        context["input"] = "hello"

        result_context = process_flow.run(context)
        assert result_context["processed"] == "HELLO"

    def test_flow_with_multiple_dependencies(self):
        """Test Flow that depends on multiple context keys."""
        first_name_key = ContextKey.create("first_name", str, "First name")
        last_name_key = ContextKey.create("last_name", str, "Last name")

        # Create a flow that combines first and last name
        def combine_names(ctx: Context) -> Context:
            first = ctx["first_name"]
            last = ctx["last_name"]
            new_ctx = ctx.fork()
            new_ctx["full_name"] = f"{first} {last}"
            return new_ctx

        create_full_name_flow = Flow.require_keys(first_name_key, last_name_key).then(
            Flow.from_sync_fn(combine_names)
        )

        context = Context()
        context["first_name"] = "Alice"
        context["last_name"] = "Smith"

        result_context = create_full_name_flow.run(context)
        assert result_context["full_name"] == "Alice Smith"


class TestFlowContextErrorHandling:
    """Test error handling in Flow-Context integration."""

    def test_missing_required_key_raises_error(self):
        """Test that missing required keys raise appropriate errors."""
        required_key = ContextKey.create("required", str, "Required key")

        require_flow = Flow.require_key(required_key)

        context = Context()
        # required_key is not set

        with pytest.raises(MissingRequiredKeyError, match="required"):
            require_flow.run(context)

    def test_type_mismatch_raises_error(self):
        """Test that type mismatches in context keys raise errors."""
        typed_key = ContextKey.create("number", int, "A number")

        context = Context()
        context["number"] = "not_a_number"  # Wrong type

        get_number_flow = Flow.get_key(typed_key)

        # Flow should detect type mismatch
        with pytest.raises(ContextTypeMismatchError, match="expected int, got str"):
            get_number_flow.run(context)

    def test_optional_key_with_default(self):
        """Test optional keys with default values."""
        optional_key = ContextKey.create("optional", str, "Optional key")

        get_optional_flow = Flow.optional_key(optional_key, "default_value")

        context = Context()
        # optional_key is not set

        result = get_optional_flow.run(context)
        assert result == "default_value"


class TestFlowContextMetadata:
    """Test metadata and introspection for Flow-Context integration."""

    def test_context_flow_decorator(self):
        """Test the @context_flow decorator for declaring dependencies."""
        input_key = ContextKey.create("input", str, "Input data")
        output_key = ContextKey.create("output", str, "Output data")

        @context_flow(inputs=[input_key], outputs=[output_key], name="transform_data")
        def transform_data(ctx: Context) -> Context:
            """Transform input to output."""
            value = ctx["input"]
            new_ctx = ctx.fork()
            new_ctx["output"] = value.upper()
            return new_ctx

        context = Context()
        context["input"] = "hello"

        result_context = transform_data.run(context)
        assert result_context["output"] == "HELLO"

        # Check metadata
        assert transform_data.metadata["context_aware"] is True
        assert input_key in transform_data.metadata["input_dependencies"]
        assert output_key in transform_data.metadata["output_dependencies"]

    def test_transform_key_flow(self):
        """Test the transform_key combinator."""
        input_key = ContextKey.create("text", str, "Text to transform")
        output_key = ContextKey.create("uppercase_text", str, "Uppercase text")

        # Transform and store in new key
        transform_flow = Flow.transform_key(
            input_key, lambda text: text.upper(), output_key
        )

        context = Context()
        context["text"] = "hello world"

        result_context = transform_flow.run(context)
        assert result_context["uppercase_text"] == "HELLO WORLD"
        assert result_context["text"] == "hello world"  # Original unchanged

    def test_transform_key_return_value(self):
        """Test transform_key that returns value directly."""
        input_key = ContextKey.create("number", int, "Number to square")

        # Transform and return value
        square_flow = Flow.transform_key(input_key, lambda x: x * x)

        context = Context()
        context["number"] = 5

        result = square_flow.run(context)
        assert result == 25
