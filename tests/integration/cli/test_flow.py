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
        result = self.runner.invoke(app, ["list"])

        assert result.exit_code == 0
        assert "No flows available" in result.output

    def test_flow_app_help(self) -> None:
        """Test main flow command help."""
        result = self.runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "List available flows" in result.output
        assert "--no-color" in result.output
        assert "--plain" in result.output

    def test_flow_list_with_no_color(self) -> None:
        """Test flow list with --no-color option."""
        result = self.runner.invoke(app, ["--no-color", "list"])

        assert result.exit_code == 0
        assert "No flows available" in result.output

    def test_flow_list_with_plain(self) -> None:
        """Test flow list with --plain option."""
        result = self.runner.invoke(app, ["--plain", "list"])

        assert result.exit_code == 0
        assert "No flows available" in result.output
