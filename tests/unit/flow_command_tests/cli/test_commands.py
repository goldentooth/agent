from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import typer

from flow_command.cli.commands import flow_list_cli, flow_run_cli, flow_search_cli
from flow_command.core.result import FlowCommandResult


class TestFlowListCli:
    """Test suite for flow_list_cli command."""

    def test_flow_list_cli_basic(self) -> None:
        """flow_list_cli should call implementation and display results."""
        mock_result = FlowCommandResult.success_result(["flow1", "flow2"])

        with (
            patch("flow_command.cli.commands.flow_list_implementation") as mock_impl,
            patch("flow_command.cli.commands.FlowDisplay") as mock_display_class,
        ):

            mock_impl.return_value = mock_result
            mock_display = Mock()
            mock_display_class.return_value = mock_display

            flow_list_cli()

        # Verify implementation was called
        mock_impl.assert_called_once()
        call_args = mock_impl.call_args
        # Should be called with positional args: category, tag, context
        assert len(call_args[0]) == 3  # category, tag, context
        assert call_args[0][0] is None  # category
        assert call_args[0][1] is None  # tag
        assert call_args[0][2] is not None  # context
        assert call_args[0][2].source == "cli"
        assert call_args[0][2].output_format == "text"

        # Verify display was used
        mock_display.show_result.assert_called_once_with(mock_result)

    def test_flow_list_cli_with_category(self) -> None:
        """flow_list_cli should pass category parameter."""
        mock_result = FlowCommandResult.success_result(["nlp_flow"])

        with (
            patch("flow_command.cli.commands.flow_list_implementation") as mock_impl,
            patch("flow_command.cli.commands.FlowDisplay") as mock_display_class,
        ):

            mock_impl.return_value = mock_result
            mock_display_class.return_value = Mock()

            flow_list_cli(category="nlp")

        # Verify category was passed
        call_args = mock_impl.call_args
        assert call_args[0][0] == "nlp"  # category

    def test_flow_list_cli_with_tag(self) -> None:
        """flow_list_cli should pass tag parameter."""
        mock_result = FlowCommandResult.success_result(["tagged_flow"])

        with (
            patch("flow_command.cli.commands.flow_list_implementation") as mock_impl,
            patch("flow_command.cli.commands.FlowDisplay") as mock_display_class,
        ):

            mock_impl.return_value = mock_result
            mock_display_class.return_value = Mock()

            flow_list_cli(tag="test")

        # Verify tag was passed
        call_args = mock_impl.call_args
        assert call_args[0][1] == "test"  # tag

    def test_flow_list_cli_with_output_format(self) -> None:
        """flow_list_cli should handle different output formats."""
        mock_result = FlowCommandResult.success_result(["flow1"])

        with (
            patch("flow_command.cli.commands.flow_list_implementation") as mock_impl,
            patch("flow_command.cli.commands.FlowDisplay") as mock_display_class,
        ):

            mock_impl.return_value = mock_result
            mock_display_class.return_value = Mock()

            flow_list_cli(output_format="json")

        # Verify context has correct output format
        call_args = mock_impl.call_args
        assert call_args[0][2].output_format == "json"

    def test_flow_list_cli_with_plain_output(self) -> None:
        """flow_list_cli should handle plain output option."""
        mock_result = FlowCommandResult.success_result(["flow1"])

        with (
            patch("flow_command.cli.commands.flow_list_implementation") as mock_impl,
            patch("flow_command.cli.commands.FlowDisplay") as mock_display_class,
        ):

            mock_impl.return_value = mock_result
            mock_display_class.return_value = Mock()

            flow_list_cli(plain=True)

        # Verify context has plain output enabled
        call_args = mock_impl.call_args
        assert call_args[0][2].plain_output is True

    def test_flow_list_cli_with_all_parameters(self) -> None:
        """flow_list_cli should handle all parameters."""
        mock_result = FlowCommandResult.success_result(["flow1"])

        with (
            patch("flow_command.cli.commands.flow_list_implementation") as mock_impl,
            patch("flow_command.cli.commands.FlowDisplay") as mock_display_class,
        ):

            mock_impl.return_value = mock_result
            mock_display_class.return_value = Mock()

            flow_list_cli(
                category="test", tag="tag1", output_format="table", plain=True
            )

        # Verify all parameters were passed correctly
        call_args = mock_impl.call_args
        assert call_args[0][0] == "test"  # category
        assert call_args[0][1] == "tag1"  # tag
        assert call_args[0][2].output_format == "table"
        assert call_args[0][2].plain_output is True

    def test_flow_list_cli_with_failure_exit(self) -> None:
        """flow_list_cli should exit with code 1 on failure."""
        mock_result: FlowCommandResult[None] = FlowCommandResult.error_result(
            "List failed"
        )

        with (
            patch("flow_command.cli.commands.flow_list_implementation") as mock_impl,
            patch("flow_command.cli.commands.FlowDisplay") as mock_display_class,
        ):

            mock_impl.return_value = mock_result
            mock_display_class.return_value = Mock()

            with pytest.raises(typer.Exit) as exc_info:
                flow_list_cli()

            assert exc_info.value.exit_code == 1


class TestFlowSearchCli:
    """Test suite for flow_search_cli command."""

    def test_flow_search_cli_basic(self) -> None:
        """flow_search_cli should call implementation and display results."""
        mock_result = FlowCommandResult.success_result(["matching_flow"])

        with (
            patch("flow_command.cli.commands.flow_search_implementation") as mock_impl,
            patch("flow_command.cli.commands.FlowDisplay") as mock_display_class,
        ):

            mock_impl.return_value = mock_result
            mock_display = Mock()
            mock_display_class.return_value = mock_display

            flow_search_cli("test_query")

        # Verify implementation was called with query
        mock_impl.assert_called_once()
        call_args = mock_impl.call_args
        assert call_args[0][0] == "test_query"  # query
        assert call_args[0][1] is not None  # context
        assert call_args[0][1].source == "cli"

        # Verify display was used
        mock_display.show_result.assert_called_once_with(mock_result)

    def test_flow_search_cli_with_output_format(self) -> None:
        """flow_search_cli should handle different output formats."""
        mock_result = FlowCommandResult.success_result(["flow1"])

        with (
            patch("flow_command.cli.commands.flow_search_implementation") as mock_impl,
            patch("flow_command.cli.commands.FlowDisplay") as mock_display_class,
        ):

            mock_impl.return_value = mock_result
            mock_display_class.return_value = Mock()

            flow_search_cli("query", output_format="table")

        # Verify context has correct output format
        call_args = mock_impl.call_args
        assert call_args[0][1].output_format == "table"

    def test_flow_search_cli_with_plain_output(self) -> None:
        """flow_search_cli should handle plain output option."""
        mock_result = FlowCommandResult.success_result(["flow1"])

        with (
            patch("flow_command.cli.commands.flow_search_implementation") as mock_impl,
            patch("flow_command.cli.commands.FlowDisplay") as mock_display_class,
        ):

            mock_impl.return_value = mock_result
            mock_display_class.return_value = Mock()

            flow_search_cli("query", plain=True)

        # Verify context has plain output enabled
        call_args = mock_impl.call_args
        assert call_args[0][1].plain_output is True

    def test_flow_search_cli_with_failure_exit(self) -> None:
        """flow_search_cli should exit with code 1 on failure."""
        mock_result: FlowCommandResult[None] = FlowCommandResult.error_result(
            "Search failed"
        )

        with (
            patch("flow_command.cli.commands.flow_search_implementation") as mock_impl,
            patch("flow_command.cli.commands.FlowDisplay") as mock_display_class,
        ):

            mock_impl.return_value = mock_result
            mock_display_class.return_value = Mock()

            with pytest.raises(typer.Exit) as exc_info:
                flow_search_cli("query")

            assert exc_info.value.exit_code == 1


class TestFlowRunCli:
    """Test suite for flow_run_cli command."""

    def test_flow_run_cli_basic(self) -> None:
        """flow_run_cli should call implementation and display execution results."""
        mock_result = FlowCommandResult.success_result(["output1", "output2"])

        with (
            patch("flow_command.cli.commands.flow_run_implementation") as mock_impl,
            patch("flow_command.cli.commands.FlowDisplay") as mock_display_class,
        ):

            mock_impl.return_value = mock_result
            mock_display = Mock()
            mock_display_class.return_value = mock_display

            flow_run_cli("test_flow")

        # Verify implementation was called with flow name
        mock_impl.assert_called_once()
        call_args = mock_impl.call_args
        assert call_args[0][0] == "test_flow"  # flow_name
        assert call_args[0][1] is None  # input_file
        assert call_args[0][2] is None  # input_data
        assert call_args[0][3] is not None  # context
        assert call_args[0][3].source == "cli"

        # Verify flow execution display was used
        mock_display.show_flow_execution.assert_called_once_with(
            "test_flow", mock_result
        )

    def test_flow_run_cli_with_input_file(self) -> None:
        """flow_run_cli should handle input file parameter."""
        mock_result = FlowCommandResult.success_result(["output"])
        input_path = Path("/test/input.json")

        with (
            patch("flow_command.cli.commands.flow_run_implementation") as mock_impl,
            patch("flow_command.cli.commands.FlowDisplay") as mock_display_class,
        ):

            mock_impl.return_value = mock_result
            mock_display_class.return_value = Mock()

            flow_run_cli("test_flow", input_file=input_path)

        # Verify input file was passed
        call_args = mock_impl.call_args
        assert call_args[0][1] == input_path

    def test_flow_run_cli_with_input_data_json(self) -> None:
        """flow_run_cli should handle JSON input data parameter."""
        mock_result = FlowCommandResult.success_result(["output"])
        input_data = '["item1", "item2"]'  # JSON string

        with (
            patch("flow_command.cli.commands.flow_run_implementation") as mock_impl,
            patch("flow_command.cli.commands.FlowDisplay") as mock_display_class,
        ):

            mock_impl.return_value = mock_result
            mock_display_class.return_value = Mock()

            flow_run_cli("test_flow", input_data=input_data)

        # Verify input data was parsed as JSON
        call_args = mock_impl.call_args
        assert call_args[0][2] == ["item1", "item2"]  # Parsed JSON

    def test_flow_run_cli_with_input_data_text(self) -> None:
        """flow_run_cli should handle text input data parameter."""
        mock_result = FlowCommandResult.success_result(["output"])
        input_data = "single_item"

        with (
            patch("flow_command.cli.commands.flow_run_implementation") as mock_impl,
            patch("flow_command.cli.commands.FlowDisplay") as mock_display_class,
        ):

            mock_impl.return_value = mock_result
            mock_display_class.return_value = Mock()

            flow_run_cli("test_flow", input_data=input_data)

        # Verify input data was passed as text
        call_args = mock_impl.call_args
        assert call_args[0][2] == "single_item"

    def test_flow_run_cli_with_output_format(self) -> None:
        """flow_run_cli should handle different output formats."""
        mock_result = FlowCommandResult.success_result(["output"])

        with (
            patch("flow_command.cli.commands.flow_run_implementation") as mock_impl,
            patch("flow_command.cli.commands.FlowDisplay") as mock_display_class,
        ):

            mock_impl.return_value = mock_result
            mock_display_class.return_value = Mock()

            flow_run_cli("test_flow", output_format="json")

        # Verify context has correct output format
        call_args = mock_impl.call_args
        assert call_args[0][3].output_format == "json"

    def test_flow_run_cli_with_timeout(self) -> None:
        """flow_run_cli should handle custom timeout parameter."""
        mock_result = FlowCommandResult.success_result(["output"])

        with (
            patch("flow_command.cli.commands.flow_run_implementation") as mock_impl,
            patch("flow_command.cli.commands.FlowDisplay") as mock_display_class,
        ):

            mock_impl.return_value = mock_result
            mock_display_class.return_value = Mock()

            flow_run_cli("test_flow", timeout=60.0)

        # Verify context has correct timeout
        call_args = mock_impl.call_args
        assert call_args[0][3].execution_timeout == 60.0

    def test_flow_run_cli_with_plain_output(self) -> None:
        """flow_run_cli should handle plain output option."""
        mock_result = FlowCommandResult.success_result(["output"])

        with (
            patch("flow_command.cli.commands.flow_run_implementation") as mock_impl,
            patch("flow_command.cli.commands.FlowDisplay") as mock_display_class,
        ):

            mock_impl.return_value = mock_result
            mock_display_class.return_value = Mock()

            flow_run_cli("test_flow", plain=True)

        # Verify context has plain output enabled
        call_args = mock_impl.call_args
        assert call_args[0][3].plain_output is True

    def test_flow_run_cli_with_failure_exit(self) -> None:
        """flow_run_cli should exit with code 1 on failure."""
        mock_result: FlowCommandResult[None] = FlowCommandResult.error_result(
            "Flow failed"
        )

        with (
            patch("flow_command.cli.commands.flow_run_implementation") as mock_impl,
            patch("flow_command.cli.commands.FlowDisplay") as mock_display_class,
        ):

            mock_impl.return_value = mock_result
            mock_display_class.return_value = Mock()

            with pytest.raises(typer.Exit) as exc_info:
                flow_run_cli("test_flow")

            assert exc_info.value.exit_code == 1
