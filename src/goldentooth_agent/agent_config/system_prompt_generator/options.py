from antidote import const, implements, inject, injectable, interface
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator
import json

DEFAULT_BACKGROUND = [
  "You are an intelligent agent named Goldentooth, designed by Nathan Douglas ('Nug Doug').",
  "You are embedded in a Pi Bramble or cluster, also named Goldentooth.",
  "You should infer from context whether a mention of 'Goldentooth' refers to yourself or the Pi Bramble.",
]

DEFAULT_STEPS = [
  "Understand the user's input and provide a relevant response.",
#  "Use tools as needed to assist with user requests.",
  "Respond to the user.",
]

DEFAULT_OUTPUT_INSTRUCTIONS = [
  "If you don't know the answer, acknowledge it and suggest alternative ways to find the information.",
]

@injectable
class SystemPromptGeneratorOptions:
  """Options for the client configuration."""
  background: list[str] = DEFAULT_BACKGROUND
  steps: list[str] = DEFAULT_STEPS
  output_instructions: list[str] = DEFAULT_OUTPUT_INSTRUCTIONS

@interface.lazy
def get_system_prompt_generator(
) -> SystemPromptGenerator:
  """Get the system prompt generator."""
  raise NotImplementedError(
    "The 'get_system_prompt_generator' function must be implemented by the client provider."
  )

@implements.lazy(get_system_prompt_generator)
def get_env_system_prompt_generator(
  options: SystemPromptGeneratorOptions = inject[SystemPromptGeneratorOptions]
) -> SystemPromptGenerator:
  """Get the system prompt generator from environment variables."""
  return SystemPromptGenerator(
    background=options.background,
    steps=options.steps,
    output_instructions=options.output_instructions,
  )

