"""Command-line interface for validation hooks."""

import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

from .core import ValidationResult, ValidationSeverity
from .file_validator import FileLengthValidator
from .module_validator import ModuleSizeValidator

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


def check_file_length() -> int:
    """Check file lengths (blocking hook)."""
    limit = int(os.environ.get("FILE_LENGTH_LIMIT", "1000"))
    validator = FileLengthValidator(
        limit=limit,
        exclude_patterns=DEFAULT_EXCLUDE_PATTERNS,
    )

    # Get files to check
    if (
        subprocess.run(
            ["git", "rev-parse", "--git-dir"], capture_output=True
        ).returncode
        == 0
    ):
        files = get_staged_files()
    else:
        files = get_all_files()

    if not files:
        print("✅ File length check: No files to check")
        return 0

    results: List[ValidationResult] = []
    for file_path in files:
        result = validator.validate(file_path)
        if result and result.severity == ValidationSeverity.ERROR:
            results.append(result)

    print_results(results, "File length check")
    return 1 if results else 0


def check_file_length_warnings() -> int:
    """Check file lengths (warning hook)."""
    limit = int(os.environ.get("FILE_LENGTH_LIMIT", "1000"))
    warn_threshold = int(os.environ.get("FILE_LENGTH_WARN_THRESHOLD", "800"))
    urgent_threshold = int(os.environ.get("FILE_LENGTH_URGENT_THRESHOLD", "900"))

    validator = FileLengthValidator(
        limit=limit,
        warn_threshold=warn_threshold,
        urgent_threshold=urgent_threshold,
        exclude_patterns=DEFAULT_EXCLUDE_PATTERNS,
    )

    # Get files to check
    if (
        subprocess.run(
            ["git", "rev-parse", "--git-dir"], capture_output=True
        ).returncode
        == 0
    ):
        files = get_staged_files()
    else:
        files = get_all_files()

    if not files:
        print("✅ File length warnings: No files to check")
        return 0

    results: List[ValidationResult] = []
    for file_path in files:
        result = validator.validate(file_path)
        if result:
            results.append(result)

    print_results(results, "File length warnings")
    return 0  # Always succeed for warnings


def check_module_size() -> int:
    """Check module sizes (blocking hook)."""
    limit = int(os.environ.get("MODULE_SIZE_LIMIT", "5000"))
    validator = ModuleSizeValidator(
        limit=limit,
        exclude_patterns=DEFAULT_EXCLUDE_PATTERNS,
    )

    modules = get_modules()
    if not modules:
        print("✅ Module size check: No modules to check")
        return 0

    results: List[ValidationResult] = []
    for module_path in modules:
        result = validator.validate(module_path)
        if result and result.severity == ValidationSeverity.ERROR:
            results.append(result)

    print_results(results, "Module size check")
    return 1 if results else 0


def check_module_size_warnings() -> int:
    """Check module sizes (warning hook)."""
    limit = int(os.environ.get("MODULE_SIZE_LIMIT", "5000"))
    warn_threshold = int(os.environ.get("MODULE_SIZE_WARN_THRESHOLD", "4000"))
    urgent_threshold = int(os.environ.get("MODULE_SIZE_URGENT_THRESHOLD", "4500"))

    validator = ModuleSizeValidator(
        limit=limit,
        warn_threshold=warn_threshold,
        urgent_threshold=urgent_threshold,
        exclude_patterns=DEFAULT_EXCLUDE_PATTERNS,
    )

    modules = get_modules()
    if not modules:
        print("✅ Module size warnings: No modules to check")
        return 0

    results: List[ValidationResult] = []
    for module_path in modules:
        result = validator.validate(module_path)
        if result:
            results.append(result)

    print_results(results, "Module size warnings")
    return 0  # Always succeed for warnings


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m src.git_hooks.cli <hook_type>")
        print(
            "Hook types: file_length, file_length_warnings, module_size, module_size_warnings"
        )
        sys.exit(1)

    hook_type = sys.argv[1]

    if hook_type == "file_length":
        sys.exit(check_file_length())
    elif hook_type == "file_length_warnings":
        sys.exit(check_file_length_warnings())
    elif hook_type == "module_size":
        sys.exit(check_module_size())
    elif hook_type == "module_size_warnings":
        sys.exit(check_module_size_warnings())
    else:
        print(f"Unknown hook type: {hook_type}")
        sys.exit(1)
