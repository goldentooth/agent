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
    def _create_threshold_calculators(cls) -> Dict[str, ThresholdCalculator]:
        """Create threshold calculators for different validator types."""
        return {
            'file_calc': ThresholdCalculator(warn_multiplier=0.8, urgent_multiplier=0.9),
            'module_calc': ThresholdCalculator(warn_multiplier=0.8, urgent_multiplier=0.9),
            'func_calc': ThresholdCalculator(warn_multiplier=0.8, urgent_multiplier=0.87),
        }

    @classmethod
    def _load_file_length_config(cls) -> Dict[str, int]:
        """Load file length configuration from environment."""
        calc = ThresholdCalculator(warn_multiplier=0.8, urgent_multiplier=0.9)
        limit = int(os.environ.get(cls.FILE_LENGTH_LIMIT_KEY, "1000"))
        warn_threshold = int(os.environ.get(
            cls.FILE_LENGTH_WARN_THRESHOLD_KEY,
            str(calc.calculate_warn_threshold(limit))
        ))
        urgent_threshold = int(os.environ.get(
            cls.FILE_LENGTH_URGENT_THRESHOLD_KEY,
            str(calc.calculate_urgent_threshold(limit))
        ))
        return {
            'file_length_limit': limit,
            'file_length_warn_threshold': warn_threshold,
            'file_length_urgent_threshold': urgent_threshold,
        }

    @classmethod
    def _load_module_size_config(cls) -> Dict[str, int]:
        """Load module size configuration from environment."""
        calc = ThresholdCalculator(warn_multiplier=0.8, urgent_multiplier=0.9)
        limit = int(os.environ.get(cls.MODULE_SIZE_LIMIT_KEY, "5000"))
        warn_threshold = int(os.environ.get(
            cls.MODULE_SIZE_WARN_THRESHOLD_KEY,
            str(calc.calculate_warn_threshold(limit))
        ))
        urgent_threshold = int(os.environ.get(
            cls.MODULE_SIZE_URGENT_THRESHOLD_KEY,
            str(calc.calculate_urgent_threshold(limit))
        ))
        return {
            'module_size_limit': limit,
            'module_size_warn_threshold': warn_threshold,
            'module_size_urgent_threshold': urgent_threshold,
        }

    @classmethod
    def _load_function_length_config(cls) -> Dict[str, int]:
        """Load function length configuration from environment."""
        calc = ThresholdCalculator(warn_multiplier=0.8, urgent_multiplier=0.87)
        limit = int(os.environ.get(cls.FUNCTION_LENGTH_LIMIT_KEY, "15"))
        warn_threshold = int(os.environ.get(
            cls.FUNCTION_LENGTH_WARN_THRESHOLD_KEY,
            str(calc.calculate_warn_threshold(limit))
        ))
        urgent_threshold = int(os.environ.get(
            cls.FUNCTION_LENGTH_URGENT_THRESHOLD_KEY,
            str(calc.calculate_urgent_threshold(limit))
        ))
        return {
            'function_length_limit': limit,
            'function_length_warn_threshold': warn_threshold,
            'function_length_urgent_threshold': urgent_threshold,
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
