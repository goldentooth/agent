#!/usr/bin/env python3
"""
Script to find potentially orphaned functions and classes in the goldentooth-agent codebase.
Uses AST analysis to identify definitions that may not be used anywhere.
"""

import ast
import sys
from collections import defaultdict
from pathlib import Path


class CodeAnalyzer(ast.NodeVisitor):
    """AST visitor to collect function/class definitions and their usage."""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.definitions: dict[str, list[tuple[str, int]]] = defaultdict(list)
        self.usages: set[str] = set()
        self.imports: set[str] = set()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        # Skip private methods, special methods, and test functions
        if not (node.name.startswith("_") or node.name.startswith("test_")):
            self.definitions["functions"].append((node.name, node.lineno))
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        # Skip private classes and test classes
        if not (node.name.startswith("_") or node.name.startswith("Test")):
            self.definitions["classes"].append((node.name, node.lineno))
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        if isinstance(node.ctx, ast.Load):
            self.usages.add(node.id)
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        self.usages.add(node.attr)
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self.imports.add(alias.name.split(".")[0])
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module:
            self.imports.add(node.module.split(".")[0])
        for alias in node.names:
            self.imports.add(alias.name)
        self.generic_visit(node)


def analyze_file(file_path: Path) -> CodeAnalyzer:
    """Analyze a single Python file for definitions and usages."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content, filename=str(file_path))
        analyzer = CodeAnalyzer(file_path)
        analyzer.visit(tree)
        return analyzer
    except (SyntaxError, UnicodeDecodeError) as e:
        print(f"Error parsing {file_path}: {e}", file=sys.stderr)
        return CodeAnalyzer(file_path)


def find_orphaned_code(src_dir: Path) -> None:
    """Find potentially orphaned functions and classes in the codebase."""

    # Collect all Python files
    python_files = list(src_dir.rglob("*.py"))
    if not python_files:
        print(f"No Python files found in {src_dir}")
        return

    print(f"Analyzing {len(python_files)} Python files...")

    # Analyze all files
    all_definitions: dict[str, list[tuple[Path, int]]] = defaultdict(list)
    all_usages: set[str] = set()
    all_imports: set[str] = set()

    for file_path in python_files:
        analyzer = analyze_file(file_path)

        # Collect definitions
        for func_name, line_no in analyzer.definitions["functions"]:
            all_definitions[func_name].append((file_path, line_no))
        for class_name, line_no in analyzer.definitions["classes"]:
            all_definitions[class_name].append((file_path, line_no))

        # Collect usages and imports
        all_usages.update(analyzer.usages)
        all_imports.update(analyzer.imports)

    # Find potentially orphaned definitions
    orphaned = []
    for name, locations in all_definitions.items():
        # Skip if used anywhere or imported
        if name not in all_usages and name not in all_imports:
            # Skip common patterns that are likely not orphaned
            if not (
                name in ["main", "app", "cli"]  # Entry points
                or name.endswith("Error")
                or name.endswith("Exception")  # Exceptions
                or name.startswith("test_")  # Test functions
                or name.startswith("Test")  # Test classes
                or name.endswith("Config")  # Configuration classes
                or len(locations) > 1  # Defined in multiple places (likely used)
            ):
                orphaned.extend([(name, path, line) for path, line in locations])

    # Report results
    if orphaned:
        print(f"\nFound {len(orphaned)} potentially orphaned definitions:")
        print("=" * 60)

        # Group by file for better readability
        by_file = defaultdict(list)
        for name, path, line in orphaned:
            by_file[path].append((name, line))

        for file_path in sorted(by_file.keys()):
            print(f"\n{file_path.relative_to(src_dir)}:")
            for name, line in sorted(by_file[file_path], key=lambda x: x[1]):
                print(f"  Line {line:3d}: {name}")
    else:
        print("\nNo obviously orphaned functions or classes found!")

    print("\nSummary:")
    print(f"  Total definitions: {len(all_definitions)}")
    print(f"  Potentially orphaned: {len(orphaned)}")
    print("\nNote: This analysis may have false positives. Manual review recommended.")


if __name__ == "__main__":
    src_dir = Path("src/goldentooth_agent")
    if not src_dir.exists():
        print(f"Source directory {src_dir} not found!")
        sys.exit(1)

    find_orphaned_code(src_dir)
