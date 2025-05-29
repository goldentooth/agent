from typing import List
from .modifier_context import PromptModifierContext
from .modifier_registry import PromptModifierRegistry
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator

class PromptGenerator:
  """Generates prompts for the Goldentooth agent."""

  modifier_registry: PromptModifierRegistry

  def __init__(self,
    modifier_registry: PromptModifierRegistry = PromptModifierRegistry(),
    modifier_context: PromptModifierContext = PromptModifierContext(),
  ) -> None:
    self.modifier_registry = modifier_registry
    self.modifier_context = modifier_context

  def prepare(self) -> None:
    """Prepare the prompt generator by loading all modifiers."""
    self.modifier_registry.load_all()

  def generate_background(self) -> List[str]:
    """Generate the background context based on the context."""
    return self.modifier_registry.generate_background(self.modifier_context)

  def generate_steps(self) -> List[str]:
    """Generate the steps based on the context."""
    return self.modifier_registry.generate_steps(self.modifier_context)

  def generate_output_instructions(self) -> List[str]:
    """Generate the output instructions based on the context."""
    return self.modifier_registry.generate_output_instructions(self.modifier_context)

  def generate(self) -> SystemPromptGenerator:
    """Generate the system prompt based on the current context."""
    background = self.modifier_registry.generate_background(self.modifier_context)
    steps = self.modifier_registry.generate_steps(self.modifier_context)
    output_instructions = self.modifier_registry.generate_output_instructions(self.modifier_context)
    return SystemPromptGenerator(
      background=background,
      steps=steps,
      output_instructions=output_instructions,
    )
