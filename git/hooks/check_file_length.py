#!/usr/bin/env python3
"""File length validation hook - fails when files exceed limit."""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from git_hooks.cli import check_file_length

if __name__ == "__main__":
    sys.exit(check_file_length())
