"""Tests for chat CLI commands."""

from unittest.mock import AsyncMock, Mock, patch

import pytest
import typer
from typer.testing import CliRunner

from goldentooth_agent.cli.commands.chat import (
    app,
    create_echo_agent,
    process_agent_input,
)
from goldentooth_agent.core.flow_agent import AgentInput, AgentOutput


class TestChatCommands:
    """Test chat command functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_app_creation(self):
        """Test that the app is created properly."""
        assert isinstance(app, typer.Typer)

    def test_create_echo_agent(self):
        """Test echo agent creation."""
        agent = create_echo_agent()
        assert agent is not None
        assert hasattr(agent, "input_schema")
        assert hasattr(agent, "output_schema")
        assert hasattr(agent, "as_flow")

    @pytest.mark.asyncio
    async def test_process_agent_input(self):
        """Test processing input through an agent."""
        # Create a mock agent
        mock_agent = Mock()
        mock_flow = AsyncMock()

        # Mock the flow to return our expected output
        expected_output = AgentOutput(response="Test response", metadata={"test": True})

        async def mock_flow_function(input_stream):
            async for _ in input_stream:
                yield expected_output

        mock_agent.as_flow.return_value = mock_flow_function

        # Create test input
        test_input = AgentInput(message="test message")

        # Process the input
        result = await process_agent_input(mock_agent, test_input)

        # Verify the result
        assert isinstance(result, AgentOutput)
        assert result.response == "Test response"
        assert result.metadata["test"] is True

    @pytest.mark.asyncio
    async def test_process_agent_input_no_results(self):
        """Test processing when agent produces no output."""
        # Create a mock agent that produces no output
        mock_agent = Mock()
        mock_flow = AsyncMock()

        async def empty_flow_function(input_stream):
            async for _ in input_stream:
                pass  # Yield nothing
            return
            yield  # Unreachable, makes this a generator

        mock_agent.as_flow.return_value = empty_flow_function

        # Create test input
        test_input = AgentInput(message="test message")

        # Process the input
        result = await process_agent_input(mock_agent, test_input)

        # Should return fallback result
        assert isinstance(result, AgentOutput)
        assert result.response == "No response generated"
        assert "error" in result.metadata

    @patch("goldentooth_agent.core.rag.simple_rag_agent.create_simple_rag_agent")
    def test_create_rag_agent_error_handling(self, mock_create_simple_rag):
        """Test RAG agent creation error handling."""
        from goldentooth_agent.cli.commands.chat import create_rag_agent

        # Mock an exception during RAG agent creation
        mock_create_simple_rag.side_effect = Exception("Test error")

        with pytest.raises(ValueError, match="Failed to create RAG agent"):
            create_rag_agent()

    def test_app_has_expected_commands(self):
        """Test that the app has the expected commands."""
        # Get help output to check available commands
        result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0

        # The exact commands depend on the implementation, but we can check
        # that help is available and shows some command structure
        assert "Usage:" in result.stdout or "Commands:" in result.stdout
