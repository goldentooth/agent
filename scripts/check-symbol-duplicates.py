#!/usr/bin/env python3
"""Check for duplicate symbol definitions across Python files."""

import ast
import sys
from collections import defaultdict
from pathlib import Path


def extract_symbols(file_path: Path) -> set[str]:
    """Extract all defined symbols from a Python file."""
    symbols = set()

    try:
        with open(file_path, encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(file_path))

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                symbols.add(node.name)
            elif isinstance(node, ast.AsyncFunctionDef):
                symbols.add(node.name)
            elif isinstance(node, ast.ClassDef):
                symbols.add(node.name)
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        symbols.add(target.id)
                    elif isinstance(target, ast.Tuple):
                        for elt in target.elts:
                            if isinstance(elt, ast.Name):
                                symbols.add(elt.id)
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                symbols.add(node.target.id)

    except Exception as e:
        print(f"Error parsing {file_path}: {e}", file=sys.stderr)

    return symbols


def find_python_files(root_dir: Path) -> list[Path]:
    """Find all Python files in the project."""
    python_files = []

    # Skip certain directories
    skip_dirs = {
        ".venv",
        "__pycache__",
        ".git",
        "build",
        "dist",
        ".tox",
        ".pytest_cache",
        ".mypy_cache",
    }

    for file_path in root_dir.rglob("*.py"):
        # Skip files in excluded directories
        if any(part in skip_dirs for part in file_path.parts):
            continue
        python_files.append(file_path)

    return python_files


def main():
    """Main function to check for duplicate symbols."""
    root_dir = Path.cwd()

    # Map symbols to files that define them
    symbol_to_files: dict[str, list[Path]] = defaultdict(list)

    print("Scanning Python files for symbol definitions...")
    python_files = find_python_files(root_dir)

    for file_path in python_files:
        symbols = extract_symbols(file_path)
        for symbol in symbols:
            symbol_to_files[symbol].append(file_path)

    # Find duplicates
    duplicates = {
        symbol: files for symbol, files in symbol_to_files.items() if len(files) > 1
    }

    if not duplicates:
        print("\nNo duplicate symbols found!")
        return

    # Categorize duplicates
    type_variables = set()
    common_methods = set()
    example_symbols = set()
    test_symbols = set()
    helper_functions = set()
    actual_duplicates = set()

    # Common generic type variable names
    type_var_names = {
        "T",
        "K",
        "V",
        "E",
        "P",
        "R",
        "S",
        "U",
        "Input",
        "Output",
        "A",
        "B",
        "C",
        "D",
    }

    # Common method names that are often duplicated
    common_method_names = {
        "get",
        "set",
        "run",
        "process",
        "handle",
        "create",
        "update",
        "delete",
        "start",
        "stop",
        "init",
        "cleanup",
        "setup",
        "teardown",
        "reset",
        "load",
        "save",
        "read",
        "write",
        "parse",
        "format",
        "validate",
        "execute",
        "call",
        "__init__",
        "__str__",
        "__repr__",
        "__call__",
        "decorator",
        "wrapper",
        "handler",
        "processor",
        "transform",
        "map",
        "filter",
        "reduce",
        "apply",
        "compose",
        "pipe",
    }

    # Common test helper names
    test_helper_names = {
        "setup_method",
        "teardown_method",
        "setup_class",
        "teardown_class",
        "setup",
        "teardown",
        "fixture",
        "mock",
        "patch",
        "assert_equal",
    }

    for symbol, files in sorted(duplicates.items()):
        # Check if all files are in examples directory
        if all("examples" in str(f) for f in files):
            example_symbols.add(symbol)
        # Check if all files are in tests directory
        elif all("test" in str(f) for f in files):
            test_symbols.add(symbol)
        # Check if it's a type variable
        elif symbol in type_var_names:
            type_variables.add(symbol)
        # Check if it's a common method name
        elif symbol in common_method_names:
            common_methods.add(symbol)
        # Check if it's a test helper
        elif symbol in test_helper_names:
            helper_functions.add(symbol)
        # Check if it's a likely helper function
        elif (
            symbol.startswith("_")
            or symbol.endswith("_helper")
            or symbol.endswith("_util")
        ):
            helper_functions.add(symbol)
        else:
            actual_duplicates.add(symbol)

    # Print categorized results
    print("\n## Symbol Uniqueness Analysis\n")

    if type_variables:
        print("### Type Variables (Probably OK to duplicate)")
        for symbol in sorted(type_variables):
            print(f"  - {symbol}: {len(duplicates[symbol])} occurrences")
            for f in duplicates[symbol][:3]:  # Show first 3 files
                print(f"    - {f.relative_to(root_dir)}")
            if len(duplicates[symbol]) > 3:
                print(f"    ... and {len(duplicates[symbol]) - 3} more")

    if common_methods:
        print("\n### Common Methods (Probably OK in different contexts)")
        for symbol in sorted(common_methods):
            print(f"  - {symbol}: {len(duplicates[symbol])} occurrences")
            for f in duplicates[symbol][:3]:
                print(f"    - {f.relative_to(root_dir)}")
            if len(duplicates[symbol]) > 3:
                print(f"    ... and {len(duplicates[symbol]) - 3} more")

    if example_symbols:
        print("\n### Example Code Symbols (Probably OK)")
        for symbol in sorted(example_symbols):
            print(f"  - {symbol}: {len(duplicates[symbol])} occurrences in examples/")

    if test_symbols:
        print("\n### Test Symbols (Probably OK)")
        for symbol in sorted(test_symbols):
            print(f"  - {symbol}: {len(duplicates[symbol])} occurrences in tests/")

    if helper_functions:
        print("\n### Helper Functions (Might be OK to duplicate)")
        for symbol in sorted(helper_functions):
            print(f"  - {symbol}: {len(duplicates[symbol])} occurrences")
            for f in duplicates[symbol][:3]:
                print(f"    - {f.relative_to(root_dir)}")
            if len(duplicates[symbol]) > 3:
                print(f"    ... and {len(duplicates[symbol]) - 3} more")

    if actual_duplicates:
        print("\n### Actual Duplicates (Need investigation)")
        for symbol in sorted(actual_duplicates):
            print(f"\n  - **{symbol}**: {len(duplicates[symbol])} occurrences")
            for f in duplicates[symbol]:
                print(f"    - {f.relative_to(root_dir)}")

    print("\n### Summary")
    print(f"  - Total duplicate symbols: {len(duplicates)}")
    print(f"  - Type variables: {len(type_variables)}")
    print(f"  - Common methods: {len(common_methods)}")
    print(f"  - Example symbols: {len(example_symbols)}")
    print(f"  - Test symbols: {len(test_symbols)}")
    print(f"  - Helper functions: {len(helper_functions)}")
    print(f"  - Actual duplicates needing investigation: {len(actual_duplicates)}")


if __name__ == "__main__":
    main()
