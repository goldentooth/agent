#!/usr/bin/env python3
"""Module size validation hook - fails when modules exceed limit."""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from git_hooks.cli import check_module_size

if __name__ == "__main__":
    sys.exit(check_module_size())
