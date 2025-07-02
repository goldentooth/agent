"""Core validation framework for git hooks."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional


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
