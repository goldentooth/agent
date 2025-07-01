#!/usr/bin/env python3
"""Analyze code complexity metrics for the goldentooth_agent codebase."""

import ast
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class FunctionComplexity:
    """Store complexity metrics for a function."""

    name: str
    lineno: int
    complexity: int
    cognitive_complexity: int
    lines: int
    parameters: int


@dataclass
class FileComplexity:
    """Store complexity metrics for a file."""

    path: Path
    functions: list[FunctionComplexity]
    total_complexity: int
    avg_complexity: float
    max_complexity: int


class ComplexityAnalyzer(ast.NodeVisitor):
    """AST visitor to calculate cyclomatic complexity."""

    def __init__(self):
        self.functions: list[FunctionComplexity] = []
        self.current_complexity = 0
        self.current_cognitive = 0
        self.nesting_level = 0

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit a function definition."""
        # Save previous state
        prev_complexity = self.current_complexity
        prev_cognitive = self.current_cognitive
        prev_nesting = self.nesting_level

        # Reset for new function
        self.current_complexity = 1  # Base complexity
        self.current_cognitive = 0
        self.nesting_level = 0

        # Calculate function metrics
        start_line = node.lineno
        end_line = node.end_lineno or node.lineno
        lines = end_line - start_line + 1
        parameters = len(node.args.args) + len(node.args.kwonlyargs)

        # Visit function body
        self.generic_visit(node)

        # Store function metrics
        self.functions.append(
            FunctionComplexity(
                name=node.name,
                lineno=node.lineno,
                complexity=self.current_complexity,
                cognitive_complexity=self.current_cognitive,
                lines=lines,
                parameters=parameters,
            )
        )

        # Restore previous state
        self.current_complexity = prev_complexity
        self.current_cognitive = prev_cognitive
        self.nesting_level = prev_nesting

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Visit an async function definition."""
        self.visit_FunctionDef(node)  # Treat the same as regular functions

    def visit_If(self, node: ast.If) -> None:
        """Visit an if statement."""
        self.current_complexity += 1
        self.current_cognitive += 1 + self.nesting_level
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1

    def visit_While(self, node: ast.While) -> None:
        """Visit a while loop."""
        self.current_complexity += 1
        self.current_cognitive += 1 + self.nesting_level
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1

    def visit_For(self, node: ast.For) -> None:
        """Visit a for loop."""
        self.current_complexity += 1
        self.current_cognitive += 1 + self.nesting_level
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        """Visit an except handler."""
        self.current_complexity += 1
        self.current_cognitive += 1 + self.nesting_level
        self.generic_visit(node)

    def visit_With(self, node: ast.With) -> None:
        """Visit a with statement."""
        self.current_cognitive += self.nesting_level
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1

    def visit_BoolOp(self, node: ast.BoolOp) -> None:
        """Visit a boolean operation (and/or)."""
        # Each additional condition adds complexity
        self.current_complexity += len(node.values) - 1
        self.current_cognitive += len(node.values) - 1
        self.generic_visit(node)

    def visit_ListComp(self, node: ast.ListComp) -> None:
        """Visit a list comprehension."""
        self.current_complexity += sum(1 for _ in node.generators)
        self.current_cognitive += 1
        self.generic_visit(node)

    def visit_DictComp(self, node: ast.DictComp) -> None:
        """Visit a dict comprehension."""
        self.current_complexity += sum(1 for _ in node.generators)
        self.current_cognitive += 1
        self.generic_visit(node)

    def visit_SetComp(self, node: ast.SetComp) -> None:
        """Visit a set comprehension."""
        self.current_complexity += sum(1 for _ in node.generators)
        self.current_cognitive += 1
        self.generic_visit(node)


def analyze_file(file_path: Path) -> FileComplexity:
    """Analyze complexity of a single Python file."""
    try:
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=str(file_path))

        analyzer = ComplexityAnalyzer()
        analyzer.visit(tree)

        if analyzer.functions:
            total_complexity = sum(f.complexity for f in analyzer.functions)
            avg_complexity = total_complexity / len(analyzer.functions)
            max_complexity = max(f.complexity for f in analyzer.functions)
        else:
            total_complexity = 0
            avg_complexity = 0
            max_complexity = 0

        return FileComplexity(
            path=file_path,
            functions=analyzer.functions,
            total_complexity=total_complexity,
            avg_complexity=avg_complexity,
            max_complexity=max_complexity,
        )
    except Exception:
        # Return empty metrics for files that can't be parsed
        return FileComplexity(
            path=file_path,
            functions=[],
            total_complexity=0,
            avg_complexity=0,
            max_complexity=0,
        )


def try_radon() -> bool:
    """Try to use radon if available."""
    try:
        result = subprocess.run(["radon", "--version"], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False


def analyze_with_radon(src_dir: Path) -> None:
    """Use radon for more detailed analysis if available."""
    print("\n=== RADON ANALYSIS (if available) ===")

    # Cyclomatic Complexity
    print("\nCyclomatic Complexity (CC):")
    subprocess.run(
        [
            "radon",
            "cc",
            str(src_dir),
            "-s",  # Show complexity score
            "-a",  # Show average
            "--total-average",
        ]
    )

    # Maintainability Index
    print("\nMaintainability Index (MI):")
    subprocess.run(["radon", "mi", str(src_dir), "-s"])  # Show MI score

    # Raw metrics
    print("\nRaw Metrics:")
    subprocess.run(["radon", "raw", str(src_dir), "-s"])  # Summary


def main():
    """Main function to analyze code complexity."""
    project_root = Path(__file__).parent.parent
    src_dir = project_root / "src" / "goldentooth_agent"

    if not src_dir.exists():
        print(f"ERROR: Source directory not found: {src_dir}")
        return 1

    # Collect all Python files
    py_files = list(src_dir.rglob("*.py"))
    py_files = [f for f in py_files if "__pycache__" not in str(f)]

    print(f"Analyzing {len(py_files)} Python files...")

    # Analyze each file
    all_results: list[FileComplexity] = []
    all_functions: list[tuple[Path, FunctionComplexity]] = []

    for file_path in py_files:
        result = analyze_file(file_path)
        all_results.append(result)
        for func in result.functions:
            all_functions.append((file_path, func))

    # Sort by complexity
    complex_functions = sorted(
        all_functions, key=lambda x: x[1].complexity, reverse=True
    )

    # Display results
    print("\n=== COMPLEXITY ANALYSIS ===")
    print("\nComplexity Grades:")
    print("  A: 1-5 (Simple)")
    print("  B: 6-10 (Slightly complex)")
    print("  C: 11-20 (Complex)")
    print("  D: 21-50 (Very complex)")
    print("  F: 50+ (Extremely complex)")

    # Top complex functions
    print("\n=== TOP 20 MOST COMPLEX FUNCTIONS ===")
    print(
        f"{'Function':<50} {'File':<40} {'CC':>4} {'Cog':>4} {'Lines':>6} {'Grade':>6}"
    )
    print("-" * 110)

    for file_path, func in complex_functions[:20]:
        rel_path = file_path.relative_to(src_dir)
        func_name = f"{func.name}()"

        # Determine grade
        if func.complexity <= 5:
            grade = "A"
        elif func.complexity <= 10:
            grade = "B"
        elif func.complexity <= 20:
            grade = "C"
        elif func.complexity <= 50:
            grade = "D"
        else:
            grade = "F"

        print(
            f"{func_name:<50} {str(rel_path):<40} {func.complexity:>4} {func.cognitive_complexity:>4} {func.lines:>6} {grade:>6}"
        )

    # Files with highest average complexity
    complex_files = sorted(
        [f for f in all_results if f.functions],
        key=lambda x: x.avg_complexity,
        reverse=True,
    )

    print("\n\n=== TOP 10 FILES BY AVERAGE COMPLEXITY ===")
    print(f"{'File':<60} {'Avg CC':>7} {'Max CC':>7} {'Functions':>10}")
    print("-" * 85)

    for file_result in complex_files[:10]:
        rel_path = file_result.path.relative_to(src_dir)
        print(
            f"{str(rel_path):<60} {file_result.avg_complexity:>7.1f} {file_result.max_complexity:>7} {len(file_result.functions):>10}"
        )

    # Summary statistics
    total_functions = sum(len(f.functions) for f in all_results)
    total_complexity = sum(f.total_complexity for f in all_results)
    avg_complexity = total_complexity / total_functions if total_functions > 0 else 0

    print("\n\n=== SUMMARY STATISTICS ===")
    print(f"Total files analyzed: {len(py_files)}")
    print(f"Total functions: {total_functions}")
    print(f"Average complexity per function: {avg_complexity:.1f}")

    # Complexity distribution
    complexity_ranges = {
        "A (1-5)": 0,
        "B (6-10)": 0,
        "C (11-20)": 0,
        "D (21-50)": 0,
        "F (50+)": 0,
    }

    for _, func in all_functions:
        if func.complexity <= 5:
            complexity_ranges["A (1-5)"] += 1
        elif func.complexity <= 10:
            complexity_ranges["B (6-10)"] += 1
        elif func.complexity <= 20:
            complexity_ranges["C (11-20)"] += 1
        elif func.complexity <= 50:
            complexity_ranges["D (21-50)"] += 1
        else:
            complexity_ranges["F (50+)"] += 1

    print("\nComplexity Distribution:")
    for grade, count in complexity_ranges.items():
        pct = (count / total_functions * 100) if total_functions > 0 else 0
        bar = "█" * int(pct / 2)
        print(f"  {grade}: {count:>5} ({pct:>5.1f}%) {bar}")

    # Recommendations
    print("\n\n=== REFACTORING RECOMMENDATIONS ===")
    print("Functions with complexity > 20 should be refactored:")

    refactor_candidates = [
        (f, func) for f, func in complex_functions if func.complexity > 20
    ]

    if refactor_candidates:
        for file_path, func in refactor_candidates[:10]:
            rel_path = file_path.relative_to(src_dir)
            print(
                f"  - {rel_path}:{func.lineno} - {func.name}() [CC: {func.complexity}]"
            )

        if len(refactor_candidates) > 10:
            print(f"  ... and {len(refactor_candidates) - 10} more")
    else:
        print("  No functions exceed complexity threshold of 20!")

    # Try to use radon if available
    if try_radon():
        analyze_with_radon(src_dir)

    return 0


if __name__ == "__main__":
    sys.exit(main())
