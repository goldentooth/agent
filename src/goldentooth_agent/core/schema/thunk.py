from antidote import inject
from atomic_agents.lib.base.base_io_schema import BaseIOSchema
from goldentooth_agent.core.thunk import Thunk, thunk
from goldentooth_agent.core.console import get_error_console
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel
import yaml

def debug_schema() -> Thunk[BaseIOSchema, BaseIOSchema]:
  """Debug the schema by printing it in a rich format."""
  @thunk
  @inject
  async def _debug(schema: BaseIOSchema, console: Console = inject[get_error_console()]) -> BaseIOSchema:
    """Print the schema in a debug format."""
    yaml_output = yaml.safe_dump(schema.model_dump(), sort_keys=True, allow_unicode=True)
    syntax = Syntax(yaml_output, "yaml", theme="monokai", line_numbers=False)
    panel = Panel(syntax, title=schema.__class__.__name__)
    console.print(panel)
    return schema
  return _debug
