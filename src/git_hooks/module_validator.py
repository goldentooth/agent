"""Module size validation."""

from pathlib import Path
from typing import Optional

from .core import ThresholdCalculator, ValidationResult, ValidationSeverity, Validator
from .guidance import get_module_refactoring_guidance
from .validator_registry import ValidatorRegistry


@ValidatorRegistry.register("module_size")
class ModuleSizeValidator(Validator):
    """Validates module total line counts."""

    def __init__(
        self,
        limit: int = 5000,
        warn_threshold: Optional[int] = None,
        urgent_threshold: Optional[int] = None,
        exclude_patterns: Optional[list[str]] = None,
    ):
        super().__init__(limit, exclude_patterns)
        self._set_thresholds(limit, warn_threshold, urgent_threshold)

    def _set_thresholds(
        self, limit: int, warn_threshold: Optional[int], urgent_threshold: Optional[int]
    ) -> None:
        """Set warning and urgent thresholds."""
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

    def _is_valid_module(self, path: Path) -> bool:
        """Check if path is valid module directory."""
        return path.exists() and path.is_dir() and not self._should_exclude(path)

    def _count_module_lines(self, path: Path) -> Optional[int]:
        """Count total lines in all Python files in module."""
        python_files = list(path.glob("*.py"))
        if not python_files:
            return None

        total_lines = 0
        for py_file in python_files:
            try:
                lines = len(py_file.read_text().splitlines())
                total_lines += lines
            except (UnicodeDecodeError, PermissionError):
                continue

        return total_lines

    def _create_module_error_result(
        self, path: Path, total_lines: int
    ) -> ValidationResult:
        """Create error result for module exceeding limit."""
        return ValidationResult(
            file_path=path,
            severity=ValidationSeverity.ERROR,
            message=f"Module exceeds {self.limit} line limit: {total_lines} lines",
            line_count=total_lines,
            limit=self.limit,
            guidance=get_module_refactoring_guidance(),
        )

    def _create_module_warning_result(
        self, path: Path, total_lines: int, threshold_type: str
    ) -> ValidationResult:
        """Create warning result for module approaching limits."""
        message = self._get_module_warning_message(total_lines, threshold_type)
        return ValidationResult(
            file_path=path,
            severity=ValidationSeverity.WARNING,
            message=message,
            line_count=total_lines,
            limit=self.limit,
            guidance=get_module_refactoring_guidance(),
        )

    def _get_module_warning_message(self, total_lines: int, threshold_type: str) -> str:
        """Get warning message for module."""
        if threshold_type == "urgent":
            remaining = self.limit - total_lines
            return f"Module approaching limit: {total_lines} lines ({remaining} lines until violation)"
        else:  # warn
            remaining = self.urgent_threshold - total_lines
            return f"Module growing large: {total_lines} lines ({remaining} lines until urgent)"

    def validate(self, path: Path) -> Optional[ValidationResult]:
        """Validate a module's total line count."""
        if not self._is_valid_module(path):
            return None

        total_lines = self._count_module_lines(path)
        if total_lines is None:
            return None

        return self._create_module_validation_result(path, total_lines)

    def _create_module_validation_result(
        self, path: Path, total_lines: int
    ) -> Optional[ValidationResult]:
        """Create validation result based on total lines."""
        if total_lines > self.limit:
            return self._create_module_error_result(path, total_lines)
        elif total_lines >= self.urgent_threshold:
            return self._create_module_warning_result(path, total_lines, "urgent")
        elif total_lines >= self.warn_threshold:
            return self._create_module_warning_result(path, total_lines, "warn")
        return None
