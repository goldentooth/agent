import importlib
import inspect
import pkgutil
from . import context_providers
from atomic_agents.lib.components.system_prompt_generator import SystemPromptContextProviderBase
from typing import List

class ContextProviderDiscovery:
  """Discovery class for context providers in the 'context_providers' package."""

  context_providers: List[SystemPromptContextProviderBase]

  def __init__(self):
    """Initialize the registry with an empty list of context providers."""
    self.context_providers = []

  def register(self, provider: SystemPromptContextProviderBase) -> None:
    """Register a new context provider."""
    if not isinstance(provider, SystemPromptContextProviderBase):
      raise TypeError("Provider must be an instance of SystemPromptContextProviderBase")
    self.context_providers.append(provider)

  def load_all(self) -> None:
    """Dynamically load all subclasses of SystemPromptContextProviderBase in the 'context_providers' package."""
    package_name = context_providers.__name__
    package_path = context_providers.__path__
    for _, name, _ in pkgutil.iter_modules(package_path):
      full_name = f"{package_name}.{name}"
      self.load_module(full_name)

  def load_module(self, full_name: str) -> None:
    """Load a module and register all SystemPromptContextProviderBase subclasses found in it."""
    try:
      module = importlib.import_module(full_name)
      for _, obj in inspect.getmembers(module, inspect.isclass):
        if issubclass(obj, SystemPromptContextProviderBase) and obj is not SystemPromptContextProviderBase:
          self.register(obj(obj.__name__))
    except ImportError as error:
      print(f"Error loading context provider module {full_name}: {error}")
