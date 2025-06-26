from __future__ import annotations
from antidote import inject, injectable
from atomic_agents.lib.components.system_prompt_generator import (
    SystemPromptContextProviderBase,
)
from goldentooth_agent.core.logging import get_logger
from goldentooth_agent.core.path import UserPaths
from goldentooth_agent.core.yaml_store import (
    YamlStoreAdapter,
    YamlStore,
    YamlStoreInstaller,
)
from goldentooth_agent.data import context_providers as context_providers_source

from pathlib import Path
from rich.syntax import Syntax
from rich.table import Table
from .registry import ContextProviderRegistry
from .simple import SimpleContextProvider


class YamlContextProviderAdapter(YamlStoreAdapter[SystemPromptContextProviderBase]):
    """Adapter for SystemPromptContextProviderBase to handle YAML serialization and deserialization."""

    @classmethod
    def from_dict(cls, data: dict) -> SystemPromptContextProviderBase:
        """Create a SystemPromptContextProviderBase instance from a dictionary."""
        return SimpleContextProvider(
            title=data["title"],
            info=data.get("info", []),
        )

    @classmethod
    def to_dict(cls, id: str, obj: SystemPromptContextProviderBase) -> dict:
        """Convert a SimpleContextProvider instance to a dictionary."""
        return {
            "id": id,
            "title": obj.title,
            "info": obj.get_info().splitlines(),
        }


@injectable(factory_method="create")
class YamlContextProviderStore(YamlStore[SystemPromptContextProviderBase]):
    """A store for context providers that uses YAML files for serialization."""

    def __init__(self, path: Path):
        """Initialize the YAML store with a given path."""
        super().__init__(path, YamlContextProviderAdapter)

    @classmethod
    def create(cls, paths: UserPaths = inject.me()) -> YamlContextProviderStore:
        """Create a new instance of the YAML context provider store."""
        directory = paths.data() / "context_providers"
        store = cls(directory)
        store.discover()
        return store

    @inject.method
    def discover(
        self,
        registry: ContextProviderRegistry = inject.me(),
        logger=inject[get_logger(__name__)],
    ) -> None:
        """Discover all YAML files in the store directory and load them."""
        logger.debug(f"Discovering context providers in {self.directory}")
        for name in self.list():
            logger.debug(f"Loading context provider '{name}'")
            cp = self.load(name)
            registry.set(name, cp)

    @inject.method
    def dump(self, logger=inject[get_logger(__name__)]) -> Table:
        """Dump all context providers in the store to a table."""
        logger.debug("Dumping all context providers to table")
        table = Table(title="Store Context Providers")
        table.add_column("Name", justify="left", style="cyan")
        table.add_column("Contents", justify="left", style="magenta")
        for name in self.list():
            contents = Syntax.from_path(str(self.directory / f"{name}.yaml"))
            table.add_row(name, contents)
        return table


@inject
def discover_yaml_context_providers(
    store: YamlContextProviderStore = inject.me(),
    logger=inject[get_logger(__name__)],
) -> None:
    """Install YAML context providers from the embedded directory to the user data directory."""
    logger.debug("Discovering YAML context providers...")
    store.discover()


discover_yaml_context_providers()


@injectable
class YamlContextProviderInstaller(YamlStoreInstaller[SystemPromptContextProviderBase]):
    """Installer for context providers that copies embedded YAML files to the user data directory."""

    def __init__(self, destination: YamlContextProviderStore = inject.me()):
        """Initialize the installer with the store."""
        source = YamlContextProviderStore(Path(context_providers_source.__path__[0]))
        super().__init__(source, destination, YamlContextProviderAdapter)


@inject
def install_yaml_context_providers(
    store: YamlContextProviderStore = inject.me(),
    installer: YamlContextProviderInstaller = inject.me(),
    logger=inject[get_logger(__name__)],
) -> None:
    """Install YAML context providers from the embedded directory to the user data directory."""
    logger.debug("Installing YAML context providers...")
    if installer.install(True):
        store.discover()
    logger.debug("YAML context providers installed successfully.")


install_yaml_context_providers()
