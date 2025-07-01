"""Tests for CLI debug commands."""

import json

import pytest
from typer.testing import CliRunner

from goldentooth_agent.cli.commands.debug import app
from goldentooth_agent.cli.main import app as main_app


class TestDebugCommands:
    """Test debug CLI commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_app_exists(self):
        """Test that debug app is properly configured."""
        assert app is not None
        assert hasattr(app, "info")

    def test_debug_help_from_main(self):
        """Test debug help appears correctly in main CLI help."""
        result = self.runner.invoke(main_app, ["--help"])
        assert result.exit_code == 0
        assert "debug" in result.output
        assert "Debugging and diagnostics tools" in result.output
        assert "guidelines/debugging-guide.md" in result.output

    def test_debug_help_command(self):
        """Test debug subcommand help displays correctly."""
        result = self.runner.invoke(main_app, ["debug", "--help"])
        assert result.exit_code == 0
        assert "health" in result.output
        assert "trace" in result.output
        assert "profile" in result.output
        # Verify commands are listed
        assert "Check system health" in result.output

    def test_debug_health_help(self):
        """Test health command help with cross-references."""
        result = self.runner.invoke(main_app, ["debug", "health", "--help"])
        assert result.exit_code == 0
        assert "Check system health and component status" in result.output
        assert "RELATED TOOLS" in result.output
        assert "goldentooth-agent debug trace" in result.output
        assert "guidelines/debugging-guide.md#system-health" in result.output

    def test_debug_trace_help(self):
        """Test trace command help with cross-references."""
        result = self.runner.invoke(main_app, ["debug", "trace", "--help"])
        assert result.exit_code == 0
        assert "Trace flow or agent execution" in result.output
        assert "RELATED TOOLS" in result.output
        assert "FlowDebugger" in result.output
        assert "guidelines/debugging-guide.md#execution-tracing" in result.output

    def test_debug_profile_help(self):
        """Test profile command help with cross-references."""
        result = self.runner.invoke(main_app, ["debug", "profile", "--help"])
        assert result.exit_code == 0
        assert "Profile command performance" in result.output
        assert "RELATED TOOLS" in result.output
        assert "PerformanceMonitor" in result.output
        assert "guidelines/debugging-guide.md#performance-analysis" in result.output

    def test_debug_health_execution(self):
        """Test health command actually executes."""
        result = self.runner.invoke(main_app, ["debug", "health"])
        assert result.exit_code == 0
        assert "System Health" in result.output
        assert "Overall Status" in result.output
        # Should show component statuses
        assert any(word in result.output for word in ["Tools", "Flows", "Agents"])

    def test_debug_health_json_format(self):
        """Test health command with JSON output."""
        result = self.runner.invoke(main_app, ["debug", "health", "--format", "json"])
        assert result.exit_code == 0
        # Verify valid JSON output
        data = json.loads(result.output)
        assert "overall_status" in data
        assert "components" in data
        assert "timestamp" in data

    def test_debug_health_export(self):
        """Test health command export functionality."""
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(
                main_app, ["debug", "health", "--export", "test_health.json"]
            )
            assert result.exit_code == 0
            assert "Health report exported to test_health.json" in result.output
            # Verify file was created
            import os

            assert os.path.exists("test_health.json")

    def test_debug_trace_execution(self):
        """Test trace command with valid agent."""
        result = self.runner.invoke(
            main_app,
            ["debug", "trace", "--agent", "echo", "--input", '{"message": "test"}'],
        )
        assert result.exit_code == 0
        assert "Execution Trace" in result.output
        assert "✅" in result.output  # Success indicator
        assert "input_validation" in result.output
        assert "agent_lookup" in result.output

    def test_debug_trace_verbose(self):
        """Test trace command with verbose output."""
        result = self.runner.invoke(
            main_app,
            [
                "debug",
                "trace",
                "--agent",
                "echo",
                "--input",
                '{"message": "test"}',
                "--verbose",
            ],
        )
        assert result.exit_code == 0
        assert "Execution Trace" in result.output
        # Verbose should show step details
        assert "Input JSON parsed successfully" in result.output
        assert "Found agent: echo" in result.output

    def test_debug_trace_invalid_agent(self):
        """Test trace command with invalid agent."""
        result = self.runner.invoke(
            main_app,
            [
                "debug",
                "trace",
                "--agent",
                "nonexistent",
                "--input",
                '{"message": "test"}',
            ],
        )
        # Should show error in output but might not exit with error code
        assert "not found" in result.output.lower() or "error" in result.output.lower()

    def test_debug_profile_missing_command(self):
        """Test profile command without required argument."""
        result = self.runner.invoke(main_app, ["debug", "profile"])
        assert result.exit_code != 0
        assert "Missing argument" in result.output

    def test_debug_no_args_shows_help(self):
        """Test that debug without args shows help (no_args_is_help)."""
        result = self.runner.invoke(main_app, ["debug"])
        # Should show help due to no_args_is_help=True
        assert "health" in result.output
        assert "trace" in result.output
        assert "profile" in result.output
