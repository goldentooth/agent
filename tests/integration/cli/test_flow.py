"""Integration tests for flow CLI commands."""

# pyright: reportUninitializedInstanceVariable=false

from typer.testing import CliRunner

from goldentooth_agent.cli.main import app


class TestFlowCLI:
    """Integration tests for flow CLI commands."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_flow_list_help(self) -> None:
        """Test flow list help command."""
        result = self.runner.invoke(app, ["flow", "list", "--help"])

        assert result.exit_code == 0
        assert "List available flows" in result.output
        assert "Shows all registered flows" in result.output

    def test_flow_list_empty_registry(self) -> None:
        """Test flow list with empty registry."""
        result = self.runner.invoke(app, ["flow", "list"])

        assert result.exit_code == 0
        assert "No flows available" in result.output

    def test_flow_app_help(self) -> None:
        """Test main flow command help."""
        result = self.runner.invoke(app, ["flow", "--help"])

        assert result.exit_code == 0
        assert "Manage and interact with flows" in result.output
        assert "list" in result.output
