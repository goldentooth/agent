"""Tests for CLI context commands."""

import pytest
from typer.testing import CliRunner

from goldentooth_agent.cli.commands.context import app


class TestContextCommands:
    """Test context CLI commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_app_exists(self):
        """Test that context app is properly configured."""
        assert app is not None
        assert hasattr(app, "info")

    def test_help_command(self):
        """Test help command displays correctly."""
        result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "context" in result.output.lower()
