from antidote import inject
from atomic_agents.lib.base.base_io_schema import BaseIOSchema
from atomic_agents.lib.base.base_tool import BaseTool
from goldentooth_agent.core.thunk import Thunk

def run_tool_th(tool: BaseTool) -> Thunk[BaseIOSchema, BaseIOSchema]:
  """Generator for thunk to print a message to the console."""
  @inject
  async def _thunk(input: BaseIOSchema) -> BaseIOSchema:
    """Thunk to run a tool and return the appropriate result."""
    if not isinstance(input, tool.input_schema):
      raise TypeError(f"Input must be of type {tool.input_schema.__name__}, got {type(input).__name__}")
    result = tool.run(type(input))
    if not isinstance(result, tool.output_schema):
      raise TypeError(f"Output must be of type {tool.output_schema.__name__}, got {type(result).__name__}")
    return result
  return Thunk(_thunk)
