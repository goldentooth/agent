#!/usr/bin/env python3
"""Check that CLAUDE.md properly references all guidelines with include directives."""

import re
import sys
from pathlib import Path


def extract_guideline_references(claude_md_content: str) -> dict[str, bool]:
    """Extract guideline references from CLAUDE.md and check for include directives.

    Returns a dict mapping guideline filename to whether it has an include directive.
    """
    guidelines = {}
    lines = claude_md_content.split("\n")

    # Pattern to match guideline references like: - **[Name](guidelines/file.md)**: Description
    guideline_pattern = r"^\s*-\s*\*\*\[([^\]]+)\]\(guidelines/([^)]+\.md)\)\*\*:"

    i = 0
    while i < len(lines):
        match = re.match(guideline_pattern, lines[i])
        if match:
            filename = match.group(2)
            # Check if the next line contains the include directive
            has_include = False
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                expected_include = f"@guidelines/{filename}"
                has_include = next_line == expected_include
            guidelines[filename] = has_include
        i += 1

    return guidelines


def get_guideline_files(guidelines_dir: Path) -> set[str]:
    """Get all .md files in the guidelines directory."""
    files = set()
    for file in guidelines_dir.glob("*.md"):
        # Skip README.md
        if file.name != "README.md":
            files.add(file.name)
    return files


def main() -> int:
    """Main function to check CLAUDE.md guidelines."""
    project_root = Path(__file__).parent.parent
    claude_md_path = project_root / "CLAUDE.md"
    guidelines_dir = project_root / "guidelines"

    if not claude_md_path.exists():
        print("ERROR: CLAUDE.md not found")
        return 1

    if not guidelines_dir.exists():
        print("ERROR: guidelines directory not found")
        return 1

    # Read CLAUDE.md
    claude_md_content = claude_md_path.read_text()

    # Extract guideline references from CLAUDE.md
    referenced_guidelines = extract_guideline_references(claude_md_content)

    # Get actual guideline files
    actual_guidelines = get_guideline_files(guidelines_dir)

    errors = []

    # Check for missing include directives
    for filename, has_include in referenced_guidelines.items():
        if not has_include:
            errors.append(f"Missing include directive for {filename}")

    # Check for guidelines not referenced in CLAUDE.md
    referenced_files = set(referenced_guidelines.keys())
    for filename in actual_guidelines:
        if filename not in referenced_files:
            errors.append(f"Guideline {filename} not referenced in CLAUDE.md")

    # Check for referenced guidelines that don't exist
    for filename in referenced_files:
        if filename not in actual_guidelines:
            errors.append(f"Referenced guideline {filename} does not exist")

    if errors:
        print("CLAUDE.md guideline check failed:")
        for error in errors:
            print(f"  - {error}")
        return 1
    else:
        print("CLAUDE.md guideline check passed")
        return 0


if __name__ == "__main__":
    sys.exit(main())
