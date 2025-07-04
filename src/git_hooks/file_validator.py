"""File length validation."""

from pathlib import Path
from typing import Optional

from .core import ValidationResult, ValidationSeverity, Validator, ThresholdCalculator
from .guidance import get_refactoring_guidance
from .validator_registry import ValidatorRegistry


@ValidatorRegistry.register("file_length")
class FileLengthValidator(Validator):
    """Validates individual file line counts."""

    def __init__(
        self,
        limit: int = 1000,
        warn_threshold: Optional[int] = None,
        urgent_threshold: Optional[int] = None,
        exclude_patterns: Optional[list[str]] = None,
    ):
        super().__init__(limit, exclude_patterns)
        calc = ThresholdCalculator(warn_multiplier=0.8, urgent_multiplier=0.9)
        self.warn_threshold = warn_threshold or calc.calculate_warn_threshold(limit)
        self.urgent_threshold = urgent_threshold or calc.calculate_urgent_threshold(
            limit
        )

    def validate(self, path: Path) -> Optional[ValidationResult]:
        """Validate a single file's line count."""
        if not path.exists() or not path.is_file():
            return None

        if self._should_exclude(path):
            return None

        try:
            line_count = len(path.read_text().splitlines())
        except (UnicodeDecodeError, PermissionError):
            # Skip binary files or files we can't read
            return None

        if line_count > self.limit:
            return ValidationResult(
                file_path=path,
                severity=ValidationSeverity.ERROR,
                message=f"File exceeds {self.limit} line limit: {line_count} lines",
                line_count=line_count,
                limit=self.limit,
                guidance=get_refactoring_guidance(path),
            )
        elif line_count >= self.urgent_threshold:
            remaining = self.limit - line_count
            return ValidationResult(
                file_path=path,
                severity=ValidationSeverity.WARNING,
                message=f"File approaching limit: {line_count} lines ({remaining} lines until violation)",
                line_count=line_count,
                limit=self.limit,
                guidance=get_refactoring_guidance(path),
            )
        elif line_count >= self.warn_threshold:
            remaining = self.urgent_threshold - line_count
            return ValidationResult(
                file_path=path,
                severity=ValidationSeverity.WARNING,
                message=f"File growing large: {line_count} lines ({remaining} lines until urgent)",
                line_count=line_count,
                limit=self.limit,
                guidance=get_refactoring_guidance(path),
            )

        return None
