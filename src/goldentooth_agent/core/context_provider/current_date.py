from __future__ import annotations
from antidote import injectable
from atomic_agents.lib.components.system_prompt_generator import SystemPromptContextProviderBase
from datetime import datetime
from .registry import register_context_provider

@injectable(factory_method='create')
@register_context_provider(name="current_date")
class CurrentDate(SystemPromptContextProviderBase):
  """Context provider that provides information about the current date."""

  def get_info(self) -> str:
    """Get info about the current date context provider."""
    date_string = datetime.now().strftime("%Y-%m-%d")
    return "\n".join([
      f"The current date in YYYY-MM-DD format is {date_string}.",
    ])

  @classmethod
  def create(cls) -> CurrentDate:
    """Create a new CurrentDate instance."""
    return cls("Current Date")
