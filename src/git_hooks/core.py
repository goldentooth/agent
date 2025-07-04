"""Core validation framework for git hooks."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional


class ThresholdCalculator:
    """Calculate warning and urgent thresholds based on limits."""

    def __init__(self, warn_multiplier: float = 0.9, urgent_multiplier: float = 0.8):
        """Initialize with multipliers for calculations."""
        super().__init__()
        if not (0 < warn_multiplier <= 1):
            raise ValueError("Multipliers must be between 0 and 1")
        if not (0 < urgent_multiplier <= 1):
            raise ValueError("Multipliers must be between 0 and 1")

        self.warn_multiplier = warn_multiplier
        self.urgent_multiplier = urgent_multiplier

    def calculate_warn_threshold(self, limit: int) -> int:
        """Calculate warning threshold."""
        if limit < 0:
            raise ValueError("Limit must be non-negative")
        return round(limit * self.warn_multiplier)

    def calculate_urgent_threshold(self, limit: int) -> int:
        """Calculate urgent threshold."""
        if limit < 0:
            raise ValueError("Limit must be non-negative")
        return round(limit * self.urgent_multiplier)


class ValidationSeverity(Enum):
    """Severity levels for validation results."""

    WARNING = "warning"
    ERROR = "error"


@dataclass
class ValidationResult:
    """Result of a validation check."""

    file_path: Path
    severity: ValidationSeverity
    message: str
    line_count: int
    limit: int
    guidance: str = ""


class Validator(ABC):
    """Abstract base class for validators."""

    def __init__(self, limit: int, exclude_patterns: Optional[List[str]] = None):
        super().__init__()
        self.limit = limit
        self.exclude_patterns = exclude_patterns or []

    @abstractmethod
    def validate(self, path: Path) -> Optional[ValidationResult]:
        """Validate a file or directory path."""
        pass

    def _should_exclude(self, path: Path) -> bool:
        """Check if path matches any exclusion pattern."""
        path_str = str(path)
        for pattern in self.exclude_patterns:
            if pattern.endswith("/"):
                # Directory pattern
                if f"/{pattern}" in f"/{path_str}/" or path_str.startswith(pattern):
                    return True
            elif path_str.endswith(pattern.lstrip("*")):
                # File extension pattern
                return True
        return False
