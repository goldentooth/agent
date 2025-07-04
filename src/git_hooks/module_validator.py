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
        self.warn_threshold = warn_threshold or calc.calculate_warn_threshold(limit)
        self.urgent_threshold = urgent_threshold or calc.calculate_urgent_threshold(
            limit
        )

    def validate(self, path: Path) -> Optional[ValidationResult]:
        """Validate a module's total line count."""
        if not path.exists() or not path.is_dir():
            return None

        if self._should_exclude(path):
            return None

        # Count lines in all Python files in the immediate directory
        total_lines = 0
        python_files = list(path.glob("*.py"))

        if not python_files:
            return None  # No Python files to check

        for py_file in python_files:
            try:
                lines = len(py_file.read_text().splitlines())
                total_lines += lines
            except (UnicodeDecodeError, PermissionError):
                # Skip files we can't read
                continue

        if total_lines > self.limit:
            return ValidationResult(
                file_path=path,
                severity=ValidationSeverity.ERROR,
                message=f"Module exceeds {self.limit} line limit: {total_lines} lines",
                line_count=total_lines,
                limit=self.limit,
                guidance=get_module_refactoring_guidance(),
            )
        elif total_lines >= self.urgent_threshold:
            remaining = self.limit - total_lines
            return ValidationResult(
                file_path=path,
                severity=ValidationSeverity.WARNING,
                message=f"Module approaching limit: {total_lines} lines ({remaining} lines until violation)",
                line_count=total_lines,
                limit=self.limit,
                guidance=get_module_refactoring_guidance(),
            )
        elif total_lines >= self.warn_threshold:
            remaining = self.urgent_threshold - total_lines
            return ValidationResult(
                file_path=path,
                severity=ValidationSeverity.WARNING,
                message=f"Module growing large: {total_lines} lines ({remaining} lines until urgent)",
                line_count=total_lines,
                limit=self.limit,
                guidance=get_module_refactoring_guidance(),
            )

        return None
