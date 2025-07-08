"""Tests for centralized configuration management."""

import os
from unittest.mock import patch

from git_hooks.config import ValidationConfig


class TestValidationConfig:
    """Test centralized configuration management."""

    def test_default_configuration(self) -> None:
        """Should provide sensible defaults for all validators."""
        config = ValidationConfig()

        assert config.file_length_limit == 1000
        assert config.file_length_warn_threshold == 800
        assert config.file_length_urgent_threshold == 900

        assert config.module_size_limit == 5000
        assert config.module_size_warn_threshold == 4000
        assert config.module_size_urgent_threshold == 4500

        assert config.function_length_limit == 15
        assert config.function_length_warn_threshold == 12
        assert config.function_length_urgent_threshold == 13

    def test_from_environment_loads_custom_values(self) -> None:
        """Should load configuration from environment variables."""
        env_vars = {
            "FILE_LENGTH_LIMIT": "500",
            "FILE_LENGTH_WARN_THRESHOLD": "400",
            "MODULE_SIZE_LIMIT": "3000",
            "FUNCTION_LENGTH_LIMIT": "10",
        }

        with patch.dict(os.environ, env_vars):
            config = ValidationConfig.from_environment()

            assert config.file_length_limit == 500
            assert config.file_length_warn_threshold == 400
            assert config.module_size_limit == 3000
            assert config.function_length_limit == 10

    def test_from_environment_uses_defaults_for_missing_vars(self) -> None:
        """Should use defaults when environment variables are missing."""
        # Ensure no relevant env vars are set
        with patch.dict(os.environ, {}, clear=True):
            config = ValidationConfig.from_environment()

            assert config.file_length_limit == 1000
            assert config.function_length_limit == 15

    def test_calculated_thresholds_when_not_provided(self) -> None:
        """Should calculate thresholds when not explicitly provided."""
        env_vars = {
            "FILE_LENGTH_LIMIT": "1000",
            # No threshold values provided
        }

        with patch.dict(os.environ, env_vars):
            config = ValidationConfig.from_environment()

            # Should calculate 80% and 90% thresholds
            assert config.file_length_warn_threshold == 800
            assert config.file_length_urgent_threshold == 900

    def test_environment_variable_constants(self) -> None:
        """Should define constants for all environment variable names."""
        # These should exist as class constants
        assert hasattr(ValidationConfig, "FILE_LENGTH_LIMIT_KEY")
        assert hasattr(ValidationConfig, "MODULE_SIZE_LIMIT_KEY")
        assert hasattr(ValidationConfig, "FUNCTION_LENGTH_LIMIT_KEY")

        assert ValidationConfig.FILE_LENGTH_LIMIT_KEY == "FILE_LENGTH_LIMIT"
        assert ValidationConfig.MODULE_SIZE_LIMIT_KEY == "MODULE_SIZE_LIMIT"
        assert ValidationConfig.FUNCTION_LENGTH_LIMIT_KEY == "FUNCTION_LENGTH_LIMIT"

    def test_get_validator_config_file_length(self) -> None:
        """Should provide validator-specific configuration."""
        config = ValidationConfig(
            file_length_limit=1200,
            file_length_warn_threshold=960,
            file_length_urgent_threshold=1080,
        )

        validator_config = config.get_validator_config("file_length")

        assert validator_config["limit"] == 1200
        assert validator_config["warn_threshold"] == 960
        assert validator_config["urgent_threshold"] == 1080

    def test_get_validator_config_unknown_validator(self) -> None:
        """Should raise error for unknown validator types."""
        config = ValidationConfig()

        try:
            config.get_validator_config("unknown_validator")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "unknown_validator" in str(e)
