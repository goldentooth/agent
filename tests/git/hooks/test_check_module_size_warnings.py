"""Comprehensive tests for module size warning hook."""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Generator

import pytest


class TestModuleSizeWarningHook:
    """Test module size warning hook behavior."""

    @pytest.fixture
    def hook_script(self) -> Path:
        """Path to the module size warning hook script."""
        # Get absolute path to hook script from project root
        project_root = Path(os.environ.get("PROJECT_ROOT", "."))
        return project_root / "git/hooks/check_module_size_warnings.sh"

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

    def test_always_exits_zero_success(
        self, hook_script: Path, temp_git_repo: Path
    ) -> None:
        """Hook always exits 0 (success) to show warnings without blocking."""
        # Create module that would trigger urgent warning
        self.create_module_with_total_lines(temp_git_repo, "large_module", 4800)

        result = subprocess.run([str(hook_script)], cwd=temp_git_repo)
        assert result.returncode == 0

    def test_no_warnings_for_small_modules(
        self, hook_script: Path, temp_git_repo: Path
    ) -> None:
        """No warnings shown for modules under warning threshold."""
        self.create_module_with_total_lines(temp_git_repo, "small_module", 3000)

        result = subprocess.run(
            [str(hook_script)], cwd=temp_git_repo, capture_output=True, text=True
        )

        assert result.returncode == 0
        assert "All modules within healthy size limits" in result.stdout
        assert "WARNING:" not in result.stdout
        assert "URGENT:" not in result.stdout

    def test_warning_for_4000_line_modules(
        self, hook_script: Path, temp_git_repo: Path
    ) -> None:
        """Shows warning for modules in 4000-4499 line range."""
        self.create_module_with_total_lines(temp_git_repo, "growing_module", 4200)

        result = subprocess.run(
            [str(hook_script)], cwd=temp_git_repo, capture_output=True, text=True
        )

        assert result.returncode == 0
        assert "⚠️  WARNING:" in result.stdout
        assert "growing_module (" in result.stdout and "4200 lines" in result.stdout
        assert "300 lines until urgent" in result.stdout
        assert "Module refactoring strategies" in result.stdout

    def test_urgent_warning_for_4500_line_modules(
        self, hook_script: Path, temp_git_repo: Path
    ) -> None:
        """Shows urgent warning for modules in 4500-4999 line range."""
        self.create_module_with_total_lines(temp_git_repo, "urgent_module", 4800)

        result = subprocess.run(
            [str(hook_script)], cwd=temp_git_repo, capture_output=True, text=True
        )

        assert result.returncode == 0
        assert "🔶 URGENT:" in result.stdout
        assert "urgent_module (" in result.stdout and "4800 lines" in result.stdout
        assert "200 lines until violation" in result.stdout
        assert "Module refactoring strategies" in result.stdout

    def test_custom_warning_thresholds_via_environment(
        self, hook_script: Path, temp_git_repo: Path
    ) -> None:
        """Hook respects custom warning threshold environment variables."""
        self.create_module_with_total_lines(temp_git_repo, "test_module", 3500)

        # Should not warn with default thresholds
        result = subprocess.run(
            [str(hook_script)], cwd=temp_git_repo, capture_output=True, text=True
        )
        assert "WARNING:" not in result.stdout

        # Should warn with custom threshold
        env = os.environ.copy()
        env["MODULE_SIZE_WARN_THRESHOLD"] = "3000"
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
        """Hook ignores modules in excluded directories."""
        # Create large modules in excluded directories
        for excluded_dir in ["tests", "docs", "old", "__pycache__", "build"]:
            excluded_path = temp_git_repo / excluded_dir
            self.create_module_with_total_lines(excluded_path, "should_ignore", 4800)

        result = subprocess.run(
            [str(hook_script)], cwd=temp_git_repo, capture_output=True, text=True
        )

        assert result.returncode == 0
        assert "All modules within healthy size limits" in result.stdout
        assert "URGENT:" not in result.stdout

    def test_counts_only_python_files(
        self, hook_script: Path, temp_git_repo: Path
    ) -> None:
        """Hook only counts .py files, ignoring other file types."""
        module_path = temp_git_repo / "mixed_module"
        module_path.mkdir()

        # Create Python files with warning-level line count
        py_file = module_path / "code.py"
        py_file.write_text("\n".join(f"# line {i}" for i in range(4200)) + "\n")

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

        # Should warn because Python files have 4200 lines
        assert "⚠️  WARNING:" in result.stdout
        assert "mixed_module (" in result.stdout and "4200 lines" in result.stdout

    def test_multiple_modules_with_different_warning_levels(
        self, hook_script: Path, temp_git_repo: Path
    ) -> None:
        """Hook handles multiple modules with different warning levels."""
        # Create modules at different warning levels
        self.create_module_with_total_lines(temp_git_repo, "warning_module", 4200)
        self.create_module_with_total_lines(temp_git_repo, "urgent_module", 4800)
        self.create_module_with_total_lines(temp_git_repo, "small_module", 2000)

        result = subprocess.run(
            [str(hook_script)], cwd=temp_git_repo, capture_output=True, text=True
        )

        assert result.returncode == 0
        assert "🔶 URGENT:" in result.stdout
        assert "urgent_module (" in result.stdout and "4800 lines" in result.stdout
        assert "⚠️  WARNING:" in result.stdout
        assert "warning_module (" in result.stdout and "4200 lines" in result.stdout
        # Small module should not be mentioned
        assert "small_module" not in result.stdout

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

        # Create subdirectory with warning-level Python files
        sub_module = base_module / "sub_module"
        sub_module.mkdir()
        (sub_module / "helper.py").write_text(
            "\n".join(f"# line {i}" for i in range(4200)) + "\n"
        )

        result = subprocess.run(
            [str(hook_script)], cwd=temp_git_repo, capture_output=True, text=True
        )

        # sub_module should trigger warning (4200 lines), base_module should not (2000 lines)
        # Only immediate Python files in each directory are counted
        assert "⚠️  WARNING:" in result.stdout
        assert (
            "base_module/sub_module (" in result.stdout
            and "4200 lines" in result.stdout
        )

    def test_works_outside_git_repository(self, hook_script: Path) -> None:
        """Hook works in non-git directories by checking all modules."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir)
            self.create_module_with_total_lines(test_dir, "warning_module", 4200)

            result = subprocess.run(
                [str(hook_script)], cwd=test_dir, capture_output=True, text=True
            )

            assert result.returncode == 0
            assert "⚠️  WARNING:" in result.stdout
            assert "warning_module (" in result.stdout and "4200 lines" in result.stdout

    def test_includes_guidance_references(
        self, hook_script: Path, temp_git_repo: Path
    ) -> None:
        """Hook includes references to guidelines and goals."""
        self.create_module_with_total_lines(temp_git_repo, "warning_module", 4200)

        result = subprocess.run(
            [str(hook_script)], cwd=temp_git_repo, capture_output=True, text=True
        )

        assert ".claude/guidelines/guidelines.txt commandment #5" in result.stdout
        assert "Keep modules focused and maintainable" in result.stdout

    def test_line_count_calculations_are_accurate(
        self, hook_script: Path, temp_git_repo: Path
    ) -> None:
        """Hook calculates remaining lines accurately."""
        # Test module at exactly warning threshold
        self.create_module_with_total_lines(temp_git_repo, "exact_warning", 4000)

        result = subprocess.run(
            [str(hook_script)], cwd=temp_git_repo, capture_output=True, text=True
        )

        assert "exact_warning (" in result.stdout and "4000 lines" in result.stdout
        assert "500 lines until urgent" in result.stdout

        # Test module at exactly urgent threshold
        subprocess.run(["rm", "-rf", str(temp_git_repo / "exact_warning")], check=True)
        self.create_module_with_total_lines(temp_git_repo, "exact_urgent", 4500)

        result = subprocess.run(
            [str(hook_script)], cwd=temp_git_repo, capture_output=True, text=True
        )

        assert "exact_urgent (" in result.stdout and "4500 lines" in result.stdout
        assert "500 lines until violation" in result.stdout

    def test_provides_detailed_refactoring_guidance(
        self, hook_script: Path, temp_git_repo: Path
    ) -> None:
        """Hook provides detailed module refactoring guidance."""
        self.create_module_with_total_lines(temp_git_repo, "guidance_test", 4200)

        result = subprocess.run(
            [str(hook_script)], cwd=temp_git_repo, capture_output=True, text=True
        )

        # Check for specific refactoring strategies
        assert "Module refactoring strategies" in result.stdout
        assert "Split into smaller, focused sub-modules" in result.stdout
        assert "Extract common utilities into separate utility modules" in result.stdout
        assert "Move models/schemas to dedicated modules" in result.stdout
        assert "Separate interface definitions from implementations" in result.stdout
        assert "Consider creating sub-packages for complex domains" in result.stdout
        assert (
            "Use __init__.py files to create clean public interfaces" in result.stdout
        )

    def test_handles_empty_directories_gracefully(
        self, hook_script: Path, temp_git_repo: Path
    ) -> None:
        """Hook handles directories with no Python files gracefully."""
        # Create directories with no Python files
        (temp_git_repo / "empty_dir").mkdir()
        (temp_git_repo / "text_only").mkdir()
        (temp_git_repo / "text_only" / "readme.txt").write_text("Not Python")

        result = subprocess.run(
            [str(hook_script)], cwd=temp_git_repo, capture_output=True, text=True
        )

        assert result.returncode == 0
        assert "All modules within healthy size limits" in result.stdout

    def test_no_modules_to_check_scenario(
        self, hook_script: Path, temp_git_repo: Path
    ) -> None:
        """Hook handles scenario with no modules to check."""
        # Create only non-Python files
        (temp_git_repo / "readme.txt").write_text("No Python here")
        (temp_git_repo / "config.json").write_text('{"key": "value"}')

        result = subprocess.run(
            [str(hook_script)], cwd=temp_git_repo, capture_output=True, text=True
        )

        assert result.returncode == 0
        assert "All modules within healthy size limits" in result.stdout
