from atomic_agents.agents.base_agent import BaseAgent
from antidote import interface, inject
from rich.console import Console
from rich.text import Text
from .config import AgentConfigBase
from ..console import get_console

@interface
class AgentBase(BaseAgent):
  """Abstract base class for all agents."""

  @inject
  def __init__(self, config: AgentConfigBase = inject.me()) -> None:
    """Initialize the agent with the provided configuration."""
    super().__init__(config=config)

  @inject
  def print(self, console: Console = inject[get_console()]) -> None:
    """Print the agent's name in a pretty format using rich."""
    console.print(Text("Agent:", style="bold yellow"), end=" ")
