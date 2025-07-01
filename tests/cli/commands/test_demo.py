"""Tests for CLI demo commands."""

import pytest
from typer.testing import CliRunner

from goldentooth_agent.cli.commands.demo import app


class TestDemoCommands:
    """Test demo CLI commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_app_exists(self):
        """Test that demo app is properly configured."""
        assert app is not None
        assert hasattr(app, "info")

    def test_help_command(self):
        """Test help command displays correctly."""
        result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "demo" in result.output.lower()
