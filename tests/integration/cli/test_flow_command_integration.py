"""Integration tests for flow command CLI integration.

This module tests the actual CLI integration of flow commands to ensure
that the flow_command package is properly integrated with the main CLI.
"""

from __future__ import annotations

import pytest
from typer.testing import CliRunner

from goldentooth_agent.cli.main import app


def test_flow_command_available_in_main_cli() -> None:
    """Main CLI should include flow commands from flow_command package."""
    runner = CliRunner()
    result = runner.invoke(app, ["flow", "--help"])

    assert result.exit_code == 0
    help_output = result.stdout.lower()
    assert "flow" in help_output
    assert "list" in help_output
    assert "run" in help_output
    assert "search" in help_output


def test_flow_list_command_execution() -> None:
    """Flow list command should execute without errors."""
    runner = CliRunner()
    result = runner.invoke(app, ["flow", "list", "--plain"])

    # Should not crash, even if no flows are available
    assert result.exit_code == 0
    # Should contain some output (even if "No results found")
    assert len(result.stdout.strip()) > 0


def test_flow_search_command_execution() -> None:
    """Flow search command should execute without errors."""
    runner = CliRunner()
    result = runner.invoke(app, ["flow", "search", "test", "--plain"])

    # Should not crash, even if no flows are found
    assert result.exit_code == 0
    # Should contain some output (even if "No results found")
    assert len(result.stdout.strip()) > 0


def test_flow_run_command_with_missing_flow() -> None:
    """Flow run command should handle missing flows gracefully."""
    runner = CliRunner()
    result = runner.invoke(app, ["flow", "run", "nonexistent_flow", "--plain"])

    # Should exit with error code 1 for missing flow
    assert result.exit_code == 1

    # Check error output
    combined_output = (result.stdout + result.stderr).lower()
    assert "not found" in combined_output
