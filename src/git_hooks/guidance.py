"""Refactoring guidance for different file types."""

from pathlib import Path


def get_refactoring_guidance(file_path: Path) -> str:
    """Get file-type specific refactoring guidance."""
    ext = file_path.suffix.lower()
    name = file_path.name.lower()

    if ext == ".py":
        if "test" in name or name.startswith("test_"):
            return _get_test_guidance()
        return _get_python_guidance()
    elif ext in {".js", ".ts", ".jsx", ".tsx"}:
        return _get_javascript_guidance()
    else:
        return _get_general_guidance()


def get_module_refactoring_guidance() -> str:
    """Get module-specific refactoring guidance."""
    return """Module refactoring strategies:
• Split into smaller, focused sub-modules by domain
• Extract common utilities into separate utility modules
• Move models/schemas to dedicated modules
• Separate interface definitions from implementations
• Consider creating sub-packages for complex domains
• Use __init__.py files to create clean public interfaces

See .claude/guidelines/guidelines.txt commandment #5
Goal: Keep modules focused and maintainable"""


def _get_python_guidance() -> str:
    """Python-specific refactoring guidance."""
    return """Python refactoring strategies:
• Extract large functions/classes into separate modules
• Split into domain-specific files (models, utils, services)
• Move constants/config to dedicated files
• Consider using composition over inheritance
• Extract complex logic into pure functions"""


def _get_javascript_guidance() -> str:
    """JavaScript/TypeScript refactoring guidance."""
    return """JavaScript/TypeScript refactoring strategies:
• Split components into smaller, focused files
• Extract utility functions and constants
• Separate business logic from UI components
• Use barrel exports for clean imports
• Consider custom hooks for reusable logic"""


def _get_test_guidance() -> str:
    """Test-specific refactoring guidance."""
    return """Test file refactoring strategies:
• Group related tests into separate test files
• Extract test fixtures and utilities to conftest.py
• Split integration and unit tests
• Use parameterized tests to reduce duplication
• Extract common test setup to shared fixtures"""


def _get_general_guidance() -> str:
    """General refactoring guidance."""
    return """General refactoring strategies:
• Split into smaller, focused files by responsibility
• Extract common utilities and constants
• Consider modular architecture patterns
• Document refactoring decisions in commit messages
• Apply single responsibility principle"""
