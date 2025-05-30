import importlib
import inspect
import pkgutil
from . import context_providers
from .initial_context import InitialContext
from .context_providers.base import ContextProviderBase
from atomic_agents.agents.base_agent import BaseAgent
from typing import List

class ContextProviderDiscovery:
  """Discovery class for context providers in the 'context_providers' package."""

  def __init__(self):
    """Initialize the registry with an empty list of context providers."""

  def populate(self, agent: BaseAgent, initial_context: InitialContext) -> None:
    """Populate the agent with all discovered context providers."""
    for provider in self.load_all(initial_context):
      agent.register_context_provider(provider.title, provider)

  def load_all(self, initial_context: InitialContext) -> List[ContextProviderBase]:
    """Dynamically load all subclasses of ContextProviderBase in the 'context_providers' package."""
    result = []
    package_name = context_providers.__name__
    package_path = context_providers.__path__
    for _, name, _ in pkgutil.iter_modules(package_path):
      full_name = f"{package_name}.{name}"
      result.extend(self.load_module(full_name, initial_context))
    return result

  def load_module(self, full_name: str, initial_context: InitialContext) -> List[ContextProviderBase]:
    """Load a module and register all ContextProviderBase subclasses found in it."""
    result = []
    try:
      module = importlib.import_module(full_name)
      for _, obj in inspect.getmembers(module, inspect.isclass):
        if issubclass(obj, ContextProviderBase) and obj is not ContextProviderBase:
          result.append(obj(initial_context))
    except ImportError as error:
      print(f"Error loading context provider module {full_name}: {error}")
    return result
