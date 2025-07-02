"""Tests for the core validation framework."""

import sys
from pathlib import Path
from typing import List

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from git_hooks.core import ValidationResult, ValidationSeverity, Validator
from git_hooks.file_validator import FileLengthValidator
from git_hooks.module_validator import ModuleSizeValidator

from .conftest import create_file_with_lines, create_module_with_total_lines


class TestValidationFramework:
    """Test core validation framework behavior."""

    def test_validation_result_creation(self) -> None:
        """ValidationResult should store file path, severity, and message."""
        result = ValidationResult(
            file_path=Path("test.py"),
            severity=ValidationSeverity.ERROR,
            message="File too long",
            line_count=1500,
            limit=1000,
        )

        assert result.file_path == Path("test.py")
        assert result.severity == ValidationSeverity.ERROR
        assert result.message == "File too long"
        assert result.line_count == 1500
        assert result.limit == 1000

    def test_validator_interface(self) -> None:
        """Validators must implement validate method."""
        validator = FileLengthValidator(limit=1000)

        # This should not raise - interface exists
        assert hasattr(validator, "validate")
        assert callable(validator.validate)

    def test_file_length_validator_passes_small_files(
        self, temp_git_repo: Path
    ) -> None:
        """FileLengthValidator should pass files under limit."""
        validator = FileLengthValidator(limit=1000)
        small_file = temp_git_repo / "small.py"
        create_file_with_lines(small_file, 500)

        result = validator.validate(small_file)

        assert result is None  # No violation

    def test_file_length_validator_fails_large_files(self, temp_git_repo: Path) -> None:
        """FileLengthValidator should fail files over limit."""
        validator = FileLengthValidator(limit=1000)
        large_file = temp_git_repo / "large.py"
        create_file_with_lines(large_file, 1500)

        result = validator.validate(large_file)

        assert result is not None
        assert result.severity == ValidationSeverity.ERROR
        assert result.line_count == 1500
        assert result.limit == 1000
        assert "1500 lines" in result.message

    def test_file_length_validator_warns_approaching_limit(
        self, temp_git_repo: Path
    ) -> None:
        """FileLengthValidator should warn for files approaching limit."""
        validator = FileLengthValidator(limit=1000, warn_threshold=800)
        warning_file = temp_git_repo / "warning.py"
        create_file_with_lines(warning_file, 850)

        result = validator.validate(warning_file)

        assert result is not None
        assert result.severity == ValidationSeverity.WARNING
        assert result.line_count == 850
        assert result.limit == 1000

    def test_module_size_validator_passes_small_modules(
        self, temp_git_repo: Path
    ) -> None:
        """ModuleSizeValidator should pass modules under limit."""
        validator = ModuleSizeValidator(limit=5000)
        create_module_with_total_lines(temp_git_repo, "small_module", 3000)
        module_path = temp_git_repo / "small_module"

        result = validator.validate(module_path)

        assert result is None

    def test_module_size_validator_fails_large_modules(
        self, temp_git_repo: Path
    ) -> None:
        """ModuleSizeValidator should fail modules over limit."""
        validator = ModuleSizeValidator(limit=5000)
        create_module_with_total_lines(temp_git_repo, "large_module", 6000)
        module_path = temp_git_repo / "large_module"

        result = validator.validate(module_path)

        assert result is not None
        assert result.severity == ValidationSeverity.ERROR
        assert result.line_count == 6000
        assert result.limit == 5000

    def test_validators_respect_exclusion_patterns(self, temp_git_repo: Path) -> None:
        """Validators should skip files matching exclusion patterns."""
        validator = FileLengthValidator(
            limit=1000, exclude_patterns=["old/", "*.min.js"]
        )

        # Create large file in excluded directory
        old_dir = temp_git_repo / "old"
        old_dir.mkdir()
        large_old_file = old_dir / "legacy.py"
        create_file_with_lines(large_old_file, 1500)

        result = validator.validate(large_old_file)

        assert result is None  # Should be excluded

    def test_validation_result_provides_refactoring_guidance(
        self, temp_git_repo: Path
    ) -> None:
        """ValidationResult should include file-type specific guidance."""
        validator = FileLengthValidator(limit=1000)
        large_py_file = temp_git_repo / "large.py"
        create_file_with_lines(large_py_file, 1500)

        result = validator.validate(large_py_file)

        assert result is not None
        assert "Python refactoring strategies" in result.guidance
        assert "Extract large functions" in result.guidance
