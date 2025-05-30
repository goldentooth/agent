from rich.console import Console
from rich.text import Text
from rich.live import Live
from atomic_agents.agents.base_agent import BaseAgentInputSchema, BaseAgentOutputSchema
from .agent_factory import AgentFactory
from .initial_context import InitialContext

class ChatSession:
  """A simple chat agent."""
  def __init__(self, initial_context: InitialContext) -> None:
    self.console = Console()
    self.initial_context = initial_context
    self.agent = AgentFactory.create_agent(initial_context)

  def format_agent_text(self, text: str) -> Text:
    """Format the agent's text with a specific style."""
    return Text.assemble(("Goldentooth: ", "bold yellow"), (text, "yellow"))

  def greet_user(self) -> None:
    """Display a greeting message to the user."""
    self.console.print()
    greeting = self.initial_context.get_greeting()
    self.agent.memory.add_message("assistant", BaseAgentOutputSchema(chat_message=greeting))
    self.console.print(self.format_agent_text(greeting))

  def prompt_user(self) -> str:
    """Prompt the user for input with a styled prompt."""
    user_input = self.console.input("\n[bold blue]You:[/bold blue] ")
    if user_input.lower().strip() in ["/exit", "/quit"]:
      raise SystemExit("Exiting chat...")
    self.console.print()
    return user_input

  async def start(self) -> None:
    """Start a chat session with the agent."""
    self.greet_user()

    while True:
      user_input = BaseAgentInputSchema(chat_message=self.prompt_user())

      with Live("", refresh_per_second=10, auto_refresh=True) as live:
        current_response = ""
        async for partial_response in self.agent.run_async(user_input):
          if hasattr(partial_response, "chat_message") and partial_response.chat_message:
            if partial_response.chat_message != current_response:
              live.update(self.format_agent_text(partial_response.chat_message))
