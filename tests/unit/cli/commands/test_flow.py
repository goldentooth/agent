"""Tests for flow CLI commands."""

import pytest

from goldentooth_agent.cli.commands.flow import flow_list_implementation
from goldentooth_agent.cli.core.context import CommandResult


class TestFlowListImplementation:
    """Test flow list command implementation."""

    def test_flow_list_empty_registry(self) -> None:
        """Test flow list with empty registry."""
        result = flow_list_implementation()

        assert isinstance(result, CommandResult)
        assert result.success is True
        assert result.data == {"flows": []}
        assert result.formatted_output is not None
        assert "[dim]No flows available[/dim]" in result.formatted_output
        assert result.error_message is None
        assert result.exit_code == 0

    def test_flow_list_returns_command_result(self) -> None:
        """Test that flow list returns a CommandResult."""
        result = flow_list_implementation()

        assert isinstance(result, CommandResult)
        assert hasattr(result, "success")
        assert hasattr(result, "data")
        assert hasattr(result, "formatted_output")
        assert hasattr(result, "error_message")
        assert hasattr(result, "exit_code")
