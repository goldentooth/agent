"""Function length validation."""

import ast
from pathlib import Path
from typing import Optional

from .core import ThresholdCalculator, ValidationResult, ValidationSeverity, Validator
from .guidance import get_refactoring_guidance
from .validator_registry import ValidatorRegistry


@ValidatorRegistry.register("function_length")
class FunctionLengthValidator(Validator):
    """Validates function line counts within Python files."""

    def __init__(
        self,
        limit: int = 15,
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
        calc = ThresholdCalculator(warn_multiplier=0.8, urgent_multiplier=0.87)
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

    def _is_valid_python_file(self, path: Path) -> bool:
        """Check if path is valid Python file."""
        return (
            path.exists()
            and path.is_file()
            and path.suffix == ".py"
            and not self._should_exclude(path)
        )

    def _parse_python_file(self, path: Path) -> Optional[ast.AST]:
        """Parse Python file, return None if invalid."""
        try:
            content = path.read_text()
            return ast.parse(content)
        except (UnicodeDecodeError, PermissionError, SyntaxError):
            return None

    def _create_error_violation(
        self, path: Path, func_name: str, line_count: int
    ) -> ValidationResult:
        """Create error validation result."""
        return ValidationResult(
            file_path=path,
            severity=ValidationSeverity.ERROR,
            message=f"Function '{func_name}' exceeds {self.limit} line limit: {line_count} lines",
            line_count=line_count,
            limit=self.limit,
            guidance=get_refactoring_guidance(path),
        )

    def _create_warning_violation(
        self, path: Path, func_name: str, line_count: int, threshold_type: str
    ) -> ValidationResult:
        """Create warning validation result."""
        message = self._get_warning_message(func_name, line_count, threshold_type)
        return ValidationResult(
            file_path=path,
            severity=ValidationSeverity.WARNING,
            message=message,
            line_count=line_count,
            limit=self.limit,
            guidance=get_refactoring_guidance(path),
        )

    def _get_warning_message(
        self, func_name: str, line_count: int, threshold_type: str
    ) -> str:
        """Get warning message based on threshold type."""
        if threshold_type == "urgent":
            remaining = self.limit - line_count
            return f"Function '{func_name}' approaching limit: {line_count} lines ({remaining} lines until violation)"
        else:  # warn
            remaining = self.urgent_threshold - line_count
            return f"Function '{func_name}' growing large: {line_count} lines ({remaining} lines until urgent)"

    def _update_worst_violation(
        self, current: Optional[ValidationResult], new: ValidationResult
    ) -> ValidationResult:
        """Update worst violation with new candidate."""
        if current is None:
            return new
        if (
            new.severity == ValidationSeverity.ERROR
            and current.severity == ValidationSeverity.WARNING
        ):
            return new
        if new.severity == current.severity and new.line_count > current.line_count:
            return new
        return current

    def _find_worst_violation(
        self, path: Path, functions: list[tuple[str, int, int]]
    ) -> Optional[ValidationResult]:
        """Find worst function length violation."""
        worst_violation = None
        for func_name, start_line, end_line in functions:
            line_count = end_line - start_line + 1
            violation = self._create_function_violation(path, func_name, line_count)
            if violation:
                worst_violation = self._update_worst_violation(
                    worst_violation, violation
                )
        return worst_violation

    def _create_function_violation(
        self, path: Path, func_name: str, line_count: int
    ) -> Optional[ValidationResult]:
        """Create violation for a function if it exceeds thresholds."""
        if line_count > self.limit:
            return self._create_error_violation(path, func_name, line_count)
        elif line_count >= self.urgent_threshold:
            return self._create_warning_violation(path, func_name, line_count, "urgent")
        elif line_count >= self.warn_threshold:
            return self._create_warning_violation(path, func_name, line_count, "warn")
        return None

    def validate(self, path: Path) -> Optional[ValidationResult]:
        """Validate all functions in a Python file."""
        if not self._is_valid_python_file(path):
            return None

        tree = self._parse_python_file(path)
        if tree is None:
            return None

        functions = self._find_functions(tree)
        if not functions:
            return None

        return self._find_worst_violation(path, functions)

    def get_all_function_info(self, path: Path) -> list[tuple[str, int, int, int]]:
        """Get information about all functions in a file for verbose output.

        Returns:
            List of tuples: (function_name, start_line, end_line, line_count)
        """
        if not self._is_valid_python_file(path):
            return []

        tree = self._parse_python_file(path)
        if tree is None:
            return []

        functions = self._find_functions(tree)
        function_info: list[tuple[str, int, int, int]] = []
        for func_name, start_line, end_line in functions:
            line_count = end_line - start_line + 1
            function_info.append((func_name, start_line, end_line, line_count))

        # Sort by line count descending
        function_info.sort(key=lambda x: x[3], reverse=True)
        return function_info

    def _find_functions(self, tree: ast.AST) -> list[tuple[str, int, int]]:
        """Find all function definitions with their line ranges."""
        functions: list[tuple[str, int, int]] = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                start_line = node.lineno
                end_line = node.end_lineno or start_line
                functions.append((node.name, start_line, end_line))

        return functions
