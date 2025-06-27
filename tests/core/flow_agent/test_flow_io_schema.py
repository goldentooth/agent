"""Tests for FlowIOSchema base class with context integration."""

from typing import Any

import pytest
from pydantic import Field, ValidationError

from goldentooth_agent.core.context import Context
from goldentooth_agent.core.flow_agent.schema import FlowIOSchema


class TestFlowIOSchema:
    """Test the FlowIOSchema base class."""

    def test_flow_io_schema_can_be_subclassed(self):
        """Test that FlowIOSchema can be subclassed with fields."""

        class TestSchema(FlowIOSchema):
            message: str = Field(..., description="Test message")
            count: int = Field(default=1, description="Test count")

        # Should create instance successfully
        schema = TestSchema(message="hello", count=5)
        assert schema.message == "hello"
        assert schema.count == 5

    def test_flow_io_schema_validates_fields(self):
        """Test that FlowIOSchema validates fields properly."""

        class TestSchema(FlowIOSchema):
            required_field: str = Field(..., description="Required field")
            optional_field: int = Field(default=0, description="Optional field")

        # Should validate required fields
        with pytest.raises(ValidationError):
            TestSchema(optional_field=5)  # Missing required_field

        # Should work with required field
        schema = TestSchema(required_field="test")
        assert schema.required_field == "test"
        assert schema.optional_field == 0

    def test_to_context_creates_context_entries(self):
        """Test that to_context() creates appropriate context entries."""

        class TestSchema(FlowIOSchema):
            name: str = Field(..., description="Name field")
            value: int = Field(..., description="Value field")

        schema = TestSchema(name="test", value=42)
        context = Context()

        # Convert to context
        updated_context = schema.to_context(context)

        # Should have created context keys for each field
        # We'll need to check that appropriate keys were created
        assert updated_context is not None
        assert isinstance(updated_context, Context)

        # Context should contain the schema data somehow
        # The exact implementation will depend on how we design the key creation

    def test_from_context_extracts_schema_data(self):
        """Test that from_context() extracts schema from context."""

        class TestSchema(FlowIOSchema):
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

    def test_context_roundtrip_preserves_data(self):
        """Test that to_context -> from_context preserves all data."""

        class ComplexSchema(FlowIOSchema):
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

    def test_schema_forbids_extra_fields(self):
        """Test that FlowIOSchema forbids extra fields."""

        class TestSchema(FlowIOSchema):
            name: str = Field(..., description="Name field")

        # Should reject extra fields
        with pytest.raises(ValidationError):
            TestSchema(name="test", extra_field="not allowed")

    def test_schema_validates_assignment(self):
        """Test that FlowIOSchema validates field assignments."""

        class TestSchema(FlowIOSchema):
            count: int = Field(..., description="Count field")

        schema = TestSchema(count=5)

        # Should validate on assignment
        with pytest.raises(ValidationError):
            schema.count = "not an integer"

    def test_multiple_schemas_share_context_safely(self):
        """Test that multiple schema types can share the same context."""

        class SchemaA(FlowIOSchema):
            field_a: str = Field(..., description="Field A")

        class SchemaB(FlowIOSchema):
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
