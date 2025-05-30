from atomic_agents.lib.components.system_prompt_generator import SystemPromptContextProviderBase
from datetime import datetime

class CurrentDate(SystemPromptContextProviderBase):
  def __init__(self, title: str = "") -> None:
    super().__init__(title=title or "Current Date")

  def get_info(self) -> str:
    current_date = datetime.now().strftime("%Y-%m-%d")
    return f"The current date is: {current_date}"
