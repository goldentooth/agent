from typing import List
from .modifier_context import PromptModifierContext

class PromptModifier:
  """
  Base class for prompt modifiers that can alter the prompt generation process.
  Subclasses should implement the methods to modify the background, steps, and output
  instructions based on the provided context.
  """

  priority: int = 100

  def __init__(self, priority: int = 100):
    """
    Initialize the prompt modifier with an optional priority.
    Lower priority modifiers are applied first.

    Args:
      priority (int): The priority of the modifier. Default is 0.
    """
    self.priority = priority

  def modify_background(self, context: PromptModifierContext) -> List[str]:
    """Modify the background context based on the context."""
    return []

  def modify_steps(self, context: PromptModifierContext) -> List[str]:
    """Modify the steps based on the context."""
    return []

  def modify_output_instructions(self, context: PromptModifierContext) -> List[str]:
    """Modify the output instructions based on the context."""
    return []
