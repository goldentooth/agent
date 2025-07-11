"""Test fixtures for CLI testing."""

from unittest.mock import Mock

import pytest
from rich.console import Console
from typer.testing import CliRunner

from ..core import CommandContext


@pytest.fixture
def cli_runner() -> CliRunner:
    """Create a CLI runner for testing."""
    return CliRunner()


@pytest.fixture
def mock_console() -> Mock:
    """Create a mock console for testing."""
    return Mock(spec=Console)


@pytest.fixture
def cli_context(mock_console: Mock) -> CommandContext:
    """Create a test command context."""
    return CommandContext(
        output_format="text",
        plain_output=True,
        interactive=False,
        console=mock_console,
    )


@pytest.fixture
def cli_context_json(mock_console: Mock) -> CommandContext:
    """Create a test command context with JSON output."""
    return CommandContext(
        output_format="json",
        plain_output=True,
        interactive=False,
        console=mock_console,
    )


@pytest.fixture
def cli_context_interactive(mock_console: Mock) -> CommandContext:
    """Create a test command context for interactive mode."""
    return CommandContext(
        output_format="text",
        plain_output=False,
        interactive=True,
        console=mock_console,
    )
