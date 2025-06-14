from atomic_agents.agents.base_agent import BaseAgent
from dataclasses import dataclass

@dataclass
class ChatContext:
  """The fold accumulator: all state needed for the next agent step."""

  agent: BaseAgent
  """The agent that is being used."""
  is_straight: bool = False
  """Whether to use straightness (don't mess around) or not."""
  should_quit: bool = False
  """Whether the agent should quit."""
