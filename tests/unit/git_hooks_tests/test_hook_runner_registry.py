"""Tests for hook runner with validator registry."""

from pathlib import Path
from typing import Any, Dict, Optional
from unittest.mock import patch

import pytest

from git_hooks.config import ValidationConfig
from git_hooks.core import ValidationResult, Validator
from git_hooks.hook_runner import HookConfig, HookRunner
from git_hooks.validator_registry import ValidatorNotFoundError, ValidatorRegistry


class MockRegistryValidator(Validator):
    """Mock validator for registry testing."""

    def __init__(self, limit: int, **kwargs: Any) -> None:
        super().__init__(limit)
        self.config: Dict[str, Any] = kwargs

    def validate(self, path: Path) -> Optional[ValidationResult]:
        return None


class TestHookRunnerWithRegistry:
    """Test hook runner integration with validator registry."""

    def setup_method(self) -> None:
        """Setup for each test."""
        # Import actual validators to trigger registration FIRST
        from git_hooks import (  # noqa: F401
            file_validator,
            function_validator,
            module_validator,
        )

        # Then add our mock validator
        ValidatorRegistry.register("mock_validator", MockRegistryValidator)

    def teardown_method(self) -> None:
        """Cleanup after each test."""
        # Only remove the mock validator, keep the real validators
        ValidatorRegistry.unregister("mock_validator")

    def test_creates_validator_from_registry(self) -> None:
        """Should create validator using registry instead of factory function."""
        assert ValidatorRegistry.is_registered(
            "file_length"
        ), "file_length validator should be registered"

        config = ValidationConfig()
        runner = HookRunner(config)
        hook_config = HookConfig(
            name="Test hook",
            validator_type="file_length",  # Use existing validator type
            discovery_method="files",
        )

        with patch("git_hooks.hook_runner.get_staged_files", return_value=[]):
            with patch("git_hooks.hook_runner.is_git_repo", return_value=True):
                result = runner.run_hook(hook_config)

        assert result == 0

    def test_unknown_validator_raises_error(self) -> None:
        """Should raise error for unknown validator type."""
        config = ValidationConfig()
        # Mock get_validator_config to avoid the config error and test registry error
        with patch.object(config, "get_validator_config") as mock_get_config:
            mock_get_config.return_value = {"limit": 100}

            runner = HookRunner(config)
            hook_config = HookConfig(
                name="Test hook",
                validator_type="unknown_validator",
                discovery_method="files",
            )

            with pytest.raises(ValidatorNotFoundError):
                runner.run_hook(hook_config)

    def test_passes_configuration_to_validator(self) -> None:
        """Should pass validator configuration through to registry."""
        config = ValidationConfig()
        runner = HookRunner(config)
        hook_config = HookConfig(
            name="Test hook", validator_type="file_length", discovery_method="files"
        )

        with patch("git_hooks.hook_runner.get_staged_files", return_value=[]):
            with patch("git_hooks.hook_runner.is_git_repo", return_value=True):
                with patch.object(ValidatorRegistry, "create") as mock_create:
                    mock_create.return_value = MockRegistryValidator(1000)
                    runner.run_hook(hook_config)

                    # Verify that registry create was called with file_length config
                    args, _ = mock_create.call_args
                    assert args[0] == "file_length"
                    assert "limit" in args[1]
                    assert "warn_threshold" in args[1]
                    assert "urgent_threshold" in args[1]
                    assert "exclude_patterns" in args[1]
