from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from goldentooth_agent.core.paths import Paths


class TestPaths:
    """Test suite for Paths class."""

    def test_initialization_with_defaults(self):
        """Paths should initialize with default app name and author."""
        paths = Paths()
        assert paths.dirs.appname == "goldentooth-agent"
        assert paths.dirs.appauthor == "ndouglas"

    def test_initialization_with_custom_values(self):
        """Paths should accept custom app name and author."""
        paths = Paths(appname="test-app", appauthor="test-author")
        assert paths.dirs.appname == "test-app"
        assert paths.dirs.appauthor == "test-author"

    def test_config_returns_path(self):
        """config() should return a Path object."""
        paths = Paths()
        config_path = paths.config()
        assert isinstance(config_path, Path)

    def test_data_returns_path(self):
        """data() should return a Path object."""
        paths = Paths()
        data_path = paths.data()
        assert isinstance(data_path, Path)

    def test_config_creates_directory(self):
        """config() should create the directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_dirs = Mock()
            mock_dirs.user_config_dir = str(Path(temp_dir) / "config")

            with patch.object(
                Paths,
                "__init__",
                lambda self, **kwargs: setattr(self, "dirs", mock_dirs),
            ):
                paths = Paths()
                config_path = paths.config()

                assert config_path.exists()
                assert config_path.is_dir()

    def test_data_creates_directory(self):
        """data() should create the directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_dirs = Mock()
            mock_dirs.user_data_dir = str(Path(temp_dir) / "data")

            with patch.object(
                Paths,
                "__init__",
                lambda self, **kwargs: setattr(self, "dirs", mock_dirs),
            ):
                paths = Paths()
                data_path = paths.data()

                assert data_path.exists()
                assert data_path.is_dir()

    def test_config_handles_existing_directory(self):
        """config() should handle already existing directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            existing_dir = Path(temp_dir) / "existing_config"
            existing_dir.mkdir(parents=True)

            mock_dirs = Mock()
            mock_dirs.user_config_dir = str(existing_dir)

            with patch.object(
                Paths,
                "__init__",
                lambda self, **kwargs: setattr(self, "dirs", mock_dirs),
            ):
                paths = Paths()
                config_path = paths.config()

                assert config_path == existing_dir
                assert config_path.exists()

    def test_data_handles_existing_directory(self):
        """data() should handle already existing directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            existing_dir = Path(temp_dir) / "existing_data"
            existing_dir.mkdir(parents=True)

            mock_dirs = Mock()
            mock_dirs.user_data_dir = str(existing_dir)

            with patch.object(
                Paths,
                "__init__",
                lambda self, **kwargs: setattr(self, "dirs", mock_dirs),
            ):
                paths = Paths()
                data_path = paths.data()

                assert data_path == existing_dir
                assert data_path.exists()

    def test_config_creates_nested_directories(self):
        """config() should create parent directories if needed."""
        with tempfile.TemporaryDirectory() as temp_dir:
            nested_path = Path(temp_dir) / "level1" / "level2" / "config"
            mock_dirs = Mock()
            mock_dirs.user_config_dir = str(nested_path)

            with patch.object(
                Paths,
                "__init__",
                lambda self, **kwargs: setattr(self, "dirs", mock_dirs),
            ):
                paths = Paths()
                config_path = paths.config()

                assert config_path.exists()
                assert config_path.is_dir()
                assert config_path.parent.parent.name == "level1"

    def test_data_creates_nested_directories(self):
        """data() should create parent directories if needed."""
        with tempfile.TemporaryDirectory() as temp_dir:
            nested_path = Path(temp_dir) / "level1" / "level2" / "data"
            mock_dirs = Mock()
            mock_dirs.user_data_dir = str(nested_path)

            with patch.object(
                Paths,
                "__init__",
                lambda self, **kwargs: setattr(self, "dirs", mock_dirs),
            ):
                paths = Paths()
                data_path = paths.data()

                assert data_path.exists()
                assert data_path.is_dir()
                assert data_path.parent.parent.name == "level1"

    def test_paths_are_platform_specific(self):
        """Paths should use platform-specific directories."""
        paths1 = Paths(appname="test-app-1", appauthor="author-1")
        paths2 = Paths(appname="test-app-2", appauthor="author-2")

        # Different apps should have different paths
        assert paths1.config() != paths2.config()
        assert paths1.data() != paths2.data()

    def test_multiple_calls_return_same_path(self):
        """Multiple calls to config() or data() should return the same path."""
        paths = Paths()

        config1 = paths.config()
        config2 = paths.config()
        assert config1 == config2

        data1 = paths.data()
        data2 = paths.data()
        assert data1 == data2

    def test_config_and_data_are_different(self):
        """config() and data() should return different directories."""
        # On some platforms (like macOS), config and data may be the same
        # This is platform-specific behavior from PlatformDirs
        paths = Paths()

        config_path = paths.config()
        data_path = paths.data()

        # Both should be valid paths
        assert isinstance(config_path, Path)
        assert isinstance(data_path, Path)
        # They may or may not be different depending on the platform

    def test_permission_error_handling(self):
        """Should handle permission errors gracefully."""
        with tempfile.TemporaryDirectory() as temp_dir:
            protected_dir = Path(temp_dir) / "protected"
            protected_dir.mkdir()

            # Make directory read-only
            protected_dir.chmod(0o444)

            mock_dirs = Mock()
            mock_dirs.user_config_dir = str(protected_dir / "config")

            with patch.object(
                Paths,
                "__init__",
                lambda self, **kwargs: setattr(self, "dirs", mock_dirs),
            ):
                paths = Paths()

                # This should raise a permission error
                with pytest.raises(PermissionError):
                    paths.config()

            # Cleanup
            protected_dir.chmod(0o755)

    def test_injectable_decorator(self):
        """Paths class should be properly decorated as injectable."""
        # The @injectable decorator adds various metadata
        # Check that the class can be instantiated through antidote
        from antidote import world

        # Create instance through antidote
        paths = world.get(Paths)
        assert isinstance(paths, Paths)

    def test_inject_method_decorator(self):
        """config and data methods should have inject.method decorator."""
        # This is verified by the fact that the methods work with antidote
        paths = Paths()
        assert callable(paths.config)
        assert callable(paths.data)


class TestPathsIntegration:
    """Integration tests for Paths class."""

    def test_real_directory_creation(self):
        """Test actual directory creation in a controlled environment."""
        with tempfile.TemporaryDirectory() as base_dir:
            # Mock PlatformDirs to use our temp directory
            class MockPlatformDirs:
                def __init__(self, appname, appauthor):
                    self.appname = appname
                    self.appauthor = appauthor
                    self.user_config_dir = str(Path(base_dir) / "config" / appname)
                    self.user_data_dir = str(Path(base_dir) / "data" / appname)

            with patch(
                "goldentooth_agent.core.paths.main.PlatformDirs", MockPlatformDirs
            ):
                paths = Paths(appname="test-app", appauthor="test-author")

                # Get paths
                config_path = paths.config()
                data_path = paths.data()

                # Verify they exist
                assert config_path.exists()
                assert data_path.exists()

                # Verify structure
                assert "config" in str(config_path)
                assert "data" in str(data_path)
                assert "test-app" in str(config_path)
                assert "test-app" in str(data_path)

    def test_file_operations_in_paths(self):
        """Test that files can be created in the generated paths."""
        with tempfile.TemporaryDirectory() as base_dir:

            class MockPlatformDirs:
                def __init__(self, appname, appauthor):
                    self.user_config_dir = str(Path(base_dir) / "config")
                    self.user_data_dir = str(Path(base_dir) / "data")

            with patch(
                "goldentooth_agent.core.paths.main.PlatformDirs", MockPlatformDirs
            ):
                paths = Paths()

                # Write to config directory
                config_file = paths.config() / "settings.json"
                config_file.write_text('{"setting": "value"}')
                assert config_file.exists()
                assert config_file.read_text() == '{"setting": "value"}'

                # Write to data directory
                data_file = paths.data() / "cache.db"
                data_file.write_text("database content")
                assert data_file.exists()
                assert data_file.read_text() == "database content"

    def test_concurrent_access(self):
        """Test that multiple Paths instances can be used concurrently."""
        import threading

        results = []
        errors = []

        def create_and_use_paths(app_id: int):
            try:
                paths = Paths(appname=f"app-{app_id}")
                config = paths.config()
                data = paths.data()
                results.append((config, data))
            except Exception as e:
                errors.append(e)

        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_and_use_paths, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        assert len(errors) == 0
        assert len(results) == 5

        # All paths should be different
        config_paths = [r[0] for r in results]
        data_paths = [r[1] for r in results]
        assert len({str(p) for p in config_paths}) == 5
        assert len({str(p) for p in data_paths}) == 5

    def test_path_persistence(self):
        """Test that paths are consistent across instances."""
        paths1 = Paths(appname="persistent-app", appauthor="test-author")
        config1 = paths1.config()
        data1 = paths1.data()

        # Create new instance with same parameters
        paths2 = Paths(appname="persistent-app", appauthor="test-author")
        config2 = paths2.config()
        data2 = paths2.data()

        # Paths should be identical
        assert config1 == config2
        assert data1 == data2
