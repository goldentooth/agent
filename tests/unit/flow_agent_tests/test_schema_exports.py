"""Tests for flow_agent schema re-exports."""

from flow_agent.schema import AgentInput, AgentOutput, ContextFlowSchema


class TestSchemaReExports:
    """Test that flow_agent schema module properly re-exports from context_flow."""

    def test_context_flow_schema_import(self) -> None:
        """Test that ContextFlowSchema is properly re-exported."""
        # Verify we can import the base schema class
        assert ContextFlowSchema is not None
        assert hasattr(ContextFlowSchema, "to_context")
        assert hasattr(ContextFlowSchema, "from_context")

    def test_agent_input_import(self) -> None:
        """Test that AgentInput is properly re-exported."""
        # Verify we can import AgentInput
        assert AgentInput is not None
        assert issubclass(AgentInput, ContextFlowSchema)

        # Test basic functionality
        input_data = AgentInput(message="test message")
        assert input_data.message == "test message"
        assert input_data.context_data == {}

    def test_agent_output_import(self) -> None:
        """Test that AgentOutput is properly re-exported."""
        # Verify we can import AgentOutput
        assert AgentOutput is not None
        assert issubclass(AgentOutput, ContextFlowSchema)

        # Test basic functionality
        output_data = AgentOutput(response="test response")
        assert output_data.response == "test response"
        assert output_data.metadata == {}

    def test_schemas_maintain_context_integration(self) -> None:
        """Test that re-exported schemas maintain context integration."""
        from context import Context

        # Test that schemas work with context
        input_data = AgentInput(message="test", context_data={"key": "value"})
        context = Context()

        # Should be able to convert to context
        updated_context = input_data.to_context(context)
        assert updated_context is not None

        # Should be able to extract from context
        extracted = AgentInput.from_context(updated_context)
        assert extracted.message == "test"
        assert extracted.context_data == {"key": "value"}
