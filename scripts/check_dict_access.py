#!/usr/bin/env python3
"""Check for potentially unsafe dictionary attribute access patterns."""

import ast
import sys
from pathlib import Path
from typing import Any


class DictAccessChecker(ast.NodeVisitor):
    """AST visitor to find potential dict.attribute access patterns."""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.issues: list[dict[str, Any]] = []
        self.current_function: str | None = None

        # Common variable names that might be dictionaries
        self.suspicious_names = {
            "result",
            "response",
            "data",
            "payload",
            "output",
            "rag_result",
            "agent_result",
            "api_response",
            "json_data",
            "config",
            "metadata",
            "params",
            "body",
            "content",
        }

        # Known safe object types (not dictionaries)
        self.safe_patterns = {
            "self",
            "cls",
            "logger",
            "client",
            "session",
            "request",
            "ctx",
            "app",
            "db",
            "cache",
        }

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Track current function context."""
        old_function = self.current_function
        self.current_function = node.name
        self.generic_visit(node)
        self.current_function = old_function

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Track async function context."""
        self.visit_FunctionDef(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        """Check for suspicious attribute access patterns."""
        # Look for pattern: variable.attribute
        if isinstance(node.value, ast.Name):
            var_name = node.value.id

            # Skip if it's a known safe pattern
            if var_name in self.safe_patterns:
                self.generic_visit(node)
                return

            # Check if variable name is suspicious
            is_suspicious = False
            for pattern in self.suspicious_names:
                if pattern in var_name.lower():
                    is_suspicious = True
                    break

            if is_suspicious:
                # Try to get the source line
                try:
                    with open(self.file_path) as f:
                        lines = f.readlines()
                        source_line = (
                            lines[node.lineno - 1].strip()
                            if node.lineno <= len(lines)
                            else ""
                        )
                except Exception:
                    source_line = ""

                self.issues.append(
                    {
                        "line": node.lineno,
                        "col": node.col_offset,
                        "attr": node.attr,
                        "var": var_name,
                        "function": self.current_function,
                        "source": source_line,
                    }
                )

        self.generic_visit(node)


def check_file(file_path: Path) -> list[dict[str, Any]]:
    """Check a single file for dictionary access issues.

    Args:
        file_path: Path to Python file to check

    Returns:
        List of potential issues found
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            tree = ast.parse(f.read())
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return []

    checker = DictAccessChecker(file_path)
    checker.visit(tree)

    # Add file path to each issue
    for issue in checker.issues:
        issue["file"] = file_path

    return checker.issues


def is_likely_false_positive(issue: dict[str, Any]) -> bool:
    """Check if an issue is likely a false positive.

    Args:
        issue: Issue dictionary

    Returns:
        True if likely false positive
    """
    # Common false positive patterns
    false_positive_patterns = [
        # Standard library objects
        ("response", "status_code"),
        ("response", "json"),
        ("response", "text"),
        ("response", "headers"),
        ("request", "method"),
        ("request", "path"),
        # Pydantic models
        ("config", "model_dump"),
        ("data", "model_validate"),
        # AsyncIO
        ("result", "result"),
        ("result", "exception"),
    ]

    for var_pattern, attr_pattern in false_positive_patterns:
        if var_pattern in issue["var"].lower() and issue["attr"] == attr_pattern:
            return True

    return False


def main() -> None:
    """Main entry point for dict access checking."""
    # Only check staged files if running in pre-commit context
    if len(sys.argv) > 1 and sys.argv[1] == "--staged":
        # Get staged files from git
        import subprocess

        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            capture_output=True,
            text=True,
        )
        files = [
            Path(f)
            for f in result.stdout.strip().split("\n")
            if f.endswith(".py") and Path(f).exists()
        ]
    else:
        # Check all source files
        src_dir = Path("src")
        files = list(src_dir.rglob("*.py")) if src_dir.exists() else []

    all_issues = []
    for py_file in files:
        issues = check_file(py_file)
        # Filter out likely false positives
        real_issues = [issue for issue in issues if not is_likely_false_positive(issue)]
        all_issues.extend(real_issues)

    if all_issues:
        print("⚠️  Potential unsafe dictionary attribute access found:")
        print("=" * 70)

        # Group by file
        by_file: dict[Path, list[dict[str, Any]]] = {}
        for issue in all_issues:
            file_path = issue["file"]
            if file_path not in by_file:
                by_file[file_path] = []
            by_file[file_path].append(issue)

        for file_path, issues in sorted(by_file.items()):
            print(f"\n📁 {file_path}")
            for issue in sorted(issues, key=lambda x: x["line"]):
                func_ctx = f" in {issue['function']}()" if issue["function"] else ""
                print(
                    f"  L{issue['line']:4d}: {issue['var']}.{issue['attr']}{func_ctx}"
                )
                if issue["source"]:
                    print(f"        > {issue['source']}")

        print("\n💡 Suggestions:")
        print("  - If accessing dict values, use: result['key'] or result.get('key')")
        print("  - If it's an object, ensure it's properly typed")
        print("  - Consider using the AgentResponse schema for consistency")

        # Don't fail in pre-commit for now (warning only)
        if "--strict" in sys.argv:
            sys.exit(1)
    else:
        print("✅ No suspicious dictionary attribute access patterns found")


if __name__ == "__main__":
    main()
