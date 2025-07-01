#!/usr/bin/env python3
"""Quick development feedback triggered by Claude Code hooks."""

import ast
import re
import sys
from pathlib import Path
from typing import Any


def has_complex_help_text(file_path: Path) -> bool:
    """Check if file has complex CLI help text that may not render well."""
    try:
        content = file_path.read_text()

        # Look for multiline strings in help parameters
        multiline_help_pattern = r'help\s*=\s*["\']([^"\']*\n[^"\']*)["\']'
        multiline_matches = re.findall(multiline_help_pattern, content, re.MULTILINE | re.DOTALL)

        # Look for help text with unicode characters
        unicode_help_pattern = r'help\s*=\s*["\']([^"\']*[🔧🔍📊⚡💡📝🎯🏥🤖🌊⚙️🚨][^"\']*)["\']'
        unicode_matches = re.findall(unicode_help_pattern, content)

        return len(multiline_matches) > 0 or len(unicode_matches) > 0

    except Exception:
        return False


def count_missing_return_types(file_path: Path) -> int:
    """Count functions missing return type annotations."""
    try:
        content = file_path.read_text()
        tree = ast.parse(content)

        missing_count = 0

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Skip private methods and special methods
                if node.name.startswith('_'):
                    continue

                # Check if function has return annotation
                if node.returns is None:
                    missing_count += 1

        return missing_count

    except Exception:
        return 0


def check_dict_access_patterns(file_path: Path) -> list[str]:
    """Check for potential dict.attribute access patterns."""
    try:
        content = file_path.read_text()
        issues = []

        # Look for common problematic patterns
        patterns = [
            (r'result\.response', "Consider: result['response'] if result is a dict"),
            (r'data\.get\(\s*["\'](\w+)["\'].*?\)\.(\w+)', "Chained .get().attribute access may fail"),
            (r'\.response\s*=', "Assignment to .response - ensure object has this attribute")
        ]

        for pattern, suggestion in patterns:
            if re.search(pattern, content):
                issues.append(suggestion)

        return issues

    except Exception:
        return []


def check_import_organization(file_path: Path) -> list[str]:
    """Check for import organization issues."""
    try:
        content = file_path.read_text()
        lines = content.split('\n')

        issues = []
        imports_started = False
        non_import_seen = False

        for i, line in enumerate(lines):
            stripped = line.strip()

            # Skip docstrings and comments
            if not stripped or stripped.startswith('#') or stripped.startswith('"""') or stripped.startswith("'''"):
                continue

            if stripped.startswith('from __future__'):
                continue

            if stripped.startswith(('import ', 'from ')):
                imports_started = True
                if non_import_seen:
                    issues.append("Imports mixed with other code - consider reorganizing")
                    break
            elif imports_started and stripped and not stripped.startswith(('import ', 'from ')):
                non_import_seen = True

        return issues

    except Exception:
        return []


def quick_check(file_path: str) -> None:
    """Provide quick development feedback without blocking."""
    path = Path(file_path)

    # Only check Python files
    if path.suffix != '.py':
        return

    # Skip __pycache__ and other generated files
    if '__pycache__' in str(path) or '.pyc' in str(path):
        return

    issues = []

    # Check for complex CLI help text
    if "cli/commands" in str(path):
        if has_complex_help_text(path):
            issues.append("💡 CLI help text contains multiline/unicode - may not render well")
            issues.append("   Consider: Simple help text + link to documentation")

    # Check for missing type annotations
    missing_types = count_missing_return_types(path)
    if missing_types > 0:
        issues.append(f"🔍 {missing_types} functions missing return type annotations")
        issues.append("   Fix: Add -> ReturnType to function definitions")

    # Check for dict access patterns
    dict_issues = check_dict_access_patterns(path)
    if dict_issues:
        issues.append("📝 Potential dict/object access issues:")
        for issue in dict_issues:
            issues.append(f"   {issue}")

    # Check import organization
    import_issues = check_import_organization(path)
    if import_issues:
        issues.extend([f"📦 {issue}" for issue in import_issues])

    # Show feedback but don't block
    if issues:
        print(f"\n💡 Quick feedback for {path.name}:")
        for issue in issues:
            print(f"  {issue}")
        print("  ℹ️  These are suggestions - your work is automatically saved!")
        print()


def main() -> None:
    """CLI entry point for quick check."""
    if len(sys.argv) < 2:
        print("Usage: goldentooth-agent dev quick-check <file_path>")
        sys.exit(1)

    quick_check(sys.argv[1])


if __name__ == "__main__":
    main()
