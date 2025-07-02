#!/usr/bin/env python3
"""
Run pre-commit hooks individually for faster feedback and debugging.

This script parses the .pre-commit-config.yaml file and runs each hook
individually, stopping at the first failure for immediate feedback.
"""

import subprocess
import sys
from pathlib import Path

import yaml


def load_precommit_config():
    """Load pre-commit configuration."""
    config_path = Path(".pre-commit-config.yaml")
    if not config_path.exists():
        print("Error: .pre-commit-config.yaml not found")
        return None

    with open(config_path) as f:
        return yaml.safe_load(f)


def get_hook_ids(config):
    """Extract hook IDs from configuration."""
    hook_ids = []

    for repo in config.get("repos", []):
        for hook in repo.get("hooks", []):
            hook_id = hook.get("id")
            if hook_id:
                hook_ids.append(hook_id)

    return hook_ids


def run_hook(hook_id, verbose=False):
    """Run a specific pre-commit hook."""
    cmd = ["pre-commit", "run", hook_id]

    if verbose:
        print(f"\n🔍 Running hook: {hook_id}")
        print(f"Command: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout per hook
        )

        if result.returncode == 0:
            if verbose:
                print(f"✅ {hook_id}: PASSED")
            return True, result.stdout
        else:
            print(f"❌ {hook_id}: FAILED")
            if result.stdout:
                print("STDOUT:")
                print(result.stdout)
            if result.stderr:
                print("STDERR:")
                print(result.stderr)
            return False, result.stdout + result.stderr

    except subprocess.TimeoutExpired:
        print(f"⏰ {hook_id}: TIMEOUT (>5 minutes)")
        return False, "Hook timed out"
    except Exception as e:
        print(f"💥 {hook_id}: ERROR - {e}")
        return False, str(e)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Run pre-commit hooks individually")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--start-from", help="Start from specific hook ID")
    parser.add_argument("--only", help="Run only this specific hook ID")
    parser.add_argument("--list", action="store_true", help="List all hook IDs")

    args = parser.parse_args()

    config = load_precommit_config()
    if not config:
        return 1

    hook_ids = get_hook_ids(config)

    if args.list:
        print("Available hook IDs:")
        for i, hook_id in enumerate(hook_ids, 1):
            print(f"  {i:2d}. {hook_id}")
        return 0

    if args.only:
        if args.only not in hook_ids:
            print(f"Error: Hook '{args.only}' not found")
            return 1

        success, output = run_hook(args.only, args.verbose)
        return 0 if success else 1

    start_index = 0
    if args.start_from:
        try:
            start_index = hook_ids.index(args.start_from)
            print(f"Starting from hook: {args.start_from} (index {start_index})")
        except ValueError:
            print(f"Error: Hook '{args.start_from}' not found")
            return 1

    print(f"Running {len(hook_ids) - start_index} hooks individually...")

    passed = 0
    failed = 0

    for i, hook_id in enumerate(hook_ids[start_index:], start_index + 1):
        print(f"\n[{i}/{len(hook_ids)}] Running: {hook_id}")

        success, output = run_hook(hook_id, args.verbose)

        if success:
            passed += 1
        else:
            failed += 1
            print(f"\n🛑 Stopping at first failure: {hook_id}")
            print(f"Fix this hook and re-run with: --start-from {hook_id}")
            break

    print(f"\n📊 Summary: {passed} passed, {failed} failed")

    if failed == 0:
        print("🎉 All hooks passed!")
        return 0
    else:
        print("💡 Fix the failing hook and re-run to continue")
        return 1


if __name__ == "__main__":
    sys.exit(main())
