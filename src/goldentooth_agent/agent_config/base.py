from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator
from instructor import AsyncInstructor, Instructor
from atomic_agents.agents.base_agent import BaseAgentConfig
from antidote import interface
from pydantic import Field

@interface
class AgentConfigBase(BaseAgentConfig):
  """Abstract base class for all agent configs."""
