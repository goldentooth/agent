"""Comprehensive tests for file length validation hook."""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Generator

import pytest


class TestFileLengthHook:
    """Test file length validation hook behavior."""

    @pytest.fixture
    def hook_script(self) -> Path:
        """Path to the file length hook script."""
        # Get absolute path to hook script from project root
        project_root = Path(os.environ.get("PROJECT_ROOT", "."))
        return project_root / "git/hooks/check_file_length.sh"

    @pytest.fixture
    def temp_git_repo(self) -> Generator[Path, None, None]:
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

    def create_file_with_lines(self, path: Path, line_count: int) -> None:
        """Create file with specified number of lines."""
        path.write_text("\n".join(f"line {i}" for i in range(line_count)) + "\n")

    def test_hook_script_exists_and_executable(self, hook_script: Path) -> None:
        """Hook script must exist and be executable."""
        assert hook_script.exists()
        assert os.access(hook_script, os.X_OK)

    def test_passes_with_files_under_limit(
        self, hook_script: Path, temp_git_repo: Path
    ) -> None:
        """Hook passes when all files are under line limit."""
        # Create files under limit
        small_file = temp_git_repo / "small.py"
        self.create_file_with_lines(small_file, 500)

        # Stage file and run hook
        subprocess.run(["git", "add", "small.py"], cwd=temp_git_repo, check=True)
        result = subprocess.run([str(hook_script)], cwd=temp_git_repo)

        assert result.returncode == 0

    def test_fails_with_files_over_limit(
        self, hook_script: Path, temp_git_repo: Path
    ) -> None:
        """Hook fails when files exceed line limit."""
        large_file = temp_git_repo / "large.py"
        self.create_file_with_lines(large_file, 1500)

        subprocess.run(["git", "add", "large.py"], cwd=temp_git_repo, check=True)
        result = subprocess.run(
            [str(hook_script)], cwd=temp_git_repo, capture_output=True, text=True
        )

        assert result.returncode == 1
        assert "File length violations" in result.stdout
        assert "large.py:" in result.stdout and "1500 lines" in result.stdout

    def test_respects_exclusion_patterns(
        self, hook_script: Path, temp_git_repo: Path
    ) -> None:
        """Hook ignores files matching exclusion patterns."""
        # Create large file in excluded directory
        old_dir = temp_git_repo / "old"
        old_dir.mkdir()
        large_old_file = old_dir / "legacy.py"
        self.create_file_with_lines(large_old_file, 1500)

        subprocess.run(["git", "add", "old/legacy.py"], cwd=temp_git_repo, check=True)
        result = subprocess.run([str(hook_script)], cwd=temp_git_repo)

        assert result.returncode == 0

    def test_custom_line_limit_via_environment(
        self, hook_script: Path, temp_git_repo: Path
    ) -> None:
        """Hook respects FILE_LENGTH_LIMIT environment variable."""
        test_file = temp_git_repo / "test.py"
        self.create_file_with_lines(test_file, 800)

        subprocess.run(["git", "add", "test.py"], cwd=temp_git_repo, check=True)

        # Should pass with default limit (1000)
        result = subprocess.run([str(hook_script)], cwd=temp_git_repo)
        assert result.returncode == 0

        # Should fail with custom limit (500)
        env = os.environ.copy()
        env["FILE_LENGTH_LIMIT"] = "500"
        result = subprocess.run([str(hook_script)], cwd=temp_git_repo, env=env)
        assert result.returncode == 1

    def test_handles_nonexistent_files_gracefully(
        self, hook_script: Path, temp_git_repo: Path
    ) -> None:
        """Hook handles deleted/nonexistent files without error."""
        # Create and stage file, then delete it
        test_file = temp_git_repo / "temp.py"
        self.create_file_with_lines(test_file, 100)
        subprocess.run(["git", "add", "temp.py"], cwd=temp_git_repo, check=True)
        test_file.unlink()

        result = subprocess.run([str(hook_script)], cwd=temp_git_repo)
        assert result.returncode == 0

    def test_works_outside_git_repository(self, hook_script: Path) -> None:
        """Hook works in non-git directories by checking all files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir)
            large_file = test_dir / "large.py"
            self.create_file_with_lines(large_file, 1500)

            result = subprocess.run(
                [str(hook_script)], cwd=test_dir, capture_output=True, text=True
            )

            assert result.returncode == 1
            assert "large.py:" in result.stdout and "1500 lines" in result.stdout
