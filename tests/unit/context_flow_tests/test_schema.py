"""Tests for ContextFlowSchema base class and standard schemas with context integration."""

from typing import Any

import pytest
from pydantic import Field, ValidationError

from context import Context
from context_flow.schema import AgentInput, AgentOutput, ContextFlowSchema


class TestContextFlowSchema:
    """Test the ContextFlowSchema base class."""

    def test_context_flow_schema_can_be_subclassed(self) -> None:
        """Test that ContextFlowSchema can be subclassed with fields."""

        class TestSchema(ContextFlowSchema):
            message: str = Field(..., description="Test message")
            count: int = Field(default=1, description="Test count")

        # Should create instance successfully
        schema = TestSchema(message="hello", count=5)
        assert schema.message == "hello"
        assert schema.count == 5

    def test_context_flow_schema_validates_fields(self) -> None:
        """Test that ContextFlowSchema validates fields properly."""

        class TestSchema(ContextFlowSchema):
            required_field: str = Field(..., description="Required field")
            optional_field: int = Field(default=0, description="Optional field")

        # Should validate required fields
        with pytest.raises(ValidationError):
            TestSchema(optional_field=5)  # type: ignore[call-arg]  # Missing required_field

        # Should work with required field
        schema = TestSchema(required_field="test")
        assert schema.required_field == "test"
        assert schema.optional_field == 0

    def test_to_context_creates_context_entries(self) -> None:
        """Test that to_context() creates appropriate context entries."""

        class TestSchema(ContextFlowSchema):
            name: str = Field(..., description="Name field")
            value: int = Field(..., description="Value field")

        schema = TestSchema(name="test", value=42)
        context = Context()

        # Convert to context
        updated_context = schema.to_context(context)

        # Should have created context keys for each field
        assert updated_context is not None
        assert isinstance(updated_context, Context)

        # Verify context contains the schema data with proper key namespacing
        assert "schema.TestSchema.name" in [
            str(key) for key in updated_context.frames[-1].data.keys()
        ]
        assert "schema.TestSchema.value" in [
            str(key) for key in updated_context.frames[-1].data.keys()
        ]

    def test_from_context_extracts_schema_data(self) -> None:
        """Test that from_context() extracts schema from context."""

        class TestSchema(ContextFlowSchema):
            name: str = Field(..., description="Name field")
            value: int = Field(..., description="Value field")

        # Create context with relevant data
        context = Context()

        # First, put a schema into context via to_context
        original_schema = TestSchema(name="test", value=42)
        context = original_schema.to_context(context)

        # Then extract it back
        extracted_schema = TestSchema.from_context(context)

        assert extracted_schema.name == "test"
        assert extracted_schema.value == 42

    def test_context_roundtrip_preserves_data(self) -> None:
        """Test that to_context -> from_context preserves all data."""

        class ComplexSchema(ContextFlowSchema):
            message: str = Field(..., description="Message")
            metadata: dict[str, Any] = Field(
                default_factory=dict, description="Metadata"
            )
            tags: list[str] = Field(default_factory=list, description="Tags")

        original = ComplexSchema(
            message="hello world",
            metadata={"type": "test", "priority": 1},
            tags=["important", "test"],
        )

        context = Context()
        context = original.to_context(context)
        extracted = ComplexSchema.from_context(context)

        assert extracted.message == original.message
        assert extracted.metadata == original.metadata
        assert extracted.tags == original.tags

    def test_schema_forbids_extra_fields(self) -> None:
        """Test that ContextFlowSchema forbids extra fields."""

        class TestSchema(ContextFlowSchema):
            name: str = Field(..., description="Name field")

        # Should reject extra fields
        with pytest.raises(ValidationError):
            TestSchema(name="test", extra_field="not allowed")  # type: ignore[call-arg]

    def test_schema_validates_assignment(self) -> None:
        """Test that ContextFlowSchema validates field assignments."""

        class TestSchema(ContextFlowSchema):
            count: int = Field(..., description="Count field")

        schema = TestSchema(count=5)

        # Should validate on assignment
        with pytest.raises(ValidationError):
            schema.count = "not an integer"  # type: ignore[assignment]

    def test_multiple_schemas_share_context_safely(self) -> None:
        """Test that multiple schema types can share the same context."""

        class SchemaA(ContextFlowSchema):
            field_a: str = Field(..., description="Field A")

        class SchemaB(ContextFlowSchema):
            field_b: int = Field(..., description="Field B")

        context = Context()

        # Add both schemas to same context
        schema_a = SchemaA(field_a="hello")
        schema_b = SchemaB(field_b=42)

        context = schema_a.to_context(context)
        context = schema_b.to_context(context)

        # Should be able to extract both
        extracted_a = SchemaA.from_context(context)
        extracted_b = SchemaB.from_context(context)

        assert extracted_a.field_a == "hello"
        assert extracted_b.field_b == 42

    def test_from_context_handles_missing_required_fields(self) -> None:
        """Test that from_context raises ValueError for missing required fields."""

        class TestSchema(ContextFlowSchema):
            required_field: str = Field(..., description="Required field")
            optional_field: int = Field(default=42, description="Optional field")

        context = Context()

        # Try to extract schema when required field is missing
        with pytest.raises(
            ValueError, match="Required field 'required_field' not found in context"
        ):
            TestSchema.from_context(context)

    def test_from_context_uses_defaults_for_optional_fields(self) -> None:
        """Test that from_context uses default values for missing optional fields."""

        class TestSchema(ContextFlowSchema):
            required_field: str = Field(..., description="Required field")
            optional_field: int = Field(default=42, description="Optional field")
            factory_field: list[str] = Field(
                default_factory=list, description="Factory field"
            )

        # Create context with only required field
        context = Context()
        partial_schema = TestSchema(
            required_field="test", optional_field=100, factory_field=["item"]
        )
        context = partial_schema.to_context(context)

        # Remove optional fields from context to test defaults
        # We'll create a new context with only the required field
        minimal_context = Context()
        minimal_context.set("schema.TestSchema.required_field", "test")

        extracted = TestSchema.from_context(minimal_context)
        assert extracted.required_field == "test"
        assert extracted.optional_field == 42  # Default value
        assert extracted.factory_field == []  # Factory default

    def test_context_key_namespacing_prevents_conflicts(self) -> None:
        """Test that context key namespacing prevents conflicts between schemas."""

        class UserSchema(ContextFlowSchema):
            name: str = Field(..., description="User name")

        class ProductSchema(ContextFlowSchema):
            name: str = Field(..., description="Product name")

        context = Context()
        user = UserSchema(name="Alice")
        product = ProductSchema(name="Widget")

        context = user.to_context(context)
        context = product.to_context(context)

        # Both schemas should coexist with their own namespaces
        extracted_user = UserSchema.from_context(context)
        extracted_product = ProductSchema.from_context(context)

        assert extracted_user.name == "Alice"
        assert extracted_product.name == "Widget"


class TestAgentInput:
    """Test the AgentInput standard schema."""

    def test_agent_input_basic_usage(self) -> None:
        """Test basic usage of AgentInput schema."""
        input_schema = AgentInput(message="Hello, world!")
        assert input_schema.message == "Hello, world!"
        assert input_schema.context_data == {}

    def test_agent_input_with_context_data(self) -> None:
        """Test AgentInput with context data."""
        context_data = {"user_id": 123, "session_id": "abc123"}
        input_schema = AgentInput(message="Hello", context_data=context_data)
        assert input_schema.message == "Hello"
        assert input_schema.context_data == context_data

    def test_agent_input_requires_message(self) -> None:
        """Test that AgentInput requires a message field."""
        with pytest.raises(ValidationError):
            AgentInput(context_data={"test": "data"})  # type: ignore[call-arg]

    def test_agent_input_context_roundtrip(self) -> None:
        """Test AgentInput context conversion roundtrip."""
        original = AgentInput(
            message="Test message", context_data={"key": "value", "num": 42}
        )
        context = Context()
        context = original.to_context(context)
        extracted = AgentInput.from_context(context)
        assert extracted.message == original.message
        assert extracted.context_data == original.context_data

    def test_agent_input_validates_types(self) -> None:
        """Test that AgentInput validates field types."""
        AgentInput(message="test", context_data={"key": "value"})
        with pytest.raises(ValidationError):
            AgentInput(message=123)  # type: ignore[arg-type]
        with pytest.raises(ValidationError):
            AgentInput(message="test", context_data="not a dict")  # type: ignore[arg-type]


class TestAgentOutput:
    """Test the AgentOutput standard schema."""

    def test_agent_output_basic_usage(self) -> None:
        """Test basic usage of AgentOutput schema."""
        output_schema = AgentOutput(response="Hello back!")
        assert output_schema.response == "Hello back!"
        assert output_schema.metadata == {}

    def test_agent_output_with_metadata(self) -> None:
        """Test AgentOutput with metadata."""
        metadata = {"confidence": 0.95, "model": "gpt-4", "tokens": 42}
        output_schema = AgentOutput(response="Response", metadata=metadata)
        assert output_schema.response == "Response"
        assert output_schema.metadata == metadata

    def test_agent_output_requires_response(self) -> None:
        """Test that AgentOutput requires a response field."""
        with pytest.raises(ValidationError):
            AgentOutput(metadata={"test": "data"})  # type: ignore[call-arg]

    def test_agent_output_context_roundtrip(self) -> None:
        """Test AgentOutput context conversion roundtrip."""
        original = AgentOutput(
            response="Test response", metadata={"model": "test", "confidence": 0.9}
        )
        context = Context()
        context = original.to_context(context)
        extracted = AgentOutput.from_context(context)
        assert extracted.response == original.response
        assert extracted.metadata == original.metadata

    def test_agent_output_validates_types(self) -> None:
        """Test that AgentOutput validates field types."""
        AgentOutput(response="test", metadata={"key": "value"})
        with pytest.raises(ValidationError):
            AgentOutput(response=123)  # type: ignore[arg-type]
        with pytest.raises(ValidationError):
            AgentOutput(response="test", metadata="not a dict")  # type: ignore[arg-type]


class TestSchemaInteroperability:
    """Test interoperability between standard schemas."""

    def test_schemas_can_coexist_in_context(self) -> None:
        """Test that AgentInput and AgentOutput can coexist in same context."""
        input_schema = AgentInput(message="Hello", context_data={"user": "alice"})
        output_schema = AgentOutput(response="Hi Alice!", metadata={"greeting": True})
        context = Context()
        context = input_schema.to_context(context)
        context = output_schema.to_context(context)
        extracted_input = AgentInput.from_context(context)
        extracted_output = AgentOutput.from_context(context)
        assert extracted_input.message == "Hello"
        assert extracted_input.context_data == {"user": "alice"}
        assert extracted_output.response == "Hi Alice!"
        assert extracted_output.metadata == {"greeting": True}

    def test_schemas_use_different_context_keys(self) -> None:
        """Test that different schema types use different context key namespaces."""
        input_schema = AgentInput(message="test")
        output_schema = AgentOutput(response="test")
        context = Context()
        context = input_schema.to_context(context)
        context = output_schema.to_context(context)
        frame_data = context.frames[-1].data
        assert len(frame_data) == 4  # 2 fields from each schema
        key_names = [str(key) for key in frame_data.keys()]
        input_keys = [k for k in key_names if "AgentInput" in k]
        output_keys = [k for k in key_names if "AgentOutput" in k]
        assert len(input_keys) == 2  # message and context_data
        assert len(output_keys) == 2  # response and metadata
        assert set(input_keys).isdisjoint(set(output_keys))  # No overlap
