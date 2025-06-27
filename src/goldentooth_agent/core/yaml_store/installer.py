from typing import Generic, TypeVar

from .adapter import YamlStoreAdapter
from .base import YamlStore

T = TypeVar("T")  # Type being serialized/deserialized


class YamlStoreInstaller(Generic[T]):
    """A generic base class for installing YAML files from an embedded directory into a YAML store."""

    def __init__(
        self,
        source: YamlStore[T],
        destination: YamlStore[T],
        adapter: type[YamlStoreAdapter[T]],
    ):
        """Initialize the installer with a source store, a destination store, and an adapter."""
        self.source = source
        self.destination = destination
        self.adapter = adapter

    def install(self, overwrite: bool = False) -> bool:
        """Install all YAML files from the embedded directory into the store."""
        changed = False
        for id in self.source.list():
            if overwrite or not self.destination.exists(id):
                self.destination.save(id, self.source.load(id))
                changed = True
        return changed
