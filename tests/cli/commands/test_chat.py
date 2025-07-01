"""Tests for chat CLI commands."""

from unittest.mock import AsyncMock, Mock, patch

import pytest
import typer
from typer.testing import CliRunner

from goldentooth_agent.cli.commands.chat import (
    SlashCommandHandler,
    app,
    create_echo_agent,
    get_command_handler,
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


class TestSlashCommandHandler:
    """Test the new slash command handler system."""

    def setup_method(self):
        """Set up test fixtures."""
        from io import StringIO

        from rich.console import Console

        # Create console that captures output
        self.output = StringIO()
        self.console = Console(file=self.output, width=80)
        self.handler = SlashCommandHandler(self.console)

    def get_output(self) -> str:
        """Get captured console output."""
        return self.output.getvalue()

    def test_handler_initialization(self):
        """Test that handler initializes with core commands."""
        # Check that core commands are registered
        assert "quit" in self.handler.commands
        assert "exit" in self.handler.commands
        assert "help" in self.handler.commands
        assert "clear" in self.handler.commands
        assert "status" in self.handler.commands

        # Check command info structure
        quit_cmd = self.handler.commands["quit"]
        assert "handler" in quit_cmd
        assert "description" in quit_cmd
        assert "category" in quit_cmd
        assert quit_cmd["category"] == "exit"

    def test_slash_command_detection(self):
        """Test detection of slash commands vs regular input."""
        # Slash commands should be detected
        assert self.handler.handle_command("/help") is not None
        assert self.handler.handle_command("/quit") is not None

        # Regular input should return None
        assert self.handler.handle_command("hello world") is None
        assert self.handler.handle_command("quit") is None  # Legacy handled elsewhere

    def test_exit_commands(self):
        """Test exit command variations."""
        for cmd in ["/quit", "/exit", "/bye"]:
            result = self.handler.handle_command(cmd)
            assert result == "exit", f"Command {cmd} should return 'exit'"

    def test_help_command(self):
        """Test help command."""
        result = self.handler.handle_command("/help")
        assert result == "continue"

        # Check that help output was generated
        output = self.get_output()
        assert "Available Slash Commands" in output
        assert "/quit" in output
        assert "/help" in output

    def test_clear_command(self):
        """Test clear command."""
        with patch("subprocess.run") as mock_subprocess:
            result = self.handler.handle_command("/clear")
            assert result == "continue"
            mock_subprocess.assert_called_once()

    def test_status_command(self):
        """Test status command."""
        result = self.handler.handle_command("/status")
        assert result == "continue"

        # Check that status output was generated
        output = self.get_output()
        assert "System Status" in output
        assert "Python Version" in output
        assert "Platform" in output

    def test_unknown_command(self):
        """Test handling of unknown commands."""
        result = self.handler.handle_command("/unknowncommand")
        assert result == "continue"

        output = self.get_output()
        assert "Unknown command: /unknowncommand" in output
        assert "Type /help" in output

    def test_empty_slash_command(self):
        """Test handling of empty slash command."""
        result = self.handler.handle_command("/")
        assert result == "continue"

        output = self.get_output()
        assert "Empty command" in output

    def test_command_with_arguments(self):
        """Test commands that accept arguments."""
        # Status command should ignore arguments gracefully
        result = self.handler.handle_command("/status some args")
        assert result == "continue"

    def test_command_registration(self):
        """Test custom command registration."""

        def test_handler(args: str) -> str:
            return "test_result"

        # Register a test command
        self.handler.register_command(
            names=["test"],
            handler=test_handler,
            description="Test command",
            category="testing",
        )

        # Verify command was registered
        assert "test" in self.handler.commands

        # Test command execution
        result = self.handler.handle_command("/test")
        assert result == "test_result"

    def test_command_aliases(self):
        """Test command aliases."""
        # Clear command should work with both 'clear' and 'cls'
        with patch("os.system"):
            result1 = self.handler.handle_command("/clear")
            result2 = self.handler.handle_command("/cls")
            assert result1 == result2 == "continue"

    def test_case_insensitive_commands(self):
        """Test that commands are case insensitive."""
        with patch("os.system"):
            assert self.handler.handle_command("/CLEAR") == "continue"
            assert self.handler.handle_command("/Clear") == "continue"
            assert self.handler.handle_command("/help") == "continue"
            assert self.handler.handle_command("/HELP") == "continue"

    def test_get_command_handler_singleton(self):
        """Test that get_command_handler returns singleton."""
        handler1 = get_command_handler(self.console)
        handler2 = get_command_handler(self.console)
        assert handler1 is handler2  # Should be the same instance
