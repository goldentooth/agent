#!/usr/bin/env python3
"""File length warning hook - provides early warnings for large files."""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from git_hooks.cli import check_file_length_warnings

if __name__ == "__main__":
    sys.exit(check_file_length_warnings())
