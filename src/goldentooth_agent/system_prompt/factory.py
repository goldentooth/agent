from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator
from ..tool.registry import ToolRegistry
from ..initial_context import InitialContext

class SystemPromptFactory:
  """Class for managing the system prompt generator."""

  @classmethod
  def get(cls, initial_context: InitialContext) -> SystemPromptGenerator:
    """Get the system prompt generator for the Goldentooth agent."""
    background = [
      "You are Goldentooth, a chat agent designed to assist users with various tasks and provide information.",
    ]
    output_instructions = [
      "Respond to user queries in a helpful and informative manner.",
      "Maintain a friendly and engaging tone throughout the conversation.",
      "If you don't know the answer, acknowledge it and suggest alternative ways to find the information.",
      "Use tools as needed to assist with user requests.",
    ]
    output_instructions.extend(ToolRegistry.instructions())
    return SystemPromptGenerator(
      background=background,
      output_instructions=output_instructions,
    )
