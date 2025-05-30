import instructor
import anthropic
from rich.console import Console
from rich.text import Text
from rich.live import Live
from atomic_agents.lib.components.agent_memory import AgentMemory
from atomic_agents.agents.base_agent import BaseAgent, BaseAgentConfig, BaseAgentInputSchema, BaseAgentOutputSchema
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator
from .context_provider_discovery import ContextProviderDiscovery

class GoldentoothAgent:
  """A simple chat agent."""
  def __init__(self):
    self.console = Console()
    self.memory = AgentMemory()
    self.model = "claude-sonnet-4-20250514"

    initial_chat_message = "Hello! I am Goldentooth, your chat agent. How can I assist you today?"
    self.initial_message = BaseAgentOutputSchema(chat_message=initial_chat_message)
    self.memory.add_message("assistant", self.initial_message)

    system_prompt_generator = SystemPromptGenerator(
      background=[
        "You are Goldentooth, a chat agent designed to assist users with various tasks and provide information.",
      ],
      output_instructions=[
        "Respond to user queries in a helpful and informative manner.",
        "Maintain a friendly and engaging tone throughout the conversation.",
        "If you don't know the answer, acknowledge it and suggest alternative ways to find the information.",
      ],
    )

    client = instructor.from_anthropic(anthropic.AsyncClient())
    self.agent = BaseAgent(
      config=BaseAgentConfig(
        client=client,
        memory=self.memory,
        model=self.model,
        system_prompt_generator=system_prompt_generator,
        model_api_parameters={
          "max_tokens": 2048,
        },
      )
    )

    self.context_provider_discovery = ContextProviderDiscovery()
    self.context_provider_discovery.load_all()
    for provider in self.context_provider_discovery.context_providers:
      self.agent.register_context_provider(provider.title, provider)

  def display_initial_message(self):
    """Display the initial message in a styled format."""
    display_text = Text.assemble(("Goldentooth: ", "bold yellow"), (self.initial_message.chat_message, "yellow"))
    self.console.print(display_text)

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
              display_text = Text.assemble(("Goldentooth: ", "bold yellow"), (current_response, "yellow"))
              live.update(display_text)
