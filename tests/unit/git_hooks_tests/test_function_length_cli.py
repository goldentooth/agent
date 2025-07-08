"""Tests for function length CLI integration."""

import tempfile
from pathlib import Path
from unittest.mock import patch

from git_hooks.cli import check_function_length, check_function_length_warnings


class TestFunctionLengthCLI:
    """Test CLI integration for function length validation."""

    def test_check_function_length_no_files(self) -> None:
        """Should return 0 when no files to check."""
        with patch("git_hooks.hook_runner.is_git_repo", return_value=True):
            with patch("git_hooks.hook_runner.get_staged_files", return_value=[]):
                result = check_function_length()
                assert result == 0

    def test_check_function_length_valid_files(self) -> None:
        """Should return 0 when all functions are within limits."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text(
                '''def short_function():
    """A short function."""
    return 42
'''
            )

            with patch("git_hooks.hook_runner.is_git_repo", return_value=True):
                with patch(
                    "git_hooks.hook_runner.get_staged_files",
                    return_value=[test_file],
                ):
                    result = check_function_length()
                    assert result == 0

    def test_check_function_length_invalid_files(self) -> None:
        """Should return 1 when functions exceed limits."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            # Create a long function
            function_body = "\n".join(f"    line_{i} = {i}" for i in range(20))
            test_file.write_text(
                f'''def long_function():
    """A long function."""
{function_body}
    return 42
'''
            )

            with patch("git_hooks.hook_runner.is_git_repo", return_value=True):
                with patch(
                    "git_hooks.hook_runner.get_staged_files",
                    return_value=[test_file],
                ):
                    result = check_function_length()
                    assert result == 1

    def test_check_function_length_warnings_no_files(self) -> None:
        """Should return 0 when no files to check."""
        with patch("git_hooks.hook_runner.is_git_repo", return_value=True):
            with patch("git_hooks.hook_runner.get_staged_files", return_value=[]):
                result = check_function_length_warnings()
                assert result == 0

    def test_check_function_length_warnings_always_succeeds(self) -> None:
        """Should always return 0 (warnings never fail)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            # Create a long function
            function_body = "\n".join(f"    line_{i} = {i}" for i in range(20))
            test_file.write_text(
                f'''def long_function():
    """A long function."""
{function_body}
    return 42
'''
            )

            with patch("git_hooks.hook_runner.is_git_repo", return_value=True):
                with patch(
                    "git_hooks.hook_runner.get_staged_files",
                    return_value=[test_file],
                ):
                    result = check_function_length_warnings()
                    assert result == 0  # Always succeeds

    def test_check_function_length_uses_env_vars(self) -> None:
        """Should use environment variables for configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            # Create a function with 8 lines
            function_body = "\n".join(f"    line_{i} = {i}" for i in range(4))
            test_file.write_text(
                f'''def medium_function():
    """A medium function."""
{function_body}
    return 42
'''
            )

            with patch("git_hooks.hook_runner.is_git_repo", return_value=True):
                with patch(
                    "git_hooks.hook_runner.get_staged_files",
                    return_value=[test_file],
                ):
                    # Set limit to 5 lines via environment variable
                    with patch("os.environ.get") as mock_env:
                        mock_env.return_value = "5"
                        result = check_function_length()
                        assert result == 1  # Should fail with 5 line limit

    def test_check_function_length_non_git_repo(self) -> None:
        """Should handle non-git repositories gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text(
                '''def short_function():
    """A short function."""
    return 42
'''
            )

            with patch("git_hooks.hook_runner.is_git_repo", return_value=False):
                with patch(
                    "git_hooks.hook_runner.get_all_files", return_value=[test_file]
                ):
                    result = check_function_length()
                    assert result == 0
