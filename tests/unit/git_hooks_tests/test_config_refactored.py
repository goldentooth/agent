"""Tests for refactored config functionality."""

import os
from unittest.mock import patch

from pytest import MonkeyPatch

from git_hooks.config import ValidationConfig


class TestConfigRefactored:
    """Test the refactored config methods."""

    def test_load_file_length_config(self) -> None:
        """Test loading file length configuration."""
        with patch.dict(
            os.environ,
            {
                "FILE_LENGTH_LIMIT": "500",
                "FILE_LENGTH_WARN_THRESHOLD": "400",
                "FILE_LENGTH_URGENT_THRESHOLD": "450",
            },
        ):
            config = ValidationConfig.from_environment()
            assert config.file_length_limit == 500
            assert config.file_length_warn_threshold == 400
            assert config.file_length_urgent_threshold == 450

    def test_load_module_size_config(self) -> None:
        """Test loading module size configuration."""
        with patch.dict(
            os.environ,
            {
                "MODULE_SIZE_LIMIT": "3000",
                "MODULE_SIZE_WARN_THRESHOLD": "2400",
                "MODULE_SIZE_URGENT_THRESHOLD": "2700",
            },
        ):
            config = ValidationConfig.from_environment()
            assert config.module_size_limit == 3000
            assert config.module_size_warn_threshold == 2400
            assert config.module_size_urgent_threshold == 2700

    def test_load_function_length_config(self) -> None:
        """Test loading function length configuration."""
        with patch.dict(
            os.environ,
            {
                "FUNCTION_LENGTH_LIMIT": "20",
                "FUNCTION_LENGTH_WARN_THRESHOLD": "16",
                "FUNCTION_LENGTH_URGENT_THRESHOLD": "17",
            },
        ):
            config = ValidationConfig.from_environment()
            assert config.function_length_limit == 20
            assert config.function_length_warn_threshold == 16
            assert config.function_length_urgent_threshold == 17

    def test_from_environment_uses_refactored_methods(
        self, monkeypatch: MonkeyPatch
    ) -> None:
        """Test that from_environment uses the new refactored methods."""
        # Clear environment
        for key in ["FILE_LENGTH_LIMIT", "MODULE_SIZE_LIMIT", "FUNCTION_LENGTH_LIMIT"]:
            monkeypatch.delenv(key, raising=False)

        config = ValidationConfig.from_environment()

        # Should use defaults
        assert config.file_length_limit == 1000
        assert config.module_size_limit == 5000
        assert config.function_length_limit == 15
