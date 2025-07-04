"""Centralized configuration management for git hooks validation."""

import os
from dataclasses import dataclass
from typing import Any, Dict

from .core import ThresholdCalculator


@dataclass
class ValidationConfig:
    """Centralized configuration for all validators."""

    # Environment variable constants
    FILE_LENGTH_LIMIT_KEY = "FILE_LENGTH_LIMIT"
    FILE_LENGTH_WARN_THRESHOLD_KEY = "FILE_LENGTH_WARN_THRESHOLD"
    FILE_LENGTH_URGENT_THRESHOLD_KEY = "FILE_LENGTH_URGENT_THRESHOLD"

    MODULE_SIZE_LIMIT_KEY = "MODULE_SIZE_LIMIT"
    MODULE_SIZE_WARN_THRESHOLD_KEY = "MODULE_SIZE_WARN_THRESHOLD"
    MODULE_SIZE_URGENT_THRESHOLD_KEY = "MODULE_SIZE_URGENT_THRESHOLD"

    FUNCTION_LENGTH_LIMIT_KEY = "FUNCTION_LENGTH_LIMIT"
    FUNCTION_LENGTH_WARN_THRESHOLD_KEY = "FUNCTION_LENGTH_WARN_THRESHOLD"
    FUNCTION_LENGTH_URGENT_THRESHOLD_KEY = "FUNCTION_LENGTH_URGENT_THRESHOLD"

    # File length configuration
    file_length_limit: int = 1000
    file_length_warn_threshold: int = 800
    file_length_urgent_threshold: int = 900

    # Module size configuration
    module_size_limit: int = 5000
    module_size_warn_threshold: int = 4000
    module_size_urgent_threshold: int = 4500

    # Function length configuration
    function_length_limit: int = 15
    function_length_warn_threshold: int = 12
    function_length_urgent_threshold: int = 13

    @classmethod
    def _load_file_length_config(cls) -> Dict[str, int]:
        """Load file length configuration from environment."""
        calc = ThresholdCalculator(warn_multiplier=0.8, urgent_multiplier=0.9)
        return cls._load_config_values(
            cls.FILE_LENGTH_LIMIT_KEY,
            "1000",
            cls.FILE_LENGTH_WARN_THRESHOLD_KEY,
            cls.FILE_LENGTH_URGENT_THRESHOLD_KEY,
            calc,
            "file_length",
        )

    @classmethod
    def _load_module_size_config(cls) -> Dict[str, int]:
        """Load module size configuration from environment."""
        calc = ThresholdCalculator(warn_multiplier=0.8, urgent_multiplier=0.9)
        return cls._load_config_values(
            cls.MODULE_SIZE_LIMIT_KEY,
            "5000",
            cls.MODULE_SIZE_WARN_THRESHOLD_KEY,
            cls.MODULE_SIZE_URGENT_THRESHOLD_KEY,
            calc,
            "module_size",
        )

    @classmethod
    def _load_function_length_config(cls) -> Dict[str, int]:
        """Load function length configuration from environment."""
        calc = ThresholdCalculator(warn_multiplier=0.8, urgent_multiplier=0.87)
        return cls._load_config_values(
            cls.FUNCTION_LENGTH_LIMIT_KEY,
            "15",
            cls.FUNCTION_LENGTH_WARN_THRESHOLD_KEY,
            cls.FUNCTION_LENGTH_URGENT_THRESHOLD_KEY,
            calc,
            "function_length",
        )

    @classmethod
    def _load_config_values(
        cls,
        limit_key: str,
        default_limit: str,
        warn_key: str,
        urgent_key: str,
        calc: ThresholdCalculator,
        prefix: str,
    ) -> Dict[str, int]:
        """Load configuration values from environment."""
        limit = cls._get_limit_from_env(limit_key, default_limit)
        thresholds = cls._get_thresholds_from_env(warn_key, urgent_key, calc, limit)
        return cls._build_config_dict(
            prefix, limit, thresholds["warn"], thresholds["urgent"]
        )

    @classmethod
    def _get_limit_from_env(cls, limit_key: str, default_limit: str) -> int:
        """Get limit value from environment."""
        return int(os.environ.get(limit_key, default_limit))

    @classmethod
    def _get_thresholds_from_env(
        cls, warn_key: str, urgent_key: str, calc: ThresholdCalculator, limit: int
    ) -> Dict[str, int]:
        """Get threshold values from environment."""
        warn_threshold = cls._load_threshold_value(
            warn_key, calc.calculate_warn_threshold(limit)
        )
        urgent_threshold = cls._load_threshold_value(
            urgent_key, calc.calculate_urgent_threshold(limit)
        )
        return {"warn": warn_threshold, "urgent": urgent_threshold}

    @classmethod
    def _load_threshold_value(cls, key: str, default_value: int) -> int:
        """Load threshold value from environment with fallback."""
        return int(os.environ.get(key, str(default_value)))

    @classmethod
    def _build_config_dict(
        cls, prefix: str, limit: int, warn_threshold: int, urgent_threshold: int
    ) -> Dict[str, int]:
        """Build configuration dictionary with proper keys."""
        return {
            f"{prefix}_limit": limit,
            f"{prefix}_warn_threshold": warn_threshold,
            f"{prefix}_urgent_threshold": urgent_threshold,
        }

    @classmethod
    def from_environment(cls) -> "ValidationConfig":
        """Load configuration from environment variables with defaults."""
        file_config = cls._load_file_length_config()
        module_config = cls._load_module_size_config()
        function_config = cls._load_function_length_config()

        return cls(**file_config, **module_config, **function_config)

    def _get_file_length_config(self) -> Dict[str, Any]:
        """Get file length validator configuration."""
        return {
            "limit": self.file_length_limit,
            "warn_threshold": self.file_length_warn_threshold,
            "urgent_threshold": self.file_length_urgent_threshold,
        }

    def _get_module_size_config(self) -> Dict[str, Any]:
        """Get module size validator configuration."""
        return {
            "limit": self.module_size_limit,
            "warn_threshold": self.module_size_warn_threshold,
            "urgent_threshold": self.module_size_urgent_threshold,
        }

    def _get_function_length_config(self) -> Dict[str, Any]:
        """Get function length validator configuration."""
        return {
            "limit": self.function_length_limit,
            "warn_threshold": self.function_length_warn_threshold,
            "urgent_threshold": self.function_length_urgent_threshold,
        }

    def get_validator_config(self, validator_type: str) -> Dict[str, Any]:
        """Get configuration for a specific validator type."""
        config_methods = {
            "file_length": self._get_file_length_config,
            "module_size": self._get_module_size_config,
            "function_length": self._get_function_length_config,
        }

        if validator_type not in config_methods:
            raise ValueError(f"Unknown validator type: {validator_type}")

        return config_methods[validator_type]()
