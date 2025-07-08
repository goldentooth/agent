"""Tests for function length validation."""

import tempfile
from pathlib import Path

from git_hooks.core import ValidationSeverity
from git_hooks.function_validator import FunctionLengthValidator


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
            # Create a function with 13 statements (at urgent threshold)
            function_body = "\n".join(f"    line_{i} = {i}" for i in range(13))
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
            assert result.line_count >= 13  # Should be 13 statements

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
    line_14 = 14
    line_15 = 15
    line_16 = 16
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

    def test_get_all_function_info_multiple_functions(self) -> None:
        """get_all_function_info should return info for all functions sorted by line count."""
        validator = FunctionLengthValidator(limit=15)

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text(
                '''def short_function():
    """A short function."""
    return 42

def medium_function():
    """A medium function."""
    x = 1
    y = 2
    z = 3
    return x + y + z

def long_function():
    """A long function."""
    x = 1
    y = 2
    z = 3
    a = 4
    b = 5
    c = 6
    d = 7
    e = 8
    return x + y + z + a + b + c + d + e

async def async_function():
    """An async function."""
    await some_call()
    return 42
'''
            )

            result = validator.get_all_function_info(test_file)

            # Should return 4 functions
            assert len(result) == 4

            # Should be sorted by line count descending
            function_names = [func[0] for func in result]
            line_counts = [func[3] for func in result]

            # Verify sorting (long_function should be first)
            assert function_names[0] == "long_function"
            assert line_counts == sorted(line_counts, reverse=True)

            # Verify structure: (name, start_line, end_line, line_count)
            for name, start_line, end_line, line_count in result:
                assert isinstance(name, str)
                assert isinstance(start_line, int)
                assert isinstance(end_line, int)
                assert isinstance(line_count, int)
                assert start_line > 0
                assert end_line >= start_line
                assert line_count == end_line - start_line + 1

    def test_get_all_function_info_non_python_file(self) -> None:
        """get_all_function_info should return empty list for non-Python files."""
        validator = FunctionLengthValidator(limit=15)

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("This is not Python code")

            result = validator.get_all_function_info(test_file)
            assert result == []

    def test_get_all_function_info_invalid_python(self) -> None:
        """get_all_function_info should return empty list for invalid Python."""
        validator = FunctionLengthValidator(limit=15)

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("def invalid_syntax(\n")

            result = validator.get_all_function_info(test_file)
            assert result == []

    def test_get_all_function_statements_multiple_functions(self) -> None:
        """get_all_function_statements should return statement counts for all functions."""
        validator = FunctionLengthValidator(limit=15)

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text(
                '''def simple_function():
    """Simple function with few statements."""
    return 42

def complex_function():
    """Function with many statements."""
    x = 1
    y = 2
    z = x + y
    if z > 2:
        z = z * 2
    for i in range(3):
        z += i
    while z < 10:
        z += 1
    try:
        result = z / 2
    except ZeroDivisionError:
        result = 0
    return result

async def async_function():
    """Async function."""
    await some_call()
    x = 1
    return x
'''
            )

            result = validator.get_all_function_statements(test_file)

            # Should return 3 functions
            assert len(result) == 3

            # Should be sorted by statement count descending
            function_names = [func[0] for func in result]
            statement_counts = [func[4] for func in result]

            # complex_function should be first (most statements)
            assert function_names[0] == "complex_function"
            assert statement_counts == sorted(statement_counts, reverse=True)

            # Verify structure: (name, start_line, end_line, line_count, statement_count)
            for name, start_line, end_line, line_count, stmt_count in result:
                assert isinstance(name, str)
                assert isinstance(start_line, int)
                assert isinstance(end_line, int)
                assert isinstance(line_count, int)
                assert isinstance(stmt_count, int)
                assert start_line > 0
                assert end_line >= start_line
                assert line_count == end_line - start_line + 1
                assert (
                    stmt_count > 0
                )  # All functions should have at least one statement

    def test_get_all_function_statements_non_python_file(self) -> None:
        """get_all_function_statements should return empty list for non-Python files."""
        validator = FunctionLengthValidator(limit=15)

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("This is not Python code")

            result = validator.get_all_function_statements(test_file)
            assert result == []

    def test_get_all_function_statements_invalid_python(self) -> None:
        """get_all_function_statements should return empty list for invalid Python."""
        validator = FunctionLengthValidator(limit=15)

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("def invalid_syntax(\n")

            result = validator.get_all_function_statements(test_file)
            assert result == []
