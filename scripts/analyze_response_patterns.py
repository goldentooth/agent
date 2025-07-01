#!/usr/bin/env python3
"""Analyze response handling patterns in the codebase."""

import ast
from collections import defaultdict
from pathlib import Path
from typing import Any


class ResponsePatternAnalyzer(ast.NodeVisitor):
    """Analyze how responses are handled throughout the codebase."""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.patterns = {
            "dict_access": [],  # response["key"]
            "attr_access": [],  # response.key
            "mixed_access": False,  # both patterns in same file
        }
        self.current_function: str | None = None

        # Track response-like variable names
        self.response_vars = {
            "response",
            "result",
            "output",
            "data",
            "payload",
            "rag_result",
            "agent_result",
            "api_response",
        }

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Track current function."""
        old_func = self.current_function
        self.current_function = node.name
        self.generic_visit(node)
        self.current_function = old_func

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Track async function."""
        self.visit_FunctionDef(node)

    def visit_Subscript(self, node: ast.Subscript) -> None:
        """Track dict-style access: obj["key"]."""
        if isinstance(node.value, ast.Name):
            var_name = node.value.id
            if any(resp in var_name.lower() for resp in self.response_vars):
                key = None
                if isinstance(node.slice, ast.Constant):
                    key = node.slice.value

                self.patterns["dict_access"].append(
                    {
                        "var": var_name,
                        "key": key,
                        "line": node.lineno,
                        "function": self.current_function,
                    }
                )
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        """Track attribute access: obj.attr."""
        if isinstance(node.value, ast.Name):
            var_name = node.value.id
            if any(resp in var_name.lower() for resp in self.response_vars):
                self.patterns["attr_access"].append(
                    {
                        "var": var_name,
                        "attr": node.attr,
                        "line": node.lineno,
                        "function": self.current_function,
                    }
                )
        self.generic_visit(node)

    def finalize(self) -> None:
        """Finalize analysis."""
        has_dict = bool(self.patterns["dict_access"])
        has_attr = bool(self.patterns["attr_access"])
        self.patterns["mixed_access"] = has_dict and has_attr


def analyze_file(file_path: Path) -> dict[str, Any]:
    """Analyze a single file for response patterns.

    Args:
        file_path: Path to Python file

    Returns:
        Analysis results
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            tree = ast.parse(f.read())
    except Exception as e:
        return {"error": str(e)}

    analyzer = ResponsePatternAnalyzer(file_path)
    analyzer.visit(tree)
    analyzer.finalize()

    return analyzer.patterns


def analyze_codebase() -> dict[Path, dict[str, Any]]:
    """Analyze response patterns across the entire codebase.

    Returns:
        Dictionary mapping file paths to their patterns
    """
    results = {}
    src_dir = Path("src")

    if not src_dir.exists():
        print("Error: src directory not found")
        return results

    for py_file in sorted(src_dir.rglob("*.py")):
        if "__pycache__" in str(py_file):
            continue

        patterns = analyze_file(py_file)
        if patterns.get("dict_access") or patterns.get("attr_access"):
            results[py_file] = patterns

    return results


def print_analysis_report(results: dict[Path, dict[str, Any]]) -> None:
    """Print a formatted analysis report.

    Args:
        results: Analysis results
    """
    print("🔍 Response Handling Pattern Analysis")
    print("=" * 70)

    # Statistics
    total_files = len(results)
    dict_only_files = sum(
        1 for p in results.values() if p["dict_access"] and not p["attr_access"]
    )
    attr_only_files = sum(
        1 for p in results.values() if p["attr_access"] and not p["dict_access"]
    )
    mixed_files = sum(1 for p in results.values() if p["mixed_access"])

    print("\n📊 Statistics:")
    print(f"  Total files with response handling: {total_files}")
    print(f"  Dictionary access only: {dict_only_files}")
    print(f"  Attribute access only: {attr_only_files}")
    print(f"  Mixed patterns: {mixed_files}")

    # Detailed breakdown
    if mixed_files > 0:
        print("\n⚠️  Files with mixed access patterns (potential issues):")
        print("=" * 70)
        for file_path, patterns in sorted(results.items()):
            if patterns["mixed_access"]:
                print(f"\n📁 {file_path}")

                print("  Dictionary access:")
                for access in patterns["dict_access"][:3]:  # Show first 3
                    func = f" in {access['function']}()" if access["function"] else ""
                    key = f"['{access['key']}']" if access["key"] else "[...]"
                    print(f"    L{access['line']:4d}: {access['var']}{key}{func}")

                print("  Attribute access:")
                for access in patterns["attr_access"][:3]:  # Show first 3
                    func = f" in {access['function']}()" if access["function"] else ""
                    print(
                        f"    L{access['line']:4d}: {access['var']}.{access['attr']}{func}"
                    )

    # Common patterns
    print("\n📋 Common Access Patterns:")

    # Collect all keys and attributes
    all_dict_keys: dict[str, int] = defaultdict(int)
    all_attrs: dict[str, int] = defaultdict(int)

    for patterns in results.values():
        for access in patterns["dict_access"]:
            if access["key"]:
                all_dict_keys[access["key"]] += 1

        for access in patterns["attr_access"]:
            all_attrs[access["attr"]] += 1

    if all_dict_keys:
        print("\n  Most common dictionary keys:")
        for key, count in sorted(all_dict_keys.items(), key=lambda x: -x[1])[:10]:
            print(f"    '{key}': {count} occurrences")

    if all_attrs:
        print("\n  Most common attributes:")
        for attr, count in sorted(all_attrs.items(), key=lambda x: -x[1])[:10]:
            print(f"    .{attr}: {count} occurrences")


def main() -> None:
    """Main entry point."""
    print("Analyzing response handling patterns...")
    results = analyze_codebase()

    if results:
        print_analysis_report(results)

        # Recommendations
        print("\n💡 Recommendations:")
        print("  1. Use AgentResponse schema for consistent handling")
        print("  2. Standardize on either dict or object access patterns")
        print("  3. Add type hints to clarify expected response types")
        print("  4. Use runtime validation for external API responses")
    else:
        print("No response handling patterns found in the codebase.")


if __name__ == "__main__":
    main()
