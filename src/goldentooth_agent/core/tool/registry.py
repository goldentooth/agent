from antidote import injectable
from atomic_agents.lib.base.base_io_schema import BaseIOSchema
from atomic_agents.lib.base.base_tool import BaseTool
from goldentooth_agent.core.named_registry import NamedRegistry, make_register_fn
from goldentooth_agent.core.thunk import Thunk
from rich.table import Table

@injectable()
class ToolRegistry(NamedRegistry[BaseTool]):
  """Registry for managing tools."""

  def get_thunk(self, tool_name: str) -> Thunk[BaseIOSchema, BaseIOSchema]:
    from .thunk import thunkify_tool
    tool = self.get(tool_name)
    return thunkify_tool(tool)

  def get_by_input_schema(self, schema: type[BaseIOSchema]) -> BaseTool:
    for tool in self.all():
      if issubclass(schema, tool.input_schema):
        return tool
    raise LookupError(f"No tool found for input schema: {schema}")

  def dump(self) -> Table:
    """Dump the context to the console."""
    table = Table(title=f"Tool Registry")
    table.add_column("Name")
    table.add_column("Info", overflow="fold")
    for k, v in self.items():
      table.add_row(str(k), v.get_info() if hasattr(v, 'get_info') else repr(v)) # type: ignore[no-any-return]
    return table

register_tool = make_register_fn(ToolRegistry, default_id_fn=lambda tool: tool.tool_name)
