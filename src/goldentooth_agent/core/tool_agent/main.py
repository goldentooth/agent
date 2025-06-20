from atomic_agents.agents.base_agent import BaseAgent, BaseAgentConfig, AgentMemory
from atomic_agents.lib.base.base_io_schema import BaseIOSchema
from atomic_agents.lib.base.base_tool import BaseTool
from pydantic import BaseModel
from typing import Optional, AsyncGenerator
from .no_op_instructor import NoOpInstructor

class ToolAgent(BaseAgent):
  """Agent that wraps a tool and provides a simple interface for interaction."""

  def __init__(self, tool: BaseTool):
    """Initialize the ToolAgent with a given tool."""
    agent_config = BaseAgentConfig(
      client=NoOpInstructor(),
      model=tool.tool_name,
      memory=AgentMemory(),
      system_prompt_generator=None,
      system_role="system",
      input_schema=tool.input_schema,
      output_schema=tool.output_schema,
      temperature=None,
      max_tokens=None,
      model_api_parameters=None,
    )
    super().__init__(agent_config)
    self.tool = tool

  def get_response(self, response_model=None) -> type[BaseModel]:
    """Get the response from the tool agent."""
    return self.tool.run(self.current_user_input)  # type: ignore

  def run(self, user_input: Optional[BaseIOSchema] = None) -> BaseIOSchema:
    """Run the tool agent with the provided user input."""
    if user_input:
      self.memory.initialize_turn()
      self.current_user_input = user_input
      self.memory.add_message("user", user_input)
    if not isinstance(user_input, self.input_schema):
      raise TypeError(f"Expected input of type {self.input_schema}, got {type(user_input)}")
    return self.tool.run(user_input) # type: ignore[call-arg]

  async def run_async(self, user_input: Optional[BaseIOSchema] = None) -> AsyncGenerator[BaseIOSchema, None]:
    """Run the tool agent asynchronously with the provided user input."""
    if user_input:
      self.memory.initialize_turn()
      self.current_user_input = user_input
      self.memory.add_message("user", user_input)
    response = self.tool.run(user_input)  # type: ignore[call-arg]
    yield response
    self.memory.add_message("assistant", response)

if __name__ == "__main__":
  from antidote import world
  from goldentooth_agent.core.tool import EchoTool, EchoInput, ReverseTool, ReverseInput
  from rich.console import Console

  tool = world[EchoTool]
  agent = ToolAgent(tool)
  response = agent.run(EchoInput(string="Hello, world!"))
  Console().print(response)

  tool = world[ReverseTool]
  agent = ToolAgent(tool)
  response = agent.run(ReverseInput(string="Hello, world!"))
  Console().print(response)
