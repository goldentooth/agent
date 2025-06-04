from typing import TYPE_CHECKING
from rich.console import Console
from rich.text import Text
from atomic_agents.agents.base_agent import BaseAgent, BaseIOSchema
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator
from ..initial_context import InitialContext

class ChatSession:
  def __init__(self,
    agent: BaseAgent,
    initial_context: InitialContext,
  ) -> None:
    self.agent = agent
    self.console = Console()
    self.initial_context = initial_context

  async def start(self) -> None:
    """Start a chat session with the agent."""
    self.console.print()
    self.greet_user()

  def greet_user(self) -> None:
    """Display a greeting message to the user."""
    from .visitors.greeter import GreeterVisitor
    GreeterVisitor().visit(self)

#  async def run(self) -> None:
#    from .visitors.greeter import GreeterVisitor
#    GreeterVisitor().visit(self)
#
#    while True:
#      user_input = self.console.input("\n[bold blue]You:[/bold blue] ")
#      if user_input.strip().lower() in ["/exit", "/quit"]:
#        break
#
#      schema = ChatSessionIOSchema.model_validate({
#        "chat_message": user_input,
#        "tool_name": None,
#        "tool_parameters": None,
#        "tool_output": None,
#        "ttl": 3,
#      })
#      await self.conversation_loop(schema)
#
#  async def conversation_loop(self, schema: BaseIOSchema):
#    while schema.ttl > 0:
#      schema.ttl -= 1
#      self.agent.input_schema = ChatSessionIOSchema
#      self.agent.output_schema = ChatSessionIOSchema
#      schema = await self.agent.run(schema)
#
#      if schema.tool_name and schema.tool_parameters:
#        ToolExecutionVisitor().visit(self, schema)
#      elif schema.tool_output:
#        ToolResponseSynthesisVisitor().visit(self, schema)
#      else:
#        FinalResponseVisitor().visit(self, schema)
#        break
#
#  def format_agent_text(self, text: str) -> Text:
#    """Format the agent's text with a specific style."""
#    return Text.assemble(("Goldentooth: ", "bold yellow"), text)
#