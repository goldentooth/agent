"""Comprehensive tests for module size validation hook."""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Generator

import pytest


class TestModuleSizeHook:
    """Test module size validation hook behavior."""

    @pytest.fixture
    def hook_script(self) -> Path:
        """Path to the module size hook script."""
        # Get absolute path to hook script from project root
        project_root = Path(os.environ.get("PROJECT_ROOT", "."))
        return project_root / "git/hooks/check_module_size.sh"

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

    def create_module_with_total_lines(
        self, base_path: Path, module_name: str, total_lines: int
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
            file_path.write_text(
                "\n".join(f"# line {j}" for j in range(file_lines)) + "\n"
            )

        return module_path

    def test_hook_script_exists_and_executable(self, hook_script: Path) -> None:
        """Hook script must exist and be executable."""
        assert hook_script.exists()
        assert os.access(hook_script, os.X_OK)

    def test_passes_with_modules_under_limit(
        self, hook_script: Path, temp_git_repo: Path
    ) -> None:
        """Hook passes when all modules are under line limit."""
        # Create module under limit
        self.create_module_with_total_lines(temp_git_repo, "small_module", 3000)

        result = subprocess.run([str(hook_script)], cwd=temp_git_repo)
        assert result.returncode == 0

    def test_fails_with_modules_over_limit(
        self, hook_script: Path, temp_git_repo: Path
    ) -> None:
        """Hook fails when modules exceed line limit."""
        large_module = self.create_module_with_total_lines(
            temp_git_repo, "large_module", 6000
        )

        result = subprocess.run(
            [str(hook_script)], cwd=temp_git_repo, capture_output=True, text=True
        )

        assert result.returncode == 1
        assert "Module size violations" in result.stdout
        assert "large_module: 6000 lines" in result.stdout

    def test_respects_exclusion_patterns(
        self, hook_script: Path, temp_git_repo: Path
    ) -> None:
        """Hook ignores modules in excluded directories."""
        # Create large module in excluded directories
        for excluded_dir in ["tests", "docs", "old"]:
            excluded_path = temp_git_repo / excluded_dir
            self.create_module_with_total_lines(excluded_path, "excluded_module", 6000)

        result = subprocess.run([str(hook_script)], cwd=temp_git_repo)
        assert result.returncode == 0

    def test_custom_line_limit_via_environment(
        self, hook_script: Path, temp_git_repo: Path
    ) -> None:
        """Hook respects MODULE_SIZE_LIMIT environment variable."""
        self.create_module_with_total_lines(temp_git_repo, "test_module", 4000)

        # Should pass with default limit (5000)
        result = subprocess.run([str(hook_script)], cwd=temp_git_repo)
        assert result.returncode == 0

        # Should fail with custom limit (3000)
        env = os.environ.copy()
        env["MODULE_SIZE_LIMIT"] = "3000"
        result = subprocess.run([str(hook_script)], cwd=temp_git_repo, env=env)
        assert result.returncode == 1

    def test_handles_empty_modules_gracefully(
        self, hook_script: Path, temp_git_repo: Path
    ) -> None:
        """Hook handles modules with no Python files gracefully."""
        # Create directory with no Python files
        empty_dir = temp_git_repo / "empty_module"
        empty_dir.mkdir()
        (empty_dir / "readme.txt").write_text("Not a Python file")

        result = subprocess.run([str(hook_script)], cwd=temp_git_repo)
        assert result.returncode == 0

    def test_counts_only_python_files(
        self, hook_script: Path, temp_git_repo: Path
    ) -> None:
        """Hook only counts .py files, ignoring other file types."""
        module_path = temp_git_repo / "mixed_module"
        module_path.mkdir()

        # Create Python file with many lines
        py_file = module_path / "code.py"
        py_file.write_text("\n".join(f"# line {i}" for i in range(3000)) + "\n")

        # Create non-Python files with many lines (should be ignored)
        (module_path / "data.txt").write_text(
            "\n".join(f"data {i}" for i in range(5000)) + "\n"
        )
        (module_path / "config.json").write_text(
            "{\n" + ",\n".join(f'"key{i}": "value{i}"' for i in range(3000)) + "\n}"
        )

        result = subprocess.run(
            [str(hook_script)], cwd=temp_git_repo, capture_output=True, text=True
        )

        # Should pass because only Python files count (3000 lines < 5000 limit)
        assert result.returncode == 0

    def test_multiple_modules_with_different_sizes(
        self, hook_script: Path, temp_git_repo: Path
    ) -> None:
        """Hook handles multiple modules with different sizes."""
        # Create modules at different sizes
        self.create_module_with_total_lines(temp_git_repo, "small_module", 2000)
        self.create_module_with_total_lines(temp_git_repo, "medium_module", 4000)
        self.create_module_with_total_lines(temp_git_repo, "large_module", 6000)

        result = subprocess.run(
            [str(hook_script)], cwd=temp_git_repo, capture_output=True, text=True
        )

        assert result.returncode == 1
        assert "large_module: 6000 lines" in result.stdout
        # Small and medium modules should not be mentioned in violations
        assert "small_module:" not in result.stdout
        assert "medium_module:" not in result.stdout

    def test_nested_module_structure(
        self, hook_script: Path, temp_git_repo: Path
    ) -> None:
        """Hook correctly handles nested module structures."""
        # Create nested module structure
        base_module = temp_git_repo / "base_module"
        base_module.mkdir()

        # Create Python files in base directory
        (base_module / "main.py").write_text(
            "\n".join(f"# line {i}" for i in range(2000)) + "\n"
        )

        # Create subdirectory with more Python files
        sub_module = base_module / "sub_module"
        sub_module.mkdir()
        (sub_module / "helper.py").write_text(
            "\n".join(f"# line {i}" for i in range(4000)) + "\n"
        )

        result = subprocess.run(
            [str(hook_script)], cwd=temp_git_repo, capture_output=True, text=True
        )

        # Both base_module and base_module/sub_module should be checked separately
        # base_module has 2000 lines (pass), sub_module has 4000 lines (pass)
        # Only immediate Python files in each directory are counted
        assert result.returncode == 0

    def test_works_outside_git_repository(self, hook_script: Path) -> None:
        """Hook works in non-git directories by checking all modules."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir)
            self.create_module_with_total_lines(test_dir, "large_module", 6000)

            result = subprocess.run(
                [str(hook_script)], cwd=test_dir, capture_output=True, text=True
            )

            assert result.returncode == 1
            assert "large_module: 6000 lines" in result.stdout

    def test_provides_helpful_error_message(
        self, hook_script: Path, temp_git_repo: Path
    ) -> None:
        """Hook provides helpful error messages with refactoring guidance."""
        self.create_module_with_total_lines(temp_git_repo, "violation_module", 6000)

        result = subprocess.run(
            [str(hook_script)], cwd=temp_git_repo, capture_output=True, text=True
        )

        assert result.returncode == 1
        assert "Module size violations found" in result.stdout
        assert "refactor large modules into smaller" in result.stdout
        assert ".claude/guidelines/guidelines.txt commandment #5" in result.stdout
        assert "Module refactoring strategies" in result.stdout
        assert "Split into smaller, domain-focused sub-modules" in result.stdout

    def test_handles_pycache_and_build_exclusions(
        self, hook_script: Path, temp_git_repo: Path
    ) -> None:
        """Hook excludes __pycache__, build, and dist directories."""
        for excluded_dir in ["__pycache__", "build", "dist", ".pytest_cache"]:
            excluded_path = temp_git_repo / excluded_dir
            self.create_module_with_total_lines(excluded_path, "should_ignore", 6000)

        result = subprocess.run([str(hook_script)], cwd=temp_git_repo)
        assert result.returncode == 0

    def test_single_file_modules_are_handled(
        self, hook_script: Path, temp_git_repo: Path
    ) -> None:
        """Hook handles modules that are just single Python files."""
        # Create a directory with a single large Python file
        module_path = temp_git_repo / "single_file_module"
        module_path.mkdir()
        large_file = module_path / "main.py"
        large_file.write_text("\n".join(f"# line {i}" for i in range(6000)) + "\n")

        result = subprocess.run(
            [str(hook_script)], cwd=temp_git_repo, capture_output=True, text=True
        )

        assert result.returncode == 1
        assert "single_file_module: 6000 lines" in result.stdout

    def test_module_at_exact_limit(
        self, hook_script: Path, temp_git_repo: Path
    ) -> None:
        """Hook handles modules at exactly the line limit."""
        # Create module with exactly the limit (should pass)
        self.create_module_with_total_lines(temp_git_repo, "at_limit", 5000)

        result = subprocess.run([str(hook_script)], cwd=temp_git_repo)
        assert result.returncode == 0

        # Create module with one line over the limit (should fail)
        self.create_module_with_total_lines(temp_git_repo, "over_limit", 5001)

        result = subprocess.run(
            [str(hook_script)], cwd=temp_git_repo, capture_output=True, text=True
        )
        assert result.returncode == 1
        assert "over_limit: 5001 lines" in result.stdout
