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
        self, path: Path, func_name: str, stmt_count: int
    ) -> ValidationResult:
        """Create error validation result."""
        return ValidationResult(
            file_path=path,
            severity=ValidationSeverity.ERROR,
            message=f"Function '{func_name}' exceeds {self.limit} statement limit: {stmt_count} statements",
            line_count=stmt_count,
            limit=self.limit,
            guidance=get_refactoring_guidance(path),
        )

    def _create_warning_violation(
        self, path: Path, func_name: str, stmt_count: int, threshold_type: str
    ) -> ValidationResult:
        """Create warning validation result."""
        message = self._get_warning_message(func_name, stmt_count, threshold_type)
        return ValidationResult(
            file_path=path,
            severity=ValidationSeverity.WARNING,
            message=message,
            line_count=stmt_count,
            limit=self.limit,
            guidance=get_refactoring_guidance(path),
        )

    def _get_warning_message(
        self, func_name: str, stmt_count: int, threshold_type: str
    ) -> str:
        """Get warning message based on threshold type."""
        if threshold_type == "urgent":
            remaining = self.limit - stmt_count
            return f"Function '{func_name}' approaching limit: {stmt_count} statements ({remaining} statements until violation)"
        else:  # warn
            remaining = self.urgent_threshold - stmt_count
            return f"Function '{func_name}' growing large: {stmt_count} statements ({remaining} statements until urgent)"

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

        # Parse the file to get statement counts
        tree = self._parse_python_file(path)
        if tree is None:
            return None

        for func_name, start_line, end_line in functions:
            # Find the function node to count statements
            stmt_count = self._get_statement_count_for_function(
                tree, func_name, start_line
            )
            violation = self._create_function_violation(path, func_name, stmt_count)
            if violation:
                worst_violation = self._update_worst_violation(
                    worst_violation, violation
                )
        return worst_violation

    def _get_statement_count_for_function(
        self, tree: ast.AST, func_name: str, start_line: int
    ) -> int:
        """Get statement count for a specific function."""
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name == func_name and node.lineno == start_line:
                    return self._count_statements(node)
        return 0

    def _create_function_violation(
        self, path: Path, func_name: str, stmt_count: int
    ) -> Optional[ValidationResult]:
        """Create violation for a function if it exceeds thresholds."""
        if stmt_count > self.limit:
            return self._create_error_violation(path, func_name, stmt_count)
        elif stmt_count >= self.urgent_threshold:
            return self._create_warning_violation(path, func_name, stmt_count, "urgent")
        elif stmt_count >= self.warn_threshold:
            return self._create_warning_violation(path, func_name, stmt_count, "warn")
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

    def _count_statements(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
        """Count the number of statements in a function."""
        # Count all statement nodes within the function body
        # Exclude the function definition itself
        statements: list[ast.stmt] = []
        for child in ast.walk(node):
            if isinstance(child, ast.stmt) and child != node:
                # Only count statements that are direct children or in the function body
                # Don't count nested function statements
                if self._is_in_function_body(child, node):
                    statements.append(child)
        return len(statements)

    def _is_in_function_body(
        self, stmt: ast.stmt, func: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> bool:
        """Check if a statement is directly in the function body (not nested)."""
        # Simple check: if the statement is in the function's body list
        return stmt in func.body

    def get_all_function_statements(
        self, path: Path
    ) -> list[tuple[str, int, int, int, int]]:
        """Get statement count information about all functions in a file.

        Returns:
            List of tuples: (function_name, start_line, end_line, line_count, statement_count)
        """
        if not self._is_valid_python_file(path):
            return []

        tree = self._parse_python_file(path)
        if tree is None:
            return []

        function_info: list[tuple[str, int, int, int, int]] = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                start_line = node.lineno
                end_line = node.end_lineno or start_line
                line_count = end_line - start_line + 1
                stmt_count = self._count_statements(node)
                function_info.append(
                    (node.name, start_line, end_line, line_count, stmt_count)
                )

        # Sort by statement count descending
        function_info.sort(key=lambda x: x[4], reverse=True)
        return function_info
