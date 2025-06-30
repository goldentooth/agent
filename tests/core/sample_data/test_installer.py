"""
Tests for sample data installer functionality.
"""

import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, Mock, patch

import pytest

from goldentooth_agent.core.sample_data.installer import install_sample_data


class TestSampleDataInstaller:
    """Test sample data installer functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_root = Path(self.temp_dir.name)

    def teardown_method(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()

    @patch("goldentooth_agent.core.sample_data.installer.DocumentStore")
    @patch("goldentooth_agent.core.sample_data.installer.importlib.resources.files")
    def test_install_sample_data_success(self, mock_files, mock_document_store_class):
        """Test successful sample data installation."""
        # Mock paths
        mock_paths = Mock()
        mock_paths.data.return_value = self.test_root

        # Mock document store
        mock_store = Mock()
        mock_document_store_class.return_value = mock_store

        # Mock file structure
        mock_package_files = Mock()
        mock_files.return_value = mock_package_files

        # Mock org files
        mock_org_dir = Mock()
        mock_org_dir.is_dir.return_value = True
        mock_org_file = Mock()
        mock_org_file.name = "test_org.yaml"
        mock_org_file.stem = "test_org"
        mock_org_file.read_text.return_value = (
            "name: Test Org\ndescription: A test organization"
        )
        mock_org_dir.iterdir.return_value = [mock_org_file]
        mock_package_files.joinpath.return_value = mock_org_dir

        # Mock adapters
        with patch("yaml.safe_load") as mock_yaml:
            with patch(
                "goldentooth_agent.core.sample_data.installer.GitHubOrgAdapter"
            ) as mock_org_adapter:
                mock_yaml.return_value = {"name": "Test Org"}
                mock_org_adapter.from_dict.return_value = Mock()

                result = install_sample_data(mock_paths)

        assert result["success"] is True
        assert result["total_installed"] >= 0
        assert "installed_counts" in result
        assert "data_directory" in result

    @patch("goldentooth_agent.core.sample_data.installer.DocumentStore")
    @patch("goldentooth_agent.core.sample_data.installer.importlib.resources.files")
    def test_install_sample_data_with_repos(
        self, mock_files, mock_document_store_class
    ):
        """Test sample data installation with repositories."""
        mock_paths = Mock()
        mock_paths.data.return_value = self.test_root

        mock_store = Mock()
        mock_document_store_class.return_value = mock_store

        # Mock package structure
        mock_package_files = Mock()
        mock_files.return_value = mock_package_files

        # Create a side effect function for joinpath
        def joinpath_side_effect(path):
            mock_dir = Mock()
            if "orgs" in path:
                mock_dir.is_dir.return_value = False  # No orgs
            elif "repos" in path:
                mock_dir.is_dir.return_value = True
                mock_file = Mock()
                mock_file.name = "test_repo.yaml"
                mock_file.stem = "test_repo"
                mock_file.read_text.return_value = (
                    "name: test-repo\ndescription: A test repository"
                )
                mock_dir.iterdir.return_value = [mock_file]
            elif "notes" in path:
                mock_dir.is_dir.return_value = False  # No notes
            else:
                mock_dir.is_dir.return_value = False
            return mock_dir

        mock_package_files.joinpath.side_effect = joinpath_side_effect

        with patch("yaml.safe_load") as mock_yaml:
            with patch(
                "goldentooth_agent.core.sample_data.installer.GitHubRepoAdapter"
            ) as mock_repo_adapter:
                mock_yaml.return_value = {"name": "test-repo"}
                mock_repo_adapter.from_dict.return_value = Mock()

                result = install_sample_data(mock_paths)

        assert result["success"] is True
        assert "github.repos" in result["installed_counts"]

    @patch("goldentooth_agent.core.sample_data.installer.DocumentStore")
    @patch("goldentooth_agent.core.sample_data.installer.importlib.resources.files")
    def test_install_sample_data_with_notes(
        self, mock_files, mock_document_store_class
    ):
        """Test sample data installation with notes."""
        mock_paths = Mock()
        mock_paths.data.return_value = self.test_root

        mock_store = Mock()
        mock_document_store_class.return_value = mock_store

        # Mock package structure
        mock_package_files = Mock()
        mock_files.return_value = mock_package_files

        # Create a side effect function for joinpath
        def joinpath_side_effect(path):
            mock_dir = Mock()
            if "notes" in path:
                mock_dir.is_dir.return_value = True
                mock_file = Mock()
                mock_file.name = "test_note.yaml"
                mock_file.stem = "test_note"
                mock_file.read_text.return_value = (
                    "title: Test Note\ncontent: This is a test note"
                )
                mock_dir.iterdir.return_value = [mock_file]
            else:
                mock_dir.is_dir.return_value = False
            return mock_dir

        mock_package_files.joinpath.side_effect = joinpath_side_effect

        with patch("yaml.safe_load") as mock_yaml:
            with patch(
                "goldentooth_agent.core.sample_data.installer.NoteAdapter"
            ) as mock_note_adapter:
                mock_yaml.return_value = {"title": "Test Note"}
                mock_note_adapter.from_dict.return_value = Mock()

                result = install_sample_data(mock_paths)

        assert result["success"] is True
        assert "notes" in result["installed_counts"]

    @patch("goldentooth_agent.core.sample_data.installer.DocumentStore")
    @patch("goldentooth_agent.core.sample_data.installer.importlib.resources.files")
    def test_install_sample_data_no_directories(
        self, mock_files, mock_document_store_class
    ):
        """Test sample data installation when no directories exist."""
        mock_paths = Mock()
        mock_paths.data.return_value = self.test_root

        mock_store = Mock()
        mock_document_store_class.return_value = mock_store

        # Mock empty package structure
        mock_package_files = Mock()
        mock_files.return_value = mock_package_files

        mock_empty_dir = Mock()
        mock_empty_dir.is_dir.return_value = False
        mock_package_files.joinpath.return_value = mock_empty_dir

        result = install_sample_data(mock_paths)

        assert result["success"] is True
        assert result["total_installed"] == 0
        assert all(count == 0 for count in result["installed_counts"].values())

    @patch("goldentooth_agent.core.sample_data.installer.DocumentStore")
    @patch("goldentooth_agent.core.sample_data.installer.importlib.resources.files")
    def test_install_sample_data_with_mixed_files(
        self, mock_files, mock_document_store_class
    ):
        """Test installation with mixed file types (some .yaml, some not)."""
        mock_paths = Mock()
        mock_paths.data.return_value = self.test_root

        mock_store = Mock()
        mock_document_store_class.return_value = mock_store

        mock_package_files = Mock()
        mock_files.return_value = mock_package_files

        # Mock directory with mixed files
        mock_dir = Mock()
        mock_dir.is_dir.return_value = True

        # Create YAML and non-YAML files
        yaml_file = Mock()
        yaml_file.name = "valid.yaml"
        yaml_file.stem = "valid"
        yaml_file.read_text.return_value = "name: Valid File"

        txt_file = Mock()
        txt_file.name = "invalid.txt"

        mock_dir.iterdir.return_value = [yaml_file, txt_file]
        mock_package_files.joinpath.return_value = mock_dir

        with patch("yaml.safe_load") as mock_yaml:
            with patch(
                "goldentooth_agent.core.sample_data.installer.GitHubOrgAdapter"
            ) as mock_adapter:
                mock_yaml.return_value = {"name": "Valid File"}
                mock_adapter.from_dict.return_value = Mock()

                result = install_sample_data(mock_paths)

        assert result["success"] is True
        # Should process .yaml files (called for each directory: orgs, repos, notes)
        assert mock_yaml.call_count >= 1

    @patch("goldentooth_agent.core.sample_data.installer.DocumentStore")
    def test_install_sample_data_document_store_error(self, mock_document_store_class):
        """Test handling of document store initialization error."""
        mock_paths = Mock()
        mock_paths.data.return_value = self.test_root

        # Make DocumentStore raise an exception
        mock_document_store_class.side_effect = Exception("Document store error")

        result = install_sample_data(mock_paths)

        assert result["success"] is False
        assert "error" in result
        assert result["total_installed"] == 0
        assert "Document store error" in result["error"]

    @patch("goldentooth_agent.core.sample_data.installer.DocumentStore")
    @patch("goldentooth_agent.core.sample_data.installer.importlib.resources.files")
    def test_install_sample_data_org_parsing_error(
        self, mock_files, mock_document_store_class
    ):
        """Test handling of organization parsing error."""
        mock_paths = Mock()
        mock_paths.data.return_value = self.test_root

        mock_store = Mock()
        mock_document_store_class.return_value = mock_store

        mock_package_files = Mock()
        mock_files.return_value = mock_package_files

        # Mock org directory that will cause parsing error
        mock_org_dir = Mock()
        mock_org_dir.is_dir.return_value = True
        mock_org_file = Mock()
        mock_org_file.name = "bad_org.yaml"
        mock_org_file.stem = "bad_org"
        mock_org_file.read_text.side_effect = Exception("File read error")
        mock_org_dir.iterdir.return_value = [mock_org_file]

        # Create a side effect for joinpath
        def joinpath_side_effect(path):
            if "orgs" in path:
                return mock_org_dir
            else:
                mock_empty = Mock()
                mock_empty.is_dir.return_value = False
                return mock_empty

        mock_package_files.joinpath.side_effect = joinpath_side_effect

        # Should continue despite error and return success
        result = install_sample_data(mock_paths)

        assert result["success"] is True
        assert result["installed_counts"]["github.orgs"] == 0

    @patch("goldentooth_agent.core.sample_data.installer.DocumentStore")
    @patch("goldentooth_agent.core.sample_data.installer.importlib.resources.files")
    def test_install_sample_data_yaml_parsing_error(
        self, mock_files, mock_document_store_class
    ):
        """Test handling of YAML parsing error."""
        mock_paths = Mock()
        mock_paths.data.return_value = self.test_root

        mock_store = Mock()
        mock_document_store_class.return_value = mock_store

        mock_package_files = Mock()
        mock_files.return_value = mock_package_files

        # Mock file with invalid YAML
        mock_dir = Mock()
        mock_dir.is_dir.return_value = True
        mock_file = Mock()
        mock_file.name = "invalid.yaml"
        mock_file.stem = "invalid"
        mock_file.read_text.return_value = "invalid: yaml: content: ["
        mock_dir.iterdir.return_value = [mock_file]

        def joinpath_side_effect(path):
            if "orgs" in path:
                return mock_dir
            else:
                mock_empty = Mock()
                mock_empty.is_dir.return_value = False
                return mock_empty

        mock_package_files.joinpath.side_effect = joinpath_side_effect

        with patch("yaml.safe_load") as mock_yaml:
            mock_yaml.side_effect = Exception("YAML parsing error")

            result = install_sample_data(mock_paths)

        assert result["success"] is True
        assert result["installed_counts"]["github.orgs"] == 0

    @patch("goldentooth_agent.core.sample_data.installer.DocumentStore")
    @patch("goldentooth_agent.core.sample_data.installer.importlib.resources.files")
    def test_install_sample_data_complete_workflow(
        self, mock_files, mock_document_store_class
    ):
        """Test complete workflow with all types of data."""
        mock_paths = Mock()
        mock_paths.data.return_value = self.test_root

        mock_store = Mock()
        mock_document_store_class.return_value = mock_store

        mock_package_files = Mock()
        mock_files.return_value = mock_package_files

        # Create comprehensive mock structure
        def create_mock_dir_with_files(file_names):
            mock_dir = Mock()
            mock_dir.is_dir.return_value = True
            mock_files_list = []

            for name in file_names:
                mock_file = Mock()
                mock_file.name = f"{name}.yaml"
                mock_file.stem = name
                mock_file.read_text.return_value = (
                    f"name: {name}\ndescription: Test {name}"
                )
                mock_files_list.append(mock_file)

            mock_dir.iterdir.return_value = mock_files_list
            return mock_dir

        def joinpath_side_effect(path):
            if "orgs" in path:
                return create_mock_dir_with_files(["org1", "org2"])
            elif "repos" in path:
                return create_mock_dir_with_files(["repo1", "repo2", "repo3"])
            elif "notes" in path:
                return create_mock_dir_with_files(["note1"])
            else:
                mock_empty = Mock()
                mock_empty.is_dir.return_value = False
                return mock_empty

        mock_package_files.joinpath.side_effect = joinpath_side_effect

        with patch("yaml.safe_load") as mock_yaml:
            with patch(
                "goldentooth_agent.core.sample_data.installer.GitHubOrgAdapter"
            ) as mock_org_adapter:
                with patch(
                    "goldentooth_agent.core.sample_data.installer.GitHubRepoAdapter"
                ) as mock_repo_adapter:
                    with patch(
                        "goldentooth_agent.core.sample_data.installer.NoteAdapter"
                    ) as mock_note_adapter:
                        mock_yaml.return_value = {"name": "test"}
                        mock_org_adapter.from_dict.return_value = Mock()
                        mock_repo_adapter.from_dict.return_value = Mock()
                        mock_note_adapter.from_dict.return_value = Mock()

                        result = install_sample_data(mock_paths)

        assert result["success"] is True
        assert result["total_installed"] == 6  # 2 orgs + 3 repos + 1 note
        assert result["installed_counts"]["github.orgs"] == 2
        assert result["installed_counts"]["github.repos"] == 3
        assert result["installed_counts"]["notes"] == 1
        assert result["data_directory"] == str(self.test_root)


class TestSampleDataInstallerImports:
    """Test imports and dependencies."""

    def test_function_import(self):
        """Test that the main function can be imported."""
        from goldentooth_agent.core.sample_data.installer import install_sample_data

        assert callable(install_sample_data)

    def test_dependencies_import(self):
        """Test that all dependencies can be imported."""
        from goldentooth_agent.core.document_store import DocumentStore
        from goldentooth_agent.core.paths import Paths
        from goldentooth_agent.core.schemas import (
            GitHubOrgAdapter,
            GitHubRepoAdapter,
            NoteAdapter,
        )

        assert DocumentStore is not None
        assert Paths is not None
        assert GitHubOrgAdapter is not None
        assert GitHubRepoAdapter is not None
        assert NoteAdapter is not None

    def test_standard_library_imports(self):
        """Test standard library imports."""
        import importlib.resources

        import yaml

        assert importlib.resources is not None
        assert yaml is not None

    def test_function_signature(self):
        """Test function signature."""
        import inspect

        from goldentooth_agent.core.sample_data.installer import install_sample_data

        sig = inspect.signature(install_sample_data)

        # Should have paths parameter
        assert "paths" in sig.parameters
        # Should return dict
        assert sig.return_annotation == dict[str, Any] or "dict" in str(
            sig.return_annotation
        )

    def test_function_docstring(self):
        """Test function has proper docstring."""
        from goldentooth_agent.core.sample_data.installer import install_sample_data

        assert install_sample_data.__doc__ is not None
        assert "Install sample GitHub data" in install_sample_data.__doc__


class TestSampleDataInstallerEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_paths_object(self):
        """Test behavior with empty paths object."""
        mock_paths = Mock()
        mock_paths.data.return_value = Path("/nonexistent")

        with patch(
            "goldentooth_agent.core.sample_data.installer.DocumentStore"
        ) as mock_ds:
            mock_ds.side_effect = Exception("Path error")

            result = install_sample_data(mock_paths)

            assert result["success"] is False
            assert "error" in result

    def test_missing_package_resources(self):
        """Test behavior when package resources are missing."""
        mock_paths = Mock()
        mock_paths.data.return_value = Path("/test")

        with patch("goldentooth_agent.core.sample_data.installer.DocumentStore"):
            with patch(
                "goldentooth_agent.core.sample_data.installer.importlib.resources.files"
            ) as mock_files:
                mock_files.side_effect = Exception("Package not found")

                result = install_sample_data(mock_paths)

                # The function continues despite package errors (it catches exceptions)
                assert result["success"] is True
                assert result["total_installed"] == 0

    def test_result_structure(self):
        """Test that result has proper structure."""
        mock_paths = Mock()
        mock_paths.data.return_value = Path("/test")

        with patch("goldentooth_agent.core.sample_data.installer.DocumentStore"):
            with patch(
                "goldentooth_agent.core.sample_data.installer.importlib.resources.files"
            ) as mock_files:
                mock_package = Mock()
                mock_dir = Mock()
                mock_dir.is_dir.return_value = False
                mock_package.joinpath.return_value = mock_dir
                mock_files.return_value = mock_package

                result = install_sample_data(mock_paths)

        # Verify result structure
        required_keys = [
            "success",
            "total_installed",
            "installed_counts",
            "data_directory",
        ]
        for key in required_keys:
            assert key in result

        # Verify installed_counts structure
        count_keys = ["github.orgs", "github.repos", "notes"]
        for key in count_keys:
            assert key in result["installed_counts"]
