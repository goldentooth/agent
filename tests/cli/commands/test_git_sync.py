"""Tests for CLI git sync commands."""

import pytest
from typer.testing import CliRunner

from goldentooth_agent.cli.commands.git_sync import app


class TestGitSyncCommands:
    """Test git sync CLI commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_app_exists(self):
        """Test that git_sync app is properly configured."""
        assert app is not None
        assert hasattr(app, "info")

    def test_help_command(self):
        """Test help command displays correctly."""
        result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "git" in result.output.lower()
