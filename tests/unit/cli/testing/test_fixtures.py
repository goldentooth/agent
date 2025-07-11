"""Tests for CLI testing fixtures."""

from unittest.mock import Mock

import pytest
from typer.testing import CliRunner

from goldentooth_agent.cli.core.context import CommandContext
from goldentooth_agent.cli.testing.fixtures import (
    cli_context,
    cli_context_interactive,
    cli_context_json,
    cli_runner,
    mock_console,
)


class TestFixtures:
    """Test fixture functionality."""

    def test_cli_runner_fixture(self, cli_runner: CliRunner) -> None:
        """Test cli_runner fixture."""
        assert isinstance(cli_runner, CliRunner)

    def test_mock_console_fixture(self, mock_console: Mock) -> None:
        """Test mock_console fixture."""
        assert isinstance(mock_console, Mock)

    def test_cli_context_fixture(self, cli_context: CommandContext) -> None:
        """Test cli_context fixture."""
        assert isinstance(cli_context, CommandContext)
        assert cli_context.output_format == "text"
        assert cli_context.plain_output is True
        assert cli_context.interactive is False
        assert cli_context.console is not None

    def test_cli_context_json_fixture(self, cli_context_json: CommandContext) -> None:
        """Test cli_context_json fixture."""
        assert isinstance(cli_context_json, CommandContext)
        assert cli_context_json.output_format == "json"
        assert cli_context_json.plain_output is True
        assert cli_context_json.interactive is False
        assert cli_context_json.console is not None

    def test_cli_context_interactive_fixture(
        self, cli_context_interactive: CommandContext
    ) -> None:
        """Test cli_context_interactive fixture."""
        assert isinstance(cli_context_interactive, CommandContext)
        assert cli_context_interactive.output_format == "text"
        assert cli_context_interactive.plain_output is False
        assert cli_context_interactive.interactive is True
        assert cli_context_interactive.console is not None
