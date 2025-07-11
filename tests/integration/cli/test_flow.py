"""Integration tests for flow CLI commands."""

# pyright: reportUninitializedInstanceVariable=false

from typer.testing import CliRunner

from goldentooth_agent.cli.commands.flow import app


class TestFlowCLI:
    """Integration tests for flow CLI commands."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_flow_list_help(self) -> None:
        """Test flow list help command."""
        result = self.runner.invoke(app, ["list", "--help"])

        assert result.exit_code == 0
        assert "List available flows" in result.output
        assert "Shows all registered flows" in result.output

    def test_flow_list_empty_registry(self) -> None:
        """Test flow list with empty registry."""
        # Note: The flow app currently executes list command by default
        result = self.runner.invoke(app, [])

        assert result.exit_code == 0
        assert "No flows available" in result.output

    def test_flow_app_help(self) -> None:
        """Test main flow command help."""
        result = self.runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "List available flows" in result.output
