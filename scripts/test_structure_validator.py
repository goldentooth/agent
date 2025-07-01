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

        # Test patterns that indicate module-level or integration testing
        self.module_test_patterns = {
            "test_integration.py",
            "test_basic.py",
            "test_computed.py",
            "test_eventflow.py",
            "test_queries.py",
            "test_snapshots.py",
            "test_refactored.py",
        }

        # Root-level test files that don't map to source files
        self.framework_test_patterns = {
            "test_mock_compliance.py",
            "test_sanity.py",
            "conftest.py",
        }

        # Directories that contain cross-module integration tests
        self.integration_test_dirs = {
            "integration",
            "e2e",
            "system",
        }

        # Modules that use modular testing (multiple test files per module)
        self.modular_test_modules = {
            "context",
            "flow_engine",
            "rag",
            "embeddings",
            "agent_codebase",
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

    def is_module_level_test(self, test_file: Path) -> bool:
        """Check if this is a module-level test that doesn't map to a single source file."""
        test_name = test_file.name

        # Check if it's a known module-level test pattern
        if test_name in self.module_test_patterns:
            return True

        # Check if it's in a module that uses modular testing
        rel_path = test_file.relative_to(self.test_root)
        module_parts = rel_path.parts[:-1]  # Exclude filename

        for part in module_parts:
            if part in self.modular_test_modules:
                return True

        return False

    def is_integration_test(self, test_file: Path) -> bool:
        """Check if this is an integration test that tests cross-module functionality."""
        rel_path = test_file.relative_to(self.test_root)
        test_parts = rel_path.parts[:-1]  # Exclude filename

        # Check if it's in an integration test directory
        for part in test_parts:
            if part in self.integration_test_dirs:
                return True

        return False

    def is_framework_test(self, test_file: Path) -> bool:
        """Check if this is a framework test that doesn't map to source code."""
        test_name = test_file.name
        return test_name in self.framework_test_patterns

    def get_module_source_dir(self, test_file: Path) -> Path | None:
        """Get the source directory for a module-level test."""
        rel_path = test_file.relative_to(self.test_root)
        module_parts = list(rel_path.parts[:-1])  # Exclude filename

        if module_parts:
            source_dir = self.source_root / "goldentooth_agent" / Path(*module_parts)
            if source_dir.exists() and source_dir.is_dir():
                return source_dir

        return None

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
            if self.is_framework_test(test_file):
                # Framework tests are valid by definition (testing framework itself)
                valid_mappings += 1
            elif self.is_integration_test(test_file):
                # Integration tests are valid by definition (cross-module testing)
                valid_mappings += 1
            elif self.is_module_level_test(test_file):
                # For module-level tests, check if the source module exists
                source_dir = self.get_module_source_dir(test_file)
                if source_dir and source_dir.exists():
                    valid_mappings += 1
                else:
                    rel_test = test_file.relative_to(self.test_root)
                    orphaned_tests.append(
                        f"{rel_test} → module-level test without source module"
                    )
            else:
                # For file-level tests, check specific source file
                expected_source = self.map_test_to_source(test_file)
                if not expected_source.exists():
                    rel_test = test_file.relative_to(self.test_root)
                    rel_expected = expected_source.relative_to(self.source_root)
                    orphaned_tests.append(f"{rel_test} → {rel_expected} (missing)")

        # Check for missing test files (source without tests)
        tested_source_files = set()
        tested_source_modules = set()

        for test_file in test_files:
            if self.is_framework_test(test_file):
                # Framework tests don't map to source files
                continue
            elif self.is_integration_test(test_file):
                # Integration tests don't map to specific source files
                continue
            elif self.is_module_level_test(test_file):
                # Module-level test covers the entire source directory
                source_dir = self.get_module_source_dir(test_file)
                if source_dir and source_dir.exists():
                    tested_source_modules.add(source_dir)
            else:
                # File-level test covers specific source file
                expected_source = self.map_test_to_source(test_file)
                if expected_source.exists():
                    tested_source_files.add(expected_source)

        for source_file in source_files:
            # Check if this source file is covered by tests
            source_dir = source_file.parent

            # Check if covered by module-level tests
            is_covered_by_module_test = any(
                source_dir == tested_module or source_dir.is_relative_to(tested_module)
                for tested_module in tested_source_modules
            )

            # Check if covered by file-level tests
            is_covered_by_file_test = source_file in tested_source_files

            if not is_covered_by_module_test and not is_covered_by_file_test:
                expected_test = self.map_source_to_test(source_file)
                rel_source = source_file.relative_to(self.source_root)
                rel_expected = expected_test.relative_to(self.test_root)
                missing_tests.append(f"{rel_source} → {rel_expected} (missing)")

        # Calculate valid mappings (count covered source files)
        for source_file in source_files:
            source_dir = source_file.parent
            is_covered_by_module_test = any(
                source_dir == tested_module or source_dir.is_relative_to(tested_module)
                for tested_module in tested_source_modules
            )
            is_covered_by_file_test = source_file in tested_source_files

            if is_covered_by_module_test or is_covered_by_file_test:
                valid_mappings += 1

        # Advanced validation: check if tested symbols exist in source
        for test_file in test_files:
            tested_symbols = self.extract_tested_symbols(test_file)

            if self.is_framework_test(test_file):
                # Skip symbol validation for framework tests
                continue
            elif self.is_integration_test(test_file):
                # Skip symbol validation for integration tests (they import from multiple modules)
                continue
            elif self.is_module_level_test(test_file):
                # For module-level tests, collect symbols from all source files in the module
                source_dir = self.get_module_source_dir(test_file)
                if source_dir and source_dir.exists():
                    source_symbols = set()
                    for source_file in source_dir.glob("*.py"):
                        if source_file.name != "__init__.py":
                            source_symbols.update(
                                self.extract_source_symbols(source_file)
                            )

                    # Check for symbols tested but not present in module
                    missing_symbols = tested_symbols - source_symbols
                    if (
                        missing_symbols and len(missing_symbols) > 5
                    ):  # Higher threshold for modules
                        rel_test = test_file.relative_to(self.test_root)
                        symbol_list = ", ".join(sorted(missing_symbols)[:5])
                        if len(missing_symbols) > 5:
                            symbol_list += f" (and {len(missing_symbols) - 5} more)"
                        misaligned_tests.append(
                            (
                                str(rel_test),
                                f"Tests symbols not found in module: {symbol_list}",
                            )
                        )
            else:
                # For file-level tests, check against specific source file
                expected_source = self.map_test_to_source(test_file)
                if expected_source.exists():
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
        print("\n💡 Traceability Recommendations:")
        if result.orphaned_tests:
            print("   1. 🔍 Review orphaned tests:")
            print("      - Check if they test functionality moved to different files")
            print("      - Consider renaming to match current source structure")
            print("      - Add comments linking to the actual code being tested")

        if result.missing_tests:
            print("   2. 📝 Consider adding tests for uncovered source files:")
            print("      - Focus on public APIs and complex logic")
            print("      - CLI commands and main entry points benefit from tests")
            print("      - Utility modules may not need individual test files")

        if result.misaligned_tests:
            print("   3. 🔗 Improve test-to-code navigation:")
            print("      - Update imports to reflect current module structure")
            print("      - Add docstrings explaining what code is being tested")
            print("      - Consider using more descriptive test file names")

        print("\n📋 Navigation Tips:")
        print(
            "   • Use meaningful test class/function names that indicate what's tested"
        )
        print("   • Add module-level docstrings explaining test scope and purpose")
        print(
            "   • Group related functionality in test modules (e.g., test_integration.py)"
        )
        print(
            "   • Consider test discovery: can you easily find tests for specific code?"
        )


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
