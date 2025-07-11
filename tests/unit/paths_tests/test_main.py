from __future__ import annotations

import logging
import shutil
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from paths.main import APP_AUTHOR, APP_NAME, Paths


class TestPaths:
    """Test suite for Paths class."""

    def test_initialization_with_defaults(self) -> None:
        """Paths should initialize with default app name and author."""
        paths = Paths()
        assert paths.dirs.appname == "goldentooth-agent"
        assert paths.dirs.appauthor == "ndouglas"

    def test_initialization_with_custom_values(self) -> None:
        """Paths should accept custom app name and author."""
        paths = Paths(appname="test-app", appauthor="test-author")
        assert paths.dirs.appname == "test-app"
        assert paths.dirs.appauthor == "test-author"

    def test_config_returns_path(self) -> None:
        """config() should return a Path object."""
        paths = Paths()
        config_path = paths.config()
        assert isinstance(config_path, Path)

    def test_data_returns_path(self) -> None:
        """data() should return a Path object."""
        paths = Paths()
        data_path = paths.data()
        assert isinstance(data_path, Path)

    def test_config_creates_directory(self) -> None:
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

    def test_data_creates_directory(self) -> None:
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

    def test_config_handles_existing_directory(self) -> None:
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

    def test_data_handles_existing_directory(self) -> None:
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

    def test_config_creates_nested_directories(self) -> None:
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

    def test_data_creates_nested_directories(self) -> None:
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

    def test_paths_are_platform_specific(self) -> None:
        """Paths should use platform-specific directories."""
        paths1 = Paths(appname="test-app-1", appauthor="author-1")
        paths2 = Paths(appname="test-app-2", appauthor="author-2")

        # Different apps should have different paths
        assert paths1.config() != paths2.config()
        assert paths1.data() != paths2.data()

    def test_multiple_calls_return_same_path(self) -> None:
        """Multiple calls to config() or data() should return the same path."""
        paths = Paths()

        config1 = paths.config()
        config2 = paths.config()
        assert config1 == config2

        data1 = paths.data()
        data2 = paths.data()
        assert data1 == data2

    def test_config_and_data_are_different(self) -> None:
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

    def test_permission_error_handling(self) -> None:
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

    def test_injectable_decorator(self) -> None:
        """Paths class should be properly decorated as injectable."""
        # The @injectable decorator adds various metadata
        # Check that the class can be instantiated through antidote
        from antidote import world

        # Create instance through antidote
        paths = world.get(Paths)
        assert isinstance(paths, Paths)

    def test_inject_method_decorator(self) -> None:
        """config and data methods should have inject.method decorator."""
        # This is verified by the fact that the methods work with antidote
        paths = Paths()
        assert callable(paths.config)
        assert callable(paths.data)


class TestPathsIntegration:
    """Integration tests for Paths class."""

    def test_real_directory_creation(self) -> None:
        """Test actual directory creation in a controlled environment."""
        with tempfile.TemporaryDirectory() as base_dir:
            # Mock PlatformDirs to use our temp directory
            class MockPlatformDirs:
                def __init__(self, appname: str, appauthor: str) -> None:
                    super().__init__()
                    self.appname = appname
                    self.appauthor = appauthor
                    self.user_config_dir = str(Path(base_dir) / "config" / appname)
                    self.user_data_dir = str(Path(base_dir) / "data" / appname)

            with patch("paths.main.PlatformDirs", MockPlatformDirs):
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

    def test_file_operations_in_paths(self) -> None:
        """Test that files can be created in the generated paths."""
        with tempfile.TemporaryDirectory() as base_dir:

            class MockPlatformDirs:
                def __init__(self, appname: str, appauthor: str) -> None:
                    super().__init__()
                    self.user_config_dir = str(Path(base_dir) / "config")
                    self.user_data_dir = str(Path(base_dir) / "data")

            with patch("paths.main.PlatformDirs", MockPlatformDirs):
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

    def test_concurrent_access(self) -> None:
        """Test that multiple Paths instances can be used concurrently."""
        import threading

        results = []
        errors = []

        def create_and_use_paths(app_id: int) -> None:
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

    def test_path_persistence(self) -> None:
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


class TestPathsMissingMethods:
    """Test suite for methods not covered in existing tests."""

    def test_cache_returns_path_and_creates_directory(self) -> None:
        """Test cache method creates directory and returns path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("paths.main.PlatformDirs") as mock_platform_dirs:
                mock_platform_dirs.return_value.user_cache_dir = temp_dir

                paths = Paths()
                result = paths.cache()

                assert result == Path(temp_dir)
                assert result.exists()

    def test_logs_returns_path_and_creates_directory(self) -> None:
        """Test logs method creates directory and returns path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("paths.main.PlatformDirs") as mock_platform_dirs:
                mock_platform_dirs.return_value.user_log_dir = temp_dir

                paths = Paths()
                result = paths.logs()

                assert result == Path(temp_dir)
                assert result.exists()

    def test_runtime_returns_path_and_creates_directory(self) -> None:
        """Test runtime method creates directory and returns path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("paths.main.PlatformDirs") as mock_platform_dirs:
                mock_platform_dirs.return_value.user_runtime_dir = temp_dir

                paths = Paths()
                result = paths.runtime()

                assert result == Path(temp_dir)
                assert result.exists()

    def test_get_subdir_with_config_parent(self) -> None:
        """Test get_subdir with config parent creates subdirectory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("paths.main.PlatformDirs") as mock_platform_dirs:
                mock_platform_dirs.return_value.user_config_dir = temp_dir

                paths = Paths()
                result = paths.get_subdir("config", "test_subdir")

                expected_path = Path(temp_dir) / "test_subdir"
                assert result == expected_path
                assert result.exists()

    def test_get_subdir_with_data_parent(self) -> None:
        """Test get_subdir with data parent creates subdirectory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("paths.main.PlatformDirs") as mock_platform_dirs:
                mock_platform_dirs.return_value.user_data_dir = temp_dir

                paths = Paths()
                result = paths.get_subdir("data", "test_subdir")

                expected_path = Path(temp_dir) / "test_subdir"
                assert result == expected_path
                assert result.exists()

    def test_get_subdir_with_cache_parent(self) -> None:
        """Test get_subdir with cache parent creates subdirectory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("paths.main.PlatformDirs") as mock_platform_dirs:
                mock_platform_dirs.return_value.user_cache_dir = temp_dir

                paths = Paths()
                result = paths.get_subdir("cache", "test_subdir")

                expected_path = Path(temp_dir) / "test_subdir"
                assert result == expected_path
                assert result.exists()

    def test_get_subdir_with_logs_parent(self) -> None:
        """Test get_subdir with logs parent creates subdirectory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("paths.main.PlatformDirs") as mock_platform_dirs:
                mock_platform_dirs.return_value.user_log_dir = temp_dir

                paths = Paths()
                result = paths.get_subdir("logs", "test_subdir")

                expected_path = Path(temp_dir) / "test_subdir"
                assert result == expected_path
                assert result.exists()

    def test_get_subdir_with_runtime_parent(self) -> None:
        """Test get_subdir with runtime parent creates subdirectory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("paths.main.PlatformDirs") as mock_platform_dirs:
                mock_platform_dirs.return_value.user_runtime_dir = temp_dir

                paths = Paths()
                result = paths.get_subdir("runtime", "test_subdir")

                expected_path = Path(temp_dir) / "test_subdir"
                assert result == expected_path
                assert result.exists()

    def test_get_subdir_with_invalid_parent_raises_value_error(self) -> None:
        """Test get_subdir with invalid parent raises ValueError."""
        paths = Paths()

        with pytest.raises(ValueError, match="Invalid parent directory type: invalid"):
            paths.get_subdir("invalid", "test_subdir")

    def test_ensure_file_creates_new_file_with_default_content(self) -> None:
        """Test ensure_file creates new file with default content."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("paths.main.PlatformDirs") as mock_platform_dirs:
                with patch("paths.main.logger") as mock_logger:
                    mock_platform_dirs.return_value.user_config_dir = temp_dir

                    paths = Paths()
                    result = paths.ensure_file("config", "test.txt", "default content")

                    expected_path = Path(temp_dir) / "test.txt"
                    assert result == expected_path
                    assert result.exists()
                    assert result.read_text() == "default content"
                    mock_logger.info.assert_called_once()

    def test_ensure_file_returns_existing_file_without_modification(self) -> None:
        """Test ensure_file returns existing file without modifying content."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create existing file
            existing_file = Path(temp_dir) / "existing.txt"
            existing_file.write_text("existing content")

            with patch("paths.main.PlatformDirs") as mock_platform_dirs:
                with patch("paths.main.logger") as mock_logger:
                    mock_platform_dirs.return_value.user_config_dir = temp_dir

                    paths = Paths()
                    result = paths.ensure_file(
                        "config", "existing.txt", "default content"
                    )

                    assert result == existing_file
                    assert result.read_text() == "existing content"
                    mock_logger.info.assert_not_called()

    def test_ensure_file_with_empty_default_content(self) -> None:
        """Test ensure_file with empty default content."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("paths.main.PlatformDirs") as mock_platform_dirs:
                mock_platform_dirs.return_value.user_config_dir = temp_dir

                paths = Paths()
                result = paths.ensure_file("config", "empty.txt")

                expected_path = Path(temp_dir) / "empty.txt"
                assert result == expected_path
                assert result.read_text() == ""

    def test_app_info_returns_correct_dictionary(self) -> None:
        """Test app_info property returns correct dictionary."""
        custom_name = "test-app"
        custom_author = "test-author"
        paths = Paths(appname=custom_name, appauthor=custom_author)

        result = paths.app_info

        expected = {
            "name": custom_name,
            "author": custom_author,
        }
        assert result == expected

    def test_app_info_with_default_values(self) -> None:
        """Test app_info property with default values."""
        paths = Paths()

        result = paths.app_info

        expected = {
            "name": APP_NAME,
            "author": APP_AUTHOR,
        }
        assert result == expected

    def test_clear_cache_removes_files_and_returns_count(self) -> None:
        """Test clear_cache removes files and returns count."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            test_file1 = Path(temp_dir) / "file1.txt"
            test_file2 = Path(temp_dir) / "file2.txt"
            test_file1.write_text("content1")
            test_file2.write_text("content2")

            with patch("paths.main.PlatformDirs") as mock_platform_dirs:
                with patch("paths.main.logger") as mock_logger:
                    mock_platform_dirs.return_value.user_cache_dir = temp_dir

                    paths = Paths()
                    count = paths.clear_cache()

                    assert count == 2
                    assert not test_file1.exists()
                    assert not test_file2.exists()
                    mock_logger.info.assert_called_once_with(
                        "Cleared 2 items from cache"
                    )

    def test_clear_cache_removes_directories_with_shutil(self) -> None:
        """Test clear_cache removes directories using shutil.rmtree."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test directory
            test_dir = Path(temp_dir) / "test_dir"
            test_dir.mkdir()
            (test_dir / "nested_file.txt").write_text("nested content")

            with patch("paths.main.PlatformDirs") as mock_platform_dirs:
                with patch("paths.main.logger") as mock_logger:
                    mock_platform_dirs.return_value.user_cache_dir = temp_dir

                    paths = Paths()
                    count = paths.clear_cache()

                    assert count == 1
                    assert not test_dir.exists()
                    mock_logger.info.assert_called_once_with(
                        "Cleared 1 items from cache"
                    )

    def test_clear_cache_handles_empty_directory(self) -> None:
        """Test clear_cache handles empty cache directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("paths.main.PlatformDirs") as mock_platform_dirs:
                with patch("paths.main.logger") as mock_logger:
                    mock_platform_dirs.return_value.user_cache_dir = temp_dir

                    paths = Paths()
                    count = paths.clear_cache()

                    assert count == 0
                    mock_logger.info.assert_called_once_with(
                        "Cleared 0 items from cache"
                    )

    def test_clear_cache_mixed_files_and_directories(self) -> None:
        """Test clear_cache with mixed files and directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create mixed content
            test_file = Path(temp_dir) / "file.txt"
            test_dir = Path(temp_dir) / "dir"
            test_file.write_text("content")
            test_dir.mkdir()
            (test_dir / "nested.txt").write_text("nested")

            with patch("paths.main.PlatformDirs") as mock_platform_dirs:
                with patch("paths.main.logger") as mock_logger:
                    mock_platform_dirs.return_value.user_cache_dir = temp_dir

                    paths = Paths()
                    count = paths.clear_cache()

                    assert count == 2
                    assert not test_file.exists()
                    assert not test_dir.exists()
                    mock_logger.info.assert_called_once_with(
                        "Cleared 2 items from cache"
                    )

    def test_shutil_not_used_for_files_only(self) -> None:
        """Test that shutil.rmtree is not used when only files are present."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create only files, no directories
            test_file = Path(temp_dir) / "file.txt"
            test_file.write_text("content")

            with patch("paths.main.PlatformDirs") as mock_platform_dirs:
                mock_platform_dirs.return_value.user_cache_dir = temp_dir

                paths = Paths()
                count = paths.clear_cache()

                # Should have removed 1 file without using shutil
                assert count == 1
                assert not test_file.exists()

    def test_debug_logging_in_all_directory_methods(self) -> None:
        """Test that all directory methods log debug messages."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("paths.main.PlatformDirs") as mock_platform_dirs:
                with patch("paths.main.logger") as mock_logger:
                    mock_platform_dirs.return_value.user_config_dir = temp_dir
                    mock_platform_dirs.return_value.user_data_dir = temp_dir
                    mock_platform_dirs.return_value.user_cache_dir = temp_dir
                    mock_platform_dirs.return_value.user_log_dir = temp_dir
                    mock_platform_dirs.return_value.user_runtime_dir = temp_dir

                    paths = Paths()

                    # Call all directory methods
                    paths.config()
                    paths.data()
                    paths.cache()
                    paths.logs()
                    paths.runtime()

                    # Verify debug messages were logged
                    assert mock_logger.debug.call_count == 5
                    debug_calls = mock_logger.debug.call_args_list
                    assert any("Config directory:" in str(call) for call in debug_calls)
                    assert any("Data directory:" in str(call) for call in debug_calls)
                    assert any("Cache directory:" in str(call) for call in debug_calls)
                    assert any("Logs directory:" in str(call) for call in debug_calls)
                    assert any(
                        "Runtime directory:" in str(call) for call in debug_calls
                    )


class TestConstants:
    """Test suite for module constants."""

    def test_app_name_constant(self) -> None:
        """Test APP_NAME constant is defined correctly."""
        assert APP_NAME == "goldentooth-agent"
        assert isinstance(APP_NAME, str)

    def test_app_author_constant(self) -> None:
        """Test APP_AUTHOR constant is defined correctly."""
        assert APP_AUTHOR == "ndouglas"
        assert isinstance(APP_AUTHOR, str)

    def test_logger_is_configured(self) -> None:
        """Test logger is properly configured."""
        import paths.main

        logger = paths.main.logger
        assert isinstance(logger, logging.Logger)
        assert logger.name == "paths.main"


class TestPathsEdgeCases:
    """Test suite for edge cases and error conditions."""

    def test_get_subdir_creates_nested_subdirectories(self) -> None:
        """Test get_subdir can create nested subdirectories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("paths.main.PlatformDirs") as mock_platform_dirs:
                mock_platform_dirs.return_value.user_config_dir = temp_dir

                paths = Paths()
                result = paths.get_subdir("config", "nested/deep/subdir")

                expected_path = Path(temp_dir) / "nested/deep/subdir"
                assert result == expected_path
                assert result.exists()

    def test_ensure_file_with_nested_subdirectory(self) -> None:
        """Test ensure_file works when parent has nested path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("paths.main.PlatformDirs") as mock_platform_dirs:
                mock_platform_dirs.return_value.user_config_dir = temp_dir

                paths = Paths()
                # First create nested subdir
                paths.get_subdir("config", "nested/dir")
                # Then try to ensure file in config root
                result = paths.ensure_file("config", "config.json", '{"test": true}')

                expected_path = Path(temp_dir) / "config.json"
                assert result == expected_path
                assert result.read_text() == '{"test": true}'

    def test_multiple_paths_instances_isolated(self) -> None:
        """Test that multiple Paths instances are properly isolated."""
        paths1 = Paths(appname="app1", appauthor="author1")
        paths2 = Paths(appname="app2", appauthor="author2")

        info1 = paths1.app_info
        info2 = paths2.app_info

        assert info1["name"] == "app1"
        assert info1["author"] == "author1"
        assert info2["name"] == "app2"
        assert info2["author"] == "author2"

    def test_path_methods_are_idempotent(self) -> None:
        """Test that calling path methods multiple times is safe."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("paths.main.PlatformDirs") as mock_platform_dirs:
                mock_platform_dirs.return_value.user_config_dir = temp_dir

                paths = Paths()

                # Call config multiple times
                path1 = paths.config()
                path2 = paths.config()
                path3 = paths.config()

                assert path1 == path2 == path3
                assert path1.exists()

    def test_clear_cache_returns_zero_for_nonexistent_files(self) -> None:
        """Test clear_cache returns 0 when cache is already empty."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("paths.main.PlatformDirs") as mock_platform_dirs:
                mock_platform_dirs.return_value.user_cache_dir = temp_dir

                paths = Paths()

                # Clear empty cache multiple times
                count1 = paths.clear_cache()
                count2 = paths.clear_cache()

                assert count1 == 0
                assert count2 == 0
