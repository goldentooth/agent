"""Tests for function length validation."""

import tempfile
from pathlib import Path

from src.git_hooks.core import ValidationSeverity
from src.git_hooks.function_validator import FunctionLengthValidator


class TestFunctionLengthValidator:
    """Test function length validation behavior."""

    def test_function_under_limit_passes(self) -> None:
        """Functions under limit should pass validation."""
        validator = FunctionLengthValidator(limit=15)

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text(
                '''def short_function():
    """A short function."""
    return 42
'''
            )

            result = validator.validate(test_file)
            assert result is None

    def test_function_over_limit_fails(self) -> None:
        """Functions over limit should fail validation."""
        validator = FunctionLengthValidator(limit=15)

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            # Create a function with 20 lines
            function_body = "\n".join(f"    line_{i} = {i}" for i in range(16))
            test_file.write_text(
                f'''def long_function():
    """A long function."""
{function_body}
    return 42
'''
            )

            result = validator.validate(test_file)
            assert result is not None
            assert result.severity == ValidationSeverity.ERROR
            assert "long_function" in result.message
            assert result.line_count > 15

    def test_function_at_warn_threshold_warns(self) -> None:
        """Functions at warning threshold should warn."""
        validator = FunctionLengthValidator(limit=15, warn_threshold=10)

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            # Create a function with 12 lines
            function_body = "\n".join(f"    line_{i} = {i}" for i in range(8))
            test_file.write_text(
                f'''def medium_function():
    """A medium function."""
{function_body}
    return 42
'''
            )

            result = validator.validate(test_file)
            assert result is not None
            assert result.severity == ValidationSeverity.WARNING
            assert "medium_function" in result.message

    def test_function_at_urgent_threshold_warns(self) -> None:
        """Functions at urgent threshold should warn urgently."""
        validator = FunctionLengthValidator(limit=15, urgent_threshold=13)

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            # Create a function with 14 lines
            function_body = "\n".join(f"    line_{i} = {i}" for i in range(10))
            test_file.write_text(
                f'''def urgent_function():
    """An urgent function."""
{function_body}
    return 42
'''
            )

            result = validator.validate(test_file)
            assert result is not None
            assert result.severity == ValidationSeverity.WARNING
            assert "urgent_function" in result.message
            assert result.line_count >= 13

    def test_multiple_functions_validates_longest(self) -> None:
        """Should validate all functions and return longest violation."""
        validator = FunctionLengthValidator(limit=15)

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            # Create multiple functions, one long
            test_file.write_text(
                '''def short_function():
    """A short function."""
    return 42

def long_function():
    """A long function."""
    line_1 = 1
    line_2 = 2
    line_3 = 3
    line_4 = 4
    line_5 = 5
    line_6 = 6
    line_7 = 7
    line_8 = 8
    line_9 = 9
    line_10 = 10
    line_11 = 11
    line_12 = 12
    line_13 = 13
    return 42
'''
            )

            result = validator.validate(test_file)
            assert result is not None
            assert result.severity == ValidationSeverity.ERROR
            assert "long_function" in result.message

    def test_class_methods_are_validated(self) -> None:
        """Class methods should be validated."""
        validator = FunctionLengthValidator(limit=15)

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            # Create a class with a long method (ensure it's over limit)
            method_body = "\n".join(f"        line_{i} = {i}" for i in range(14))
            test_file.write_text(
                f'''class TestClass:
    """A test class."""

    def long_method(self):
        """A long method."""
{method_body}
        return 42
'''
            )

            result = validator.validate(test_file)
            assert result is not None
            assert result.severity == ValidationSeverity.ERROR
            assert "long_method" in result.message

    def test_nested_functions_are_validated(self) -> None:
        """Nested functions should be validated."""
        validator = FunctionLengthValidator(limit=15)

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            # Create nested functions where nested function is longer
            nested_body = "\n".join(f"        line_{i} = {i}" for i in range(14))
            test_file.write_text(
                f'''def outer_function():
    """A short outer function."""

    def nested_long_function():
        """A long nested function."""
{nested_body}
        return 42

    return nested_long_function()
'''
            )

            result = validator.validate(test_file)
            assert result is not None
            assert result.severity == ValidationSeverity.ERROR
            # The result should report the longest function violation
            assert result.line_count > 15

    def test_async_functions_are_validated(self) -> None:
        """Async functions should be validated."""
        validator = FunctionLengthValidator(limit=15)

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            # Create an async function
            async_body = "\n".join(f"    line_{i} = {i}" for i in range(14))
            test_file.write_text(
                f'''async def long_async_function():
    """A long async function."""
{async_body}
    return 42
'''
            )

            result = validator.validate(test_file)
            assert result is not None
            assert result.severity == ValidationSeverity.ERROR
            assert "long_async_function" in result.message

    def test_exclude_patterns_respected(self) -> None:
        """Files matching exclude patterns should be skipped."""
        validator = FunctionLengthValidator(
            limit=15, exclude_patterns=["old/", "*.min.py"]
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create file in excluded directory
            excluded_file = Path(tmpdir) / "old" / "test.py"
            excluded_file.parent.mkdir(parents=True, exist_ok=True)
            # Create a long function that would normally fail
            long_body = "\n".join(f"    line_{i} = {i}" for i in range(20))
            excluded_file.write_text(
                f"""def long_function():
{long_body}
    return 42
"""
            )

            result = validator.validate(excluded_file)
            assert result is None

    def test_non_python_files_ignored(self) -> None:
        """Non-Python files should be ignored."""
        validator = FunctionLengthValidator(limit=15)

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("This is not Python code with many lines" * 20)

            result = validator.validate(test_file)
            assert result is None

    def test_binary_files_ignored(self) -> None:
        """Binary files should be ignored."""
        validator = FunctionLengthValidator(limit=15)

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_bytes(b"\x00\x01\x02\x03" * 100)

            result = validator.validate(test_file)
            assert result is None

    def test_nonexistent_file_ignored(self) -> None:
        """Nonexistent files should be ignored."""
        validator = FunctionLengthValidator(limit=15)

        result = validator.validate(Path("/nonexistent/file.py"))
        assert result is None

    def test_default_thresholds_calculated(self) -> None:
        """Default warning and urgent thresholds should be calculated."""
        validator = FunctionLengthValidator(limit=15)

        assert validator.warn_threshold == 12  # 80% of 15
        assert validator.urgent_threshold == 13  # 87% of 15 (rounded)

    def test_custom_thresholds_respected(self) -> None:
        """Custom thresholds should be respected."""
        validator = FunctionLengthValidator(
            limit=15, warn_threshold=8, urgent_threshold=12
        )

        assert validator.warn_threshold == 8
        assert validator.urgent_threshold == 12
