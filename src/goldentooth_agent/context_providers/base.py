from atomic_agents.lib.components.system_prompt_generator import SystemPromptContextProviderBase
from typing import List
from ..initial_context import InitialContext

class ContextProviderBase(SystemPromptContextProviderBase):
  """Base class for context providers in the Goldentooth agent."""

  initial_context: InitialContext

  def __init__(self, initial_context: InitialContext) -> None:
    """Initialize the context provider with the initial context."""
    self.initial_context = initial_context
    super().__init__(title=self.__class__.__name__)

  def suggest_greetings(self) -> List[str]:
    """Suggest a greeting based on the initial context."""
    return []

  def get_instructions(self) -> List[str]:
    """Get instructions for the context provider."""
    return []

  def get_info(self) -> str:
    """Get information about the context provider."""
    return "\n".join(self.get_instructions())
