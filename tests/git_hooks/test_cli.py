"""Tests for CLI functionality."""

import os
import subprocess
from pathlib import Path

import pytest

from .conftest import create_file_with_lines, create_module_with_total_lines


class TestCLI:
    """Test CLI hook functionality."""

    def test_file_length_hook_passes_small_files(self, temp_git_repo: Path) -> None:
        """File length hook passes with small files."""
        small_file = temp_git_repo / "small.py"
        create_file_with_lines(small_file, 500)

        subprocess.run(["git", "add", "small.py"], cwd=temp_git_repo, check=True)
        result = subprocess.run(
            [
                "python",
                str(
                    Path(__file__).parent.parent.parent
                    / "git/hooks/check_file_length.py"
                ),
            ],
            cwd=temp_git_repo,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "All files within healthy limits" in result.stdout

    def test_file_length_hook_fails_large_files(self, temp_git_repo: Path) -> None:
        """File length hook fails with large files."""
        large_file = temp_git_repo / "large.py"
        create_file_with_lines(large_file, 1500)

        subprocess.run(["git", "add", "large.py"], cwd=temp_git_repo, check=True)
        result = subprocess.run(
            [
                "python",
                str(
                    Path(__file__).parent.parent.parent
                    / "git/hooks/check_file_length.py"
                ),
            ],
            cwd=temp_git_repo,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1
        assert "File length check violations" in result.stdout
        assert "large.py: 1500 lines" in result.stdout

    def test_file_length_warnings_always_succeeds(self, temp_git_repo: Path) -> None:
        """File length warnings hook always returns 0."""
        large_file = temp_git_repo / "large.py"
        create_file_with_lines(large_file, 950)

        subprocess.run(["git", "add", "large.py"], cwd=temp_git_repo, check=True)
        result = subprocess.run(
            [
                "python",
                str(
                    Path(__file__).parent.parent.parent
                    / "git/hooks/check_file_length_warnings.py"
                ),
            ],
            cwd=temp_git_repo,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "URGENT:" in result.stdout

    def test_module_size_hook_passes_small_modules(self, temp_git_repo: Path) -> None:
        """Module size hook passes with small modules."""
        create_module_with_total_lines(temp_git_repo, "small_module", 3000)

        result = subprocess.run(
            [
                "python",
                str(
                    Path(__file__).parent.parent.parent
                    / "git/hooks/check_module_size.py"
                ),
            ],
            cwd=temp_git_repo,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "All files within healthy limits" in result.stdout

    def test_module_size_hook_fails_large_modules(self, temp_git_repo: Path) -> None:
        """Module size hook fails with large modules."""
        create_module_with_total_lines(temp_git_repo, "large_module", 6000)

        result = subprocess.run(
            [
                "python",
                str(
                    Path(__file__).parent.parent.parent
                    / "git/hooks/check_module_size.py"
                ),
            ],
            cwd=temp_git_repo,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1
        assert "Module size check violations" in result.stdout
        assert "large_module: 6000 lines" in result.stdout

    def test_hooks_respect_environment_variables(self, temp_git_repo: Path) -> None:
        """Hooks respect environment variable limits."""
        test_file = temp_git_repo / "test.py"
        create_file_with_lines(test_file, 800)

        subprocess.run(["git", "add", "test.py"], cwd=temp_git_repo, check=True)

        # Should pass with default limit (1000)
        result = subprocess.run(
            [
                "python",
                str(
                    Path(__file__).parent.parent.parent
                    / "git/hooks/check_file_length.py"
                ),
            ],
            cwd=temp_git_repo,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

        # Should fail with custom limit (500)
        env = os.environ.copy()
        env["FILE_LENGTH_LIMIT"] = "500"
        result = subprocess.run(
            [
                "python",
                str(
                    Path(__file__).parent.parent.parent
                    / "git/hooks/check_file_length.py"
                ),
            ],
            cwd=temp_git_repo,
            capture_output=True,
            text=True,
            env=env,
        )
        assert result.returncode == 1

    def test_hooks_work_outside_git_repo(self, tmp_path: Path) -> None:
        """Hooks work in non-git directories."""
        large_file = tmp_path / "large.py"
        create_file_with_lines(large_file, 1500)

        result = subprocess.run(
            [
                "python",
                str(
                    Path(__file__).parent.parent.parent
                    / "git/hooks/check_file_length.py"
                ),
            ],
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1
        assert "large.py: 1500 lines" in result.stdout

    def test_hooks_provide_refactoring_guidance(self, temp_git_repo: Path) -> None:
        """Hooks provide appropriate refactoring guidance."""
        warning_file = temp_git_repo / "warning.py"
        create_file_with_lines(warning_file, 850)

        subprocess.run(["git", "add", "warning.py"], cwd=temp_git_repo, check=True)
        result = subprocess.run(
            [
                "python",
                str(
                    Path(__file__).parent.parent.parent
                    / "git/hooks/check_file_length_warnings.py"
                ),
            ],
            cwd=temp_git_repo,
            capture_output=True,
            text=True,
        )

        assert "Python refactoring strategies" in result.stdout
        assert "Extract large functions" in result.stdout
