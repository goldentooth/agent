#!/usr/bin/env python3
"""
Smart vulture runner that only reports NEW dead code issues.
Compares current vulture output against a baseline to catch regressions.
"""

import subprocess
import sys
from pathlib import Path


def load_baseline() -> set[str]:
    """Load known dead code issues from baseline file."""
    baseline_file = Path(__file__).parent.parent / "vulture_baseline.txt"
    baseline_issues = set()

    if baseline_file.exists():
        with open(baseline_file) as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if line and not line.startswith("#"):
                    baseline_issues.add(line)

    return baseline_issues


def run_vulture() -> set[str]:
    """Run vulture and return the set of issues found."""
    try:
        result = subprocess.run(
            [
                "poetry",
                "run",
                "vulture",
                "src/goldentooth_agent",
                "--min-confidence=80",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        # Vulture returns non-zero exit code when it finds issues
        # We want to capture the output regardless
        issues = set()
        if result.stderr:  # Vulture outputs to stderr
            for line in result.stderr.strip().split("\n"):
                line = line.strip()
                if line and not line.startswith("Poe =>"):
                    issues.add(line)

        return issues
    except subprocess.CalledProcessError as e:
        print(f"Error running vulture: {e}", file=sys.stderr)
        return set()


def main() -> int:
    """Main function to check for new dead code issues."""
    baseline_issues = load_baseline()
    current_issues = run_vulture()

    # Find new issues (not in baseline)
    new_issues = current_issues - baseline_issues

    if new_issues:
        print("🚨 NEW dead code detected:", file=sys.stderr)
        print("=" * 50, file=sys.stderr)
        for issue in sorted(new_issues):
            print(issue, file=sys.stderr)
        print("=" * 50, file=sys.stderr)
        print(f"Found {len(new_issues)} new dead code issue(s).", file=sys.stderr)
        print(
            "Please remove the dead code or update vulture_baseline.txt if needed.",
            file=sys.stderr,
        )
        return 1

    # Check if any baseline issues were fixed
    fixed_issues = baseline_issues - current_issues
    if fixed_issues:
        print(
            f"✅ {len(fixed_issues)} existing dead code issue(s) were fixed!",
            file=sys.stderr,
        )
        print("Consider updating vulture_baseline.txt to remove:", file=sys.stderr)
        for issue in sorted(fixed_issues):
            print(f"  {issue}", file=sys.stderr)

    if current_issues:
        print(
            f"ℹ️  {len(current_issues)} known dead code issue(s) in baseline (no new issues)",
            file=sys.stderr,
        )
    else:
        print("✅ No dead code found!", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
