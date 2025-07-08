"""Tests for git hooks utilities."""

# pyright: reportPrivateUsage=false, reportUnknownParameterType=false, reportMissingParameterType=false, reportUnknownVariableType=false, reportUnknownMemberType=false

from pathlib import Path
from unittest.mock import Mock

import pytest  # type: ignore[reportMissingTypeStubs]

from git_hooks.core import ValidationResult, ValidationSeverity
from git_hooks.utils import _is_urgent_warning  # type: ignore[reportPrivateUsage]
from git_hooks.utils import _print_error_results  # type: ignore[reportPrivateUsage]
from git_hooks.utils import _print_single_warning  # type: ignore[reportPrivateUsage]
from git_hooks.utils import _print_warning_results  # type: ignore[reportPrivateUsage]
from git_hooks.utils import (
    _separate_results_by_severity,  # type: ignore[reportPrivateUsage]
)
from git_hooks.utils import print_results


class TestPrintResults:
    """Test suite for print_results function."""

    def test_print_results_empty_list(self, capsys) -> None:
        """Test print_results with empty results list."""
        print_results([], "Test Hook")
        captured = capsys.readouterr()
        assert "✅ Test Hook: All files within healthy limits" in captured.out

    def test_print_results_with_errors_only(self, capsys) -> None:
        """Test print_results with only error results."""
        error_result = ValidationResult(
            file_path=Path("test_file.py"),
            severity=ValidationSeverity.ERROR,
            message="Test error",
            line_count=100,
            limit=50,
        )

        print_results([error_result], "Test Hook")
        captured = capsys.readouterr()

        assert "❌ Test Hook violations found:" in captured.out
        assert "test_file.py: Test error" in captured.out
        assert "Please refactor large files/modules before committing." in captured.out

    def test_print_results_with_warnings_only(self, capsys) -> None:
        """Test print_results with only warning results."""
        warning_result = ValidationResult(
            file_path=Path("test_file.py"),
            severity=ValidationSeverity.WARNING,
            message="Test warning",
            line_count=40,  # Below urgent threshold (50 * 0.9 = 45)
            limit=50,
            guidance="Test guidance",
        )

        print_results([warning_result], "Test Hook")
        captured = capsys.readouterr()

        assert "⚠️  WARNING: test_file.py (Test warning)" in captured.out
        assert "Test guidance" in captured.out

    def test_print_results_with_mixed_results(self, capsys) -> None:
        """Test print_results with both errors and warnings."""
        error_result, warning_result = self._create_mixed_results()

        print_results([error_result, warning_result], "Test Hook")
        captured = capsys.readouterr()

        assert "❌ Test Hook violations found:" in captured.out
        assert "error_file.py: Test error" in captured.out
        assert "⚠️  WARNING: warning_file.py (Test warning)" in captured.out

    def _create_mixed_results(self):
        """Create error and warning results for testing."""
        error_result = self._create_error_result()
        warning_result = self._create_warning_result()
        return error_result, warning_result

    def _create_error_result(self):
        """Create error result for testing."""
        return ValidationResult(
            file_path=Path("error_file.py"),
            severity=ValidationSeverity.ERROR,
            message="Test error",
            line_count=100,
            limit=50,
        )

    def _create_warning_result(self):
        """Create warning result for testing."""
        return ValidationResult(
            file_path=Path("warning_file.py"),
            severity=ValidationSeverity.WARNING,
            message="Test warning",
            line_count=40,
            limit=50,
            guidance="Test guidance",
        )


class TestSeparateResultsBySeverity:
    """Test suite for _separate_results_by_severity function."""

    def test_separate_empty_results(self) -> None:
        """Test separating empty results list."""
        errors, warnings = _separate_results_by_severity([])
        assert errors == []
        assert warnings == []

    def test_separate_mixed_results(self) -> None:
        """Test separating mixed results."""
        error_result, warning_result = self._create_test_results_pair()

        errors, warnings = _separate_results_by_severity([error_result, warning_result])

        assert len(errors) == 1
        assert len(warnings) == 1
        assert errors[0].severity == ValidationSeverity.ERROR
        assert warnings[0].severity == ValidationSeverity.WARNING

    def _create_test_results_pair(self):
        """Create test error and warning results."""
        error_result = ValidationResult(
            file_path=Path("error.py"),
            severity=ValidationSeverity.ERROR,
            message="Error",
            line_count=100,
            limit=50,
        )
        warning_result = ValidationResult(
            file_path=Path("warning.py"),
            severity=ValidationSeverity.WARNING,
            message="Warning",
            line_count=45,
            limit=50,
        )
        return error_result, warning_result


class TestPrintErrorResults:
    """Test suite for _print_error_results function."""

    def test_print_empty_errors(self, capsys) -> None:
        """Test printing empty error list."""
        _print_error_results([], "Test Hook")
        captured = capsys.readouterr()
        assert captured.out == ""

    def test_print_single_error(self, capsys) -> None:
        """Test printing single error result."""
        error_result = ValidationResult(
            file_path=Path("./test_file.py"),
            severity=ValidationSeverity.ERROR,
            message="Test error",
            line_count=100,
            limit=50,
        )

        _print_error_results([error_result], "Test Hook")
        captured = capsys.readouterr()

        assert "❌ Test Hook violations found:" in captured.out
        assert "test_file.py: Test error" in captured.out
        assert "Please refactor large files/modules before committing." in captured.out

    def test_print_multiple_errors(self, capsys) -> None:
        """Test printing multiple error results."""
        error1 = ValidationResult(
            file_path=Path("file1.py"),
            severity=ValidationSeverity.ERROR,
            message="Error 1",
            line_count=100,
            limit=50,
        )
        error2 = ValidationResult(
            file_path=Path("file2.py"),
            severity=ValidationSeverity.ERROR,
            message="Error 2",
            line_count=200,
            limit=50,
        )

        _print_error_results([error1, error2], "Test Hook")
        captured = capsys.readouterr()

        assert "file1.py: Error 1" in captured.out
        assert "file2.py: Error 2" in captured.out


class TestPrintWarningResults:
    """Test suite for _print_warning_results function."""

    def test_print_empty_warnings(self, capsys) -> None:
        """Test printing empty warning list."""
        _print_warning_results([])
        captured = capsys.readouterr()
        assert captured.out == ""

    def test_print_single_warning(self, capsys) -> None:
        """Test printing single warning result."""
        warning_result = ValidationResult(
            file_path=Path("test_file.py"),
            severity=ValidationSeverity.WARNING,
            message="Test warning",
            line_count=40,  # Below urgent threshold
            limit=50,
            guidance="Test guidance",
        )

        _print_warning_results([warning_result])
        captured = capsys.readouterr()

        assert "⚠️  WARNING: test_file.py (Test warning)" in captured.out
        assert "Test guidance" in captured.out

    def test_print_multiple_warnings_same_guidance(self, capsys) -> None:
        """Test printing multiple warnings with same guidance only prints guidance once."""
        warning1 = ValidationResult(
            file_path=Path("file1.py"),
            severity=ValidationSeverity.WARNING,
            message="Warning 1",
            line_count=40,
            limit=50,
            guidance="Same guidance for all",
        )
        warning2 = ValidationResult(
            file_path=Path("file2.py"),
            severity=ValidationSeverity.WARNING,
            message="Warning 2",
            line_count=42,
            limit=50,
            guidance="Same guidance for all",
        )

        _print_warning_results([warning1, warning2])
        captured = capsys.readouterr()

        # Both warnings should be printed
        assert "⚠️  WARNING: file1.py (Warning 1)" in captured.out
        assert "⚠️  WARNING: file2.py (Warning 2)" in captured.out

        # Guidance should only appear once
        assert captured.out.count("Same guidance for all") == 1


class TestPrintSingleWarning:
    """Test suite for _print_single_warning function."""

    def test_print_regular_warning(self, capsys) -> None:
        """Test printing regular warning."""
        warning_result = ValidationResult(
            file_path=Path("./test_file.py"),
            severity=ValidationSeverity.WARNING,
            message="Test warning",
            line_count=40,
            limit=50,
            guidance="Test guidance",
        )

        _print_single_warning(warning_result)
        captured = capsys.readouterr()

        assert "⚠️  WARNING: test_file.py (Test warning)" in captured.out
        assert "Test guidance" in captured.out

    def test_print_urgent_warning(self, capsys) -> None:
        """Test printing urgent warning."""
        warning_result = ValidationResult(
            file_path=Path("test_file.py"),
            severity=ValidationSeverity.WARNING,
            message="Test urgent warning",
            line_count=46,  # >= 50 * 0.9 = 45
            limit=50,
            guidance="Test guidance",
        )

        _print_single_warning(warning_result)
        captured = capsys.readouterr()

        assert "🔶 URGENT: test_file.py (Test urgent warning)" in captured.out
        assert "Test guidance" in captured.out


class TestIsUrgentWarning:
    """Test suite for _is_urgent_warning function."""

    def test_urgent_warning_at_threshold(self) -> None:
        """Test urgent warning exactly at 90% threshold."""
        result = ValidationResult(
            file_path=Path("test.py"),
            severity=ValidationSeverity.WARNING,
            message="Test",
            line_count=45,  # Exactly 50 * 0.9
            limit=50,
        )
        assert _is_urgent_warning(result) is True

    def test_urgent_warning_above_threshold(self) -> None:
        """Test urgent warning above 90% threshold."""
        result = ValidationResult(
            file_path=Path("test.py"),
            severity=ValidationSeverity.WARNING,
            message="Test",
            line_count=46,  # Above 50 * 0.9
            limit=50,
        )
        assert _is_urgent_warning(result) is True

    def test_regular_warning_below_threshold(self) -> None:
        """Test regular warning below 90% threshold."""
        result = ValidationResult(
            file_path=Path("test.py"),
            severity=ValidationSeverity.WARNING,
            message="Test",
            line_count=44,  # Below 50 * 0.9
            limit=50,
        )
        assert _is_urgent_warning(result) is False
