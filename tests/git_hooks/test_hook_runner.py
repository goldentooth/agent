"""Tests for generic hook runner."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from src.git_hooks.config import ValidationConfig
from src.git_hooks.core import ValidationResult, ValidationSeverity
from src.git_hooks.hook_runner import HookConfig, HookRunner


class TestHookRunner:
    """Test generic hook runner functionality."""

    def test_run_hook_no_files_returns_success(self) -> None:
        """Should return 0 when no files are found."""
        config = ValidationConfig()
        hook_config = HookConfig(
            name="test_hook", validator_type="file_length", discovery_method="files"
        )

        runner = HookRunner(config)

        with patch("src.git_hooks.hook_runner.get_staged_files", return_value=[]):
            with patch("src.git_hooks.hook_runner.get_all_files", return_value=[]):
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
                "src.git_hooks.hook_runner.get_staged_files", return_value=[test_file]
            ):
                with patch(
                    "src.git_hooks.hook_runner.create_validator",
                    return_value=mock_validator,
                ):
                    with patch(
                        "src.git_hooks.hook_runner.is_git_repo", return_value=True
                    ):
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
                "src.git_hooks.hook_runner.get_staged_files", return_value=[test_file]
            ):
                with patch(
                    "src.git_hooks.hook_runner.create_validator",
                    return_value=mock_validator,
                ):
                    with patch(
                        "src.git_hooks.hook_runner.is_git_repo", return_value=True
                    ):
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
                "src.git_hooks.hook_runner.get_staged_files", return_value=[test_file]
            ):
                with patch(
                    "src.git_hooks.hook_runner.create_validator",
                    return_value=mock_validator,
                ):
                    with patch(
                        "src.git_hooks.hook_runner.is_git_repo", return_value=True
                    ):
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
            "src.git_hooks.hook_runner.get_modules", return_value=[]
        ) as mock_get_modules:
            with patch("src.git_hooks.hook_runner.is_git_repo", return_value=False):
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
        with patch("src.git_hooks.hook_runner.is_git_repo", return_value=True):
            with patch(
                "src.git_hooks.hook_runner.get_staged_files", return_value=[]
            ) as mock_staged:
                with patch("src.git_hooks.hook_runner.get_all_files") as mock_all:
                    runner.run_hook(hook_config, warning_mode=False)
                    mock_staged.assert_called_once()
                    mock_all.assert_not_called()

        # Test non-git context
        with patch("src.git_hooks.hook_runner.is_git_repo", return_value=False):
            with patch("src.git_hooks.hook_runner.get_staged_files") as mock_staged:
                with patch(
                    "src.git_hooks.hook_runner.get_all_files", return_value=[]
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
                "src.git_hooks.hook_runner.get_staged_files", return_value=[test_file]
            ):
                with patch(
                    "src.git_hooks.hook_runner.create_validator",
                    return_value=mock_validator,
                ):
                    with patch(
                        "src.git_hooks.hook_runner.is_git_repo", return_value=True
                    ):
                        result = runner.run_hook(hook_config, warning_mode=False)
                        assert result == 0  # Warning doesn't fail in blocking mode
