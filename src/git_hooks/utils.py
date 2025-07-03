"""Utility functions for git hooks validation."""

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

    errors = [r for r in results if r.severity == ValidationSeverity.ERROR]
    warnings = [r for r in results if r.severity == ValidationSeverity.WARNING]

    if errors:
        print(f"❌ {hook_type} violations found:")
        for result in errors:
            display_path = str(result.file_path).lstrip("./")
            print(f"  {display_path}: {result.line_count} lines")
        print("\nPlease refactor large files/modules before committing.")
        print("See .claude/guidelines/guidelines.txt for requirements")

    if warnings:
        for result in warnings:
            display_path = str(result.file_path).lstrip("./")
            if result.severity == ValidationSeverity.WARNING:
                if result.line_count >= result.limit * 0.9:  # Urgent threshold
                    print(f"🔶 URGENT: {display_path} ({result.message})")
                else:
                    print(f"⚠️  WARNING: {display_path} ({result.message})")
                print(result.guidance)
                print()
