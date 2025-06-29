from __future__ import annotations

import tempfile
from collections.abc import AsyncIterator
from pathlib import Path
from typing import TypeVar
from unittest.mock import patch

import pytest

from goldentooth_agent.core.paths import (
    ensure_parent_dir,
    list_directory_flow,
    path_exists_filter,
    read_config_file,
    resolve_config_path,
    resolve_data_path,
    write_config_file,
)
from goldentooth_agent.flow_engine import Flow

T = TypeVar("T")


def flow_from_list(items: list[T]) -> Flow[None, T]:
    """Create a flow that yields items from a list."""
    return Flow.from_iterable(items)


async def empty_stream() -> AsyncIterator[None]:
    """Create an empty async stream."""
    return
    yield  # unreachable, but makes this an async generator


class TestPathsFlowIntegration:
    """Test suite for paths Flow integration."""

    @pytest.mark.asyncio
    async def test_path_exists_filter(self):
        """path_exists_filter should filter out non-existent paths."""
        with tempfile.TemporaryDirectory() as temp_dir:
            existing = Path(temp_dir) / "existing.txt"
            existing.write_text("content")

            paths = [
                existing,
                Path(temp_dir) / "missing.txt",
                Path(temp_dir),
            ]

            flow = flow_from_list(paths)
            processed = flow >> path_exists_filter()
            result = [item async for item in processed(empty_stream())]

            assert len(result) == 2
            assert existing in result
            assert Path(temp_dir) in result

    @pytest.mark.asyncio
    async def test_resolve_config_path(self):
        """resolve_config_path should resolve paths in config directory."""
        # This function creates a flow that resolves relative paths
        # The actual path depends on the current system's config directory
        flow = flow_from_list([None])
        processed = flow >> resolve_config_path("settings.json")
        result = [item async for item in processed(empty_stream())]

        assert len(result) == 1
        # Just verify it ends with the relative path we specified
        assert str(result[0]).endswith("settings.json")

    @pytest.mark.asyncio
    async def test_resolve_data_path(self):
        """resolve_data_path should resolve paths in data directory."""
        # This function creates a flow that resolves relative paths in data directory
        # The actual path depends on the current system's data directory
        flow = flow_from_list([None])
        processed = flow >> resolve_data_path("cache.db")
        result = [item async for item in processed(empty_stream())]

        assert len(result) == 1
        # Just verify it ends with the relative path we specified
        assert str(result[0]).endswith("cache.db")

    @pytest.mark.asyncio
    async def test_list_directory_flow(self):
        """list_directory_flow should list files matching pattern."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test files
            (temp_path / "file1.json").write_text("{}")
            (temp_path / "file2.json").write_text("{}")
            (temp_path / "file3.txt").write_text("text")

            flow = flow_from_list([temp_path])
            processed = flow >> list_directory_flow("*.json")
            result = [item async for item in processed(empty_stream())]

            assert len(result) == 2
            assert all(p.suffix == ".json" for p in result)

    @pytest.mark.asyncio
    async def test_ensure_parent_dir(self):
        """ensure_parent_dir should create parent directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "nested" / "dir" / "file.txt"

            flow = flow_from_list([file_path])
            processed = flow >> ensure_parent_dir()
            result = [item async for item in processed(empty_stream())]

            assert result == [file_path]
            assert file_path.parent.exists()
            assert file_path.parent.is_dir()

    @pytest.mark.asyncio
    async def test_read_config_file_existing(self):
        """read_config_file should read existing files."""
        # Since dependency injection creates a global instance,
        # we'll test the functionality differently by creating our own test file
        # in the actual config directory
        from goldentooth_agent.core.paths import Paths

        paths = Paths()
        config_dir = paths.config()

        # Create a test file that we'll clean up
        test_file = config_dir / "test_flow_integration.json"
        test_content = '{"test": "flow_integration"}'
        test_file.write_text(test_content)

        try:
            flow = flow_from_list([None])
            processed = flow >> read_config_file("test_flow_integration.json")
            result = [item async for item in processed(empty_stream())]

            assert result == [test_content]
        finally:
            # Clean up test file
            if test_file.exists():
                test_file.unlink()

    @pytest.mark.asyncio
    async def test_read_config_file_missing(self):
        """read_config_file should return default for missing files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("goldentooth_agent.core.paths.main.PlatformDirs") as mock_dirs:
                mock_dirs.return_value.user_config_dir = temp_dir

                flow = flow_from_list([None])
                processed = flow >> read_config_file(
                    "missing.json", default_content="{}"
                )
                result = [item async for item in processed(empty_stream())]

                assert result == ["{}"]

    @pytest.mark.asyncio
    async def test_write_config_file(self):
        """write_config_file should write content to config file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("goldentooth_agent.core.paths.main.PlatformDirs") as mock_dirs:
                mock_dirs.return_value.user_config_dir = temp_dir

                flow = flow_from_list(['{"setting": "value"}'])
                processed = flow >> write_config_file("output.json")
                result = [item async for item in processed(empty_stream())]

                assert len(result) == 1
                assert result[0].name == "output.json"
                assert result[0].read_text() == '{"setting": "value"}'
