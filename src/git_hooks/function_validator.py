"""Function length validation."""

import ast
from pathlib import Path
from typing import Optional

from .core import ValidationResult, ValidationSeverity, Validator, ThresholdCalculator
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
        calc = ThresholdCalculator(warn_multiplier=0.8, urgent_multiplier=0.87)
        self.warn_threshold = warn_threshold or calc.calculate_warn_threshold(limit)
        self.urgent_threshold = urgent_threshold or calc.calculate_urgent_threshold(
            limit
        )

    def validate(self, path: Path) -> Optional[ValidationResult]:
        """Validate all functions in a Python file."""
        if not path.exists() or not path.is_file():
            return None

        if self._should_exclude(path):
            return None

        # Only validate Python files
        if not path.suffix == ".py":
            return None

        try:
            content = path.read_text()
            tree = ast.parse(content)
        except (UnicodeDecodeError, PermissionError, SyntaxError):
            # Skip binary files, files we can't read, or invalid Python
            return None

        # Find all function definitions
        functions = self._find_functions(tree)
        if not functions:
            return None

        # Find the longest function that violates limits
        worst_violation = None
        for func_name, start_line, end_line in functions:
            line_count = end_line - start_line + 1

            if line_count > self.limit:
                violation = ValidationResult(
                    file_path=path,
                    severity=ValidationSeverity.ERROR,
                    message=f"Function '{func_name}' exceeds {self.limit} line limit: {line_count} lines",
                    line_count=line_count,
                    limit=self.limit,
                    guidance=get_refactoring_guidance(path),
                )
                if worst_violation is None or line_count > worst_violation.line_count:
                    worst_violation = violation
            elif line_count >= self.urgent_threshold:
                remaining = self.limit - line_count
                violation = ValidationResult(
                    file_path=path,
                    severity=ValidationSeverity.WARNING,
                    message=f"Function '{func_name}' approaching limit: {line_count} lines ({remaining} lines until violation)",
                    line_count=line_count,
                    limit=self.limit,
                    guidance=get_refactoring_guidance(path),
                )
                if worst_violation is None or (
                    worst_violation.severity == ValidationSeverity.WARNING
                    and line_count > worst_violation.line_count
                ):
                    worst_violation = violation
            elif line_count >= self.warn_threshold:
                remaining = self.urgent_threshold - line_count
                violation = ValidationResult(
                    file_path=path,
                    severity=ValidationSeverity.WARNING,
                    message=f"Function '{func_name}' growing large: {line_count} lines ({remaining} lines until urgent)",
                    line_count=line_count,
                    limit=self.limit,
                    guidance=get_refactoring_guidance(path),
                )
                if worst_violation is None or (
                    worst_violation.severity == ValidationSeverity.WARNING
                    and line_count > worst_violation.line_count
                ):
                    worst_violation = violation

        return worst_violation

    def _find_functions(self, tree: ast.AST) -> list[tuple[str, int, int]]:
        """Find all function definitions with their line ranges."""
        functions: list[tuple[str, int, int]] = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                start_line = node.lineno
                end_line = node.end_lineno or start_line
                functions.append((node.name, start_line, end_line))

        return functions
