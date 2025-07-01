#!/usr/bin/env python3
"""
File formatting script that replicates pre-commit hooks for formatting.

This script applies the same formatting transformations as pre-commit hooks
but without the checking/validation aspects. It's designed to auto-fix files
that then need to be `git add`ed again.

Formatting operations performed:
- Remove trailing whitespace
- Ensure files end with newline
- Fix mixed line endings
- Remove empty lines at end of files (beyond the single required newline)

Usage:
    python scripts/format_files.py              # Format all eligible files
    python scripts/format_files.py --check      # Check formatting without fixing
    python scripts/format_files.py --verbose    # Show detailed output
"""

import argparse
import sys
from pathlib import Path


class FileFormatter:
    """Apply pre-commit-style file formatting transformations."""

    def __init__(self, verbose: bool = False, dry_run: bool = False):
        self.verbose = verbose
        self.dry_run = dry_run
        self.files_modified = 0
        self.files_checked = 0

    def log(self, message: str) -> None:
        """Log a message if verbose mode is enabled."""
        if self.verbose:
            print(f"🔧 {message}")

    def should_process_file(self, file_path: Path) -> bool:
        """Check if a file should be processed for formatting."""
        # Skip excluded directories (match pre-commit config: exclude: ^(old/|docs/))
        excluded_dirs = {
            "old",
            "docs",
            ".git",
            "__pycache__",
            ".pytest_cache",
            "htmlcov",
        }
        if any(part in excluded_dirs for part in file_path.parts):
            return False

        # Skip binary files and certain extensions
        excluded_extensions = {
            ".pyc",
            ".pyo",
            ".so",
            ".dll",
            ".exe",
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".ico",
        }
        if file_path.suffix.lower() in excluded_extensions:
            return False

        # Process text files
        text_extensions = {
            ".py",
            ".md",
            ".yaml",
            ".yml",
            ".json",
            ".toml",
            ".txt",
            ".rst",
            ".cfg",
            ".ini",
        }
        if file_path.suffix.lower() in text_extensions:
            return True

        # Process files without extensions that are likely text
        if not file_path.suffix and file_path.is_file():
            try:
                with open(file_path, "rb") as f:
                    # Read first 1024 bytes to check if it's text
                    sample = f.read(1024)
                    # Simple heuristic: if it contains null bytes, it's probably binary
                    return b"\x00" not in sample
            except OSError:
                return False

        return False

    def fix_trailing_whitespace(self, content: str) -> tuple[str, bool]:
        """Remove trailing whitespace from lines."""
        lines = content.splitlines(keepends=True)
        modified = False
        result_lines = []

        for line in lines:
            # Remove trailing whitespace but preserve line ending
            if line.endswith("\n"):
                stripped = line.rstrip() + "\n"
            elif line.endswith("\r\n"):
                stripped = line.rstrip() + "\r\n"
            else:
                stripped = line.rstrip()

            if stripped != line:
                modified = True

            result_lines.append(stripped)

        return "".join(result_lines), modified

    def fix_end_of_file(self, content: str) -> tuple[str, bool]:
        """Ensure file ends with exactly one newline."""
        if not content:
            return content, False

        # Remove all trailing newlines, then add exactly one
        original_content = content
        content = content.rstrip("\r\n")

        # Add single newline
        content += "\n"

        return content, content != original_content

    def normalize_line_endings(self, content: str) -> tuple[str, bool]:
        """Normalize line endings to Unix style (\n)."""
        original_content = content
        # Replace \r\n with \n, then \r with \n
        content = content.replace("\r\n", "\n").replace("\r", "\n")
        return content, content != original_content

    def format_file(self, file_path: Path) -> bool:
        """Format a single file and return True if modified."""
        if not self.should_process_file(file_path):
            return False

        try:
            # Read file content
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                original_content = f.read()

            content = original_content
            file_modified = False

            # Apply formatting transformations
            content, trailing_ws_fixed = self.fix_trailing_whitespace(content)
            if trailing_ws_fixed:
                file_modified = True
                self.log(f"Fixed trailing whitespace in {file_path}")

            content, line_endings_fixed = self.normalize_line_endings(content)
            if line_endings_fixed:
                file_modified = True
                self.log(f"Normalized line endings in {file_path}")

            content, eof_fixed = self.fix_end_of_file(content)
            if eof_fixed:
                file_modified = True
                self.log(f"Fixed end-of-file in {file_path}")

            # Write back if modified and not in dry-run mode
            if file_modified and not self.dry_run:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

            if file_modified:
                self.files_modified += 1
                if not self.dry_run:
                    print(f"✅ Formatted: {file_path}")
                else:
                    print(f"🔍 Would format: {file_path}")

            self.files_checked += 1
            return file_modified

        except (OSError, UnicodeDecodeError) as e:
            print(f"❌ Error processing {file_path}: {e}")
            return False

    def format_directory(self, directory: Path) -> None:
        """Recursively format files in a directory."""
        for item in directory.rglob("*"):
            if item.is_file():
                self.format_file(item)

    def format_project(self) -> int:
        """Format the entire project and return exit code."""
        project_root = Path.cwd()

        print("🚀 Starting File Formatting")
        print("=" * 50)

        if self.dry_run:
            print("🔍 DRY RUN MODE - No files will be modified")
            print()

        # Format main source directories (exclude docs/ per pre-commit config)
        for directory in ["src", "tests", "scripts"]:
            dir_path = project_root / directory
            if dir_path.exists():
                self.log(f"Processing directory: {dir_path}")
                self.format_directory(dir_path)

        # Format root-level files
        for pattern in ["*.py", "*.md", "*.yaml", "*.yml", "*.toml", "*.txt"]:
            for file_path in project_root.glob(pattern):
                if file_path.is_file():
                    self.format_file(file_path)

        print()
        print("=" * 50)
        print("🎯 File Formatting Summary")
        print("=" * 50)
        print(f"📁 Files checked: {self.files_checked}")
        print(f"✏️  Files modified: {self.files_modified}")

        if self.files_modified > 0:
            if not self.dry_run:
                print()
                print("📝 Files have been modified. Remember to:")
                print("   git add <modified-files>")
                print("   git commit -m 'Apply code formatting'")
            else:
                print()
                print("📝 Run without --check to apply formatting changes")
            return 1
        else:
            print("✨ All files are already properly formatted!")
            return 0


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Apply file formatting transformations (trailing whitespace, end-of-file, etc.)"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check formatting without making changes (dry-run mode)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed output for each file processed",
    )

    args = parser.parse_args()

    formatter = FileFormatter(verbose=args.verbose, dry_run=args.check)
    return formatter.format_project()


if __name__ == "__main__":
    sys.exit(main())
