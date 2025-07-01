"""Tests for CLI codebase commands."""

import pytest
from typer.testing import CliRunner

from goldentooth_agent.cli.commands.codebase import app


class TestCodebaseCommands:
    """Test codebase CLI commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_app_exists(self):
        """Test that codebase app is properly configured."""
        assert app is not None
        assert app.info.name == "codebase"

    def test_help_command(self):
        """Test help command displays correctly."""
        result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "codebase" in result.output.lower()
        assert "introspection" in result.output.lower()
