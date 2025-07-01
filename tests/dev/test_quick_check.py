"""Tests for quick development feedback tool."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from goldentooth_agent.dev.quick_check import (
    check_dict_access_patterns,
    check_import_organization,
    count_missing_return_types,
    has_complex_help_text,
    quick_check,
)


class TestQuickCheck:
    """Test quick development feedback functionality."""

    def test_has_complex_help_text_simple(self):
        """Test detection of simple help text."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write('app.command(help="Simple help text")')
            f.flush()

            result = has_complex_help_text(Path(f.name))
            assert not result

    def test_has_complex_help_text_with_unicode(self):
        """Test detection of help text with unicode characters."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write('app.command(help="Complex help text with 🔧 unicode")')
            f.flush()

            result = has_complex_help_text(Path(f.name))
            assert result

    def test_has_complex_help_text_multiline(self):
        """Test detection of multiline help text."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("""app.command(help="Line 1\nLine 2")""")
            f.flush()

            result = has_complex_help_text(Path(f.name))
            assert result

    def test_count_missing_return_types_with_missing(self):
        """Test counting functions missing return type annotations."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(
                """
def function_with_return() -> str:
    return "hello"

def function_without_return():
    return "hello"

def _private_function():
    return "private"  # Should be skipped
"""
            )
            f.flush()

            result = count_missing_return_types(Path(f.name))
            assert result == 1  # Only one public function without return type

    def test_count_missing_return_types_all_annotated(self):
        """Test counting when all functions have return types."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(
                """
def function_with_return() -> str:
    return "hello"

async def async_function_with_return() -> str:
    return "hello"
"""
            )
            f.flush()

            result = count_missing_return_types(Path(f.name))
            assert result == 0

    def test_check_dict_access_patterns_found(self):
        """Test detection of dict.attribute access patterns."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(
                """
def bad_access():
    return result.response  # This pattern should be detected
"""
            )
            f.flush()

            result = check_dict_access_patterns(Path(f.name))
            assert len(result) > 0

    def test_check_dict_access_patterns_none_found(self):
        """Test when no dict.attribute patterns are found."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(
                """
def good_access():
    result = {"key": "value"}
    return result["key"]

class MyClass:
    def method(self):
        return self.attribute  # This is fine
"""
            )
            f.flush()

            result = check_dict_access_patterns(Path(f.name))
            assert len(result) == 0

    def test_check_import_organization_good(self):
        """Test when import organization is good."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(
                """
import os
import sys
from pathlib import Path
from typing import Any

import pytest

from goldentooth_agent.core import something
"""
            )
            f.flush()

            result = check_import_organization(Path(f.name))
            assert len(result) == 0

    @patch("builtins.print")
    def test_quick_check_non_python_file(self, mock_print):
        """Test quick_check with non-Python file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Some text content")
            f.flush()

            quick_check(f.name)

            # Should not print anything for non-Python files
            mock_print.assert_not_called()

    @patch("builtins.print")
    def test_quick_check_cli_commands_file(self, mock_print):
        """Test quick_check with CLI commands file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            # Create a temporary file in a cli/commands directory structure
            cli_commands_dir = Path(f.name).parent / "cli" / "commands"
            cli_commands_dir.mkdir(parents=True, exist_ok=True)

            cli_file = cli_commands_dir / "test_command.py"
            cli_file.write_text(
                """
app.command(help="Help with 🔧 unicode")

def function_without_return():
    return "hello"
"""
            )

            quick_check(str(cli_file))

            # Should print warnings about complex help text and missing return types
            assert mock_print.call_count > 0

    @patch("builtins.print")
    def test_quick_check_good_file(self, mock_print):
        """Test quick_check with a well-formatted file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(
                '''
def good_function() -> str:
    """A well-documented function."""
    result = {"key": "value"}
    return result["key"]
'''
            )
            f.flush()

            quick_check(f.name)

            # Should not print any issues for a good file
            mock_print.assert_not_called()

    def test_quick_check_invalid_file_path(self):
        """Test quick_check with invalid file path."""
        # Should not raise an exception for invalid paths
        quick_check("/nonexistent/file.py")

    def test_quick_check_ast_parse_error(self):
        """Test quick_check with file that has syntax errors."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(
                """
def invalid_syntax(
    # Missing closing parenthesis and other syntax errors
    return "hello"
"""
            )
            f.flush()

            # Should not raise an exception for files with syntax errors
            quick_check(f.name)
