#!/usr/bin/env python3
"""Pre-commit hook script to update README.meta.yaml files."""

import subprocess
import sys
from pathlib import Path


def main() -> int:
    """Main entry point for the pre-commit hook."""
    try:
        # Get the project root (assuming script is in scripts/ subdirectory)
        project_root = Path(__file__).parent.parent

        # Run the metadata update command
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "goldentooth_agent.cli.main",
                "dev",
                "module",
                "update-all",
                "--root",
                str(project_root),
            ],
            capture_output=True,
            text=True,
            cwd=project_root,
        )

        if result.returncode != 0:
            print("❌ Failed to update module metadata:")
            print(result.stderr)
            return 1

        # Check if any files were updated
        output = result.stdout.strip()
        if "Updated" in output and "0 of" not in output:
            print("✓ Module metadata updated successfully")
            print(output)

            # Stage the updated files for commit
            subprocess.run(["git", "add", "*/README.meta.yaml"], cwd=project_root)

        else:
            print("✓ No metadata updates needed")

        return 0

    except Exception as e:
        print(f"❌ Error updating metadata: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
