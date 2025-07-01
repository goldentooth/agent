#!/usr/bin/env python3
"""Show the line counts of Python files in src/goldentooth_agent directory."""

import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple


def count_lines(file_path: Path) -> int:
    """Count non-empty lines in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return sum(1 for line in f if line.strip())
    except Exception:
        return 0


def get_module_files(src_dir: Path) -> Dict[str, List[Tuple[Path, int]]]:
    """Get all Python files organized by module."""
    modules = defaultdict(list)
    
    for py_file in src_dir.rglob("*.py"):
        # Skip __pycache__ directories
        if "__pycache__" in str(py_file):
            continue
            
        # Get relative path from src_dir
        rel_path = py_file.relative_to(src_dir)
        
        # Determine module name (first directory level)
        parts = rel_path.parts
        if len(parts) > 1:
            module = parts[0]
        else:
            module = "root"
            
        line_count = count_lines(py_file)
        modules[module].append((py_file, line_count))
    
    return dict(modules)


def format_size_bar(size: int, max_size: int, width: int = 30) -> str:
    """Create a visual bar for file size."""
    if max_size == 0:
        return ""
    ratio = size / max_size
    filled = int(ratio * width)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}]"


def main():
    """Main function to display module sizes."""
    project_root = Path(__file__).parent.parent
    src_dir = project_root / "src" / "goldentooth_agent"
    
    if not src_dir.exists():
        print(f"ERROR: Source directory not found: {src_dir}")
        return 1
    
    # Collect all files by module
    modules = get_module_files(src_dir)
    
    if not modules:
        print("No Python files found")
        return 1
    
    # Calculate totals and find max size
    module_totals = {}
    all_files = []
    max_file_size = 0
    
    for module, files in modules.items():
        module_totals[module] = sum(size for _, size in files)
        for file_path, size in files:
            all_files.append((file_path, size, module))
            max_file_size = max(max_file_size, size)
    
    # Sort modules by total size
    sorted_modules = sorted(module_totals.items(), key=lambda x: x[1], reverse=True)
    
    # Display summary
    print("\n=== MODULE SUMMARY ===")
    print(f"{'Module':<20} {'Lines':>8} {'Files':>6}")
    print("-" * 36)
    
    total_lines = 0
    total_files = 0
    
    for module, total in sorted_modules:
        file_count = len(modules[module])
        total_lines += total
        total_files += file_count
        print(f"{module:<20} {total:>8,} {file_count:>6}")
    
    print("-" * 36)
    print(f"{'TOTAL':<20} {total_lines:>8,} {total_files:>6}")
    
    # Show large files (>500 lines)
    large_files = [(f, s, m) for f, s, m in all_files if s > 500]
    if large_files:
        print("\n\n=== LARGE FILES (>500 lines) ===")
        print(f"{'File':<60} {'Lines':>8} {'Module':<15}")
        print("-" * 85)
        
        for file_path, size, module in sorted(large_files, key=lambda x: x[1], reverse=True):
            rel_path = file_path.relative_to(src_dir)
            bar = format_size_bar(size, max_file_size, 20)
            print(f"{str(rel_path):<60} {size:>8,} {module:<15} {bar}")
    
    # Show top 20 files overall
    print("\n\n=== TOP 20 FILES BY SIZE ===")
    print(f"{'File':<60} {'Lines':>8}")
    print("-" * 70)
    
    top_files = sorted(all_files, key=lambda x: x[1], reverse=True)[:20]
    for file_path, size, _ in top_files:
        rel_path = file_path.relative_to(src_dir)
        bar = format_size_bar(size, max_file_size, 20)
        print(f"{str(rel_path):<60} {size:>8,} {bar}")
    
    # Find potential files for refactoring (>1000 lines)
    very_large_files = [(f, s) for f, s, _ in all_files if s > 1000]
    if very_large_files:
        print("\n\n=== CANDIDATES FOR REFACTORING (>1000 lines) ===")
        for file_path, size in sorted(very_large_files, key=lambda x: x[1], reverse=True):
            rel_path = file_path.relative_to(src_dir)
            print(f"  - {rel_path}: {size:,} lines")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())