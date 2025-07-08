"""Tests for generic hook runner."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from git_hooks.config import ValidationConfig
from git_hooks.core import ValidationResult, ValidationSeverity
from git_hooks.hook_runner import HookConfig, HookRunner


class TestHookRunner:
    """Test generic hook runner functionality."""

    def test_run_hook_no_files_returns_success(self) -> None:
        """Should return 0 when no files are found."""
        config = ValidationConfig()
        hook_config = HookConfig(
            name="test_hook", validator_type="file_length", discovery_method="files"
        )

        runner = HookRunner(config)

        with patch("git_hooks.hook_runner.get_staged_files", return_value=[]):
            with patch("git_hooks.hook_runner.get_all_files", return_value=[]):
                result = runner.run_hook(hook_config, warning_mode=False)
                assert result == 0

    def test_run_hook_with_valid_files_returns_success(self) -> None:
        """Should return 0 when all files pass validation."""
        config = ValidationConfig()
        hook_config = HookConfig(
            name="test_hook", validator_type="file_length", discovery_method="files"
        )

        # Mock validator that always passes
        mock_validator = Mock()
        mock_validator.validate.return_value = None

        runner = HookRunner(config)

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("short content")

            with patch(
                "git_hooks.hook_runner.get_staged_files", return_value=[test_file]
            ):
                with patch(
                    "git_hooks.hook_runner.create_validator",
                    return_value=mock_validator,
                ):
                    with patch("git_hooks.hook_runner.is_git_repo", return_value=True):
                        result = runner.run_hook(hook_config, warning_mode=False)
                        assert result == 0

    def test_run_hook_with_violations_returns_failure_in_blocking_mode(self) -> None:
        """Should return 1 when violations are found in blocking mode."""
        config = ValidationConfig()
        hook_config = HookConfig(
            name="test_hook", validator_type="file_length", discovery_method="files"
        )

        # Mock validator that returns an error
        mock_validator = Mock()
        mock_validator.validate.return_value = ValidationResult(
            file_path=Path("test.py"),
            severity=ValidationSeverity.ERROR,
            message="Test error",
            line_count=1500,
            limit=1000,
        )

        runner = HookRunner(config)

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("content")

            with patch(
                "git_hooks.hook_runner.get_staged_files", return_value=[test_file]
            ):
                with patch(
                    "git_hooks.hook_runner.create_validator",
                    return_value=mock_validator,
                ):
                    with patch("git_hooks.hook_runner.is_git_repo", return_value=True):
                        result = runner.run_hook(hook_config, warning_mode=False)
                        assert result == 1

    def test_run_hook_with_violations_returns_success_in_warning_mode(self) -> None:
        """Should return 0 even with violations in warning mode."""
        config = ValidationConfig()
        hook_config = HookConfig(
            name="test_hook", validator_type="file_length", discovery_method="files"
        )

        # Mock validator that returns an error
        mock_validator = Mock()
        mock_validator.validate.return_value = ValidationResult(
            file_path=Path("test.py"),
            severity=ValidationSeverity.ERROR,
            message="Test error",
            line_count=1500,
            limit=1000,
        )

        runner = HookRunner(config)

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("content")

            with patch(
                "git_hooks.hook_runner.get_staged_files", return_value=[test_file]
            ):
                with patch(
                    "git_hooks.hook_runner.create_validator",
                    return_value=mock_validator,
                ):
                    with patch("git_hooks.hook_runner.is_git_repo", return_value=True):
                        result = runner.run_hook(hook_config, warning_mode=True)
                        assert result == 0  # Always succeeds in warning mode

    def test_run_hook_uses_modules_discovery_for_module_validators(self) -> None:
        """Should use module discovery for module size validators."""
        config = ValidationConfig()
        hook_config = HookConfig(
            name="test_hook", validator_type="module_size", discovery_method="modules"
        )

        runner = HookRunner(config)

        with patch(
            "git_hooks.hook_runner.get_modules", return_value=[]
        ) as mock_get_modules:
            with patch("git_hooks.hook_runner.is_git_repo", return_value=False):
                runner.run_hook(hook_config, warning_mode=False)
                mock_get_modules.assert_called_once()

    def test_run_hook_respects_git_context(self) -> None:
        """Should use staged files in git repos, all files otherwise."""
        config = ValidationConfig()
        hook_config = HookConfig(
            name="test_hook", validator_type="file_length", discovery_method="files"
        )

        runner = HookRunner(config)

        # Test git repo context
        with patch("git_hooks.hook_runner.is_git_repo", return_value=True):
            with patch(
                "git_hooks.hook_runner.get_staged_files", return_value=[]
            ) as mock_staged:
                with patch("git_hooks.hook_runner.get_all_files") as mock_all:
                    runner.run_hook(hook_config, warning_mode=False)
                    mock_staged.assert_called_once()
                    mock_all.assert_not_called()

        # Test non-git context
        with patch("git_hooks.hook_runner.is_git_repo", return_value=False):
            with patch("git_hooks.hook_runner.get_staged_files") as mock_staged:
                with patch(
                    "git_hooks.hook_runner.get_all_files", return_value=[]
                ) as mock_all:
                    runner.run_hook(hook_config, warning_mode=False)
                    mock_staged.assert_not_called()
                    mock_all.assert_called_once()

    def test_hook_config_creation(self) -> None:
        """Should create HookConfig instances with required fields."""
        hook_config = HookConfig(
            name="test_hook", validator_type="file_length", discovery_method="files"
        )

        assert hook_config.name == "test_hook"
        assert hook_config.validator_type == "file_length"
        assert hook_config.discovery_method == "files"

    def test_hook_runner_filters_results_by_severity_in_blocking_mode(self) -> None:
        """Should only include ERROR results in blocking mode."""
        config = ValidationConfig()
        hook_config = HookConfig(
            name="test_hook", validator_type="file_length", discovery_method="files"
        )

        # Mock validator that returns a warning
        mock_validator = Mock()
        mock_validator.validate.return_value = ValidationResult(
            file_path=Path("test.py"),
            severity=ValidationSeverity.WARNING,
            message="Test warning",
            line_count=800,
            limit=1000,
        )

        runner = HookRunner(config)

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("content")

            with patch(
                "git_hooks.hook_runner.get_staged_files", return_value=[test_file]
            ):
                with patch(
                    "git_hooks.hook_runner.create_validator",
                    return_value=mock_validator,
                ):
                    with patch("git_hooks.hook_runner.is_git_repo", return_value=True):
                        result = runner.run_hook(hook_config, warning_mode=False)
                        assert result == 0  # Warning doesn't fail in blocking mode

    def test_verbose_mode_with_function_statements_validator(self) -> None:
        """Verbose mode should show detailed function statement info."""
        config = ValidationConfig()
        hook_config = HookConfig(
            name="test_hook", validator_type="function_length", discovery_method="files"
        )

        # Mock validator with get_all_function_statements method
        mock_validator = Mock()
        mock_validator.validate.return_value = None
        mock_validator.get_all_function_statements.return_value = [
            ("test_function", 1, 10, 10, 5),  # name, start, end, lines, statements
            ("another_function", 15, 30, 16, 12),
        ]

        runner = HookRunner(config)

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("def test_function(): pass")

            with patch(
                "git_hooks.hook_runner.get_staged_files", return_value=[test_file]
            ):
                with patch(
                    "git_hooks.hook_runner.create_validator",
                    return_value=mock_validator,
                ):
                    with patch("git_hooks.hook_runner.is_git_repo", return_value=True):
                        with patch("builtins.print") as mock_print:
                            result = runner.run_hook(
                                hook_config, warning_mode=False, verbose=True
                            )
                            assert result == 0

                            # Verify verbose output was printed
                            print_calls = [
                                call.args[0] for call in mock_print.call_args_list
                            ]
                            assert any("Checking" in call for call in print_calls)
                            assert any(
                                "Functions found:" in call for call in print_calls
                            )
                            assert any(
                                "test_function: 5 statements" in call
                                for call in print_calls
                            )
                            assert any(
                                "another_function: 12 statements" in call
                                for call in print_calls
                            )

    def test_verbose_mode_with_function_info_validator(self) -> None:
        """Verbose mode should show function info when statement method not available."""
        config = ValidationConfig()
        hook_config = HookConfig(
            name="test_hook", validator_type="file_length", discovery_method="files"
        )

        # Mock validator with get_all_function_info method but not get_all_function_statements
        mock_validator = Mock()
        mock_validator.validate.return_value = None
        mock_validator.get_all_function_info.return_value = [
            ("test_function", 1, 10, 10),  # name, start, end, lines
            ("another_function", 15, 30, 16),
        ]
        # Ensure the method check fails for get_all_function_statements
        del mock_validator.get_all_function_statements

        runner = HookRunner(config)

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("def test_function(): pass")

            with patch(
                "git_hooks.hook_runner.get_staged_files", return_value=[test_file]
            ):
                with patch(
                    "git_hooks.hook_runner.create_validator",
                    return_value=mock_validator,
                ):
                    with patch("git_hooks.hook_runner.is_git_repo", return_value=True):
                        with patch("builtins.print") as mock_print:
                            result = runner.run_hook(
                                hook_config, warning_mode=False, verbose=True
                            )
                            assert result == 0

                            # Verify verbose output was printed
                            print_calls = [
                                call.args[0] for call in mock_print.call_args_list
                            ]
                            assert any("Checking" in call for call in print_calls)
                            assert any(
                                "Functions found:" in call for call in print_calls
                            )
                            assert any(
                                "test_function: 10 lines" in call
                                for call in print_calls
                            )

    def test_verbose_mode_no_functions_found(self) -> None:
        """Verbose mode should show 'No functions found' when list is empty."""
        config = ValidationConfig()
        hook_config = HookConfig(
            name="test_hook", validator_type="function_length", discovery_method="files"
        )

        # Mock validator that returns empty function list
        mock_validator = Mock()
        mock_validator.validate.return_value = None
        mock_validator.get_all_function_statements.return_value = []

        runner = HookRunner(config)

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("# No functions here")

            with patch(
                "git_hooks.hook_runner.get_staged_files", return_value=[test_file]
            ):
                with patch(
                    "git_hooks.hook_runner.create_validator",
                    return_value=mock_validator,
                ):
                    with patch("git_hooks.hook_runner.is_git_repo", return_value=True):
                        with patch("builtins.print") as mock_print:
                            result = runner.run_hook(
                                hook_config, warning_mode=False, verbose=True
                            )
                            assert result == 0

                            # Verify 'No functions found' was printed
                            print_calls = [
                                call.args[0] for call in mock_print.call_args_list
                            ]
                            assert any(
                                "No functions found" in call for call in print_calls
                            )

    def test_verbose_mode_validation_result_message(self) -> None:
        """Verbose mode should show validation result messages."""
        config = ValidationConfig()
        hook_config = HookConfig(
            name="test_hook", validator_type="file_length", discovery_method="files"
        )

        # Mock validator that returns a warning result
        mock_validator = Mock()
        validation_result = ValidationResult(
            file_path=Path("test.py"),
            severity=ValidationSeverity.WARNING,
            message="File is getting large",
            line_count=800,
            limit=1000,
        )
        mock_validator.validate.return_value = validation_result
        # Ensure hasattr checks return False for function methods
        del mock_validator.get_all_function_statements
        del mock_validator.get_all_function_info

        runner = HookRunner(config)

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("content")

            with patch(
                "git_hooks.hook_runner.get_staged_files", return_value=[test_file]
            ):
                with patch(
                    "git_hooks.hook_runner.create_validator",
                    return_value=mock_validator,
                ):
                    with patch("git_hooks.hook_runner.is_git_repo", return_value=True):
                        with patch("builtins.print") as mock_print:
                            result = runner.run_hook(
                                hook_config, warning_mode=True, verbose=True
                            )
                            assert result == 0

                            # Verify result message was printed
                            print_calls = [
                                call.args[0] for call in mock_print.call_args_list
                            ]
                            assert any(
                                "📋 Validation result: File is getting large" in call
                                for call in print_calls
                            )

    def test_verbose_mode_no_validation_issues(self) -> None:
        """Verbose mode should show success message when no issues found."""
        config = ValidationConfig()
        hook_config = HookConfig(
            name="test_hook", validator_type="file_length", discovery_method="files"
        )

        # Mock validator that returns None (no issues)
        mock_validator = Mock()
        mock_validator.validate.return_value = None
        # Ensure hasattr checks return False for function methods
        del mock_validator.get_all_function_statements
        del mock_validator.get_all_function_info

        runner = HookRunner(config)

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("content")

            with patch(
                "git_hooks.hook_runner.get_staged_files", return_value=[test_file]
            ):
                with patch(
                    "git_hooks.hook_runner.create_validator",
                    return_value=mock_validator,
                ):
                    with patch("git_hooks.hook_runner.is_git_repo", return_value=True):
                        with patch("builtins.print") as mock_print:
                            result = runner.run_hook(
                                hook_config, warning_mode=False, verbose=True
                            )
                            assert result == 0

                            # Verify success message was printed
                            print_calls = [
                                call.args[0] for call in mock_print.call_args_list
                            ]
                            assert any(
                                "✅ No validation issues found" in call
                                for call in print_calls
                            )

    def test_unknown_discovery_method_raises_error(self) -> None:
        """Should raise ValueError for unknown discovery methods."""
        config = ValidationConfig()
        hook_config = HookConfig(
            name="test_hook", validator_type="file_length", discovery_method="unknown"
        )

        runner = HookRunner(config)

        with patch("git_hooks.hook_runner.create_validator", return_value=Mock()):
            try:
                runner.run_hook(hook_config, warning_mode=False)
                assert False, "Expected ValueError was not raised"
            except ValueError as e:
                assert "Unknown discovery method: unknown" in str(e)
