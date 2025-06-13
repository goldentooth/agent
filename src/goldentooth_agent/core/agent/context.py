from dataclasses import dataclass
from goldentooth_agent.core.agent import AgentBase
from goldentooth_agent.core.tool import ToolRegistry
from typing import Optional

@dataclass
class AgentContext:
  """The fold accumulator: all state needed for the next agent step."""
  agent: AgentBase
  tool_registry: ToolRegistry
  user_input: Optional[str] = None
  agent_output: Optional[str] = None
