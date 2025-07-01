#!/usr/bin/env python3
"""
Coverage analysis script to identify modules/files with lowest coverage.

This script runs pytest with coverage, parses the output, and identifies
files with the lowest coverage percentages to help prioritize testing efforts.

USAGE EXAMPLES:
    # Basic analysis - show 15 lowest coverage files
    python scripts/coverage_analysis.py

    # Show top 20 lowest coverage files
    python scripts/coverage_analysis.py --limit=20

    # Show only files with at least 20 lines of code
    python scripts/coverage_analysis.py --min-lines=20

    # JSON output for programmatic use
    python scripts/coverage_analysis.py --json

    # Via poe tasks (recommended):
    poetry run poe test-cov-analyze    # Runs this script with default settings
    poetry run poe test-cov-targets    # Runs this script --limit=10

INTERPRETATION:
    🔴 Red indicator: <50% coverage (critical - immediate attention)
    🟡 Yellow indicator: 50-74% coverage (needs improvement)
    🟢 Green indicator: 75%+ coverage (good coverage)

    Focus on:
    1. Files with 0% coverage (completely untested)
    2. High-impact files (many lines, low coverage)
    3. Core business logic modules over CLI modules
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


def run_coverage() -> str | None:
    """Run pytest with coverage and capture output."""
    try:
        result = subprocess.run(
            [
                "poetry",
                "run",
                "pytest",
                "tests/",
                "--cov=goldentooth_agent",
                "--cov-report=term-missing",
                "--tb=no",
                "-q",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running coverage: {e}")
        return None


def parse_coverage_output(output: str) -> list[tuple[str, int, int, float]]:
    """Parse coverage output and extract file coverage data.

    Returns list of tuples: (file_path, total_lines, missed_lines, coverage_percent)
    """
    coverage_data = []

    # Look for the coverage table section
    lines = output.split("\n")
    in_coverage_section = False

    for line in lines:
        # Start of coverage table
        if line.strip().startswith("src/goldentooth_agent/"):
            in_coverage_section = True

        # End of coverage table (dashes or TOTAL line)
        if in_coverage_section and (line.startswith("-") or line.startswith("TOTAL")):
            break

        if in_coverage_section:
            # Parse coverage line: file_path  total_lines  missed_lines  coverage%  missing_lines
            # Example: src/goldentooth_agent/core/context/main.py    123    45   63.41%   12-15, 23-25
            parts = line.split()
            if len(parts) >= 4:
                try:
                    file_path = parts[0]
                    total_lines = int(parts[1])
                    missed_lines = int(parts[2])
                    coverage_str = parts[3].rstrip("%")
                    coverage_percent = float(coverage_str)

                    coverage_data.append(
                        (file_path, total_lines, missed_lines, coverage_percent)
                    )
                except (ValueError, IndexError):
                    continue

    return coverage_data


def analyze_coverage(
    coverage_data: list[tuple[str, int, int, float]],
    limit: int = 10,
    min_lines: int = 10,
) -> None:
    """Analyze coverage data and display results."""

    if not coverage_data:
        print("No coverage data found. Make sure tests run successfully.")
        return

    # Filter out files with very few lines (likely just imports/constants)
    significant_files = [
        (path, total, missed, pct)
        for path, total, missed, pct in coverage_data
        if total >= min_lines
    ]

    if not significant_files:
        print(f"No files with at least {min_lines} lines found.")
        return

    # Sort by coverage percentage (lowest first)
    lowest_coverage = sorted(significant_files, key=lambda x: x[3])

    print("\n📊 Coverage Analysis Results")
    print(f"{'='*60}")

    # Overall stats
    total_files = len(significant_files)
    total_lines = sum(total for _, total, _, _ in significant_files)
    total_missed = sum(missed for _, _, missed, _ in significant_files)
    overall_coverage = (
        ((total_lines - total_missed) / total_lines * 100) if total_lines > 0 else 0
    )

    print(f"📈 Overall Coverage: {overall_coverage:.1f}%")
    print(f"📁 Total Files: {total_files}")
    print(f"📝 Total Lines: {total_lines:,}")
    print(f"❌ Missed Lines: {total_missed:,}")

    print(f"\n🎯 Files with Lowest Coverage (limit: {limit}):")
    print(f"{'File':<50} {'Coverage':<10} {'Lines':<8} {'Missed':<8}")
    print(f"{'-'*76}")

    for _i, (file_path, total_lines, missed_lines, coverage_pct) in enumerate(
        lowest_coverage[:limit]
    ):
        # Shorten long file paths
        display_path = file_path
        if len(display_path) > 48:
            display_path = "..." + display_path[-45:]

        # Color coding for coverage levels
        if coverage_pct < 50:
            coverage_indicator = "🔴"
        elif coverage_pct < 75:
            coverage_indicator = "🟡"
        else:
            coverage_indicator = "🟢"

        print(
            f"{display_path:<50} {coverage_indicator} {coverage_pct:>6.1f}% {total_lines:>6} {missed_lines:>6}"
        )

    # Show files with zero coverage separately
    zero_coverage = [item for item in lowest_coverage if item[3] == 0.0]
    if zero_coverage:
        print(f"\n🚨 Files with Zero Coverage ({len(zero_coverage)} files):")
        for file_path, total_lines, _, _ in zero_coverage[:5]:  # Show first 5
            display_path = file_path.replace("src/goldentooth_agent/", "")
            print(f"   • {display_path} ({total_lines} lines)")
        if len(zero_coverage) > 5:
            print(f"   ... and {len(zero_coverage) - 5} more files")

    # Recommendations
    print("\n💡 Recommendations:")
    if zero_coverage:
        print("   1. Start with zero-coverage files - easiest wins!")

    lowest_non_zero = [item for item in lowest_coverage if item[3] > 0][:3]
    if lowest_non_zero:
        print("   2. Focus on these low-coverage files:")
        for file_path, _, _, coverage_pct in lowest_non_zero:
            module_name = (
                file_path.replace("src/goldentooth_agent/", "")
                .replace(".py", "")
                .replace("/", ".")
            )
            print(f"      • {module_name} ({coverage_pct:.1f}%)")

    # Show high-impact opportunities (many lines, low coverage)
    high_impact = sorted(
        [item for item in significant_files if item[3] < 70],
        key=lambda x: x[1] * (100 - x[3]),
        reverse=True,
    )[:3]

    if high_impact:
        print("   3. High-impact opportunities (many uncovered lines):")
        for file_path, _total_lines, missed_lines, coverage_pct in high_impact:
            module_name = (
                file_path.replace("src/goldentooth_agent/", "")
                .replace(".py", "")
                .replace("/", ".")
            )
            # impact_score = missed_lines  # Not used currently
            print(
                f"      • {module_name} ({missed_lines} uncovered lines, {coverage_pct:.1f}%)"
            )


def main():
    parser = argparse.ArgumentParser(
        description="Analyze test coverage and identify lowest coverage files"
    )
    parser.add_argument(
        "--limit", type=int, default=15, help="Number of lowest coverage files to show"
    )
    parser.add_argument(
        "--min-lines",
        type=int,
        default=10,
        help="Minimum lines to consider a file significant",
    )
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    print("🔍 Running coverage analysis...")

    # Run coverage
    output = run_coverage()
    if not output:
        print("❌ Failed to run coverage analysis")
        sys.exit(1)

    # Parse results
    coverage_data = parse_coverage_output(output)

    if args.json:
        # JSON output for scripting
        json_data = {
            "files": [
                {
                    "path": path,
                    "total_lines": total,
                    "missed_lines": missed,
                    "coverage_percent": pct,
                }
                for path, total, missed, pct in coverage_data
            ]
        }
        print(json.dumps(json_data, indent=2))
    else:
        # Human-readable analysis
        analyze_coverage(coverage_data, args.limit, args.min_lines)


if __name__ == "__main__":
    main()
