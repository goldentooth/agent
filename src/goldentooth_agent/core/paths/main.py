import logging
from pathlib import Path

from antidote import inject, injectable
from platformdirs import PlatformDirs

APP_AUTHOR = "ndouglas"
APP_NAME = "goldentooth-agent"

logger = logging.getLogger(__name__)


@injectable
class Paths:
    """A class to manage user-specific paths for configuration and data storage."""

    def __init__(self, appname: str = APP_NAME, appauthor: str = APP_AUTHOR) -> None:
        """Initialize the Paths with application name and author.

        Args:
            appname: Name of the application
            appauthor: Author/organization name
        """
        self.dirs = PlatformDirs(appname, appauthor)
        self._appname = appname
        self._appauthor = appauthor

    @inject.method
    def config(self) -> Path:
        """Get the user configuration directory, creating it if it doesn't exist.

        Returns:
            Path to the configuration directory
        """
        path = Path(self.dirs.user_config_dir)
        path.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Config directory: {path}")
        return path

    @inject.method
    def data(self) -> Path:
        """Get the user data directory, creating it if it doesn't exist.

        Returns:
            Path to the data directory
        """
        path = Path(self.dirs.user_data_dir)
        path.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Data directory: {path}")
        return path

    @inject.method
    def cache(self) -> Path:
        """Get the user cache directory, creating it if it doesn't exist.

        Returns:
            Path to the cache directory
        """
        path = Path(self.dirs.user_cache_dir)
        path.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Cache directory: {path}")
        return path

    @inject.method
    def logs(self) -> Path:
        """Get the user logs directory, creating it if it doesn't exist.

        Returns:
            Path to the logs directory
        """
        path = Path(self.dirs.user_log_dir)
        path.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Logs directory: {path}")
        return path

    @inject.method
    def runtime(self) -> Path:
        """Get the user runtime directory, creating it if it doesn't exist.

        Returns:
            Path to the runtime directory
        """
        path = Path(self.dirs.user_runtime_dir)
        path.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Runtime directory: {path}")
        return path

    @inject.method
    def get_subdir(self, parent: str, subdir: str) -> Path:
        """Get a subdirectory within one of the standard directories.

        Args:
            parent: Parent directory type ('config', 'data', 'cache', 'logs', 'runtime')
            subdir: Name of the subdirectory

        Returns:
            Path to the subdirectory

        Raises:
            ValueError: If parent is not a valid directory type
        """
        parent_map = {
            "config": self.config,
            "data": self.data,
            "cache": self.cache,
            "logs": self.logs,
            "runtime": self.runtime,
        }

        if parent not in parent_map:
            raise ValueError(f"Invalid parent directory type: {parent}")

        parent_path = parent_map[parent]()
        subdir_path = parent_path / subdir
        subdir_path.mkdir(parents=True, exist_ok=True)
        return subdir_path

    @inject.method
    def ensure_file(
        self, parent: str, filename: str, default_content: str = ""
    ) -> Path:
        """Ensure a file exists with default content if it doesn't.

        Args:
            parent: Parent directory type
            filename: Name of the file
            default_content: Content to write if file doesn't exist

        Returns:
            Path to the file
        """
        parent_path = self.get_subdir(parent, "")
        file_path = parent_path / filename

        if not file_path.exists():
            file_path.write_text(default_content)
            logger.info(f"Created file with default content: {file_path}")

        return file_path

    @property
    def app_info(self) -> dict[str, str]:
        """Get application information.

        Returns:
            Dictionary with app name and author
        """
        return {
            "name": self._appname,
            "author": self._appauthor,
        }

    def clear_cache(self) -> int:
        """Clear all files in the cache directory.

        Returns:
            Number of files removed
        """
        cache_dir = self.cache()
        count = 0

        for file in cache_dir.iterdir():
            if file.is_file():
                file.unlink()
                count += 1
            elif file.is_dir():
                import shutil

                shutil.rmtree(file)
                count += 1

        logger.info(f"Cleared {count} items from cache")
        return count
