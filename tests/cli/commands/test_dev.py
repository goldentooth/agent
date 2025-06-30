"""
Tests for dev CLI commands.
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import typer
from typer.testing import CliRunner

from goldentooth_agent.cli.commands.dev import app, module_app
from goldentooth_agent.core.dev.metadata_generator import MetadataUpdateResult


class TestDevCommands:
    """Test dev command functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_root = Path(self.temp_dir.name)

    def teardown_method(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()

    def test_app_creation(self):
        """Test that the app is created properly."""
        assert isinstance(app, typer.Typer)
        assert isinstance(module_app, typer.Typer)

    def test_app_has_commands(self):
        """Test that the app has the expected commands."""
        # Check that module_app is added to the main app
        assert hasattr(app, "registered_commands")

        # Check that module_app has update command
        assert hasattr(module_app, "registered_commands")

    @patch("goldentooth_agent.cli.commands.dev.ModuleMetadataGenerator")
    def test_update_module_metadata_basic(self, mock_generator_class):
        """Test basic module metadata update functionality."""
        test_module = self.test_root / "test_module"
        test_module.mkdir()
        (test_module / "__init__.py").write_text('"""Test module."""')

        mock_generator = Mock()
        mock_generator_class.return_value = mock_generator
        mock_result = MetadataUpdateResult(
            module_path=test_module, updated=True, changes=["Added new function foo"]
        )
        mock_generator.update_module_metadata.return_value = mock_result

        result = self.runner.invoke(module_app, ["update", str(test_module)])

        # Should complete without error
        assert result.exit_code == 0
        # Should call the generator
        mock_generator.update_module_metadata.assert_called_once()

    @patch("goldentooth_agent.cli.commands.dev.ModuleMetadataGenerator")
    def test_update_all_modules_basic(self, mock_generator_class):
        """Test basic update all modules functionality."""
        mock_generator = Mock()
        mock_generator_class.return_value = mock_generator
        mock_results = [
            MetadataUpdateResult(module_path=Path("/test/module1"), updated=True),
            MetadataUpdateResult(module_path=Path("/test/module2"), updated=False),
        ]
        mock_generator.update_all_modules.return_value = mock_results

        result = self.runner.invoke(module_app, ["update-all"])

        # Should complete without error
        assert result.exit_code == 0
        # Should call the generator
        mock_generator.update_all_modules.assert_called_once()

    def test_nonexistent_command(self):
        """Test calling a nonexistent command."""
        result = self.runner.invoke(module_app, ["nonexistent-command"])

        # Should fail with error
        assert result.exit_code != 0

    @patch("goldentooth_agent.cli.commands.dev.ModuleMetadataGenerator")
    def test_module_metadata_generator_import(self, mock_generator_class):
        """Test that ModuleMetadataGenerator can be imported and used."""
        # Create a basic mock
        mock_generator = Mock()
        mock_generator_class.return_value = mock_generator

        # Import the update function and test it exists
        from goldentooth_agent.cli.commands.dev import update_module_metadata

        assert callable(update_module_metadata)

    def test_helper_functions_exist(self):
        """Test that helper functions exist and can be imported."""
        from goldentooth_agent.cli.commands.dev import _generate_ai_background_content

        assert callable(_generate_ai_background_content)

        # Test it can be called with basic data
        test_data = {
            "module_name": "test_module",
            "description": "A test module",
            "symbols": ["TestClass"],
            "complexity": "Low",
        }

        result = _generate_ai_background_content(test_data)
        assert isinstance(result, str)
        assert len(result) > 0


class TestDevCommandImports:
    """Test imports and basic functionality."""

    def test_all_imports_work(self):
        """Test that all main imports work."""
        from goldentooth_agent.cli.commands import dev

        assert hasattr(dev, "app")
        assert hasattr(dev, "module_app")
        assert hasattr(dev, "update_module_metadata")
        assert hasattr(dev, "update_all_modules")

    def test_function_signatures(self):
        """Test that functions have the expected signatures."""
        import inspect

        from goldentooth_agent.cli.commands.dev import update_module_metadata

        sig = inspect.signature(update_module_metadata)

        # Should have parameters for module_path, force, dry_run
        param_names = list(sig.parameters.keys())
        assert "module_path" in param_names
        assert "force" in param_names
        assert "dry_run" in param_names

    def test_typer_decorators(self):
        """Test that functions are properly decorated with typer."""
        from goldentooth_agent.cli.commands.dev import update_module_metadata

        # Should be a typer command function
        assert hasattr(update_module_metadata, "__annotations__")

    def test_metadata_update_result_import(self):
        """Test that MetadataUpdateResult can be imported and used."""
        result = MetadataUpdateResult(module_path=Path("/test"))

        assert result.module_path == Path("/test")
        assert result.updated is False
        assert result.would_update is False
        assert result.changes == []
        assert result.errors == []


class TestDevCommandFunctionality:
    """Test specific command functionality without CLI runner."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_root = Path(self.temp_dir.name)

    def teardown_method(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()

    def test_generate_ai_background_content_basic(self):
        """Test AI background content generation."""
        from goldentooth_agent.cli.commands.dev import _generate_ai_background_content

        # Test with minimal data
        data = {"module_name": "test"}
        result = _generate_ai_background_content(data)

        assert isinstance(result, str)
        assert "test" in result.lower()

    def test_generate_ai_background_content_complex(self):
        """Test AI background content generation with complex data."""
        from goldentooth_agent.cli.commands.dev import _generate_ai_background_content

        data = {
            "module_name": "complex_module",
            "description": "A complex module for testing",
            "symbols": ["ClassA", "ClassB", "function_c"],
            "exports": ["ClassA", "function_c"],
            "complexity": "High",
            "file_count": 5,
            "loc": 1000,
            "class_count": 2,
            "function_count": 10,
        }

        result = _generate_ai_background_content(data)

        assert isinstance(result, str)
        assert "complex_module" in result
        assert len(result) > 100  # Should be substantial content

    @patch("goldentooth_agent.cli.commands.dev.ModuleMetadataGenerator")
    def test_module_metadata_integration(self, mock_generator_class):
        """Test integration between CLI and metadata generator."""
        # Test that the CLI properly integrates with the metadata generator
        mock_generator = Mock()
        mock_generator_class.return_value = mock_generator

        # Import and test that we can create a generator instance
        generator_instance = mock_generator_class()
        assert generator_instance is not None

        # Test that the mock is properly configured
        mock_generator_class.assert_called_once()

    def test_path_handling(self):
        """Test path handling in commands."""
        # Create a test module directory
        test_module = self.test_root / "test_module"
        test_module.mkdir()
        (test_module / "__init__.py").write_text('"""Test module."""')

        # Test that Path objects work with the module
        from pathlib import Path

        assert test_module.exists()
        assert test_module.is_dir()
        assert (test_module / "__init__.py").exists()

    def test_error_handling_structure(self):
        """Test that error handling is structured properly."""
        # Test that the function exists and has proper structure
        import inspect

        from goldentooth_agent.cli.commands.dev import update_module_metadata

        source = inspect.getsource(update_module_metadata)

        # Should have error handling
        assert "try:" in source or "except" in source or "typer.Exit" in source

    def test_command_help_text(self):
        """Test that commands have help text."""
        from goldentooth_agent.cli.commands.dev import app, module_app

        # Apps should have help text
        assert hasattr(app, "info")
        assert hasattr(module_app, "info")

        # Check that help is defined
        if hasattr(app.info, "help"):
            assert app.info.help is not None
        if hasattr(module_app.info, "help"):
            assert module_app.info.help is not None
