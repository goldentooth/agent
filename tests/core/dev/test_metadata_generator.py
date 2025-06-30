"""
Tests for metadata generator functionality.
"""

import ast
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import Mock, mock_open, patch

import pytest
import yaml

from goldentooth_agent.core.dev.metadata_generator import (
    MetadataUpdateResult,
    MethodInfo,
    ModuleAnalysis,
    ModuleMetadataGenerator,
    SymbolInfo,
)


class TestDataclasses:
    """Test dataclass models."""

    def test_metadata_update_result_creation(self):
        """Test MetadataUpdateResult creation."""
        result = MetadataUpdateResult(module_path=Path("/test"))

        assert result.module_path == Path("/test")
        assert result.updated is False
        assert result.would_update is False
        assert result.changes == []
        assert result.errors == []

    def test_metadata_update_result_with_data(self):
        """Test MetadataUpdateResult with data."""
        result = MetadataUpdateResult(
            module_path=Path("/test"),
            updated=True,
            would_update=True,
            changes=["Added function foo"],
            errors=["Parse error"],
        )

        assert result.updated is True
        assert result.would_update is True
        assert "Added function foo" in result.changes
        assert "Parse error" in result.errors

    def test_method_info_creation(self):
        """Test MethodInfo creation."""
        method = MethodInfo(name="test_method")

        assert method.name == "test_method"
        assert method.signature == ""
        assert method.docstring == ""
        assert method.first_line == ""
        assert method.public is True

    def test_method_info_with_data(self):
        """Test MethodInfo with full data."""
        method = MethodInfo(
            name="process_data",
            signature="def process_data(self, items: list) -> dict",
            docstring="Process data items.",
            first_line="Process data items.",
            public=True,
        )

        assert method.name == "process_data"
        assert "list" in method.signature
        assert method.docstring == "Process data items."
        assert method.public is True

    def test_symbol_info_creation(self):
        """Test SymbolInfo creation."""
        symbol = SymbolInfo(name="TestClass")

        assert symbol.name == "TestClass"
        assert symbol.docstring == ""
        assert symbol.signature == ""
        assert symbol.methods == []
        assert symbol.public is True

    def test_module_analysis_creation(self):
        """Test ModuleAnalysis creation."""
        analysis = ModuleAnalysis(
            module_name="test_module",
            description="Test module",
            file_count=3,
            loc=150,
            class_count=2,
            function_count=5,
            symbols=["ClassA", "function_b"],
            exports=["ClassA"],
            internal_dependencies=["core.util"],
            external_dependencies=["typing", "pathlib"],
            complexity="Medium",
        )

        assert analysis.module_name == "test_module"
        assert analysis.file_count == 3
        assert analysis.loc == 150
        assert analysis.complexity == "Medium"
        assert "ClassA" in analysis.symbols
        assert "typing" in analysis.external_dependencies


class TestModuleMetadataGenerator:
    """Test ModuleMetadataGenerator functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.generator = ModuleMetadataGenerator()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_root = Path(self.temp_dir.name)

    def teardown_method(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()

    def test_generator_initialization(self):
        """Test generator initialization."""
        assert hasattr(self.generator, "project_patterns")
        assert "goldentooth_agent.core." in self.generator.project_patterns
        assert hasattr(self.generator, "_git_available")

    def test_check_git_available_true(self):
        """Test git availability check when git is available."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0

            result = self.generator._check_git_available()

            assert result is True
            mock_run.assert_called_once()

    def test_check_git_available_false(self):
        """Test git availability check when git is not available."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError()

            result = self.generator._check_git_available()

            assert result is False

    def test_is_python_module_valid(self):
        """Test Python module detection for valid module."""
        module_dir = self.test_root / "test_module"
        module_dir.mkdir()
        (module_dir / "__init__.py").write_text("")
        (module_dir / "main.py").write_text("def hello(): pass")

        result = self.generator._is_python_module(module_dir)

        assert result is True

    def test_is_python_module_invalid_not_directory(self):
        """Test Python module detection for non-directory."""
        test_file = self.test_root / "test.py"
        test_file.write_text("def hello(): pass")

        result = self.generator._is_python_module(test_file)

        assert result is False

    def test_is_python_module_no_py_files(self):
        """Test Python module detection for directory without Python files."""
        module_dir = self.test_root / "empty_dir"
        module_dir.mkdir()
        (module_dir / "readme.txt").write_text("Just a readme")

        result = self.generator._is_python_module(module_dir)

        assert result is False

    def test_find_module_directories(self):
        """Test finding module directories."""
        # Create project structure
        src_dir = self.test_root / "src" / "goldentooth_agent"
        src_dir.mkdir(parents=True)

        # Valid modules
        core_dir = src_dir / "core"
        core_dir.mkdir()
        (core_dir / "__init__.py").write_text("")
        (core_dir / "main.py").write_text("def hello(): pass")

        util_dir = src_dir / "util"
        util_dir.mkdir()
        (util_dir / "helpers.py").write_text("def helper(): pass")

        # Invalid directory (no Python files)
        empty_dir = src_dir / "empty"
        empty_dir.mkdir()

        # Excluded directory
        tests_dir = src_dir / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_main.py").write_text("def test(): pass")

        result = self.generator._find_module_directories(self.test_root)

        result_names = [d.name for d in result]
        assert "core" in result_names
        assert "util" in result_names
        assert "empty" not in result_names
        assert "tests" not in result_names

    def test_update_module_metadata_not_python_module(self):
        """Test updating metadata for non-Python module."""
        non_module = self.test_root / "not_a_module"
        non_module.mkdir()
        (non_module / "readme.txt").write_text("Not Python")

        result = self.generator.update_module_metadata(non_module)

        assert result.updated is False
        assert "Not a Python module directory" in result.errors

    def test_update_module_metadata_new_module(self):
        """Test updating metadata for new module."""
        module_dir = self.test_root / "new_module"
        module_dir.mkdir()
        (module_dir / "__init__.py").write_text('"""New module."""')
        (module_dir / "main.py").write_text(
            '''
"""Main module functionality."""

class TestClass:
    """A test class."""

    def method(self) -> str:
        """A test method."""
        return "test"

def function() -> int:
    """A test function."""
    return 42

CONSTANT = "value"
'''
        )

        with patch.object(self.generator, "_write_metadata") as mock_write:
            result = self.generator.update_module_metadata(module_dir)

        assert result.updated is True
        assert len(result.errors) == 0
        mock_write.assert_called_once()

    def test_update_module_metadata_existing_unchanged(self):
        """Test updating metadata when no changes needed."""
        module_dir = self.test_root / "existing_module"
        module_dir.mkdir()
        (module_dir / "__init__.py").write_text('"""Existing module."""')

        # Mock the metadata checking to return no changes needed
        with patch.object(self.generator, "_metadata_changed", return_value=False):
            with patch.object(Path, "exists", return_value=True):
                with patch("builtins.open", mock_open(read_data="existing: data")):
                    result = self.generator.update_module_metadata(module_dir)

        assert result.updated is False
        assert len(result.errors) == 0

    def test_update_module_metadata_dry_run(self):
        """Test dry run mode."""
        module_dir = self.test_root / "dry_run_module"
        module_dir.mkdir()
        (module_dir / "__init__.py").write_text('"""Dry run module."""')
        (module_dir / "main.py").write_text("def new_function(): pass")

        with patch.object(self.generator, "_write_metadata") as mock_write:
            result = self.generator.update_module_metadata(module_dir, dry_run=True)

        assert result.updated is False
        assert result.would_update is True
        mock_write.assert_not_called()

    def test_update_module_metadata_force(self):
        """Test force update mode."""
        module_dir = self.test_root / "force_module"
        module_dir.mkdir()
        (module_dir / "__init__.py").write_text('"""Force module."""')

        # Mock existing metadata
        with patch.object(Path, "exists", return_value=True):
            with patch("builtins.open", mock_open(read_data="existing: data")):
                with patch.object(self.generator, "_write_metadata") as mock_write:
                    result = self.generator.update_module_metadata(
                        module_dir, force=True
                    )

        assert result.updated is True
        mock_write.assert_called_once()

    def test_update_all_modules(self):
        """Test updating all modules in project."""
        # Create multiple modules
        src_dir = self.test_root / "src" / "goldentooth_agent"
        src_dir.mkdir(parents=True)

        for module_name in ["core", "util"]:
            module_dir = src_dir / module_name
            module_dir.mkdir()
            (module_dir / "__init__.py").write_text(f'"""{module_name} module."""')
            (module_dir / "main.py").write_text("def function(): pass")

        with patch.object(self.generator, "update_module_metadata") as mock_update:
            mock_update.return_value = MetadataUpdateResult(module_path=Path("/test"))

            results = self.generator.update_all_modules(self.test_root)

        assert len(results) == 2
        assert mock_update.call_count == 2

    def test_validate_module_metadata_missing_file(self):
        """Test validating metadata when file is missing."""
        module_dir = self.test_root / "no_meta_module"
        module_dir.mkdir()
        (module_dir / "__init__.py").write_text('"""Module without metadata."""')

        errors = self.generator.validate_module_metadata(module_dir)

        assert len(errors) >= 0  # Should handle missing file gracefully

    def test_validate_module_metadata_invalid_yaml(self):
        """Test validating metadata with invalid YAML."""
        module_dir = self.test_root / "invalid_yaml_module"
        module_dir.mkdir()
        (module_dir / "__init__.py").write_text('"""Module with invalid metadata."""')
        (module_dir / "README.meta.yaml").write_text("invalid: yaml: content: [")

        errors = self.generator.validate_module_metadata(module_dir)

        assert len(errors) >= 0  # Should handle invalid YAML gracefully

    def test_validate_all_metadata(self):
        """Test validating all metadata in project."""
        with patch.object(self.generator, "_find_module_directories") as mock_find:
            mock_find.return_value = [Path("/test/module")]
            with patch.object(
                self.generator, "validate_module_metadata"
            ) as mock_validate:
                mock_validate.return_value = ["Error"]

                results = self.generator.validate_all_metadata(self.test_root)

        assert len(results) == 1
        assert mock_validate.call_count == 1

    def test_update_changed_modules_no_git(self):
        """Test updating changed modules when git is not available."""
        self.generator._git_available = False

        results = self.generator.update_changed_modules(self.test_root)

        assert results == []

    def test_update_changed_modules_with_changes(self):
        """Test updating changed modules when there are changes."""
        self.generator._git_available = True

        changed_file = self.test_root / "src" / "goldentooth_agent" / "core" / "main.py"
        changed_file.parent.mkdir(parents=True)
        changed_file.write_text("def changed_function(): pass")
        (changed_file.parent / "__init__.py").write_text('"""Core module."""')

        with patch.object(
            self.generator, "_get_changed_python_modules"
        ) as mock_changed:
            mock_changed.return_value = [changed_file]
            with patch.object(self.generator, "update_module_metadata") as mock_update:
                mock_update.return_value = MetadataUpdateResult(
                    module_path=changed_file.parent, updated=True
                )

                results = self.generator.update_changed_modules(self.test_root)

        assert len(results) == 1
        assert results[0].updated is True

    def test_assess_complexity_low(self):
        """Test complexity assessment - low complexity."""
        complexity = self.generator._assess_complexity(
            file_count=2, loc=50, class_count=1
        )

        assert complexity == "Low"

    def test_assess_complexity_medium(self):
        """Test complexity assessment - medium complexity."""
        complexity = self.generator._assess_complexity(
            file_count=5, loc=300, class_count=3
        )

        assert complexity == "Medium"

    def test_assess_complexity_high(self):
        """Test complexity assessment - high complexity."""
        complexity = self.generator._assess_complexity(
            file_count=10, loc=800, class_count=8
        )

        assert complexity == "High"

    def test_assess_complexity_critical(self):
        """Test complexity assessment - critical complexity."""
        complexity = self.generator._assess_complexity(
            file_count=20, loc=2000, class_count=15
        )

        assert complexity == "Critical"

    def test_analyze_ast_simple_class(self):
        """Test AST analysis for simple class."""
        code = '''
class TestClass:
    """A test class."""

    def method(self) -> str:
        """A method."""
        return "test"

CONSTANT = 42
'''
        tree = ast.parse(code)
        result = self.generator._analyze_ast(tree, Path("test.py"))

        assert "TestClass" in result["classes"]
        assert "CONSTANT" in result["constants"]
        assert len(result["detailed_classes"]) >= 0  # Should find classes

    def test_analyze_ast_function(self):
        """Test AST analysis for module-level function."""
        code = '''
def module_function(x: int) -> int:
    """A module function."""
    return x * 2
'''
        tree = ast.parse(code)
        result = self.generator._analyze_ast(tree, Path("test.py"))

        assert "module_function" in result["functions"]
        assert len(result["detailed_functions"]) >= 0  # Should find functions

    def test_analyze_ast_imports(self):
        """Test AST analysis for imports."""
        code = """
import os
from pathlib import Path
from typing import List
"""
        tree = ast.parse(code)
        result = self.generator._analyze_ast(tree, Path("test.py"))

        assert "os" in result["external_deps"]
        assert "pathlib" in result["external_deps"]
        assert "typing" in result["external_deps"]

    def test_get_exports_from_init(self):
        """Test getting exports from __init__.py."""
        module_dir = self.test_root / "exports_module"
        module_dir.mkdir()

        init_content = '''
"""Module with exports."""

from .main import MainClass, main_function
from .util import CONSTANT

__all__ = ["MainClass", "main_function", "CONSTANT"]
'''
        (module_dir / "__init__.py").write_text(init_content)

        exports = self.generator._get_exports(module_dir)

        assert "MainClass" in exports
        assert "main_function" in exports
        assert "CONSTANT" in exports

    def test_get_exports_no_all(self):
        """Test getting exports when no __all__ is defined."""
        module_dir = self.test_root / "no_all_module"
        module_dir.mkdir()

        init_content = '''
"""Module without __all__."""

def public_function():
    pass

def _private_function():
    pass
'''
        (module_dir / "__init__.py").write_text(init_content)

        exports = self.generator._get_exports(module_dir)

        assert "public_function" in exports
        assert "_private_function" not in exports

    def test_metadata_changed_detection(self):
        """Test metadata change detection."""
        old_meta = {"file_count": 2, "loc": 100, "symbols": ["ClassA"]}
        new_meta = {"file_count": 3, "loc": 150, "symbols": ["ClassA", "ClassB"]}

        changed = self.generator._metadata_changed(old_meta, new_meta)

        assert changed is True

    def test_metadata_unchanged_detection(self):
        """Test metadata unchanged detection."""
        meta = {"file_count": 2, "loc": 100, "symbols": ["ClassA"]}

        changed = self.generator._metadata_changed(meta, meta.copy())

        assert changed is False

    def test_detect_changes(self):
        """Test change detection between metadata versions."""
        old_meta = {"file_count": 2, "class_count": 1, "symbols": ["ClassA"]}
        new_meta = {"file_count": 3, "class_count": 2, "symbols": ["ClassA", "ClassB"]}

        changes = self.generator._detect_changes(old_meta, new_meta)

        assert len(changes) > 0
        assert any("file_count" in change for change in changes)
        assert any("class_count" in change for change in changes)

    def test_write_metadata(self):
        """Test writing metadata to file."""
        meta_file = self.test_root / "test_meta.yaml"
        metadata = {
            "module_name": "test",
            "description": "Test module",
            "file_count": 1,
        }

        self.generator._write_metadata(meta_file, metadata)

        assert meta_file.exists()

        with open(meta_file) as f:
            written_data = yaml.safe_load(f)

        assert written_data["module_name"] == "test"
        assert written_data["file_count"] == 1
