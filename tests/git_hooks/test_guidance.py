"""Tests for the guidance module."""

from pathlib import Path

from git_hooks.guidance import get_module_refactoring_guidance, get_refactoring_guidance


class TestGuidance:
    """Test refactoring guidance generation."""

    def test_python_file_guidance(self) -> None:
        """Test guidance for Python files."""
        guidance = get_refactoring_guidance(Path("main.py"))
        assert "Python refactoring strategies" in guidance
        assert "Extract large functions" in guidance

    def test_javascript_file_guidance(self) -> None:
        """Test guidance for JavaScript files."""
        guidance = get_refactoring_guidance(Path("main.js"))
        assert "JavaScript/TypeScript refactoring strategies" in guidance
        assert "Extract utility functions" in guidance

    def test_typescript_file_guidance(self) -> None:
        """Test guidance for TypeScript files."""
        guidance = get_refactoring_guidance(Path("main.ts"))
        assert "JavaScript/TypeScript refactoring strategies" in guidance
        assert "Split components" in guidance

    def test_unknown_file_guidance(self) -> None:
        """Test guidance for unknown file types."""
        guidance = get_refactoring_guidance(Path("main.xyz"))
        assert "General refactoring strategies" in guidance
        assert "Split into smaller" in guidance

    def test_test_file_guidance(self) -> None:
        """Test guidance for test files."""
        guidance = get_refactoring_guidance(Path("test_something.py"))
        assert "Test file refactoring strategies" in guidance
        assert "Extract test fixtures" in guidance

    def test_various_extensions(self) -> None:
        """Test guidance for various file extensions."""
        test_cases = [
            ("main.py", "Python refactoring strategies"),
            ("main.js", "JavaScript/TypeScript refactoring strategies"),
            ("main.jsx", "JavaScript/TypeScript refactoring strategies"),
            ("main.ts", "JavaScript/TypeScript refactoring strategies"),
            ("main.tsx", "JavaScript/TypeScript refactoring strategies"),
            ("main.unknown", "General refactoring strategies"),
            ("test_foo.py", "Test file refactoring strategies"),
        ]

        for filename, expected in test_cases:
            guidance = get_refactoring_guidance(Path(filename))
            assert expected in guidance, f"Failed for {filename}"

    def test_module_refactoring_guidance(self) -> None:
        """Test module refactoring guidance."""
        guidance = get_module_refactoring_guidance()
        assert "Module refactoring strategies" in guidance
        assert "Split into smaller" in guidance
        assert "sub-modules" in guidance
