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

  def display_greeting(self, greeting: str) -> None:
    """Display the greeting in a styled format."""
    self.agent.memory.add_message("assistant", BaseAgentOutputSchema(chat_message=greeting))
    display_text = Text.assemble(("Goldentooth: ", "bold yellow"), (greeting, "yellow"))
    self.console.print(display_text)

  def prompt_user(self) -> str:
    """Prompt the user for input with a styled prompt."""
    user_input = self.console.input("\n[bold blue]You:[/bold blue] ")
    if user_input.lower().strip() in ["/exit", "/quit"]:
      raise SystemExit("Exiting chat...")
    self.console.print()
    return user_input

  async def start(self) -> None:
    """Start a chat session with the agent."""
    self.console.print()
    self.display_greeting(self.initial_context.get_greeting())

    while True:
      user_input = self.prompt_user()
      input_schema = BaseAgentInputSchema(chat_message=user_input)

      with Live("", refresh_per_second=10, auto_refresh=True) as live:
        current_response = ""
        async for partial_response in self.agent.run_async(input_schema):
          if hasattr(partial_response, "chat_message") and partial_response.chat_message:
            if partial_response.chat_message != current_response:
              current_response = partial_response.chat_message
              display_text = Text.assemble(("Goldentooth: ", "bold yellow"), (current_response, "yellow"))
              live.update(display_text)
