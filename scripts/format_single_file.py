#!/usr/bin/env python3
"""
Format a single file using all formatters/linters from pre-commit hooks.

Takes JSON input via stdin with file path information from Claude Code PostToolUse hook.
Applies black, isort, ruff, and other relevant formatting tools to the specified file.

Expected JSON input format:
{
  "session_id": "abc123",
  "transcript_path": "~/.claude/projects/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
  "tool_name": "Write",
  "tool_input": {
    "file_path": "/path/to/file.txt",
    "content": "file content"
  },
  "tool_response": {
    "filePath": "/path/to/file.txt",
    "success": true
  }
}
"""

import json
import subprocess
import sys
from pathlib import Path


def is_python_file(file_path: str) -> bool:
    """Check if the file is a Python file."""
    return file_path.endswith(".py")


def is_excluded_path(file_path: str) -> bool:
    """Check if the file path should be excluded from formatting."""
    path = Path(file_path)

    # Check if path starts with excluded directories
    excluded_dirs = ["old/", "docs/"]
    for excluded in excluded_dirs:
        if str(path).startswith(excluded) or any(
            part.startswith("old") or part.startswith("docs") for part in path.parts
        ):
            return True

    return False


def run_command(cmd: list[str], file_path: str) -> tuple[bool, str]:
    """Run a command and return success status and output."""
    try:
        result = subprocess.run(
            cmd,
            cwd=Path(__file__).parent.parent,  # Run from project root
            capture_output=True,
            text=True,
            timeout=30,
        )

        output = f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        return result.returncode == 0, output

    except subprocess.TimeoutExpired:
        return False, f"Command timed out: {' '.join(cmd)}"
    except Exception as e:
        return False, f"Command failed: {' '.join(cmd)}\nError: {str(e)}"


def format_python_file(file_path: str) -> list[tuple[str, bool, str]]:
    """Format a Python file using black, isort, and ruff."""
    results = []

    # 1. Black formatting
    cmd = ["poetry", "run", "black", "--line-length=88", file_path]
    success, output = run_command(cmd, file_path)
    results.append(("black", success, output))

    # 2. isort import sorting
    cmd = ["poetry", "run", "isort", "--profile=black", file_path]
    success, output = run_command(cmd, file_path)
    results.append(("isort", success, output))

    # 3. Ruff linting with auto-fix
    cmd = [
        "poetry",
        "run",
        "ruff",
        "check",
        "--fix",
        "--exit-non-zero-on-fix",
        file_path,
    ]
    success, output = run_command(cmd, file_path)
    results.append(("ruff", success, output))

    return results


def format_general_file(file_path: str) -> list[tuple[str, bool, str]]:
    """Apply general file formatting (trailing whitespace, end-of-file)."""
    results = []

    try:
        # Read file content
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Remove trailing whitespace from each line
        lines = content.splitlines()
        lines = [line.rstrip() for line in lines]

        # Ensure file ends with exactly one newline
        if lines and lines[-1]:  # File has content and doesn't end with empty line
            content = "\n".join(lines) + "\n"
        elif lines:  # File has content
            content = "\n".join(lines)
        else:  # Empty file
            content = ""

        # Write back if changed
        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            results.append(
                ("whitespace-fix", True, "Fixed trailing whitespace and end-of-file")
            )
        else:
            results.append(("whitespace-check", True, "No whitespace issues found"))

    except Exception as e:
        results.append(("whitespace-fix", False, f"Failed to fix whitespace: {str(e)}"))

    return results


def main():
    """Main function that processes JSON input and formats the file."""
    try:
        # Read JSON from stdin
        input_data = json.load(sys.stdin)

        # Extract file path from the JSON structure
        tool_input = input_data.get("tool_input", {})
        file_path = tool_input.get("file_path")

        if not file_path:
            print("ERROR: No file_path found in input JSON", file=sys.stderr)
            sys.exit(2)

        # Convert to absolute path if relative
        file_path = str(Path(file_path).resolve())

        print(f"Processing file: {file_path}")

        # Check if file exists
        if not Path(file_path).exists():
            print(f"ERROR: File does not exist: {file_path}", file=sys.stderr)
            sys.exit(2)

        # Check if file should be excluded
        if is_excluded_path(file_path):
            print(f"SKIPPED: File is in excluded directory: {file_path}")
            sys.exit(0)

        all_results = []

        # Apply general file formatting to all files
        general_results = format_general_file(file_path)
        all_results.extend(general_results)

        # Apply Python-specific formatting if it's a Python file
        if is_python_file(file_path):
            python_results = format_python_file(file_path)
            all_results.extend(python_results)

        # Print results
        success_count = 0
        total_count = len(all_results)

        for tool, success, output in all_results:
            status = "✓" if success else "✗"
            print(f"{status} {tool}")
            if output.strip():
                # Indent output lines
                for line in output.strip().split("\n"):
                    print(f"  {line}")

            if success:
                success_count += 1

        print(f"\nSummary: {success_count}/{total_count} tools succeeded")

        # Return exit code should be: 0 for success, 2 for failure
        if success_count == total_count:
            print("All formatting tools succeeded")
            sys.exit(0)  # Testing exit code
        else:
            print("Some formatting tools failed")
            sys.exit(2)  # Testing exit code (later should be 2)

    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON input: {str(e)}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"ERROR: Unexpected error: {str(e)}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
