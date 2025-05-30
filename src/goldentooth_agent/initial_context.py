from datetime import datetime
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator

class InitialContext:
  """Initial context class for initializing and managing the Goldentooth agent."""

  current_date: datetime

  def __init__(self, *, current_date: datetime | None = None) -> None:
    """Initialize the context."""
    self.current_date = current_date or datetime.now()

  def get_greeting(self) -> str:
    """Get a greeting based on the current date."""
    if self.current_date.hour < 12:
      return "Good morning! How can I assist you today?"
    elif self.current_date.hour < 18:
      return "Good afternoon! How can I assist you today?"
    else:
      return "Good evening! How can I assist you today?"

  def get_system_prompt_generator(self) -> SystemPromptGenerator:
    """Get the system prompt generator for the Goldentooth agent."""
    return SystemPromptGenerator(
      background=[
        "You are Goldentooth, a chat agent designed to assist users with various tasks and provide information.",
      ],
      output_instructions=[
        "Respond to user queries in a helpful and informative manner.",
        "Maintain a friendly and engaging tone throughout the conversation.",
        "If you don't know the answer, acknowledge it and suggest alternative ways to find the information.",
      ],
    )
