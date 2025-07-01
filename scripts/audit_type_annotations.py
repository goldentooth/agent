#!/usr/bin/env python3
"""Audit and fix missing type annotations in the codebase."""

import ast
import sys
from pathlib import Path
from typing import Any


def find_untyped_functions(file_path: Path) -> list[dict[str, Any]]:
    """Find functions missing return type annotations.

    Args:
        file_path: Path to Python file to analyze

    Returns:
        List of dictionaries containing untyped function information
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            tree = ast.parse(f.read())
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return []

    untyped = []

    class FunctionVisitor(ast.NodeVisitor):
        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            if node.returns is None:  # Missing return annotation
                # Skip special methods and private functions in tests
                if file_path.parts[-2] == "tests" and node.name.startswith("_"):
                    return

                untyped.append(
                    {
                        "file": file_path,
                        "function": node.name,
                        "line": node.lineno,
                        "is_async": isinstance(node, ast.AsyncFunctionDef),
                    }
                )
            self.generic_visit(node)

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
            self.visit_FunctionDef(node)

    visitor = FunctionVisitor()
    visitor.visit(tree)

    return untyped


def find_any_return_types(file_path: Path) -> list[dict[str, Any]]:
    """Find functions that return 'Any' type.

    Args:
        file_path: Path to Python file to analyze

    Returns:
        List of functions with 'Any' return type
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            tree = ast.parse(f.read())
    except Exception:
        return []

    any_returns = []

    class AnyReturnVisitor(ast.NodeVisitor):
        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            if node.returns and isinstance(node.returns, ast.Name):
                if node.returns.id == "Any":
                    any_returns.append(
                        {"file": file_path, "function": node.name, "line": node.lineno}
                    )
            self.generic_visit(node)

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
            self.visit_FunctionDef(node)

    visitor = AnyReturnVisitor()
    visitor.visit(tree)

    return any_returns


def main() -> None:
    """Main entry point for type annotation audit."""
    src_dir = Path("src/goldentooth_agent")

    if not src_dir.exists():
        print(f"Error: Source directory {src_dir} not found")
        sys.exit(1)

    all_untyped = []
    all_any_returns = []
    total_functions = 0

    print("🔍 Auditing type annotations...")

    for py_file in sorted(src_dir.rglob("*.py")):
        # Skip __pycache__ and other generated files
        if "__pycache__" in str(py_file):
            continue

        untyped = find_untyped_functions(py_file)
        any_returns = find_any_return_types(py_file)

        all_untyped.extend(untyped)
        all_any_returns.extend(any_returns)

        # Count total functions (rough estimate)
        try:
            with open(py_file) as f:
                content = f.read()
                total_functions += content.count("def ")
        except Exception:
            pass

    # Report findings
    print("\n📊 Type Annotation Audit Results")
    print(f"{'='*60}")
    print(f"Total functions (estimate): {total_functions}")
    print(f"Functions missing return annotations: {len(all_untyped)}")
    print(f"Functions returning 'Any': {len(all_any_returns)}")
    print(
        f"Type annotation coverage: {((total_functions - len(all_untyped)) / total_functions * 100):.1f}%"
    )

    if all_untyped:
        print("\n❌ Functions missing return type annotations:")
        print(f"{'='*60}")

        # Group by file
        by_file = {}
        for item in all_untyped:
            file_path = item["file"]
            if file_path not in by_file:
                by_file[file_path] = []
            by_file[file_path].append(item)

        for file_path, functions in sorted(by_file.items()):
            try:
                rel_path = file_path.relative_to(Path.cwd())
            except ValueError:
                # If not relative to cwd, just use the path as is
                rel_path = file_path
            print(f"\n📁 {rel_path}")
            for func in sorted(functions, key=lambda x: x["line"]):
                async_marker = "async " if func.get("is_async") else ""
                print(f"  L{func['line']:4d}: {async_marker}{func['function']}()")

    if all_any_returns:
        print("\n⚠️  Functions returning 'Any' (consider more specific types):")
        print(f"{'='*60}")

        # Group by file
        by_file = {}
        for item in all_any_returns:
            file_path = item["file"]
            if file_path not in by_file:
                by_file[file_path] = []
            by_file[file_path].append(item)

        for file_path, functions in sorted(by_file.items()):
            try:
                rel_path = file_path.relative_to(Path.cwd())
            except ValueError:
                # If not relative to cwd, just use the path as is
                rel_path = file_path
            print(f"\n📁 {rel_path}")
            for func in sorted(functions, key=lambda x: x["line"]):
                print(f"  L{func['line']:4d}: {func['function']}() -> Any")

    # Exit with error code if issues found
    if all_untyped:
        print(
            f"\n❗ Action required: Add return type annotations to {len(all_untyped)} functions"
        )
        sys.exit(1)
    else:
        print("\n✅ All functions have return type annotations!")


if __name__ == "__main__":
    main()
