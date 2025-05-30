from .. import PromptModifier, PromptModifierContext
from datetime import datetime

cutoff_date = datetime(2025, 1, 1).strftime("%Y-%m-%d")
current_date = datetime.now().strftime("%Y-%m-%d")

class CurrentDate(PromptModifier):
  def __init__(self):
    super().__init__(0)

  def modify_background(self, context: PromptModifierContext) -> list[str]:
    return [
      f"The current date is: {current_date}",
      f"Goldentooth's reliable knowledge cutoff date - the date past which it cannot answer questions reliably - is {cutoff_date}.",
      f"Goldentooth answers all questions the way a highly informed individual in {cutoff_date} would if they were talking to someone from {current_date}, and can let the person it's talking to know this if relevant.",
      f"Goldentooth should use web search if asked to confirm or deny claims about things that happened after {cutoff_date}.",
    ]

  def modify_steps(self, context: PromptModifierContext) -> list[str]:
    return []

  def modify_output_instructions(self, context: PromptModifierContext) -> list[str]:
    return [
      "If asked or told about events or news that occurred after the cutoff date, use the web search tool to find more info.",
      "If asked about current news or events, such as the current status of elected officials, use the search tool without asking for permission.",
      "Do not remind the person of the cutoff date unless it is relevant to the person's message.",
    ]
