"""Integration tests for main CLI application."""

# pyright: reportUninitializedInstanceVariable=false

import pytest
from typer.testing import CliRunner

from goldentooth_agent.cli.main import app


class TestMainCLI:
    """Integration tests for main CLI application."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_main_help(self) -> None:
        """Test main help command."""
        result = self.runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "Goldentooth Agent" in result.output
        assert "AI-powered document processing and chat" in result.output

    def test_version_option(self) -> None:
        """Test version option."""
        result = self.runner.invoke(app, ["--version"])

        assert result.exit_code == 0
        assert "Goldentooth Agent" in result.output
        assert "v0.1.0" in result.output

    def test_version_short_option(self) -> None:
        """Test short version option."""
        result = self.runner.invoke(app, ["-v"])

        assert result.exit_code == 0
        assert "Goldentooth Agent" in result.output

    def test_invalid_command(self) -> None:
        """Test invalid command handling."""
        result = self.runner.invoke(app, ["nonexistent-command"])

        assert result.exit_code != 0
        assert "No such command" in result.output or "Usage:" in result.output

    def test_main_without_args(self) -> None:
        """Test main command without arguments."""
        result = self.runner.invoke(app, [])

        assert result.exit_code == 2  # Missing command error
        assert "Usage:" in result.output
        assert "Missing command" in result.output

    def test_flow_command_available(self) -> None:
        """Test that flow command is available in main CLI."""
        result = self.runner.invoke(app, ["flow", "--help"])

        assert result.exit_code == 0
        assert "flow" in result.output.lower()
        assert "List available flows" in result.output

    def test_global_color_options_available(self) -> None:
        """Test that global color options are available in main CLI."""
        result = self.runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "--no-color" in result.output
        assert "--plain" in result.output
        assert "Disable colored output" in result.output
        assert "Use plain text output without formatting" in result.output

    def test_global_no_color_option_works(self) -> None:
        """Test that global --no-color option works with flow command."""
        result = self.runner.invoke(app, ["--no-color", "flow", "list"])

        assert result.exit_code == 0
        assert "No flows available" in result.output

    def test_global_plain_option_works(self) -> None:
        """Test that global --plain option works with flow command."""
        result = self.runner.invoke(app, ["--plain", "flow", "list"])

        assert result.exit_code == 0
        assert "No flows available" in result.output

    def test_color_options_hierarchical_precedence(self) -> None:
        """Test that color options work with proper precedence."""
        # Global level
        result = self.runner.invoke(app, ["--no-color", "flow", "list"])
        assert result.exit_code == 0
        assert "No flows available" in result.output

        # Flow level
        result = self.runner.invoke(app, ["flow", "--no-color", "list"])
        assert result.exit_code == 0
        assert "No flows available" in result.output

        # Command level (flexible positioning)
        result = self.runner.invoke(app, ["flow", "list", "--no-color"])
        assert result.exit_code == 0
        assert "No flows available" in result.output

    def test_flexible_positioning_comprehensive(self) -> None:
        """Test comprehensive flexible positioning patterns."""
        test_patterns = [
            # Different positions for --no-color
            ["--no-color", "flow", "list"],
            ["flow", "--no-color", "list"],
            ["flow", "list", "--no-color"],
            # Different positions for --plain
            ["--plain", "flow", "list"],
            ["flow", "--plain", "list"],
            ["flow", "list", "--plain"],
            # Multiple options
            ["flow", "list", "--no-color", "--plain"],
            ["flow", "list", "--plain", "--no-color"],
        ]

        for pattern in test_patterns:
            result = self.runner.invoke(app, pattern)
            assert result.exit_code == 0, f"Pattern {pattern} failed"
            assert "No flows available" in result.output
