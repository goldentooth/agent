"""Tests for agents CLI commands."""

from unittest.mock import Mock, patch

import pytest
import typer
from typer.testing import CliRunner

from goldentooth_agent.cli.commands.agents import (
    app,
    get_agent_description,
    get_agent_metadata,
    get_available_agents,
)


class TestAgentsCommands:
    """Test agents command functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_app_creation(self):
        """Test that the app is created properly."""
        assert isinstance(app, typer.Typer)

    def test_get_agent_description(self):
        """Test agent description function."""
        assert (
            get_agent_description("echo")
            == "Simple echo agent that returns user input with metadata"
        )
        assert (
            get_agent_description("claude")
            == "AI agent powered by Anthropic's Claude models"
        )
        assert get_agent_description("unknown") == "Custom agent implementation"

    def test_get_available_agents(self):
        """Test getting available agents."""
        agents = get_available_agents()

        # Echo agent should always be available
        assert "echo" in agents
        assert agents["echo"] is not None

        # Other agents depend on configuration but shouldn't break the function
        assert isinstance(agents, dict)

    @patch("goldentooth_agent.cli.commands.agents.get_available_agents")
    def test_list_command_no_agents(self, mock_get_agents):
        """Test list command when no agents are available."""
        mock_get_agents.return_value = {}

        result = self.runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert "No agents available" in result.stdout

    @patch("goldentooth_agent.cli.commands.agents.get_available_agents")
    def test_list_command_with_agents(self, mock_get_agents):
        """Test list command with available agents."""
        mock_agent = Mock()
        mock_agent.input_schema.__name__ = "TestInput"
        mock_agent.output_schema.__name__ = "TestOutput"
        mock_agent.system_flow.name = "system_flow"
        mock_agent.processing_flow.name = "processing_flow"

        mock_get_agents.return_value = {"test_agent": mock_agent}

        result = self.runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert "Available Agents" in result.stdout
        assert "test_agent" in result.stdout

    @patch("goldentooth_agent.cli.commands.agents.get_available_agents")
    def test_describe_command_unknown_agent(self, mock_get_agents):
        """Test describe command with unknown agent."""
        mock_get_agents.return_value = {"echo": Mock()}

        result = self.runner.invoke(app, ["describe", "unknown_agent"])
        assert result.exit_code == 1
        assert "Agent 'unknown_agent' not found" in result.stdout

    @patch("goldentooth_agent.cli.commands.agents.get_available_agents")
    def test_describe_command_known_agent(self, mock_get_agents):
        """Test describe command with known agent."""
        mock_agent = Mock()
        mock_agent.input_schema.__name__ = "TestInput"
        mock_agent.output_schema.__name__ = "TestOutput"
        mock_agent.system_flow.name = "system_flow"
        mock_agent.processing_flow.name = "processing_flow"

        mock_get_agents.return_value = {"echo": mock_agent}

        result = self.runner.invoke(app, ["describe", "echo"])
        assert result.exit_code == 0
        assert "Agent: echo" in result.stdout
        assert "TestInput" in result.stdout
        assert "TestOutput" in result.stdout

    def test_get_agent_metadata(self):
        """Test agent metadata extraction."""
        mock_agent = Mock()
        mock_agent.input_schema.__name__ = "TestInput"
        mock_agent.output_schema.__name__ = "TestOutput"
        mock_agent.system_flow.name = "system_flow"
        mock_agent.processing_flow.name = "processing_flow"
        mock_agent.model = "test_model"

        metadata = get_agent_metadata("test_agent", mock_agent)

        assert metadata["name"] == "test_agent"
        assert metadata["type"] == "FlowAgent"
        assert metadata["input_schema"] == "TestInput"
        assert metadata["output_schema"] == "TestOutput"
        assert metadata["model"] == "test_model"

    @patch("goldentooth_agent.cli.commands.agents.get_available_agents")
    def test_run_command_unknown_agent(self, mock_get_agents):
        """Test run command with unknown agent."""
        mock_get_agents.return_value = {}

        result = self.runner.invoke(
            app, ["run", "unknown_agent", "--input", '{"message": "test"}']
        )
        assert result.exit_code == 1
        assert "Agent 'unknown_agent' not found" in result.stderr

    @patch("goldentooth_agent.cli.commands.agents.get_available_agents")
    def test_run_command_invalid_json(self, mock_get_agents):
        """Test run command with invalid JSON input."""
        mock_get_agents.return_value = {"echo": Mock()}

        result = self.runner.invoke(app, ["run", "echo", "--input", "invalid json"])
        assert result.exit_code == 1
        assert "Invalid JSON input" in result.stderr

    @patch("goldentooth_agent.cli.commands.agents.get_available_agents")
    def test_test_command_unknown_agent(self, mock_get_agents):
        """Test test command with unknown agent."""
        mock_get_agents.return_value = {}

        result = self.runner.invoke(app, ["test", "unknown_agent"])
        assert result.exit_code == 1
        assert "Agent 'unknown_agent' not found" in result.stdout
