from __future__ import annotations
from pathlib import Path
from typing import Callable, TypeVar, Any
from antidote import inject

from ..flow import Flow, map_stream, filter_stream, flat_map_stream
from .main import Paths


T = TypeVar("T")


@inject
def path_exists_filter(paths_instance: Paths = inject.get(Paths)) -> Flow[Path, Path]:
    """
    Create a Flow that filters paths to only existing ones.

    Returns:
        A Flow that filters out non-existent paths

    Example:
        paths = Flow.from_iterable([Path("file1.txt"), Path("file2.txt"), Path("missing.txt")])
        existing = paths >> path_exists_filter()
    """
    return filter_stream(lambda path: path.exists())


def resolve_config_path(relative_path: str) -> Flow[Any, Path]:
    """
    Create a Flow that resolves a relative path within the config directory.

    Args:
        relative_path: Relative path within the config directory

    Returns:
        A Flow that returns the resolved config path

    Example:
        flow = Flow.from_iterable([None])
        config_file = flow >> resolve_config_path("settings.json")
    """

    @inject
    def _inner(paths_instance: Paths = inject.get(Paths)) -> Flow[Any, Path]:
        config_dir = paths_instance.config()
        resolved = config_dir / relative_path
        return map_stream(lambda _: resolved)

    return _inner()


def resolve_data_path(relative_path: str) -> Flow[Any, Path]:
    """
    Create a Flow that resolves a relative path within the data directory.

    Args:
        relative_path: Relative path within the data directory

    Returns:
        A Flow that returns the resolved data path

    Example:
        flow = Flow.from_iterable([None])
        cache_file = flow >> resolve_data_path("cache.db")
    """

    @inject
    def _inner(paths_instance: Paths = inject.get(Paths)) -> Flow[Any, Path]:
        data_dir = paths_instance.data()
        resolved = data_dir / relative_path
        return map_stream(lambda _: resolved)

    return _inner()


@inject
def list_directory_flow(
    pattern: str = "*", paths_instance: Paths = inject.get(Paths)
) -> Flow[Path, Path]:
    """
    Create a Flow that lists files in a directory.

    Args:
        pattern: Glob pattern to match files
        paths_instance: Paths instance (injected)

    Returns:
        A Flow that expands directories to their contents

    Example:
        dirs = Flow.from_iterable([paths.config(), paths.data()])
        all_files = dirs >> list_directory_flow("*.json")
    """

    def list_files_async(directory: Path) -> AsyncIterator[Path]:
        async def _list():
            if directory.is_dir():
                for path in directory.glob(pattern):
                    yield path

        return _list()

    return flat_map_stream(list_files_async)


@inject
def ensure_parent_dir(paths_instance: Paths = inject.get(Paths)) -> Flow[Path, Path]:
    """
    Create a Flow that ensures parent directories exist.

    Returns:
        A Flow that creates parent directories if needed

    Example:
        file_paths = Flow.from_iterable([config_dir / "nested/dir/file.txt"])
        prepared = file_paths >> ensure_parent_dir()
    """

    def ensure_parent(path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    return map_stream(ensure_parent)


def read_config_file(filename: str, default_content: str = "") -> Flow[Any, str]:
    """
    Create a Flow that reads a config file.

    Args:
        filename: Name of the config file
        default_content: Content to return if file doesn't exist

    Returns:
        A Flow that reads the file content

    Example:
        flow = Flow.from_iterable([None])
        settings = flow >> read_config_file("settings.json", default_content="{}")
    """

    @inject
    def _inner(paths_instance: Paths = inject.get(Paths)) -> Flow[Any, str]:
        config_path = paths_instance.config() / filename

        if config_path.exists():
            content = config_path.read_text()
        else:
            content = default_content

        return map_stream(lambda _: content)

    return _inner()


def write_config_file(filename: str) -> Flow[str, Path]:
    """
    Create a Flow that writes content to a config file.

    Args:
        filename: Name of the config file

    Returns:
        A Flow that writes content and returns the path

    Example:
        content = Flow.from_iterable(['{"setting": "value"}'])
        saved = content >> write_config_file("settings.json")
    """

    @inject
    def _inner(paths_instance: Paths = inject.get(Paths)) -> Flow[str, Path]:
        def write_content(content: str) -> Path:
            config_path = paths_instance.config() / filename
            config_path.write_text(content)
            return config_path

        return map_stream(write_content)

    return _inner()
