"""Tests for CLI display utilities."""

import json
from unittest.mock import Mock, patch

import pytest

from goldentooth_agent.cli.core.context import CommandContext, CommandResult
from goldentooth_agent.cli.core.display import Display
from goldentooth_agent.cli.core.exceptions import CLIError


class TestDisplay:
    """Test Display class functionality."""

    def test_display_init_basic(self) -> None:
        """Test Display initialization."""
        context = CommandContext(console=Mock())
        display = Display(context)

        assert display.context == context
        assert display.console == context.console

    def test_display_init_with_recording(self) -> None:
        """Test Display initialization with SVG recording."""
        context = CommandContext(console=Mock(), record_svg=True)
        display = Display(context)

        assert display.context == context
        # Console should be replaced with recording console
        assert display.console != context.console

    def test_print(self) -> None:
        """Test basic print functionality."""
        console = Mock()
        context = CommandContext(console=console)
        display = Display(context)

        display.print("test message")
        console.print.assert_called_once_with("test message")

    def test_error_without_exit(self) -> None:
        """Test error display without exit."""
        console = Mock()
        context = CommandContext(console=console)
        display = Display(context)

        display.error("test error", exit_code=0)
        console.print.assert_called_once_with("❌ Error: test error", style="red")

    def test_error_with_exit(self) -> None:
        """Test error display with exit."""
        console = Mock()
        context = CommandContext(console=console)
        display = Display(context)

        with pytest.raises(CLIError) as exc_info:
            display.error("test error", exit_code=1)

        assert str(exc_info.value) == "test error"
        assert exc_info.value.exit_code == 1

    def test_success(self) -> None:
        """Test success message display."""
        console = Mock()
        context = CommandContext(console=console)
        display = Display(context)

        display.success("test success")
        console.print.assert_called_once_with("✅ test success", style="green")

    def test_warning(self) -> None:
        """Test warning message display."""
        console = Mock()
        context = CommandContext(console=console)
        display = Display(context)

        display.warning("test warning")
        console.print.assert_called_once_with("⚠️  test warning", style="yellow")

    def test_info(self) -> None:
        """Test info message display."""
        console = Mock()
        context = CommandContext(console=console)
        display = Display(context)

        display.info("test info")
        console.print.assert_called_once_with("ℹ️  test info", style="blue")

    def test_panel(self) -> None:
        """Test panel display."""
        console = Mock()
        context = CommandContext(console=console)
        display = Display(context)

        display.panel("test content", title="Test Title")
        console.print.assert_called_once()

    def test_table_empty(self) -> None:
        """Test table display with empty data."""
        console = Mock()
        context = CommandContext(console=console)
        display = Display(context)

        display.table([])
        console.print.assert_called_once_with("⚠️  No data to display", style="yellow")

    def test_table_with_data(self) -> None:
        """Test table display with data."""
        console = Mock()
        context = CommandContext(console=console)
        display = Display(context)

        data = [{"name": "test", "value": 42}]
        display.table(data)
        console.print.assert_called_once()

    def test_tree(self) -> None:
        """Test tree display."""
        console = Mock()
        context = CommandContext(console=console)
        display = Display(context)

        data = {"key": "value", "nested": {"inner": "data"}}
        display.tree(data)
        console.print.assert_called_once()

    def test_display_result_failure(self) -> None:
        """Test display result with failure."""
        console = Mock()
        context = CommandContext(console=console)
        display = Display(context)

        result = CommandResult(success=False, error_message="test error", exit_code=1)

        with pytest.raises(CLIError):
            display.display_result(result)

    def test_display_result_json(self) -> None:
        """Test display result with JSON format."""
        console = Mock()
        context = CommandContext(console=console, output_format="json")
        display = Display(context)

        result = CommandResult(success=True, data={"key": "value"})
        display.display_result(result)

        # Should print JSON
        console.print.assert_called_once()
        call_args = console.print.call_args[0][0]
        assert '"key": "value"' in call_args

    def test_display_result_text(self) -> None:
        """Test display result with text format."""
        console = Mock()
        context = CommandContext(console=console, output_format="text")
        display = Display(context)

        result = CommandResult(success=True, formatted_output="test output")
        display.display_result(result)

        console.print.assert_called_once_with("test output")

    def test_display_data_dict_small(self) -> None:
        """Test display data with small dict."""
        console = Mock()
        context = CommandContext(console=console)
        display = Display(context)

        data = {"key": "value", "num": 42}
        display._display_data(data)

        console.print.assert_called_once()

    def test_display_data_dict_large(self) -> None:
        """Test display data with large dict."""
        console = Mock()
        context = CommandContext(console=console)
        display = Display(context)

        data = {f"key{i}": f"value{i}" for i in range(10)}
        display._display_data(data)

        console.print.assert_called_once()

    def test_display_data_list_dicts(self) -> None:
        """Test display data with list of dicts."""
        console = Mock()
        context = CommandContext(console=console)
        display = Display(context)

        data = [{"name": "item1", "value": 1}, {"name": "item2", "value": 2}]
        display._display_data(data)

        console.print.assert_called_once()

    def test_display_data_list_items(self) -> None:
        """Test display data with list of items."""
        console = Mock()
        context = CommandContext(console=console)
        display = Display(context)

        data = ["item1", "item2", "item3"]
        display._display_data(data)

        assert console.print.call_count == 3

    def test_display_data_string(self) -> None:
        """Test display data with string."""
        console = Mock()
        context = CommandContext(console=console)
        display = Display(context)

        data = "test string"
        display._display_data(data)

        console.print.assert_called_once_with("test string")

    def test_save_svg_disabled(self) -> None:
        """Test save SVG when recording is disabled."""
        console = Mock()
        context = CommandContext(console=console, record_svg=False)
        display = Display(context)

        display.save_svg()
        # Should not call anything

    def test_save_svg_enabled(self) -> None:
        """Test save SVG when recording is enabled."""
        console = Mock()
        console.save_svg = Mock()
        context = CommandContext(console=console, record_svg=True)
        display = Display(context)
        display.console = console  # Override the console created in __init__

        display.save_svg("test.svg")
        console.save_svg.assert_called_once()

    def test_save_svg_no_method(self) -> None:
        """Test save SVG when console doesn't have save_svg method."""
        console = Mock()
        del console.save_svg  # Remove the method
        context = CommandContext(console=console, record_svg=True)
        display = Display(context)
        display.console = console  # Override the console created in __init__

        display.save_svg("test.svg")
        console.print.assert_called_once_with(
            "⚠️  SVG recording not available", style="yellow"
        )

    def test_measure_time(self) -> None:
        """Test measure time functionality."""
        console = Mock()
        context = CommandContext(console=console)
        display = Display(context)

        def test_func(x: int) -> int:
            return x * 2

        result, execution_time = display.measure_time(test_func, 5)

        assert result == 10
        assert execution_time >= 0

    def test_spinner_plain_output(self) -> None:
        """Test spinner with plain output."""
        console = Mock()
        context = CommandContext(console=console, plain_output=True)
        display = Display(context)

        # Mock the console
        mock_console = Mock()
        display.console = mock_console

        with display.spinner("Testing"):
            pass

        # In plain mode, display.console.print should be called before entering the context
        mock_console.print.assert_called_with("⏳ Testing...")

    def test_progress_bar_plain_output(self) -> None:
        """Test progress bar with plain output."""
        console = Mock()
        context = CommandContext(console=console, plain_output=True)
        display = Display(context)

        iterable = [1, 2, 3]
        result = display.progress_bar(iterable)

        assert result == iterable
