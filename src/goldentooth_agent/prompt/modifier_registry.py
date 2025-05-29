import importlib
import inspect
import pkgutil
from typing import List
from .modifier import PromptModifier
from .modifier_context import PromptModifierContext
from . import modifiers

class PromptModifierRegistry:
  """Registry for prompt modifiers that can alter the prompt generation process."""

  def __init__(self):
    """Initialize the registry with an empty list of modifiers."""
    self.modifiers: List[PromptModifier] = []

  def register(self, modifier) -> None:
    """Register a new prompt modifier."""
    self.modifiers.append(modifier)

  def unregister(self, modifier) -> None:
    """Unregister an existing prompt modifier."""
    self.modifiers = [m for m in self.modifiers if m is not modifier]

  def get_modifiers(self) -> List[PromptModifier]:
    """Get the list of registered prompt modifiers."""
    return self.modifiers

  def generate_background(self, context: PromptModifierContext) -> List[str]:
    """Generate the background context based on the registered modifiers."""
    background = []
    for mod in sorted(self.modifiers, key=lambda m: m.priority):
      background += mod.modify_background(context)
    return background

  def generate_steps(self, context: PromptModifierContext) -> List[str]:
    """Generate the steps based on the registered modifiers."""
    steps = []
    for mod in sorted(self.modifiers, key=lambda m: m.priority):
      steps += mod.modify_steps(context)
    return steps

  def generate_output_instructions(self, context: PromptModifierContext) -> List[str]:
    """Generate the output instructions based on the registered modifiers."""
    output = []
    for mod in sorted(self.modifiers, key=lambda m: m.priority):
      output += mod.modify_output_instructions(context)
    return output

  def load_all(self) -> None:
    """Dynamically load all subclasses of PromptModifier in the 'modifiers' package."""
    package_name = modifiers.__name__
    package_path = modifiers.__path__
    for _, name, _ in pkgutil.iter_modules(package_path):
      full_module_name = f"{package_name}.{name}"
      print(f"Loading module: {full_module_name}")
      self.load_module(full_module_name)

  def load_module(self, full_module_name: str) -> None:
    try:
      module = importlib.import_module(full_module_name)
      for _, obj in inspect.getmembers(module, inspect.isclass):
        if issubclass(obj, PromptModifier) and obj is not PromptModifier:
          self.register(obj())
    except ImportError as error:
      print(f"Error loading module {full_module_name}: {error}")
