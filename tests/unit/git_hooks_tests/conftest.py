"""Shared test fixtures for git hooks validation."""

import subprocess
import tempfile
from pathlib import Path
from typing import Generator

import pytest


@pytest.fixture
def temp_git_repo() -> Generator[Path, None, None]:
    """Create temporary git repository for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)
        subprocess.run(["git", "init"], cwd=repo_path, check=True)
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=repo_path,
            check=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"], cwd=repo_path, check=True
        )
        yield repo_path


def create_file_with_lines(path: Path, line_count: int) -> None:
    """Create file with specified number of lines."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(f"line {i}" for i in range(line_count)) + "\n")


def create_module_with_total_lines(
    base_path: Path, module_name: str, total_lines: int
) -> Path:
    """Create a module directory with Python files totaling specified lines."""
    module_path = base_path / module_name
    module_path.mkdir(parents=True, exist_ok=True)

    # Split lines across multiple files to create a realistic module
    files_to_create = min(5, max(1, total_lines // 500))  # 1-5 files
    lines_per_file = total_lines // files_to_create
    remaining_lines = total_lines % files_to_create

    for i in range(files_to_create):
        file_lines = lines_per_file + (1 if i < remaining_lines else 0)
        file_path = module_path / f"module_{i}.py"
        create_file_with_lines(file_path, file_lines)

    return module_path
