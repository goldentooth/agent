"""Centralized configuration management for git hooks validation."""

import os
from dataclasses import dataclass
from typing import Any, Dict


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
    def from_environment(cls) -> "ValidationConfig":
        """Load configuration from environment variables with defaults."""
        # File length configuration
        file_length_limit = int(os.environ.get(cls.FILE_LENGTH_LIMIT_KEY, "1000"))
        file_length_warn_threshold = int(
            os.environ.get(
                cls.FILE_LENGTH_WARN_THRESHOLD_KEY, str(int(file_length_limit * 0.8))
            )
        )
        file_length_urgent_threshold = int(
            os.environ.get(
                cls.FILE_LENGTH_URGENT_THRESHOLD_KEY, str(int(file_length_limit * 0.9))
            )
        )

        # Module size configuration
        module_size_limit = int(os.environ.get(cls.MODULE_SIZE_LIMIT_KEY, "5000"))
        module_size_warn_threshold = int(
            os.environ.get(
                cls.MODULE_SIZE_WARN_THRESHOLD_KEY, str(int(module_size_limit * 0.8))
            )
        )
        module_size_urgent_threshold = int(
            os.environ.get(
                cls.MODULE_SIZE_URGENT_THRESHOLD_KEY, str(int(module_size_limit * 0.9))
            )
        )

        # Function length configuration
        function_length_limit = int(os.environ.get(cls.FUNCTION_LENGTH_LIMIT_KEY, "15"))
        function_length_warn_threshold = int(
            os.environ.get(
                cls.FUNCTION_LENGTH_WARN_THRESHOLD_KEY,
                str(int(function_length_limit * 0.8)),
            )
        )
        function_length_urgent_threshold = int(
            os.environ.get(
                cls.FUNCTION_LENGTH_URGENT_THRESHOLD_KEY,
                str(int(function_length_limit * 0.87)),
            )
        )

        return cls(
            file_length_limit=file_length_limit,
            file_length_warn_threshold=file_length_warn_threshold,
            file_length_urgent_threshold=file_length_urgent_threshold,
            module_size_limit=module_size_limit,
            module_size_warn_threshold=module_size_warn_threshold,
            module_size_urgent_threshold=module_size_urgent_threshold,
            function_length_limit=function_length_limit,
            function_length_warn_threshold=function_length_warn_threshold,
            function_length_urgent_threshold=function_length_urgent_threshold,
        )

    def get_validator_config(self, validator_type: str) -> Dict[str, Any]:
        """Get configuration for a specific validator type."""
        if validator_type == "file_length":
            return {
                "limit": self.file_length_limit,
                "warn_threshold": self.file_length_warn_threshold,
                "urgent_threshold": self.file_length_urgent_threshold,
            }
        elif validator_type == "module_size":
            return {
                "limit": self.module_size_limit,
                "warn_threshold": self.module_size_warn_threshold,
                "urgent_threshold": self.module_size_urgent_threshold,
            }
        elif validator_type == "function_length":
            return {
                "limit": self.function_length_limit,
                "warn_threshold": self.function_length_warn_threshold,
                "urgent_threshold": self.function_length_urgent_threshold,
            }
        else:
            raise ValueError(f"Unknown validator type: {validator_type}")
