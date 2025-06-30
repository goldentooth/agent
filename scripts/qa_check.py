#!/usr/bin/env python3
"""
Quality assurance check script - overlaps with pre-commit hooks for automated quality validation.

This script provides a comprehensive quality check that can be run during development
or automatically after completing tasks. It combines the same checks as pre-commit hooks
with additional development-focused feedback.

Usage:
    python scripts/qa_check.py              # Run all checks
    python scripts/qa_check.py --fast       # Skip slow checks (coverage)
    python scripts/qa_check.py --verbose    # Detailed output
    python scripts/qa_check.py --fix        # Auto-fix issues where possible
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


class QualityChecker:
    """Run comprehensive quality checks with detailed feedback."""

    def __init__(self, verbose: bool = False, auto_fix: bool = False):
        self.verbose = verbose
        self.auto_fix = auto_fix
        self.issues_found = 0
        self.checks_passed = 0
        self.checks_failed = 0

    def run_command(self, cmd: list[str], description: str, critical: bool = True) -> bool:
        """Run a command and handle the result."""
        if self.verbose:
            print(f"🔍 {description}")
            print(f"   Command: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, check=False, cwd=Path.cwd()
            )

            if result.returncode == 0:
                self.checks_passed += 1
                if self.verbose:
                    print(f"✅ {description} - PASSED")
                else:
                    print(f"✅ {description}")
                return True
            else:
                self.checks_failed += 1
                print(f"❌ {description} - FAILED")
                if result.stdout:
                    print(f"   STDOUT:\n{result.stdout}")
                if result.stderr:
                    print(f"   STDERR:\n{result.stderr}")

                if critical:
                    self.issues_found += result.returncode
                return False

        except FileNotFoundError:
            print(f"❌ {description} - COMMAND NOT FOUND: {cmd[0]}")
            self.checks_failed += 1
            return False
        except Exception as e:
            print(f"❌ {description} - ERROR: {e}")
            self.checks_failed += 1
            return False

    def check_type_safety(self) -> bool:
        """Check type safety with mypy."""
        return self.run_command(
            ["poetry", "run", "mypy", "src/goldentooth_agent", "--strict", "--show-error-codes"],
            "Type Safety Check (mypy)"
        )

    def check_test_coverage(self, fast_mode: bool = False) -> bool:
        """Check test coverage."""
        if fast_mode:
            # Quick test run without coverage
            return self.run_command(
                ["poetry", "run", "pytest", "tests/test_sanity.py", "-v"],
                "Quick Sanity Tests"
            )
        else:
            # Full coverage check
            return self.run_command(
                ["poetry", "run", "pytest", "tests/", "--cov=goldentooth_agent", "--cov-fail-under=85"],
                "Test Coverage Check (85% minimum)"
            )

    def check_mock_compliance(self) -> bool:
        """Check mock compliance."""
        return self.run_command(
            ["poetry", "run", "pytest", "tests/test_mock_compliance.py", "-v"],
            "Mock Compliance Check"
        )

    def check_dead_code(self) -> bool:
        """Check for new dead code."""
        return self.run_command(
            ["python", "scripts/vulture_diff.py"],
            "Dead Code Detection"
        )

    def check_code_formatting(self) -> bool:
        """Check code formatting with black and isort."""
        black_ok = self.run_command(
            ["poetry", "run", "black", "--check", "src/", "tests/"],
            "Code Formatting Check (black)",
            critical=False
        )
        
        isort_ok = self.run_command(
            ["poetry", "run", "isort", "--check-only", "src/", "tests/"],
            "Import Sorting Check (isort)",
            critical=False
        )

        if not black_ok or not isort_ok:
            if self.auto_fix:
                print("🔧 Auto-fixing formatting issues...")
                subprocess.run(["poetry", "run", "black", "src/", "tests/"], check=False)
                subprocess.run(["poetry", "run", "isort", "src/", "tests/"], check=False)
                print("✅ Formatting fixed automatically")

        return black_ok and isort_ok

    def check_linting(self) -> bool:
        """Check linting with ruff."""
        return self.run_command(
            ["poetry", "run", "ruff", "check", "src/", "tests/"],
            "Linting Check (ruff)",
            critical=False
        )

    def run_pre_commit_hooks(self) -> bool:
        """Run pre-commit hooks."""
        return self.run_command(
            ["poetry", "run", "pre-commit", "run", "--all-files"],
            "Pre-commit Hooks"
        )

    def print_summary(self, start_time: float) -> None:
        """Print summary of quality check results."""
        duration = time.time() - start_time
        total_checks = self.checks_passed + self.checks_failed

        print("\n" + "="*60)
        print("🎯 Quality Check Summary")
        print("="*60)
        print(f"⏱️  Duration: {duration:.1f}s")
        print(f"✅ Passed: {self.checks_passed}/{total_checks}")
        print(f"❌ Failed: {self.checks_failed}/{total_checks}")

        if self.issues_found == 0:
            print(f"\n🎉 All quality checks passed! Ready to commit.")
            return
        else:
            print(f"\n⚠️  {self.issues_found} issues found that need attention.")
            print("\n🔧 Recommended actions:")
            if self.checks_failed > 0:
                print("   1. Review failed checks above")
                print("   2. Fix issues and re-run: python scripts/qa_check.py")
                print("   3. Consider using --fix for auto-fixable issues")

        print("\n📚 For help with specific issues:")
        print("   • Type errors: See guidelines/type-safety-development.md")
        print("   • Test coverage: Run 'poetry run poe test-cov-report'")
        print("   • Mock issues: See guidelines/mock-compliance.md")
        print("   • Dead code: Run 'poetry run poe deadcode-all' for details")

    def run_all_checks(self, fast_mode: bool = False) -> int:
        """Run all quality checks and return exit code."""
        start_time = time.time()
        
        print("🚀 Starting Quality Assurance Checks")
        print("=" * 60)

        # Critical checks (must pass)
        critical_checks = [
            ("Type Safety", lambda: self.check_type_safety()),
            ("Test Coverage", lambda: self.check_test_coverage(fast_mode)),
            ("Mock Compliance", lambda: self.check_mock_compliance()),
            ("Dead Code Detection", lambda: self.check_dead_code()),
        ]

        # Style checks (auto-fixable)
        style_checks = [
            ("Code Formatting", lambda: self.check_code_formatting()),
            ("Linting", lambda: self.check_linting()),
        ]

        # Pre-commit integration
        integration_checks = [
            ("Pre-commit Hooks", lambda: self.run_pre_commit_hooks()),
        ]

        # Run all checks
        all_checks = critical_checks + style_checks + integration_checks
        
        for check_name, check_func in all_checks:
            check_func()
            if self.verbose:
                print()  # Extra spacing in verbose mode

        self.print_summary(start_time)

        # Return appropriate exit code
        return 0 if self.issues_found == 0 else 1


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run comprehensive quality checks for the Goldentooth Agent project"
    )
    parser.add_argument(
        "--fast", 
        action="store_true", 
        help="Skip slow checks like full test coverage"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true", 
        help="Show detailed output for each check"
    )
    parser.add_argument(
        "--fix", 
        action="store_true", 
        help="Auto-fix issues where possible (formatting, imports)"
    )

    args = parser.parse_args()

    checker = QualityChecker(verbose=args.verbose, auto_fix=args.fix)
    return checker.run_all_checks(fast_mode=args.fast)


if __name__ == "__main__":
    sys.exit(main())