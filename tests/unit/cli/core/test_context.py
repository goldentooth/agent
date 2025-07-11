"""Tests for CLI context and result classes."""

import os
from unittest.mock import Mock, patch

import pytest
from rich.console import Console

from goldentooth_agent.cli.core.context import CommandContext, CommandResult


class TestCommandContext:
    """Test CommandContext class."""

    def test_context_creation_defaults(self) -> None:
        """Test creating context with defaults."""
        context = CommandContext()

        assert context.input_data is None
        assert context.output_format == "text"
        assert context.plain_output is False
        assert context.no_color is False
        assert context.interactive is True
        assert context.user_id is None
        assert context.session_id is None
        assert context.record_svg is False
        assert context.svg_output_path is None
        assert isinstance(context.console, Console)

    def test_context_from_cli(self) -> None:
        """Test creating context from CLI parameters."""
        context = CommandContext.from_cli(
            input_data="test_data",
            output_format="json",
            plain=True,
            no_color=True,
            record=True,
            record_path="test.svg",
        )

        assert context.input_data == "test_data"
        assert context.output_format == "json"
        assert context.plain_output is True
        assert context.no_color is True
        assert context.record_svg is True
        assert context.svg_output_path == "test.svg"
        assert context.interactive is True

    def test_context_from_chat(self) -> None:
        """Test creating context from chat interface."""
        context = CommandContext.from_chat(
            input_data="chat_data",
            user_id="user123",
            session_id="session456",
            output_format="text",
        )

        assert context.input_data == "chat_data"
        assert context.user_id == "user123"
        assert context.session_id == "session456"
        assert context.output_format == "text"
        assert context.interactive is True
        assert context.plain_output is False

    @patch.dict(os.environ, {"NO_COLOR": "1"})
    def test_context_no_color_env(self) -> None:
        """Test that NO_COLOR environment variable is respected."""
        context = CommandContext()
        # Console should be configured without color
        assert context.console._color_system is None

    def test_context_plain_output(self) -> None:
        """Test plain output configuration."""
        context = CommandContext(plain_output=True)

        # Console should be configured for plain output
        assert context.console._color_system is None
        assert context.console._force_terminal is False


class TestCommandResult:
    """Test CommandResult class."""

    def test_result_creation_defaults(self) -> None:
        """Test creating result with defaults."""
        result = CommandResult()

        assert result.data is None
        assert result.success is True
        assert result.error_message is None
        assert result.exit_code == 0
        assert result.display_data is None
        assert result.formatted_output is None
        assert result.execution_time is None
        assert result.metadata == {}

    def test_result_with_data(self) -> None:
        """Test creating result with data."""
        result = CommandResult(
            data={"key": "value"},
            success=True,
            execution_time=1.5,
            metadata={"source": "test"},
        )

        assert result.data == {"key": "value"}
        assert result.success is True
        assert result.execution_time == 1.5
        assert result.metadata == {"source": "test"}

    def test_result_with_error(self) -> None:
        """Test creating result with error."""
        result = CommandResult(
            success=False,
            error_message="Test error",
            exit_code=2,
        )

        assert result.success is False
        assert result.error_message == "Test error"
        assert result.exit_code == 2

    def test_result_to_json(self) -> None:
        """Test converting result to JSON."""
        result = CommandResult(
            data={"test": "data"},
            success=True,
            execution_time=0.5,
            metadata={"info": "test"},
        )

        json_data = result.to_json()

        assert json_data["data"] == {"test": "data"}
        assert json_data["success"] is True
        assert json_data["error_message"] is None
        assert json_data["exit_code"] == 0
        assert json_data["execution_time"] == 0.5
        assert json_data["metadata"] == {"info": "test"}

    def test_result_to_text_success(self) -> None:
        """Test converting successful result to text."""
        result = CommandResult(
            data="test output",
            success=True,
        )

        text = result.to_text()
        assert text == "test output"

    def test_result_to_text_formatted(self) -> None:
        """Test converting result with formatted output to text."""
        result = CommandResult(
            data="raw data",
            formatted_output="formatted output",
            success=True,
        )

        text = result.to_text()
        assert text == "formatted output"

    def test_result_to_text_error(self) -> None:
        """Test converting error result to text."""
        result = CommandResult(
            success=False,
            error_message="Test error occurred",
        )

        text = result.to_text()
        assert text == "Error: Test error occurred"

    def test_result_to_text_none_data(self) -> None:
        """Test converting result with None data to text."""
        result = CommandResult(
            data=None,
            success=True,
        )

        text = result.to_text()
        assert text == ""
