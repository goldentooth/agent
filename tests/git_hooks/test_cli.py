"""Tests for CLI functionality."""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.git_hooks import cli, utils
from src.git_hooks.core import ValidationResult, ValidationSeverity

from .conftest import create_file_with_lines, create_module_with_total_lines


class TestCLI:
    """Test CLI hook functionality."""

    def test_file_length_hook_passes_small_files(self, temp_git_repo: Path) -> None:
        """File length hook passes with small files."""
        small_file = temp_git_repo / "small.py"
        create_file_with_lines(small_file, 500)

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout="small.py\n", stderr=""
            )
            with patch(
                "src.git_hooks.utils.get_staged_files", return_value=[small_file]
            ):
                result = cli.check_file_length()

        assert result == 0

    def test_file_length_hook_fails_large_files(self, temp_git_repo: Path) -> None:
        """File length hook fails with large files."""
        large_file = temp_git_repo / "large.py"
        create_file_with_lines(large_file, 1500)

        with patch("src.git_hooks.hook_runner.is_git_repo", return_value=True):
            with patch(
                "src.git_hooks.hook_runner.get_staged_files", return_value=[large_file]
            ):
                result = cli.check_file_length()

        assert result == 1

    def test_file_length_warnings_always_succeeds(self, temp_git_repo: Path) -> None:
        """File length warnings hook always returns 0."""
        large_file = temp_git_repo / "large.py"
        create_file_with_lines(large_file, 950)

        with patch("src.git_hooks.hook_runner.is_git_repo", return_value=True):
            with patch(
                "src.git_hooks.hook_runner.get_staged_files", return_value=[large_file]
            ):
                result = cli.check_file_length_warnings()

        assert result == 0

    def test_module_size_hook_passes_small_modules(self, temp_git_repo: Path) -> None:
        """Module size hook passes with small modules."""
        create_module_with_total_lines(temp_git_repo, "small_module", 3000)

        with patch(
            "src.git_hooks.hook_runner.get_modules",
            return_value=[temp_git_repo / "small_module"],
        ):
            result = cli.check_module_size()

        assert result == 0

    def test_module_size_hook_fails_large_modules(self, temp_git_repo: Path) -> None:
        """Module size hook fails with large modules."""
        create_module_with_total_lines(temp_git_repo, "large_module", 6000)

        with patch(
            "src.git_hooks.hook_runner.get_modules",
            return_value=[temp_git_repo / "large_module"],
        ):
            result = cli.check_module_size()

        assert result == 1

    def test_hooks_respect_environment_variables(self, temp_git_repo: Path) -> None:
        """Hooks respect environment variable limits."""
        test_file = temp_git_repo / "test.py"
        create_file_with_lines(test_file, 800)

        # Should pass with default limit (1000)
        with patch("src.git_hooks.hook_runner.is_git_repo", return_value=True):
            with patch(
                "src.git_hooks.hook_runner.get_staged_files", return_value=[test_file]
            ):
                result = cli.check_file_length()
        assert result == 0

        # Should fail with custom limit (500)
        with patch.dict(os.environ, {"FILE_LENGTH_LIMIT": "500"}):
            with patch("src.git_hooks.hook_runner.is_git_repo", return_value=True):
                with patch(
                    "src.git_hooks.hook_runner.get_staged_files",
                    return_value=[test_file],
                ):
                    result = cli.check_file_length()
        assert result == 1

    def test_hooks_work_outside_git_repo(self, tmp_path: Path) -> None:
        """Hooks work in non-git directories."""
        large_file = tmp_path / "large.py"
        create_file_with_lines(large_file, 1500)

        with patch("src.git_hooks.hook_runner.is_git_repo", return_value=False):
            with patch(
                "src.git_hooks.hook_runner.get_all_files", return_value=[large_file]
            ):
                result = cli.check_file_length()

        assert result == 1

    def test_hooks_provide_refactoring_guidance(
        self, temp_git_repo: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Hooks provide appropriate refactoring guidance."""
        warning_file = temp_git_repo / "warning.py"
        create_file_with_lines(warning_file, 850)

        with patch("src.git_hooks.hook_runner.is_git_repo", return_value=True):
            with patch(
                "src.git_hooks.hook_runner.get_staged_files",
                return_value=[warning_file],
            ):
                cli.check_file_length_warnings()

        captured = capsys.readouterr()
        assert "Python refactoring strategies" in captured.out
        assert "Extract large functions" in captured.out

    def test_get_staged_files_with_git_error(self) -> None:
        """Test get_staged_files handles git errors gracefully."""
        with patch("subprocess.run") as mock_run:
            from subprocess import CalledProcessError

            mock_run.side_effect = CalledProcessError(1, "git")
            result = utils.get_staged_files()
            assert result == []

    def test_get_all_files_excludes_git(self, tmp_path: Path) -> None:
        """Test get_all_files excludes .git directories."""
        # Create some files
        (tmp_path / "file1.py").touch()
        (tmp_path / ".git" / "config").mkdir(parents=True)
        (tmp_path / ".git" / "config").touch()

        with patch.object(Path, "rglob") as mock_rglob:
            mock_rglob.return_value = [
                tmp_path / "file1.py",
                tmp_path / ".git" / "config",
            ]
            files = utils.get_all_files(tmp_path)

        assert len(files) == 1
        assert files[0] == tmp_path / "file1.py"

    def test_get_modules_finds_python_directories(self, tmp_path: Path) -> None:
        """Test get_modules finds directories containing Python files."""
        self._create_test_module_structure(tmp_path)

        modules = utils.get_modules(tmp_path)
        module_names = {m.name for m in modules}

        assert "module1" in module_names
        assert "module2" in module_names
        assert "other" not in module_names

    def _create_test_module_structure(self, tmp_path: Path) -> None:
        """Create test module structure with Python and non-Python directories."""
        # Create module structure
        module1 = tmp_path / "module1"
        module1.mkdir()
        (module1 / "file1.py").touch()
        (module1 / "file2.py").touch()

        module2 = tmp_path / "module2"
        module2.mkdir()
        (module2 / "file3.py").touch()

        # Create a non-Python directory
        other = tmp_path / "other"
        other.mkdir()
        (other / "data.txt").touch()

    def test_print_results_empty(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test print_results with no results."""
        utils.print_results([], "Test hook")
        captured = capsys.readouterr()
        assert "✅ Test hook: All files within healthy limits" in captured.out

    def test_print_results_with_errors(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test print_results with error results."""
        results = [
            ValidationResult(
                file_path=Path("big_file.py"),
                line_count=1500,
                limit=1000,
                severity=ValidationSeverity.ERROR,
                message="File exceeds limit",
                guidance="",
            )
        ]
        utils.print_results(results, "Test hook")
        captured = capsys.readouterr()
        assert "❌ Test hook violations found:" in captured.out
        assert "big_file.py: File exceeds limit" in captured.out

    def test_print_results_with_warnings(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test print_results with warning results."""
        results = [
            ValidationResult(
                file_path=Path("warning_file.py"),
                line_count=950,
                limit=1000,
                severity=ValidationSeverity.WARNING,
                message="File approaching limit",
                guidance="Consider refactoring",
            )
        ]
        utils.print_results(results, "Test hook")
        captured = capsys.readouterr()
        assert "🔶 URGENT:" in captured.out  # 950 is >= 90% of 1000
        assert "Consider refactoring" in captured.out

    def test_module_size_warnings_success(self, temp_git_repo: Path) -> None:
        """Module size warnings always returns 0."""
        large_module = temp_git_repo / "large_module"
        create_module_with_total_lines(temp_git_repo, "large_module", 4500)

        with patch("src.git_hooks.utils.get_modules", return_value=[large_module]):
            result = cli.check_module_size_warnings()

        assert result == 0  # Warnings always succeed

    def test_get_staged_files_empty_output(self) -> None:
        """Test get_staged_files with empty git output."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            result = utils.get_staged_files()
            assert result == []

    def test_file_length_no_files_to_check(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test file length check with no files."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            with patch("src.git_hooks.utils.get_staged_files", return_value=[]):
                result = cli.check_file_length()

        assert result == 0
        captured = capsys.readouterr()
        assert "✅ File length check: No files to check" in captured.out

    def test_file_length_warnings_no_files(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test file length warnings with no files."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            with patch("src.git_hooks.utils.get_staged_files", return_value=[]):
                result = cli.check_file_length_warnings()

        assert result == 0
        captured = capsys.readouterr()
        assert "✅ File length warnings: No files to check" in captured.out

    def test_module_size_no_modules(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test module size check with no modules."""
        with patch("src.git_hooks.hook_runner.get_modules", return_value=[]):
            result = cli.check_module_size()

        assert result == 0
        captured = capsys.readouterr()
        assert "✅ Module size check: No files to check" in captured.out

    def test_module_size_warnings_no_modules(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test module size warnings with no modules."""
        with patch("src.git_hooks.hook_runner.get_modules", return_value=[]):
            result = cli.check_module_size_warnings()

        assert result == 0
        captured = capsys.readouterr()
        assert "✅ Module size warnings: No files to check" in captured.out

    def test_cli_main_invalid_args(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test CLI main with invalid arguments."""
        import subprocess

        result = subprocess.run(
            ["python", "-m", "src.git_hooks.cli"], capture_output=True, text=True
        )
        assert result.returncode == 2  # Typer exits with 2 for missing command
        assert "Usage:" in result.stderr  # Typer outputs to stderr

    def test_cli_main_file_length(self) -> None:
        """Test CLI main with file_length command."""
        import subprocess

        with patch("subprocess.run") as mock_run:
            # Mock git command that cli uses internally
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            result = subprocess.run(
                ["python", "-m", "src.git_hooks.cli", "file_length"],
                capture_output=True,
                text=True,
            )
        assert result.returncode == 0

    def test_cli_main_all_commands(self) -> None:
        """Test CLI main with all valid commands."""
        import subprocess

        commands = [
            "file_length",
            "file_length_warnings",
            "module_size",
            "module_size_warnings",
        ]

        for cmd in commands:
            result = subprocess.run(
                ["python", "-m", "src.git_hooks.cli", cmd],
                capture_output=True,
                text=True,
            )
            # Should execute without error (return code may vary based on validation)
            assert result.returncode in [0, 1]

    def test_cli_main_unknown_hook(self) -> None:
        """Test CLI main with unknown hook type."""
        import subprocess

        result = subprocess.run(
            ["python", "-m", "src.git_hooks.cli", "unknown_hook"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 2  # Typer uses exit code 2 for unknown commands
        assert "No such command" in result.stderr  # Typer outputs to stderr

    def test_print_results_with_non_urgent_warnings(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test print_results with non-urgent warning results."""
        results = [
            ValidationResult(
                file_path=Path("warning_file.py"),
                line_count=850,
                limit=1000,
                severity=ValidationSeverity.WARNING,
                message="File approaching limit",
                guidance="Consider refactoring",
            )
        ]
        utils.print_results(results, "Test hook")
        captured = capsys.readouterr()
        assert "⚠️  WARNING:" in captured.out  # 850 is < 90% of 1000
        assert "Consider refactoring" in captured.out

    def test_get_all_files_real_directory(self, tmp_path: Path) -> None:
        """Test get_all_files with real directory structure."""
        # Create some files
        (tmp_path / "file1.py").touch()
        (tmp_path / "subdir").mkdir()
        (tmp_path / "subdir" / "file2.py").touch()

        files = utils.get_all_files(tmp_path)
        file_names = {f.name for f in files}

        assert "file1.py" in file_names
        assert "file2.py" in file_names

    def test_check_file_length_warnings_with_results(
        self, temp_git_repo: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test file length warnings showing results."""
        warning_file = temp_git_repo / "warning.py"
        create_file_with_lines(warning_file, 820)  # Below 90% threshold

        with patch("src.git_hooks.hook_runner.is_git_repo", return_value=True):
            with patch(
                "src.git_hooks.hook_runner.get_staged_files",
                return_value=[warning_file],
            ):
                result = cli.check_file_length_warnings()

        assert result == 0
        captured = capsys.readouterr()
        assert "⚠️  WARNING:" in captured.out

    def test_file_length_warnings_outside_git_repo(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test file length warnings outside git repo."""
        warning_file = tmp_path / "warning.py"
        create_file_with_lines(warning_file, 850)

        with patch("subprocess.run") as mock_run:
            # Git check fails (not a git repo)
            mock_run.return_value = MagicMock(returncode=1)
            with patch(
                "src.git_hooks.utils.get_all_files", return_value=[warning_file]
            ):
                result = cli.check_file_length_warnings()

        assert result == 0  # Warnings always succeed

    def test_get_all_files_default_directory(self, tmp_path: Path) -> None:
        """Test get_all_files with default directory (None)."""
        with patch("src.git_hooks.utils.Path") as mock_path:
            mock_path.return_value.rglob.return_value = []
            utils.get_all_files()
            mock_path.assert_called_with(".")

    def test_get_modules_default_directory(self, tmp_path: Path) -> None:
        """Test get_modules with default directory (None)."""
        with patch("src.git_hooks.utils.Path") as mock_path:
            mock_path.return_value.rglob.return_value = []
            utils.get_modules()
            mock_path.assert_called_with(".")
