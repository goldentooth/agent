from antidote import inject
from atomic_agents.agents.base_agent import BaseAgent, BaseAgentConfig, AgentMemory
from atomic_agents.lib.base.base_io_schema import BaseIOSchema
from atomic_agents.lib.base.base_tool import BaseTool
from goldentooth_agent.core.logging import get_logger
from logging import Logger
from pydantic import BaseModel
from typing import Optional, AsyncGenerator
from .no_op_instructor import NoOpInstructor

class ToolAgent(BaseAgent):
  """Agent that wraps a tool and provides a simple interface for interaction."""

  @inject
  def __init__(self, tool: BaseTool, logger: Logger = inject[get_logger(__name__)]):
    """Initialize the ToolAgent with a given tool."""
    logger.debug(f"Initializing ToolAgent with tool: {tool.tool_name}")
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

  @inject
  def get_response(self, response_model=None, logger: Logger = inject[get_logger(__name__)]) -> type[BaseModel]:
    """Get the response from the tool agent."""
    logger.debug(f"Getting response from ToolAgent with tool: {self.tool.tool_name}")
    return self.tool.run(self.current_user_input)  # type: ignore

  @inject
  def run(self, user_input: Optional[BaseIOSchema] = None, logger: Logger = inject[get_logger(__name__)]) -> BaseIOSchema:
    """Run the tool agent with the provided user input."""
    logger.debug(f"Running ToolAgent with tool: {self.tool.tool_name} and user input: {user_input}")
    if user_input:
      self.memory.initialize_turn()
      self.current_user_input = user_input
      self.memory.add_message("user", user_input)
    if not isinstance(user_input, self.input_schema):
      raise TypeError(f"Expected input of type {self.input_schema}, got {type(user_input)}")
    return self.tool.run(user_input) # type: ignore[call-arg]

  @inject
  async def run_async(
    self,
    user_input: Optional[BaseIOSchema] = None,
    logger: Logger = inject[get_logger(__name__)],
  ) -> AsyncGenerator[BaseIOSchema, None]:
    """Run the tool agent asynchronously with the provided user input."""
    logger.debug(f"Running ToolAgent asynchronously with tool: {self.tool.tool_name} and user input: {user_input}")
    if user_input:
      self.memory.initialize_turn()
      self.current_user_input = user_input
      self.memory.add_message("user", user_input)
    response = self.tool.run(user_input)  # type: ignore[call-arg]
    yield response
    self.memory.add_message("assistant", response)

if __name__ == "__main__":
  from antidote import world
  from atomic_agents.agents.base_agent import BaseAgentInputSchema
  from goldentooth_agent.core.tool import EchoTool, ReverseTool
  from rich.console import Console

  tool = world[EchoTool]
  agent = ToolAgent(tool)
  response = agent.run(BaseAgentInputSchema(chat_message="Hello, world!"))
  Console().print(response)

  tool = world[ReverseTool]
  agent = ToolAgent(tool)
  response = agent.run(BaseAgentInputSchema(chat_message="Hello, world!"))
  Console().print(response)
