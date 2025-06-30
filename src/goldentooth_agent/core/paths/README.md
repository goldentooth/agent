# Paths

Paths module

## Overview

- **Complexity**: Medium
- **Files**: 3 Python files
- **Lines of Code**: ~295
- **Classes**: 1
- **Functions**: 17

## API Reference

### Classes

#### Paths
A class to manage user-specific paths for configuration and data storage.

**Public Methods:**
- `config(self) -> Path` - Get the user configuration directory, creating it if it doesn't exist
- `data(self) -> Path` - Get the user data directory, creating it if it doesn't exist
- `cache(self) -> Path` - Get the user cache directory, creating it if it doesn't exist
- `logs(self) -> Path` - Get the user logs directory, creating it if it doesn't exist
- `runtime(self) -> Path` - Get the user runtime directory, creating it if it doesn't exist
- `get_subdir(self, parent: str, subdir: str) -> Path` - Get a subdirectory within one of the standard directories
- `ensure_file(self, parent: str, filename: str, default_content: str) -> Path` - Ensure a file exists with default content if it doesn't
- `app_info(self) -> dict[str, str]` - Get application information
- `clear_cache(self) -> int` - Clear all files in the cache directory

### Functions

#### `def path_exists_filter(paths_instance: Paths) -> Flow[Path, Path]`
Create a Flow that filters paths to only existing ones.

    Returns:
        A Flow that filters out non-existent paths

    Example:
        paths = Flow.from_iterable([Path("file1.txt"), Path("file2.txt"), Path("missing.txt")])
        existing = paths >> path_exists_filter()

#### `def resolve_config_path(relative_path: str) -> Flow[AnyInput, Path]`
Create a Flow that resolves a relative path within the config directory.

    Args:
        relative_path: Relative path within the config directory

    Returns:
        A Flow that returns the resolved config path

    Example:
        flow = Flow.from_iterable([None])
        config_file = flow >> resolve_config_path("settings.json")

#### `def resolve_data_path(relative_path: str) -> Flow[AnyInput, Path]`
Create a Flow that resolves a relative path within the data directory.

    Args:
        relative_path: Relative path within the data directory

    Returns:
        A Flow that returns the resolved data path

    Example:
        flow = Flow.from_iterable([None])
        cache_file = flow >> resolve_data_path("cache.db")

#### `def list_directory_flow(pattern: str, paths_instance: Paths) -> Flow[Path, Path]`
Create a Flow that lists files in a directory.

    Args:
        pattern: Glob pattern to match files
        paths_instance: Paths instance (injected)

    Returns:
        A Flow that expands directories to their contents

    Example:
        dirs = Flow.from_iterable([paths.config(), paths.data()])
        all_files = dirs >> list_directory_flow("*.json")

#### `def ensure_parent_dir(paths_instance: Paths) -> Flow[Path, Path]`
Create a Flow that ensures parent directories exist.

    Returns:
        A Flow that creates parent directories if needed

    Example:
        file_paths = Flow.from_iterable([config_dir / "nested/dir/file.txt"])
        prepared = file_paths >> ensure_parent_dir()

#### `def read_config_file(filename: str, default_content: str) -> Flow[AnyInput, str]`
Create a Flow that reads a config file.

    Args:
        filename: Name of the config file
        default_content: Content to return if file doesn't exist

    Returns:
        A Flow that reads the file content

    Example:
        flow = Flow.from_iterable([None])
        settings = flow >> read_config_file("settings.json", default_content="{}")

#### `def write_config_file(filename: str) -> Flow[str, Path]`
Create a Flow that writes content to a config file.

    Args:
        filename: Name of the config file

    Returns:
        A Flow that writes content and returns the path

    Example:
        content = Flow.from_iterable(['{"setting": "value"}'])
        saved = content >> write_config_file("settings.json")

### Constants

#### `T`

#### `APP_AUTHOR`
Value: `'ndouglas'`

#### `APP_NAME`
Value: `'goldentooth-agent'`

## Dependencies

### External Dependencies
- `__future__`
- `antidote`
- `collections`
- `flow_integration`
- `goldentooth_agent`
- `logging`
- `main`
- `pathlib`
- `platformdirs`
- `typing`

## Exports

This module exports the following symbols:

- `Paths`
- `ensure_parent_dir`
- `list_directory_flow`
- `path_exists_filter`
- `read_config_file`
- `resolve_config_path`
- `resolve_data_path`
- `write_config_file`

## Quality Metrics

- **Test Coverage**: Medium
- **Coverage Target**: 90%+
- **Performance**: All tests <200ms
