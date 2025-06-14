from antidote import injectable, inject
from platformdirs import PlatformDirs
from pathlib import Path

APP_AUTHOR = "ndouglas"
APP_NAME = "goldentooth-agent"

@injectable
class UserPaths:
  """A class to manage user-specific paths for configuration and data storage."""

  def __init__(self, appname=APP_NAME, appauthor=APP_AUTHOR) -> None:
    """Initialize the UserPaths with application name and author."""
    self.dirs = PlatformDirs(appname, appauthor)

  @inject.method
  def config(self) -> Path:
    """Get the user configuration directory, creating it if it doesn't exist."""
    path = Path(self.dirs.user_config_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path

  @inject.method
  def data(self) -> Path:
    """Get the user data directory, creating it if it doesn't exist."""
    path = Path(self.dirs.user_data_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path

if __name__ == "__main__":
  # Example usage
  user_paths = UserPaths()
  print("Config Path:", user_paths.config())
  print("Data Path:", user_paths.data())
