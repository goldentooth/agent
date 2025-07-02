"""Comprehensive tests for file length warning hook."""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Generator

import pytest


class TestFileLengthWarningHook:
    """Test file length warning hook behavior."""

    @pytest.fixture
    def hook_script(self) -> Path:
        """Path to the file length warning hook script."""
        # Get absolute path to hook script from project root
        project_root = Path(os.environ.get("PROJECT_ROOT", "."))
        return project_root / "git/hooks/check_file_length_warnings.sh"

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

    def test_always_exits_zero_success(
        self, hook_script: Path, temp_git_repo: Path
    ) -> None:
        """Hook always exits 0 (success) to show warnings without blocking."""
        # Create file that would trigger urgent warning
        large_file = temp_git_repo / "large.py"
        self.create_file_with_lines(large_file, 950)

        subprocess.run(["git", "add", "large.py"], cwd=temp_git_repo, check=True)
        result = subprocess.run([str(hook_script)], cwd=temp_git_repo)

        assert result.returncode == 0

    def test_no_warnings_for_small_files(
        self, hook_script: Path, temp_git_repo: Path
    ) -> None:
        """No warnings shown for files under warning threshold."""
        small_file = temp_git_repo / "small.py"
        self.create_file_with_lines(small_file, 500)

        subprocess.run(["git", "add", "small.py"], cwd=temp_git_repo, check=True)
        result = subprocess.run(
            [str(hook_script)], cwd=temp_git_repo, capture_output=True, text=True
        )

        assert result.returncode == 0
        assert "All files within healthy size limits" in result.stdout
        assert "WARNING:" not in result.stdout
        assert "URGENT:" not in result.stdout

    def test_warning_for_800_line_files(
        self, hook_script: Path, temp_git_repo: Path
    ) -> None:
        """Shows warning for files in 800-899 line range."""
        warning_file = temp_git_repo / "growing.py"
        self.create_file_with_lines(warning_file, 850)

        subprocess.run(["git", "add", "growing.py"], cwd=temp_git_repo, check=True)
        result = subprocess.run(
            [str(hook_script)], cwd=temp_git_repo, capture_output=True, text=True
        )

        assert result.returncode == 0
        assert "⚠️  WARNING:" in result.stdout
        assert "growing.py (" in result.stdout and "850 lines" in result.stdout
        assert "50 lines until urgent" in result.stdout
        assert "Python refactoring strategies" in result.stdout

    def test_urgent_warning_for_900_line_files(
        self, hook_script: Path, temp_git_repo: Path
    ) -> None:
        """Shows urgent warning for files in 900-999 line range."""
        urgent_file = temp_git_repo / "urgent.py"
        self.create_file_with_lines(urgent_file, 950)

        subprocess.run(["git", "add", "urgent.py"], cwd=temp_git_repo, check=True)
        result = subprocess.run(
            [str(hook_script)], cwd=temp_git_repo, capture_output=True, text=True
        )

        assert result.returncode == 0
        assert "🔶 URGENT:" in result.stdout
        assert "urgent.py (" in result.stdout and "950 lines" in result.stdout
        assert "50 lines until violation" in result.stdout
        assert "Python refactoring strategies" in result.stdout

    def test_custom_warning_thresholds_via_environment(
        self, hook_script: Path, temp_git_repo: Path
    ) -> None:
        """Hook respects custom warning threshold environment variables."""
        test_file = temp_git_repo / "test.py"
        self.create_file_with_lines(test_file, 600)

        subprocess.run(["git", "add", "test.py"], cwd=temp_git_repo, check=True)

        # Should not warn with default thresholds
        result = subprocess.run(
            [str(hook_script)], cwd=temp_git_repo, capture_output=True, text=True
        )
        assert "WARNING:" not in result.stdout

        # Should warn with custom threshold
        env = os.environ.copy()
        env["FILE_LENGTH_WARN_THRESHOLD"] = "500"
        result = subprocess.run(
            [str(hook_script)],
            cwd=temp_git_repo,
            capture_output=True,
            text=True,
            env=env,
        )
        assert "⚠️  WARNING:" in result.stdout

    def test_respects_exclusion_patterns(
        self, hook_script: Path, temp_git_repo: Path
    ) -> None:
        """Hook ignores files matching exclusion patterns."""
        # Create large file in excluded directory
        old_dir = temp_git_repo / "old"
        old_dir.mkdir()
        large_old_file = old_dir / "legacy.py"
        self.create_file_with_lines(large_old_file, 950)

        subprocess.run(["git", "add", "old/legacy.py"], cwd=temp_git_repo, check=True)
        result = subprocess.run(
            [str(hook_script)], cwd=temp_git_repo, capture_output=True, text=True
        )

        assert result.returncode == 0
        assert "All files within healthy size limits" in result.stdout
        assert "URGENT:" not in result.stdout

    def test_file_type_specific_guidance(
        self, hook_script: Path, temp_git_repo: Path
    ) -> None:
        """Hook provides file-type specific refactoring guidance."""
        # Test Python file
        py_file = temp_git_repo / "test.py"
        self.create_file_with_lines(py_file, 850)
        subprocess.run(["git", "add", "test.py"], cwd=temp_git_repo, check=True)

        result = subprocess.run(
            [str(hook_script)], cwd=temp_git_repo, capture_output=True, text=True
        )
        assert "Python refactoring strategies" in result.stdout
        assert "Extract large functions/classes" in result.stdout

        # Clear staged files
        subprocess.run(["git", "reset"], cwd=temp_git_repo, check=True)

        # Test JavaScript file
        js_file = temp_git_repo / "test.js"
        self.create_file_with_lines(js_file, 850)
        subprocess.run(["git", "add", "test.js"], cwd=temp_git_repo, check=True)

        result = subprocess.run(
            [str(hook_script)], cwd=temp_git_repo, capture_output=True, text=True
        )
        assert "JavaScript/TypeScript refactoring strategies" in result.stdout
        assert "Split components into smaller" in result.stdout

    def test_test_file_specific_guidance(
        self, hook_script: Path, temp_git_repo: Path
    ) -> None:
        """Hook provides test-specific refactoring guidance for test files."""
        test_file = temp_git_repo / "test_module.py"
        self.create_file_with_lines(test_file, 850)

        subprocess.run(["git", "add", "test_module.py"], cwd=temp_git_repo, check=True)
        result = subprocess.run(
            [str(hook_script)], cwd=temp_git_repo, capture_output=True, text=True
        )

        # Test files should get Python guidance since extension check comes first
        assert "Python refactoring strategies" in result.stdout

    def test_multiple_files_with_different_warning_levels(
        self, hook_script: Path, temp_git_repo: Path
    ) -> None:
        """Hook handles multiple files with different warning levels."""
        # Create files at different warning levels
        warning_file = temp_git_repo / "warning.py"
        self.create_file_with_lines(warning_file, 850)

        urgent_file = temp_git_repo / "urgent.py"
        self.create_file_with_lines(urgent_file, 950)

        subprocess.run(
            ["git", "add", "warning.py", "urgent.py"], cwd=temp_git_repo, check=True
        )
        result = subprocess.run(
            [str(hook_script)], cwd=temp_git_repo, capture_output=True, text=True
        )

        assert result.returncode == 0
        assert "🔶 URGENT:" in result.stdout
        assert "urgent.py (" in result.stdout and "950 lines" in result.stdout
        assert "⚠️  WARNING:" in result.stdout
        assert "warning.py (" in result.stdout and "850 lines" in result.stdout

    def test_handles_nonexistent_files_gracefully(
        self, hook_script: Path, temp_git_repo: Path
    ) -> None:
        """Hook handles deleted/nonexistent files without error."""
        # Create and stage file, then delete it
        test_file = temp_git_repo / "temp.py"
        self.create_file_with_lines(test_file, 850)
        subprocess.run(["git", "add", "temp.py"], cwd=temp_git_repo, check=True)
        test_file.unlink()

        result = subprocess.run(
            [str(hook_script)], cwd=temp_git_repo, capture_output=True, text=True
        )
        assert result.returncode == 0
        assert "All files within healthy size limits" in result.stdout

    def test_works_outside_git_repository(self, hook_script: Path) -> None:
        """Hook works in non-git directories by checking all files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir)
            warning_file = test_dir / "warning.py"
            self.create_file_with_lines(warning_file, 850)

            result = subprocess.run(
                [str(hook_script)], cwd=test_dir, capture_output=True, text=True
            )

            assert result.returncode == 0
            assert "⚠️  WARNING:" in result.stdout
            assert "warning.py (" in result.stdout and "850 lines" in result.stdout

    def test_no_files_to_check_scenario(
        self, hook_script: Path, temp_git_repo: Path
    ) -> None:
        """Hook handles scenario with no files to check."""
        # Run hook with no staged files
        result = subprocess.run(
            [str(hook_script)], cwd=temp_git_repo, capture_output=True, text=True
        )

        assert result.returncode == 0
        assert "No files to check" in result.stdout

    def test_includes_guidance_references(
        self, hook_script: Path, temp_git_repo: Path
    ) -> None:
        """Hook includes references to guidelines and goals."""
        warning_file = temp_git_repo / "warning.py"
        self.create_file_with_lines(warning_file, 850)

        subprocess.run(["git", "add", "warning.py"], cwd=temp_git_repo, check=True)
        result = subprocess.run(
            [str(hook_script)], cwd=temp_git_repo, capture_output=True, text=True
        )

        assert ".claude/guidelines/guidelines.txt commandment #4" in result.stdout
        assert "Keep files focused and maintainable" in result.stdout

    def test_mixed_file_types_get_appropriate_guidance(
        self, hook_script: Path, temp_git_repo: Path
    ) -> None:
        """Hook provides appropriate guidance for different file types."""
        # Create files of different types
        py_file = temp_git_repo / "module.py"
        self.create_file_with_lines(py_file, 850)

        ts_file = temp_git_repo / "component.ts"
        self.create_file_with_lines(ts_file, 850)

        unknown_file = temp_git_repo / "config.txt"
        self.create_file_with_lines(unknown_file, 850)

        subprocess.run(
            ["git", "add", "module.py", "component.ts", "config.txt"],
            cwd=temp_git_repo,
            check=True,
        )
        result = subprocess.run(
            [str(hook_script)], cwd=temp_git_repo, capture_output=True, text=True
        )

        assert "Python refactoring strategies" in result.stdout
        assert "JavaScript/TypeScript refactoring strategies" in result.stdout
        assert "General refactoring strategies" in result.stdout

    def test_line_count_calculations_are_accurate(
        self, hook_script: Path, temp_git_repo: Path
    ) -> None:
        """Hook calculates remaining lines accurately."""
        # Test file at exactly warning threshold
        exact_file = temp_git_repo / "exact.py"
        self.create_file_with_lines(exact_file, 800)

        subprocess.run(["git", "add", "exact.py"], cwd=temp_git_repo, check=True)
        result = subprocess.run(
            [str(hook_script)], cwd=temp_git_repo, capture_output=True, text=True
        )

        assert "exact.py (" in result.stdout and "800 lines" in result.stdout
        assert "100 lines until urgent" in result.stdout
