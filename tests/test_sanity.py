"""Sanity tests to ensure basic project functionality."""

import pytest
from typer.testing import CliRunner
from goldentooth_agent.cli.main import app


def test_imports():
    """Test that available modules can be imported without errors."""
    # Test CLI imports
    import goldentooth_agent.cli.main
    import goldentooth_agent.cli.commands.chat
    import goldentooth_agent.cli.commands.tools

    # Test core module
    import goldentooth_agent.core


def test_cli_app_creation():
    """Test that the CLI app can be created."""
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.stdout


def test_chat_command_exists():
    """Test that the chat command is available."""
    runner = CliRunner()
    result = runner.invoke(app, ["chat", "--help"])
    assert result.exit_code == 0
    assert "Start an interactive chat session" in result.stdout


def test_tools_command_exists():
    """Test that the tools command is available."""
    runner = CliRunner()
    result = runner.invoke(app, ["tools", "--help"])
    assert result.exit_code == 0
    assert "Manage tools" in result.stdout


def test_tools_list_command_exists():
    """Test that the tools list command is available."""
    runner = CliRunner()
    result = runner.invoke(app, ["tools", "list", "--help"])
    assert result.exit_code == 0
    assert "List all available tools" in result.stdout
