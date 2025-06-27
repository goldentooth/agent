"""Tests for standard AgentInput and AgentOutput schemas."""

import pytest
from pydantic import ValidationError

from goldentooth_agent.core.context import Context
from goldentooth_agent.core.flow_agent.schema import AgentInput, AgentOutput


class TestAgentInput:
    """Test the AgentInput standard schema."""

    def test_agent_input_basic_usage(self):
        """Test basic usage of AgentInput schema."""

        # Should work with just message
        input_schema = AgentInput(message="Hello, world!")
        assert input_schema.message == "Hello, world!"
        assert input_schema.context_data == {}

    def test_agent_input_with_context_data(self):
        """Test AgentInput with context data."""

        context_data = {"user_id": 123, "session_id": "abc123"}
        input_schema = AgentInput(message="Hello", context_data=context_data)

        assert input_schema.message == "Hello"
        assert input_schema.context_data == context_data

    def test_agent_input_requires_message(self):
        """Test that AgentInput requires a message field."""

        # Should raise validation error without message
        with pytest.raises(ValidationError):  # Pydantic validation error
            AgentInput(context_data={"test": "data"})

    def test_agent_input_context_roundtrip(self):
        """Test AgentInput context conversion roundtrip."""

        original = AgentInput(
            message="Test message", context_data={"key": "value", "num": 42}
        )

        context = Context()
        context = original.to_context(context)
        extracted = AgentInput.from_context(context)

        assert extracted.message == original.message
        assert extracted.context_data == original.context_data

    def test_agent_input_validates_types(self):
        """Test that AgentInput validates field types."""

        # Should accept proper types
        AgentInput(message="test", context_data={"key": "value"})

        # Should reject wrong types
        with pytest.raises(ValidationError):  # Pydantic validation error
            AgentInput(message=123)  # message should be string

        with pytest.raises(ValidationError):  # Pydantic validation error
            AgentInput(message="test", context_data="not a dict")


class TestAgentOutput:
    """Test the AgentOutput standard schema."""

    def test_agent_output_basic_usage(self):
        """Test basic usage of AgentOutput schema."""

        # Should work with just response
        output_schema = AgentOutput(response="Hello back!")
        assert output_schema.response == "Hello back!"
        assert output_schema.metadata == {}

    def test_agent_output_with_metadata(self):
        """Test AgentOutput with metadata."""

        metadata = {"confidence": 0.95, "model": "gpt-4", "tokens": 42}
        output_schema = AgentOutput(response="Response", metadata=metadata)

        assert output_schema.response == "Response"
        assert output_schema.metadata == metadata

    def test_agent_output_requires_response(self):
        """Test that AgentOutput requires a response field."""

        # Should raise validation error without response
        with pytest.raises(ValidationError):  # Pydantic validation error
            AgentOutput(metadata={"test": "data"})

    def test_agent_output_context_roundtrip(self):
        """Test AgentOutput context conversion roundtrip."""

        original = AgentOutput(
            response="Test response", metadata={"model": "test", "confidence": 0.9}
        )

        context = Context()
        context = original.to_context(context)
        extracted = AgentOutput.from_context(context)

        assert extracted.response == original.response
        assert extracted.metadata == original.metadata

    def test_agent_output_validates_types(self):
        """Test that AgentOutput validates field types."""

        # Should accept proper types
        AgentOutput(response="test", metadata={"key": "value"})

        # Should reject wrong types
        with pytest.raises(ValidationError):  # Pydantic validation error
            AgentOutput(response=123)  # response should be string

        with pytest.raises(ValidationError):  # Pydantic validation error
            AgentOutput(response="test", metadata="not a dict")


class TestSchemaInteroperability:
    """Test interoperability between standard schemas."""

    def test_schemas_can_coexist_in_context(self):
        """Test that AgentInput and AgentOutput can coexist in same context."""

        input_schema = AgentInput(message="Hello", context_data={"user": "alice"})
        output_schema = AgentOutput(response="Hi Alice!", metadata={"greeting": True})

        context = Context()

        # Add both to context
        context = input_schema.to_context(context)
        context = output_schema.to_context(context)

        # Should be able to extract both
        extracted_input = AgentInput.from_context(context)
        extracted_output = AgentOutput.from_context(context)

        assert extracted_input.message == "Hello"
        assert extracted_input.context_data == {"user": "alice"}
        assert extracted_output.response == "Hi Alice!"
        assert extracted_output.metadata == {"greeting": True}

    def test_schemas_use_different_context_keys(self):
        """Test that different schema types use different context key namespaces."""

        input_schema = AgentInput(message="test")
        output_schema = AgentOutput(response="test")

        context = Context()
        context = input_schema.to_context(context)
        context = output_schema.to_context(context)

        # The context should contain keys for both schemas
        # This is a bit of a white-box test, but important for ensuring no key collisions

        # Count the frames and check we have the expected number of keys
        frame_data = context.frames[-1].data
        assert len(frame_data) == 4  # 2 fields from each schema

        # Check that key names are different
        key_names = [str(key) for key in frame_data.keys()]
        input_keys = [k for k in key_names if "AgentInput" in k]
        output_keys = [k for k in key_names if "AgentOutput" in k]

        assert len(input_keys) == 2  # message and context_data
        assert len(output_keys) == 2  # response and metadata
        assert set(input_keys).isdisjoint(set(output_keys))  # No overlap
