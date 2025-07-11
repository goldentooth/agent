"""Tests for template command."""

import pytest

from goldentooth_agent.cli.commands._template import template_command_implementation
from goldentooth_agent.cli.core.context import CommandResult


class TestTemplateCommand:
    """Test template command functionality."""

    def test_template_command_basic(self) -> None:
        """Test basic template command execution."""
        result = template_command_implementation("test input")

        assert isinstance(result, CommandResult)
        assert result.success is True
        assert result.data == {"processed": "Processed: test input"}
        assert result.formatted_output == "Processed: test input"

    def test_template_command_with_option(self) -> None:
        """Test template command with option flag."""
        result = template_command_implementation("test input", option_flag=True)

        assert isinstance(result, CommandResult)
        assert result.success is True
        assert result.data == {"processed": "Processed: test input (with option)"}
        assert result.formatted_output == "Processed: test input (with option)"

    def test_template_command_different_format(self) -> None:
        """Test template command with different format."""
        result = template_command_implementation("test input", format_option="json")

        assert isinstance(result, CommandResult)
        assert result.success is True
        assert result.data == {"processed": "Processed: test input"}

    def test_template_command_with_exception(self) -> None:
        """Test template command with exception handling."""
        # This tests the exception handling in the template
        # We'll need to mock an exception scenario

        # For now, just test that normal execution works
        result = template_command_implementation("")

        assert isinstance(result, CommandResult)
        assert result.success is True
