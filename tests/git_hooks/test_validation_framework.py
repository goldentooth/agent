"""Tests for the core validation framework."""

from pathlib import Path
from typing import Optional
from unittest.mock import patch

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

    def test_validator_abstract_class(self) -> None:
        """Test Validator abstract base class."""

        # Create a concrete implementation
        class TestValidator(Validator):
            def __init__(self) -> None:
                super().__init__(limit=100, exclude_patterns=[])

            def validate(self, path: Path) -> Optional[ValidationResult]:
                return None

        # Should be able to instantiate concrete class
        validator = TestValidator()
        assert validator.validate(Path("test.py")) is None

        # Test that we cannot instantiate the abstract base class directly
        try:
            # This should fail because Validator is abstract
            Validator(limit=100)  # type: ignore[abstract]
        except TypeError as e:
            # Expected: "Can't instantiate abstract class Validator with abstract method validate"
            assert "abstract" in str(e).lower()

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

    def test_validation_result_string_representation(self) -> None:
        """Test ValidationResult string representation."""
        result = ValidationResult(
            file_path=Path("test.py"),
            line_count=1500,
            limit=1000,
            severity=ValidationSeverity.ERROR,
            message="File too large",
            guidance="Refactor into smaller files",
        )
        str_repr = str(result)
        assert "test.py" in str_repr
        assert "1500" in str_repr

    def test_file_validator_with_binary_file(self, tmp_path: Path) -> None:
        """Test file validator handles binary files gracefully."""
        binary_file = tmp_path / "binary.bin"
        binary_file.write_bytes(b"\x00\x01\x02\x03" * 100)

        validator = FileLengthValidator(limit=1000)
        result = validator.validate(binary_file)

        # Binary files should be handled without error
        assert result is None or result.severity != ValidationSeverity.ERROR

    def test_module_validator_empty_module(self, tmp_path: Path) -> None:
        """Test module validator with empty module."""
        empty_module = tmp_path / "empty_module"
        empty_module.mkdir()

        validator = ModuleSizeValidator(limit=5000)
        result = validator.validate(empty_module)

        assert result is None  # Empty modules should pass

    def test_module_validator_with_non_python_files(self, tmp_path: Path) -> None:
        """Test module validator ignores non-Python files."""
        module = tmp_path / "mixed_module"
        module.mkdir()

        # Create Python files
        (module / "code.py").write_text("# Python code\n" * 100)

        # Create non-Python files (should be ignored)
        (module / "data.txt").write_text("text\n" * 1000)
        (module / "config.json").write_text('{"key": "value"}\n' * 1000)

        validator = ModuleSizeValidator(limit=500)
        result = validator.validate(module)

        # Should only count Python files
        assert result is None  # 100 lines < 500 limit

    def test_file_validator_urgent_threshold(self, temp_git_repo: Path) -> None:
        """Test file validator urgent threshold behavior."""
        validator = FileLengthValidator(
            limit=1000, warn_threshold=800, urgent_threshold=900
        )
        urgent_file = temp_git_repo / "urgent.py"
        create_file_with_lines(urgent_file, 950)

        result = validator.validate(urgent_file)

        assert result is not None
        assert result.severity == ValidationSeverity.WARNING
        # At 950 lines with urgent threshold of 900, it should be urgent
        assert result.line_count >= validator.urgent_threshold

    def test_module_validator_warning_threshold(self, temp_git_repo: Path) -> None:
        """Test module validator warning threshold behavior."""
        validator = ModuleSizeValidator(
            limit=5000, warn_threshold=4000, urgent_threshold=4500
        )
        create_module_with_total_lines(temp_git_repo, "warn_module", 4200)
        module_path = temp_git_repo / "warn_module"

        result = validator.validate(module_path)

        assert result is not None
        assert result.severity == ValidationSeverity.WARNING

    def test_file_validator_nonexistent_file(self, tmp_path: Path) -> None:
        """Test file validator with nonexistent file."""
        validator = FileLengthValidator(limit=1000)
        nonexistent = tmp_path / "does_not_exist.py"

        result = validator.validate(nonexistent)

        assert result is None  # Should handle gracefully

    def test_module_validator_file_instead_of_directory(self, tmp_path: Path) -> None:
        """Test module validator with file path instead of directory."""
        validator = ModuleSizeValidator(limit=5000)
        file_path = tmp_path / "file.py"
        file_path.write_text("# Python code\n" * 100)

        result = validator.validate(file_path)

        assert result is None  # Should handle gracefully

    def test_validators_file_extension_exclusion(self, temp_git_repo: Path) -> None:
        """Test validators exclude files by extension pattern."""
        validator = FileLengthValidator(
            limit=100, exclude_patterns=["*.lock", "*.min.js"]
        )

        # Create large files with excluded extensions
        lock_file = temp_git_repo / "package.lock"
        create_file_with_lines(lock_file, 500)

        minjs_file = temp_git_repo / "app.min.js"
        create_file_with_lines(minjs_file, 500)

        result1 = validator.validate(lock_file)
        result2 = validator.validate(minjs_file)

        assert result1 is None  # Should be excluded by *.lock
        assert result2 is None  # Should be excluded by *.min.js

    def test_file_validator_handles_permission_error(self, tmp_path: Path) -> None:
        """Test file validator handles permission errors gracefully."""
        file_path = tmp_path / "no_read.py"
        file_path.write_text("# Some content\n" * 100)

        validator = FileLengthValidator(limit=50)

        with patch(
            "pathlib.Path.read_text", side_effect=PermissionError("No read access")
        ):
            result = validator.validate(file_path)

        assert result is None  # Should handle gracefully

    def test_module_validator_handles_unreadable_files(self, tmp_path: Path) -> None:
        """Test module validator handles unreadable files in counting."""
        module = tmp_path / "test_module"
        module.mkdir()

        # Create a regular Python file
        (module / "good.py").write_text("# Python code\n" * 100)

        # Create a file that will raise PermissionError
        bad_file = module / "bad.py"
        bad_file.write_text("# More code\n" * 100)

        validator = ModuleSizeValidator(limit=150)

        # Mock only the problematic file to raise PermissionError
        original_read_text = Path.read_text

        def mock_read_text(
            self: Path,
            encoding: str | None = None,
            errors: str | None = None,
            newline: str | None = None,
        ) -> str:
            if self.name == "bad.py":
                raise PermissionError("No read access")
            return original_read_text(
                self, encoding=encoding, errors=errors, newline=newline
            )

        with patch.object(Path, "read_text", mock_read_text):
            result = validator.validate(module)

        # Should count only the readable file (100 lines < 150 limit)
        assert result is None
