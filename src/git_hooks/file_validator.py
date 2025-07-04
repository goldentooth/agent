"""File length validation."""

from pathlib import Path
from typing import Optional

from .core import ThresholdCalculator, ValidationResult, ValidationSeverity, Validator
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
        self.warn_threshold = (
            warn_threshold
            if warn_threshold is not None
            else calc.calculate_warn_threshold(limit)
        )
        self.urgent_threshold = (
            urgent_threshold
            if urgent_threshold is not None
            else calc.calculate_urgent_threshold(limit)
        )

    def _get_line_count(self, path: Path) -> Optional[int]:
        """Get line count for a file, returning None if unreadable."""
        try:
            return len(path.read_text().splitlines())
        except (UnicodeDecodeError, PermissionError):
            return None

    def _create_error_result(self, path: Path, line_count: int) -> ValidationResult:
        """Create error result for file exceeding limit."""
        return ValidationResult(
            file_path=path,
            severity=ValidationSeverity.ERROR,
            message=f"File exceeds {self.limit} line limit: {line_count} lines",
            line_count=line_count,
            limit=self.limit,
            guidance=get_refactoring_guidance(path),
        )

    def _create_warning_result(
        self, path: Path, line_count: int, threshold_type: str
    ) -> ValidationResult:
        """Create warning result for file approaching limits."""
        if threshold_type == "urgent":
            remaining = self.limit - line_count
            message = f"File approaching limit: {line_count} lines ({remaining} lines until violation)"
        else:  # warn
            remaining = self.urgent_threshold - line_count
            message = f"File growing large: {line_count} lines ({remaining} lines until urgent)"

        return ValidationResult(
            file_path=path,
            severity=ValidationSeverity.WARNING,
            message=message,
            line_count=line_count,
            limit=self.limit,
            guidance=get_refactoring_guidance(path),
        )

    def validate(self, path: Path) -> Optional[ValidationResult]:
        """Validate a single file's line count."""
        if not path.exists() or not path.is_file() or self._should_exclude(path):
            return None

        line_count = self._get_line_count(path)
        if line_count is None:
            return None

        if line_count > self.limit:
            return self._create_error_result(path, line_count)
        elif line_count >= self.urgent_threshold:
            return self._create_warning_result(path, line_count, "urgent")
        elif line_count >= self.warn_threshold:
            return self._create_warning_result(path, line_count, "warn")

        return None
