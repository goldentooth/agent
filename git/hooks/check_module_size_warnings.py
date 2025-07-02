#!/usr/bin/env python3
"""Module size warning hook - provides early warnings for large modules."""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from git_hooks.cli import check_module_size_warnings

if __name__ == "__main__":
    sys.exit(check_module_size_warnings())
