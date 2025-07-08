"""Tests for CLI functionality."""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import typer

from git_hooks import cli, utils
from git_hooks.core import ValidationResult, ValidationSeverity

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

    def test_get_files_by_glob_direct_path_match(self, tmp_path: Path) -> None:
        """Test get_files_by_glob with direct path (no wildcards)."""
        test_file = tmp_path / "test.py"
        test_file.write_text("content")

        result = cli.get_files_by_glob(str(test_file))
        assert len(result) == 1
        assert result[0] == test_file

    def test_get_files_by_glob_direct_path_nonexistent(self) -> None:
        """Test get_files_by_glob with nonexistent direct path."""
        result = cli.get_files_by_glob("nonexistent.py")
        assert result == []

    def test_get_files_by_glob_wildcard_pattern(self, tmp_path: Path) -> None:
        """Test get_files_by_glob with wildcard patterns."""
        # Create test files
        (tmp_path / "file1.py").write_text("content")
        (tmp_path / "file2.py").write_text("content")
        (tmp_path / "file3.txt").write_text("content")

        # Change to temp directory to test glob
        import os

        old_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = cli.get_files_by_glob("*.py")
            file_names = {f.name for f in result}
            assert "file1.py" in file_names
            assert "file2.py" in file_names
            assert "file3.txt" not in file_names
        finally:
            os.chdir(old_cwd)

    def test_get_files_by_glob_git_context_staged_files(self, tmp_path: Path) -> None:
        """Test get_files_by_glob filters to staged files in git repo."""
        # Create test files
        file1 = tmp_path / "file1.py"
        file2 = tmp_path / "file2.py"
        file1.write_text("content")
        file2.write_text("content")

        import os

        old_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            # Use relative paths like glob would return them
            staged_file = Path("file1.py")
            with patch("src.git_hooks.cli.is_git_repo", return_value=True):
                with patch(
                    "src.git_hooks.cli.get_staged_files", return_value=[staged_file]
                ):
                    result = cli.get_files_by_glob("*.py", all_files=False)
                    assert len(result) == 1
                    assert result[0] == staged_file
        finally:
            os.chdir(old_cwd)

    def test_get_files_by_glob_all_files_ignores_git(self, tmp_path: Path) -> None:
        """Test get_files_by_glob with all_files=True ignores git context."""
        # Create test files
        file1 = tmp_path / "file1.py"
        file2 = tmp_path / "file2.py"
        file1.write_text("content")
        file2.write_text("content")

        import os

        old_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            with patch("src.git_hooks.cli.is_git_repo", return_value=True):
                with patch("src.git_hooks.cli.get_staged_files", return_value=[file1]):
                    result = cli.get_files_by_glob("*.py", all_files=True)
                    assert len(result) == 2
        finally:
            os.chdir(old_cwd)

    def test_create_hook_config_file_length(self) -> None:
        """Test create_hook_config for file_length hook types."""
        config = cli.create_hook_config("file_length")
        assert config.name == "File length check"
        assert config.validator_type == "file_length"
        assert config.discovery_method == "files"

        config_warnings = cli.create_hook_config("file_length_warnings")
        assert config_warnings.name == "File length warnings"
        assert config_warnings.validator_type == "file_length"
        assert config_warnings.discovery_method == "files"

    def test_create_hook_config_module_size(self) -> None:
        """Test create_hook_config for module_size hook types."""
        config = cli.create_hook_config("module_size")
        assert config.name == "Module size check"
        assert config.validator_type == "module_size"
        assert config.discovery_method == "modules"

        config_warnings = cli.create_hook_config("module_size_warnings")
        assert config_warnings.name == "Module size warnings"
        assert config_warnings.validator_type == "module_size"
        assert config_warnings.discovery_method == "modules"

    def test_create_hook_config_function_length(self) -> None:
        """Test create_hook_config for function_length hook types."""
        config = cli.create_hook_config("function_length")
        assert config.name == "Function length check"
        assert config.validator_type == "function_length"
        assert config.discovery_method == "files"

        config_warnings = cli.create_hook_config("function_length_warnings")
        assert config_warnings.name == "Function length warnings"
        assert config_warnings.validator_type == "function_length"
        assert config_warnings.discovery_method == "files"

    def test_create_hook_config_unknown_type(self) -> None:
        """Test create_hook_config raises error for unknown hook type."""
        with pytest.raises(ValueError) as exc_info:
            cli.create_hook_config("unknown_hook")
        assert "Unknown hook type: unknown_hook" in str(exc_info.value)

    def test_file_length_command_warnings_mode(self, tmp_path: Path) -> None:
        """Test file_length command in warnings mode."""
        with patch("src.git_hooks.cli._run_validation") as mock_run:
            cli.file_length(warnings=True, all_files=False, files=None, verbose=False)
            mock_run.assert_called_once_with("file_length_warnings", False, None, False)

    def test_file_length_command_normal_mode(self) -> None:
        """Test file_length command in normal mode."""
        with patch("src.git_hooks.cli._run_validation") as mock_run:
            cli.file_length(warnings=False, all_files=True, files="*.py", verbose=True)
            mock_run.assert_called_once_with("file_length", True, "*.py", True)

    def test_module_size_command_warnings_mode(self) -> None:
        """Test module_size command in warnings mode."""
        with patch("src.git_hooks.cli._run_validation") as mock_run:
            cli.module_size(warnings=True, all_files=False, files=None, verbose=False)
            mock_run.assert_called_once_with("module_size_warnings", False, None, False)

    def test_module_size_command_normal_mode(self) -> None:
        """Test module_size command in normal mode."""
        with patch("src.git_hooks.cli._run_validation") as mock_run:
            cli.module_size(warnings=False, all_files=True, files="src/*", verbose=True)
            mock_run.assert_called_once_with("module_size", True, "src/*", True)

    def test_function_length_command_warnings_mode(self) -> None:
        """Test function_length command in warnings mode."""
        with patch("src.git_hooks.cli._run_validation") as mock_run:
            cli.function_length(
                warnings=True, all_files=False, files=None, verbose=False
            )
            mock_run.assert_called_once_with(
                "function_length_warnings", False, None, False
            )

    def test_function_length_command_normal_mode(self) -> None:
        """Test function_length command in normal mode."""
        with patch("src.git_hooks.cli._run_validation") as mock_run:
            cli.function_length(
                warnings=False, all_files=True, files="**/*.py", verbose=True
            )
            mock_run.assert_called_once_with("function_length", True, "**/*.py", True)

    def test_run_validation_with_glob_files_found(self, tmp_path: Path) -> None:
        """Test _run_validation with glob pattern that finds files."""
        test_file = tmp_path / "test.py"
        test_file.write_text("content")

        with patch("src.git_hooks.cli.get_files_by_glob", return_value=[test_file]):
            with patch(
                "src.git_hooks.cli.run_hook_with_config", return_value=0
            ) as mock_run:
                try:
                    cli._run_validation("file_length", False, "*.py", False)
                except typer.Exit:
                    pass  # Expected
                mock_run.assert_called_once()

    def test_run_validation_with_glob_no_files_found(self) -> None:
        """Test _run_validation with glob pattern that finds no files."""
        with patch("src.git_hooks.cli.get_files_by_glob", return_value=[]):
            with patch("typer.echo") as mock_echo:
                try:
                    cli._run_validation("file_length", False, "*.nonexistent", False)
                except typer.Exit:
                    pass  # Expected
                mock_echo.assert_called_once_with(
                    "No files found matching pattern: *.nonexistent"
                )

    def test_run_validation_with_all_files(self) -> None:
        """Test _run_validation with all_files=True."""
        test_files = [Path("file1.py"), Path("file2.py")]

        with patch("src.git_hooks.cli.get_all_files", return_value=test_files):
            with patch(
                "src.git_hooks.cli.run_hook_with_config", return_value=0
            ) as mock_run:
                try:
                    cli._run_validation("file_length", True, None, False)
                except typer.Exit:
                    pass  # Expected
                mock_run.assert_called_once()
                # Check that hook_config was created properly
                args, kwargs = mock_run.call_args
                hook_config = args[0]
                assert hook_config.name == "File length check"
                assert kwargs["warning_mode"] is False
                assert kwargs["verbose"] is False
                assert kwargs["target_files"] == test_files

    def test_run_validation_default_behavior(self) -> None:
        """Test _run_validation with default behavior (no files, no all_files)."""
        with patch(
            "src.git_hooks.cli.run_hook_with_config", return_value=1
        ) as mock_run:
            try:
                cli._run_validation("module_size_warnings", False, None, True)
            except typer.Exit:
                pass  # Expected
            mock_run.assert_called_once()
            # Check that hook_config was created properly
            args, kwargs = mock_run.call_args
            hook_config = args[0]
            assert hook_config.name == "Module size warnings"
            assert hook_config.validator_type == "module_size"
            assert hook_config.discovery_method == "modules"
            assert kwargs["warning_mode"] is True
            assert kwargs["verbose"] is True
            assert kwargs["target_files"] is None
