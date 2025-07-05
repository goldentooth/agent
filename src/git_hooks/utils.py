"""Utility functions for git hooks validation."""

# pyright: reportUnusedFunction=false

import subprocess
from pathlib import Path
from typing import List, Optional

from .core import ValidationResult, ValidationSeverity

DEFAULT_EXCLUDE_PATTERNS = [
    "old/",
    "docs/_build/",
    "htmlcov/",
    "*.lock",
    "*.min.js",
    "*.min.css",
    "__pycache__/",
    "build/",
    "dist/",
    ".pytest_cache/",
    "docs/",
    "*.md",
    "*.rst",
    "*.txt",
    "*.json",
    "*.yaml",
    "*.yml",
    "*.toml",
    "*.cfg",
    "*.ini",
]


def get_staged_files() -> List[Path]:
    """Get list of staged files in git."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=AM"],
            capture_output=True,
            text=True,
            check=True,
        )
        return [Path(f) for f in result.stdout.strip().split("\n") if f]
    except subprocess.CalledProcessError:
        return []


def get_all_files(directory: Optional[Path] = None) -> List[Path]:
    """Get all files in directory (non-git context)."""
    if directory is None:
        directory = Path(".")
    files: List[Path] = []
    for path in directory.rglob("*"):
        if path.is_file() and not any(part.startswith(".git") for part in path.parts):
            files.append(path)
    return files


def get_modules(directory: Optional[Path] = None) -> List[Path]:
    """Get all directories containing Python files."""
    if directory is None:
        directory = Path(".")
    modules: set[Path] = set()
    for py_file in directory.rglob("*.py"):
        if not any(part.startswith(".git") for part in py_file.parts):
            modules.add(py_file.parent)
    return list(modules)


def print_results(results: List[ValidationResult], hook_type: str) -> None:
    """Print validation results with appropriate formatting."""
    if not results:
        print(f"✅ {hook_type}: All files within healthy limits")
        return

    errors, warnings = _separate_results_by_severity(results)
    _print_error_results(errors, hook_type)
    _print_warning_results(warnings)


def _separate_results_by_severity(
    results: List[ValidationResult],
) -> tuple[List[ValidationResult], List[ValidationResult]]:
    """Separate results into errors and warnings."""
    errors = [r for r in results if r.severity == ValidationSeverity.ERROR]
    warnings = [r for r in results if r.severity == ValidationSeverity.WARNING]
    return errors, warnings


def _print_error_results(errors: List[ValidationResult], hook_type: str) -> None:
    """Print error validation results."""
    if not errors:
        return

    print(f"❌ {hook_type} violations found:")
    for result in errors:
        display_path = str(result.file_path).lstrip("./")
        # Include the full message which contains function/module name and details
        print(f"  {display_path}: {result.message}")
    print("\nPlease refactor large files/modules before committing.")
    print("See .claude/guidelines/guidelines.txt for requirements")


def _print_warning_results(warning_results: List[ValidationResult]) -> None:
    """Print warning validation results with urgency levels."""
    if not warning_results:
        return

    # Group warnings by guidance to avoid repetition
    from collections import defaultdict

    warnings_by_guidance: defaultdict[str, List[ValidationResult]] = defaultdict(list)

    for result in warning_results:
        warnings_by_guidance[result.guidance].append(result)

    # Print warnings grouped by guidance
    for guidance, results in warnings_by_guidance.items():
        for result in results:
            _print_single_warning_without_guidance(result)

        # Print guidance once for the group
        if guidance:
            print(guidance)
            print()


def _print_single_warning(result: ValidationResult) -> None:
    """Print a single warning result with appropriate formatting.

    Note: This function is kept for backward compatibility and testing.
    The main code path uses _print_single_warning_without_guidance.
    """
    display_path = str(result.file_path).lstrip("./")

    if _is_urgent_warning(result):
        print(f"🔶 URGENT: {display_path} ({result.message})")
    else:
        print(f"⚠️  WARNING: {display_path} ({result.message})")

    print(result.guidance)
    print()


def _print_single_warning_without_guidance(result: ValidationResult) -> None:
    """Print a single warning without the guidance text."""
    display_path = str(result.file_path).lstrip("./")

    if _is_urgent_warning(result):
        print(f"🔶 URGENT: {display_path} ({result.message})")
    else:
        print(f"⚠️  WARNING: {display_path} ({result.message})")


def _is_urgent_warning(result: ValidationResult) -> bool:
    """Check if warning should be marked as urgent."""
    return result.line_count >= result.limit * 0.9
