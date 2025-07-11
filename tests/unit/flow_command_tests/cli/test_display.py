from __future__ import annotations

from io import StringIO
from unittest.mock import Mock, patch

from rich.console import Console

from flow_command.cli.display import FlowDisplay
from flow_command.core.context import FlowCommandContext
from flow_command.core.result import FlowCommandResult


class TestFlowDisplay:
    """Test suite for FlowDisplay rich terminal utilities."""

    def test_flow_display_initialization(self) -> None:
        """FlowDisplay should initialize with context and console."""
        context = FlowCommandContext.from_test()
        display = FlowDisplay(context)

        assert display.context is context
        assert display.console is context.console

    def test_show_result_text_format_success_list(self) -> None:
        """FlowDisplay should show successful list results in text format."""
        context = FlowCommandContext.from_test(output_format="text")
        display = FlowDisplay(context)
        result = FlowCommandResult.success_result(["item1", "item2", "item3"])

        # Capture console output
        string_io = StringIO()
        with patch.object(display.console, "print") as mock_print:
            display.show_result(result)

        # Verify list items were printed
        from unittest.mock import call

        expected_calls = [
            call("• item1"),
            call("• item2"),
            call("• item3"),
        ]
        mock_print.assert_has_calls(expected_calls)

    def test_show_result_text_format_success_single(self) -> None:
        """FlowDisplay should show successful single results in text format."""
        context = FlowCommandContext.from_test(output_format="text")
        display = FlowDisplay(context)
        result = FlowCommandResult.success_result("single_result")

        with patch.object(display.console, "print") as mock_print:
            display.show_result(result)

        mock_print.assert_called_once_with("single_result")

    def test_show_result_text_format_success_empty(self) -> None:
        """FlowDisplay should show message for empty results."""
        context = FlowCommandContext.from_test(output_format="text")
        display = FlowDisplay(context)
        result = FlowCommandResult.success_result(None)

        with patch.object(display.console, "print") as mock_print:
            display.show_result(result)

        mock_print.assert_called_once_with("No results found.")

    def test_show_result_text_format_error(self) -> None:
        """FlowDisplay should show error panel for failed results."""
        context = FlowCommandContext.from_test(output_format="text")
        display = FlowDisplay(context)
        result: FlowCommandResult[None] = FlowCommandResult.error_result(
            "Something went wrong"
        )

        with patch.object(display.console, "print") as mock_print:
            display.show_result(result)

        # Verify error panel was printed
        mock_print.assert_called_once()
        call_args = mock_print.call_args[0]
        assert len(call_args) == 1
        from rich.panel import Panel

        panel = call_args[0]
        assert isinstance(panel, Panel)
        # Check panel contents through its renderable text
        assert "Something went wrong" in str(panel.renderable)

    def test_show_result_json_format(self) -> None:
        """FlowDisplay should show results in JSON format."""
        context = FlowCommandContext.from_test(output_format="json")
        display = FlowDisplay(context)
        result = FlowCommandResult.success_result(["item1", "item2"])

        with patch.object(display.console, "print") as mock_print:
            display.show_result(result)

        # Verify JSON was printed
        mock_print.assert_called_once()
        call_args = mock_print.call_args[0]
        json_output = call_args[0]
        assert '"success": true' in json_output
        assert '"item1"' in json_output
        assert '"item2"' in json_output

    def test_show_result_table_format_success(self) -> None:
        """FlowDisplay should show list results in table format."""
        context = FlowCommandContext.from_test(output_format="table")
        display = FlowDisplay(context)
        result = FlowCommandResult.success_result(["flow1", "flow2"])

        with patch.object(display.console, "print") as mock_print:
            display.show_result(result)

        # Verify table was printed
        mock_print.assert_called_once()
        call_args = mock_print.call_args[0]
        from rich.table import Table

        table = call_args[0]
        assert isinstance(table, Table)
        assert table.title == "Flow Results"

    def test_show_result_table_format_fallback_to_text(self) -> None:
        """FlowDisplay should fallback to text for non-list table results."""
        context = FlowCommandContext.from_test(output_format="table")
        display = FlowDisplay(context)
        result = FlowCommandResult.success_result("single_item")

        with patch.object(display.console, "print") as mock_print:
            display.show_result(result)

        # Should fallback to text display
        mock_print.assert_called_once_with("single_item")

    def test_show_result_table_format_error_fallback(self) -> None:
        """FlowDisplay should fallback to text for error results in table format."""
        context = FlowCommandContext.from_test(output_format="table")
        display = FlowDisplay(context)
        result: FlowCommandResult[None] = FlowCommandResult.error_result(
            "Error occurred"
        )

        with patch.object(display.console, "print") as mock_print:
            display.show_result(result)

        # Should show error panel
        mock_print.assert_called_once()
        call_args = mock_print.call_args[0]
        from rich.panel import Panel

        panel = call_args[0]
        assert isinstance(panel, Panel)
        assert "Error occurred" in str(panel.renderable)

    def test_show_flow_execution_success(self) -> None:
        """FlowDisplay should show flow execution success with enhanced formatting."""
        context = FlowCommandContext.from_test(output_format="text")
        display = FlowDisplay(context)
        result = FlowCommandResult.success_result(["output1", "output2"])
        result.execution_time = 1.234

        with patch.object(display.console, "print") as mock_print:
            display.show_flow_execution("test_flow", result)

        # Should print success panel and results
        assert mock_print.call_count >= 2

        # Check success panel
        first_call = mock_print.call_args_list[0][0][0]
        from rich.panel import Panel

        assert isinstance(first_call, Panel)
        assert "test_flow" in str(first_call.renderable)
        assert "1.234s" in str(first_call.renderable)

        # Check results section
        second_call = mock_print.call_args_list[1][0][0]
        assert "Results:" in str(second_call)

    def test_show_flow_execution_success_json_format(self) -> None:
        """FlowDisplay should show flow execution in JSON format."""
        context = FlowCommandContext.from_test(output_format="json")
        display = FlowDisplay(context)
        result = FlowCommandResult.success_result(["output1", "output2"])
        result.execution_time = 1.234

        with patch.object(display.console, "print") as mock_print:
            display.show_flow_execution("test_flow", result)

        # Should print success panel and JSON results
        assert mock_print.call_count >= 2

    def test_show_flow_execution_success_no_data(self) -> None:
        """FlowDisplay should handle flow execution with no output data."""
        context = FlowCommandContext.from_test(output_format="text")
        display = FlowDisplay(context)
        result = FlowCommandResult.success_result(None)
        result.execution_time = 0.5

        with patch.object(display.console, "print") as mock_print:
            display.show_flow_execution("test_flow", result)

        # Should only print success panel, no results section
        mock_print.assert_called_once()

    def test_show_flow_execution_error(self) -> None:
        """FlowDisplay should show flow execution errors."""
        context = FlowCommandContext.from_test(output_format="text")
        display = FlowDisplay(context)
        result: FlowCommandResult[None] = FlowCommandResult.error_result(
            "Execution failed"
        )

        with patch.object(display.console, "print") as mock_print:
            display.show_flow_execution("test_flow", result)

        # Should delegate to _show_text_result for errors
        mock_print.assert_called_once()
        call_args = mock_print.call_args[0]
        from rich.panel import Panel

        panel = call_args[0]
        assert isinstance(panel, Panel)
        assert "Execution failed" in str(panel.renderable)

    def test_private_show_json_result(self) -> None:
        """FlowDisplay._show_json_result should format and print JSON."""
        context = FlowCommandContext.from_test()
        display = FlowDisplay(context)
        result = FlowCommandResult.success_result({"key": "value"})

        with patch.object(display.console, "print") as mock_print:
            display._show_json_result(result)

        mock_print.assert_called_once()
        json_output = mock_print.call_args[0][0]
        assert '"success": true' in json_output
        assert '"key": "value"' in json_output

    def test_private_show_table_result_with_data(self) -> None:
        """FlowDisplay._show_table_result should create table for list data."""
        context = FlowCommandContext.from_test()
        display = FlowDisplay(context)
        result = FlowCommandResult.success_result(["item1", "item2"])

        with patch.object(display.console, "print") as mock_print:
            display._show_table_result(result)

        mock_print.assert_called_once()
        from rich.table import Table

        table = mock_print.call_args[0][0]
        assert isinstance(table, Table)
        assert table.title == "Flow Results"

    def test_private_show_table_result_empty_data(self) -> None:
        """FlowDisplay._show_table_result should fallback for empty data."""
        context = FlowCommandContext.from_test()
        display = FlowDisplay(context)
        result: FlowCommandResult[list[str]] = FlowCommandResult.success_result([])

        with patch.object(display.console, "print") as mock_print:
            with patch.object(display, "_show_text_result") as mock_text:
                display._show_table_result(result)

        # Should fallback to text display
        mock_text.assert_called_once_with(result)

    def test_private_show_table_result_error(self) -> None:
        """FlowDisplay._show_table_result should fallback for error results."""
        context = FlowCommandContext.from_test()
        display = FlowDisplay(context)
        result: FlowCommandResult[None] = FlowCommandResult.error_result(
            "Error occurred"
        )

        with patch.object(display.console, "print") as mock_print:
            with patch.object(display, "_show_text_result") as mock_text:
                display._show_table_result(result)

        # Should fallback to text display
        mock_text.assert_called_once_with(result)
