import instructor
import anthropic
from rich.console import Console
from rich.text import Text
from rich.live import Live
from atomic_agents.lib.components.agent_memory import AgentMemory
from atomic_agents.agents.base_agent import BaseAgent, BaseAgentConfig, BaseAgentInputSchema, BaseAgentOutputSchema
from .prompt import PromptGenerator

class GoldentoothAgent:
  """A simple chat agent using the Atomic Agents framework."""
  def __init__(self):
    self.console = Console()
    self.memory = AgentMemory()
    self.model = "claude-sonnet-4-20250514"

    initial_chat_message = "Hello! How can I assist you today?"
    initial_message = BaseAgentOutputSchema(chat_message=initial_chat_message)
    self.memory.add_message("assistant", initial_message)
    self.initial_message = initial_message
    self.prompt_generator = PromptGenerator()
    self.prompt_generator.prepare()

    client = instructor.from_anthropic(anthropic.AsyncClient())
    self.agent = BaseAgent(
      config=BaseAgentConfig(
        client=client,
        memory=self.memory,
        model=self.model,
        system_prompt_generator=self.prompt_generator.generate(),
        model_api_parameters={
          "max_tokens": 2048,
        },
      )
    )

  def display_initial_message(self):
    self.console.print(Text("Agent:", style="bold green"), end=" ")
    self.console.print(Text(self.initial_message.chat_message, style="green"))

  def prompt_user(self) -> str:
    """Prompt the user for input with a styled prompt."""
    user_input = self.console.input("\n[bold blue]You:[/bold blue] ")
    if user_input.lower() in ["/exit", "/quit"]:
      raise SystemExit("Exiting chat...")
    self.console.print()
    return user_input

  async def chat(self) -> None:
    """Start a chat session with the agent."""
    self.display_initial_message()

    while True:
      user_input = self.prompt_user()
      input_schema = BaseAgentInputSchema(chat_message=user_input)

      with Live("", refresh_per_second=10, auto_refresh=True) as live:
        current_response = ""
        async for partial_response in self.agent.run_async(input_schema):
          if hasattr(partial_response, "chat_message") and partial_response.chat_message:
            if partial_response.chat_message != current_response:
              current_response = partial_response.chat_message
              display_text = Text.assemble(("Agent: ", "bold yellow"), (current_response, "yellow"))
              live.update(display_text)
