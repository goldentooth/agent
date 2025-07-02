#!/usr/bin/env python3
"""
Check test coverage for staged Python files in src/goldentooth_agent/.

This pre-commit hook ensures that staged changes meet a high coverage threshold
(default 95%). Only files in src/goldentooth_agent/ are considered for coverage
requirements.

Usage:
    python scripts/check_staged_coverage.py [--threshold 95] [--verbose]

Exit codes:
    0: Coverage meets threshold or no relevant staged files
    1: Coverage below threshold
    2: Error running coverage analysis
"""

import argparse
import subprocess
import sys
from pathlib import Path


def get_staged_python_files() -> list[str]:
    """Get list of staged Python files in src/goldentooth_agent/."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=AM"],
            capture_output=True,
            text=True,
            check=True,
        )

        # Filter for Python files in src/goldentooth_agent/
        staged_files = []
        for file_path in result.stdout.strip().split("\n"):
            if (
                file_path
                and file_path.startswith("src/goldentooth_agent/")
                and file_path.endswith(".py")
            ):
                staged_files.append(file_path)

        return staged_files
    except subprocess.CalledProcessError as e:
        print(f"Error getting staged files: {e}", file=sys.stderr)
        return []


def check_coverage_data_exists() -> bool:
    """Check if .coverage file exists."""
    coverage_file = Path(".coverage")
    return coverage_file.exists()


def get_coverage_for_files(files: list[str], verbose: bool = False) -> float:
    """
    Get coverage for specific files from existing coverage data.

    Args:
        files: List of file paths to check coverage for
        verbose: Whether to show verbose output

    Returns:
        Coverage percentage (0.0-100.0), or -1 if error
    """
    if not files:
        return 100.0  # No files to check = perfect coverage

    try:
        # Check if coverage data exists
        if not check_coverage_data_exists():
            if verbose:
                print(
                    "No .coverage file found. Running tests to generate coverage data..."
                )

            # Run minimal test to generate coverage data
            # Using --lf (last failed) to run only previously failed tests if any
            cmd = [
                "poetry",
                "run",
                "pytest",
                "--tb=no",
                "-q",
                "--cov=src/goldentooth_agent",
                "--cov-report=",  # No report, just generate .coverage
                "--lf",  # Run last failed tests only
                "-x",  # Stop on first failure
            ]

            if verbose:
                print(f"Generating coverage data with: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent,
                timeout=60,  # 60 second timeout for generating coverage
            )

            if result.returncode != 0 and not check_coverage_data_exists():
                # If failed and no coverage file, try running without --lf
                cmd.remove("--lf")
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    cwd=Path(__file__).parent.parent,
                    timeout=60,
                )

        # Now use coverage report to get data for specific files
        # Create include pattern for our specific files
        include_pattern = ",".join(files)

        cmd = [
            "poetry",
            "run",
            "coverage",
            "report",
            f"--include={include_pattern}",
            "--show-missing",
            "--skip-covered",
        ]

        if verbose:
            print(f"Getting coverage report: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        output = result.stdout

        if verbose:
            print("Coverage report output:")
            print(output)
            if result.stderr:
                print("STDERR:")
                print(result.stderr)

        # Parse coverage percentage from output
        # Look for lines like: "TOTAL      123     45    63%"
        lines = output.split("\n")
        for line in lines:
            if "TOTAL" in line and "%" in line:
                parts = line.split()
                for part in parts:
                    if part.endswith("%"):
                        try:
                            coverage_pct = float(part[:-1])
                            return coverage_pct
                        except ValueError:
                            continue

        # If no TOTAL line, calculate from individual files
        total_stmts = 0
        total_miss = 0
        coverage_found = False

        for line in lines:
            # Look for lines containing our files
            for file_path in files:
                if file_path in line and "%" in line:
                    parts = line.split()
                    # Coverage report format: filename statements missing percentage
                    if len(parts) >= 4:
                        try:
                            # Find the statements and missing columns
                            # They should be numeric values before the percentage
                            for i in range(len(parts) - 1, 0, -1):
                                if parts[i].endswith("%"):
                                    # Found percentage, stats should be before it
                                    if i >= 2:
                                        stmts = int(parts[i - 2])
                                        miss = int(parts[i - 1])
                                        total_stmts += stmts
                                        total_miss += miss
                                        coverage_found = True
                                        break
                        except (ValueError, IndexError):
                            continue
                    break

        if coverage_found and total_stmts > 0:
            coverage_pct = ((total_stmts - total_miss) / total_stmts) * 100
            return coverage_pct

        # Check if no data to report
        if "No data to report" in output or "nothing to report" in output.lower():
            # This might mean files are not covered by tests
            return 0.0

        # If we can't find coverage data, it might mean the files aren't in the report
        # Try running coverage report without filters to check
        if verbose:
            print("Could not find coverage data for staged files.")
            print("Checking if files are in coverage data at all...")

            # Run coverage report on all files to see what's available
            check_cmd = ["poetry", "run", "coverage", "report"]
            check_result = subprocess.run(
                check_cmd,
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent,
            )

            for file_path in files:
                if file_path in check_result.stdout:
                    print(f"  {file_path} - found in coverage data")
                else:
                    print(f"  {file_path} - NOT in coverage data (0% coverage)")

        # If files aren't in coverage data, they have 0% coverage
        return 0.0

    except subprocess.TimeoutExpired:
        print("Timeout while generating coverage data", file=sys.stderr)
        return -1
    except subprocess.CalledProcessError as e:
        print(f"Error running coverage: {e}", file=sys.stderr)
        return -1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return -1


def main():
    parser = argparse.ArgumentParser(
        description="Check test coverage for staged Python files"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=95.0,
        help="Minimum coverage percentage required (default: 95.0)",
    )
    parser.add_argument("--verbose", action="store_true", help="Show verbose output")

    args = parser.parse_args()

    # Get staged Python files
    staged_files = get_staged_python_files()

    if not staged_files:
        if args.verbose:
            print(
                "No staged Python files in src/goldentooth_agent/ - coverage check passed"
            )
        return 0

    if args.verbose:
        print("Staged Python files in src/goldentooth_agent/:")
        for file_path in staged_files:
            print(f"  {file_path}")
        print()

    # Check coverage for staged files
    coverage_pct = get_coverage_for_files(staged_files, args.verbose)

    if coverage_pct < 0:
        print("Error: Could not determine test coverage", file=sys.stderr)
        return 2

    # Check if coverage meets threshold
    if coverage_pct >= args.threshold:
        if args.verbose or coverage_pct < 100.0:
            print(
                f"✅ Test coverage: {coverage_pct:.1f}% (meets {args.threshold:.1f}% threshold)"
            )
        return 0
    else:
        print(
            f"❌ Test coverage: {coverage_pct:.1f}% (below {args.threshold:.1f}% threshold)",
            file=sys.stderr,
        )
        print("Staged files requiring better test coverage:", file=sys.stderr)
        for file_path in staged_files:
            print(f"  {file_path}", file=sys.stderr)
        print(
            f"\nPlease add tests to achieve at least {args.threshold:.1f}% coverage for staged changes.",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
