#!/usr/bin/env python3
"""Script to fix multiline function definitions missing return type annotations."""

import subprocess
from pathlib import Path


def get_no_untyped_def_errors():
    """Get all no-untyped-def errors from mypy."""
    result = subprocess.run(
        [
            "poetry",
            "run",
            "mypy",
            "src/goldentooth_agent",
            "--strict",
            "--show-error-codes",
            "--no-pretty",
        ],
        capture_output=True,
        text=True,
        cwd=".",
    )

    errors = []
    for line in result.stderr.split("\n"):
        if "no-untyped-def" in line and ":" in line:
            parts = line.split(":")
            if len(parts) >= 2:
                file_path = parts[0]
                try:
                    line_num = int(parts[1])
                    errors.append((file_path, line_num))
                except ValueError:
                    continue
    return errors


def fix_function_return_type(file_path: str, line_num: int):
    """Fix a function missing return type annotation."""
    path = Path(file_path)
    if not path.exists():
        return False

    lines = path.read_text().split("\n")
    if line_num > len(lines):
        return False

    # Find the end of the function definition
    func_start = line_num - 1  # Convert to 0-based index

    # Look for the function definition starting from this line
    for i in range(func_start, len(lines)):
        line = lines[i]
        if line.strip().endswith("):"):
            # Found end of function definition without return type
            lines[i] = line.rstrip() + " -> None:"
            print(f"  Fixed function at {file_path}:{i+1}")

            # Write back to file
            path.write_text("\n".join(lines))
            return True
        elif ") -> " in line:
            # Already has return type annotation
            return False

    return False


def main():
    print("🔧 Fixing multiline function return type annotations...")

    errors = get_no_untyped_def_errors()
    fixed_count = 0

    for file_path, line_num in errors:
        if fix_function_return_type(file_path, line_num):
            fixed_count += 1

    print(f"✅ Fixed {fixed_count} function return type annotations!")
    print("💡 Run 'poetry run mypy src/' to verify the fixes.")


if __name__ == "__main__":
    main()
