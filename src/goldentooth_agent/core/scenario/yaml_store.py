from __future__ import annotations
from antidote import inject, injectable
from goldentooth_agent.core.logging import get_logger
from goldentooth_agent.core.path import UserPaths
from goldentooth_agent.core.yaml_store import (
    YamlStore,
    YamlStoreAdapter,
    YamlStoreInstaller,
)
from goldentooth_agent.data import scenarios as scenarios_source

from pathlib import Path
from rich.syntax import Syntax
from rich.table import Table
from .base import Scenario
from .registry import ScenarioRegistry


class YamlScenarioAdapter(YamlStoreAdapter[Scenario]):
    """Adapter for Scenario to handle YAML serialization and deserialization."""

    @classmethod
    def from_dict(cls, data: dict) -> Scenario:
        """Create a Scenario instance from a dictionary."""
        return Scenario(
            id=data["id"],
            name=data["name"],
            hidden=data["hidden"],
            info=data["info"],
            role_ids=data["roles"],
        )

    @classmethod
    def to_dict(cls, id: str, obj: Scenario) -> dict:
        """Convert a Scenario instance to a dictionary."""
        return {
            "id": id,
            "name": obj.name,
            "hidden": obj.hidden,
            "info": obj.info,
            "roles": obj.role_ids,
        }


@injectable(factory_method="create")
class YamlScenarioStore(YamlStore[Scenario]):
    """A store for scenarios that uses YAML files for serialization."""

    def __init__(self, path: Path):
        """Initialize the YAML store with a given path."""
        super().__init__(path, YamlScenarioAdapter)

    @classmethod
    def create(cls, paths: UserPaths = inject.me()) -> YamlScenarioStore:
        """Create a new instance of the YAML scenario store."""
        directory = paths.data() / "scenarios"
        store = cls(directory)
        store.discover()
        return store

    @inject.method
    def discover(
        self,
        registry: ScenarioRegistry = inject.me(),
        logger=inject[get_logger(__name__)],
    ) -> None:
        """Discover all YAML files in the store directory and load them."""
        logger.debug(f"Discovering scenarios in {self.directory}")
        for id in self.list():
            logger.debug(f"Loading scenario '{id}'")
            scenario = self.load(id)
            registry.set(id, scenario)

    @inject.method
    def dump(self, logger=inject[get_logger(__name__)]) -> Table:
        """Dump all scenarios in the store to a table."""
        logger.debug("Dumping all scenarios to table")
        table = Table(title="Store Scenarios")
        table.add_column("ID", justify="left", style="cyan")
        table.add_column("Contents", justify="left", style="magenta")
        for id in self.list():
            contents = Syntax.from_path(str(self.directory / f"{id}.yaml"))
            table.add_row(id, contents)
        return table


@inject
def discover_yaml_scenarios(
    store: YamlScenarioStore = inject.me(),
    logger=inject[get_logger(__name__)],
) -> None:
    """Install YAML scenarios from the embedded directory to the user data directory."""
    logger.debug("Discovering YAML scenarios...")
    store.discover()


discover_yaml_scenarios()


@injectable
class YamlScenarioInstaller(YamlStoreInstaller[Scenario]):
    """Installer for scenarios that copies embedded YAML files to the user data directory."""

    def __init__(self, destination: YamlScenarioStore = inject.me()) -> None:
        """Initialize the installer with the store."""
        source = YamlScenarioStore(Path(scenarios_source.__path__[0]))
        super().__init__(source, destination, YamlScenarioAdapter)


@inject
def install_yaml_scenarios(
    store: YamlScenarioStore = inject.me(),
    installer: YamlScenarioInstaller = inject.me(),
    logger=inject[get_logger(__name__)],
) -> None:
    """Install YAML scenarios from the embedded directory to the user data directory."""
    logger.debug("Installing YAML scenarios...")
    if installer.install(True):
        store.discover()
    logger.debug("YAML scenarios installed successfully.")


install_yaml_scenarios()
