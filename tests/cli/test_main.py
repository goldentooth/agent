"""Tests for CLI main entry point."""

import pytest
from typer.testing import CliRunner

from goldentooth_agent.cli.main import app


class TestMainCLI:
    """Test main CLI application."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_app_exists(self):
        """Test that main app is properly configured."""
        assert app is not None

    def test_help_command(self):
        """Test help command displays correctly."""
        result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Usage:" in result.output

    def test_subcommands_registered(self):
        """Test that expected subcommands are registered."""
        result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0

        # Check for key subcommands
        expected_commands = ["chat", "tools", "flow", "context", "agents", "debug"]
        for cmd in expected_commands:
            assert cmd in result.output
