#!/usr/bin/env python3
"""
Test structure validation script.

Verifies that test files maintain a reasonable correspondence with source files,
preventing test structure from getting too out of sync with the codebase.

This script:
1. Maps source files to their expected test file locations
2. Identifies orphaned test files (tests without corresponding source)
3. Identifies missing test files (source files without tests)
4. Validates that test classes/functions target existing code elements
"""

import argparse
import ast
import re
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ValidationResult:
    """Results of test structure validation."""

    orphaned_tests: list[str]  # Test files without corresponding source
    missing_tests: list[str]  # Source files without corresponding tests
    misaligned_tests: list[tuple[str, str]]  # (test_file, issue_description)
    valid_mappings: int
    total_source_files: int
    total_test_files: int


class TestStructureValidator:
    """Validates that test structure aligns with source structure."""

    def __init__(self, source_root: Path, test_root: Path):
        self.source_root = source_root
        self.test_root = test_root

        # Patterns for files we should ignore
        self.ignore_patterns = {
            "__pycache__",
            ".pyc",
            "__init__.py",  # Usually don't need dedicated tests
            "conftest.py",  # Test configuration
        }

        # Directories that typically don't need 1:1 test mapping
        self.special_dirs = {
            "data",  # Data files
            "examples",  # Example code
            "scripts",  # Utility scripts
        }

    def get_source_files(self) -> list[Path]:
        """Get all Python source files that should have tests."""
        files = []
        for file_path in self.source_root.rglob("*.py"):
            if self._should_test_file(file_path):
                files.append(file_path)
        return sorted(files)

    def get_test_files(self) -> list[Path]:
        """Get all test files."""
        files = []
        for file_path in self.test_root.rglob("test_*.py"):
            files.append(file_path)
        return sorted(files)

    def _should_test_file(self, file_path: Path) -> bool:
        """Determine if a source file should have corresponding tests."""
        # Skip ignored patterns
        if any(pattern in str(file_path) for pattern in self.ignore_patterns):
            return False

        # Skip special directories that don't need 1:1 mapping
        rel_path = file_path.relative_to(self.source_root)
        if any(part in self.special_dirs for part in rel_path.parts):
            return False

        return True

    def map_source_to_test(self, source_file: Path) -> Path:
        """Map a source file to its expected test file location."""
        # Convert src/goldentooth_agent/core/rag/service.py
        # to tests/core/rag/test_service.py
        rel_path = source_file.relative_to(self.source_root)

        # Remove the leading 'goldentooth_agent' if present
        parts = list(rel_path.parts)
        if parts and parts[0] == "goldentooth_agent":
            parts = parts[1:]

        # Convert filename.py to test_filename.py
        if parts:
            stem = rel_path.stem
            parts[-1] = f"test_{stem}.py"

        return self.test_root / Path(*parts)

    def map_test_to_source(self, test_file: Path) -> Path:
        """Map a test file back to its expected source file."""
        # Convert tests/core/rag/test_service.py
        # to src/goldentooth_agent/core/rag/service.py
        rel_path = test_file.relative_to(self.test_root)

        # Convert test_filename.py to filename.py
        parts = list(rel_path.parts)
        if parts:
            test_name = rel_path.stem
            if test_name.startswith("test_"):
                source_name = test_name[5:] + ".py"  # Remove "test_" prefix
                parts[-1] = source_name

        # Add goldentooth_agent prefix
        return self.source_root / "goldentooth_agent" / Path(*parts)

    def extract_tested_symbols(self, test_file: Path) -> set[str]:
        """Extract symbols (classes/functions) that appear to be tested."""
        try:
            with open(test_file, encoding="utf-8") as f:
                content = f.read()
        except Exception:
            return set()

        tested_symbols = set()

        # Look for import statements that might indicate what's being tested
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    if node.names:
                        for alias in node.names:
                            if alias.name != "*":
                                tested_symbols.add(alias.name)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        # Extract last part of module name
                        parts = alias.name.split(".")
                        if parts:
                            tested_symbols.add(parts[-1])
        except SyntaxError:
            pass

        # Look for patterns in test method names and docstrings
        patterns = [
            r"def test_(\w+)",  # test_function_name
            r"class Test(\w+)",  # TestClassName
            r'@patch\([\'"].*\.(\w+)[\'"]',  # Mocked symbols
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content)
            tested_symbols.update(matches)

        return tested_symbols

    def extract_source_symbols(self, source_file: Path) -> set[str]:
        """Extract public symbols (classes/functions) from source file."""
        try:
            with open(source_file, encoding="utf-8") as f:
                content = f.read()
        except Exception:
            return set()

        symbols = set()

        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Include public functions (not starting with _)
                    if not node.name.startswith("_"):
                        symbols.add(node.name)
                elif isinstance(node, ast.ClassDef):
                    # Include public classes
                    if not node.name.startswith("_"):
                        symbols.add(node.name)
        except SyntaxError:
            pass

        return symbols

    def validate_structure(self) -> ValidationResult:
        """Perform comprehensive test structure validation."""
        source_files = self.get_source_files()
        test_files = self.get_test_files()

        orphaned_tests = []
        missing_tests = []
        misaligned_tests = []
        valid_mappings = 0

        # Check for orphaned test files (tests without corresponding source)
        for test_file in test_files:
            expected_source = self.map_test_to_source(test_file)
            if not expected_source.exists():
                rel_test = test_file.relative_to(self.test_root)
                rel_expected = expected_source.relative_to(self.source_root)
                orphaned_tests.append(f"{rel_test} → {rel_expected} (missing)")

        # Check for missing test files (source without tests)
        tested_source_files = set()
        for test_file in test_files:
            expected_source = self.map_test_to_source(test_file)
            if expected_source.exists():
                tested_source_files.add(expected_source)
                valid_mappings += 1

        for source_file in source_files:
            expected_test = self.map_source_to_test(source_file)
            if not expected_test.exists():
                rel_source = source_file.relative_to(self.source_root)
                rel_expected = expected_test.relative_to(self.test_root)
                missing_tests.append(f"{rel_source} → {rel_expected} (missing)")

        # Advanced validation: check if tested symbols exist in source
        for test_file in test_files:
            expected_source = self.map_test_to_source(test_file)
            if expected_source.exists():
                tested_symbols = self.extract_tested_symbols(test_file)
                source_symbols = self.extract_source_symbols(expected_source)

                # Check for symbols tested but not present in source
                missing_symbols = tested_symbols - source_symbols
                if (
                    missing_symbols and len(missing_symbols) > 2
                ):  # Allow some flexibility
                    rel_test = test_file.relative_to(self.test_root)
                    symbol_list = ", ".join(sorted(missing_symbols)[:5])
                    if len(missing_symbols) > 5:
                        symbol_list += f" (and {len(missing_symbols) - 5} more)"
                    misaligned_tests.append(
                        (
                            str(rel_test),
                            f"Tests symbols not found in source: {symbol_list}",
                        )
                    )

        return ValidationResult(
            orphaned_tests=orphaned_tests,
            missing_tests=missing_tests,
            misaligned_tests=misaligned_tests,
            valid_mappings=valid_mappings,
            total_source_files=len(source_files),
            total_test_files=len(test_files),
        )

    def print_validation_results(
        self, result: ValidationResult, show_details: bool = True
    ):
        """Print validation results in a human-readable format."""
        print("🧪 Test Structure Validation Results")
        print("=" * 50)

        # Overall statistics
        print("📊 Overall Statistics:")
        print(f"   • Source files: {result.total_source_files}")
        print(f"   • Test files: {result.total_test_files}")
        print(f"   • Valid mappings: {result.valid_mappings}")

        coverage_pct = (
            (result.valid_mappings / result.total_source_files * 100)
            if result.total_source_files > 0
            else 0
        )
        print(f"   • Test coverage ratio: {coverage_pct:.1f}%")

        # Issues summary
        total_issues = (
            len(result.orphaned_tests)
            + len(result.missing_tests)
            + len(result.misaligned_tests)
        )

        if total_issues == 0:
            print("\n✅ Perfect! Test structure is well-aligned with source structure.")
            return

        print(f"\n⚠️  Found {total_issues} structural issues:")

        # Orphaned tests
        if result.orphaned_tests:
            print(f"\n🗂️  Orphaned Tests ({len(result.orphaned_tests)} files):")
            print("   Tests without corresponding source files")
            if show_details:
                for orphan in result.orphaned_tests[:10]:
                    print(f"   • {orphan}")
                if len(result.orphaned_tests) > 10:
                    print(f"   ... and {len(result.orphaned_tests) - 10} more")
            else:
                print("   Run with --verbose to see details")

        # Missing tests
        if result.missing_tests:
            print(f"\n📝 Missing Tests ({len(result.missing_tests)} files):")
            print("   Source files without corresponding test files")
            if show_details:
                for missing in result.missing_tests[:10]:
                    print(f"   • {missing}")
                if len(result.missing_tests) > 10:
                    print(f"   ... and {len(result.missing_tests) - 10} more")
            else:
                print("   Run with --verbose to see details")

        # Misaligned tests
        if result.misaligned_tests:
            print(f"\n🎯 Misaligned Tests ({len(result.misaligned_tests)} files):")
            print("   Tests that may not match their source file content")
            if show_details:
                for test_file, issue in result.misaligned_tests[:5]:
                    print(f"   • {test_file}: {issue}")
                if len(result.misaligned_tests) > 5:
                    print(f"   ... and {len(result.misaligned_tests) - 5} more")
            else:
                print("   Run with --verbose to see details")

        # Recommendations
        print("\n💡 Recommendations:")
        if result.missing_tests:
            print("   1. Create missing test files for better coverage")
        if result.orphaned_tests:
            print("   2. Review orphaned tests - rename, move, or remove them")
        if result.misaligned_tests:
            print("   3. Check misaligned tests for outdated imports/references")


def main():
    parser = argparse.ArgumentParser(
        description="Validate test structure alignment with source code"
    )
    parser.add_argument(
        "--source-root",
        type=Path,
        default=Path("src"),
        help="Root directory of source code",
    )
    parser.add_argument(
        "--test-root", type=Path, default=Path("tests"), help="Root directory of tests"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed output"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with non-zero code if any issues found",
    )
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    # Ensure paths exist
    if not args.source_root.exists():
        print(f"❌ Source root not found: {args.source_root}")
        sys.exit(1)

    if not args.test_root.exists():
        print(f"❌ Test root not found: {args.test_root}")
        sys.exit(1)

    validator = TestStructureValidator(args.source_root, args.test_root)
    result = validator.validate_structure()

    if args.json:
        import json

        json_result = {
            "orphaned_tests": result.orphaned_tests,
            "missing_tests": result.missing_tests,
            "misaligned_tests": [
                {"file": f, "issue": i} for f, i in result.misaligned_tests
            ],
            "valid_mappings": result.valid_mappings,
            "total_source_files": result.total_source_files,
            "total_test_files": result.total_test_files,
            "issues_found": len(result.orphaned_tests)
            + len(result.missing_tests)
            + len(result.misaligned_tests),
        }
        print(json.dumps(json_result, indent=2))
    else:
        validator.print_validation_results(result, args.verbose)

    # Exit with error code if issues found and strict mode enabled
    total_issues = (
        len(result.orphaned_tests)
        + len(result.missing_tests)
        + len(result.misaligned_tests)
    )
    if args.strict and total_issues > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
