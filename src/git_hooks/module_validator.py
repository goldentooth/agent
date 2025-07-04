"""Module size validation."""

from pathlib import Path
from typing import Optional

from .core import ValidationResult, ValidationSeverity, Validator, ThresholdCalculator
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
        calc = ThresholdCalculator(warn_multiplier=0.8, urgent_multiplier=0.9)
        self.warn_threshold = calc.calculate_warn_threshold(limit) if warn_threshold is None else warn_threshold
        self.urgent_threshold = calc.calculate_urgent_threshold(limit) if urgent_threshold is None else urgent_threshold

    def _is_valid_module(self, path: Path) -> bool:
        """Check if path is valid module directory."""
        return (path.exists() and path.is_dir() and not self._should_exclude(path))

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

    def _create_module_error_result(self, path: Path, total_lines: int) -> ValidationResult:
        """Create error result for module exceeding limit."""
        return ValidationResult(
            file_path=path,
            severity=ValidationSeverity.ERROR,
            message=f"Module exceeds {self.limit} line limit: {total_lines} lines",
            line_count=total_lines,
            limit=self.limit,
            guidance=get_module_refactoring_guidance(),
        )

    def _create_module_warning_result(self, path: Path, total_lines: int, threshold_type: str) -> ValidationResult:
        """Create warning result for module approaching limits."""
        if threshold_type == "urgent":
            remaining = self.limit - total_lines
            message = f"Module approaching limit: {total_lines} lines ({remaining} lines until violation)"
        else:  # warn
            remaining = self.urgent_threshold - total_lines
            message = f"Module growing large: {total_lines} lines ({remaining} lines until urgent)"
        
        return ValidationResult(
            file_path=path,
            severity=ValidationSeverity.WARNING,
            message=message,
            line_count=total_lines,
            limit=self.limit,
            guidance=get_module_refactoring_guidance(),
        )

    def validate(self, path: Path) -> Optional[ValidationResult]:
        """Validate a module's total line count."""
        if not self._is_valid_module(path):
            return None

        total_lines = self._count_module_lines(path)
        if total_lines is None:
            return None

        if total_lines > self.limit:
            return self._create_module_error_result(path, total_lines)
        elif total_lines >= self.urgent_threshold:
            return self._create_module_warning_result(path, total_lines, "urgent")
        elif total_lines >= self.warn_threshold:
            return self._create_module_warning_result(path, total_lines, "warn")

        return None
