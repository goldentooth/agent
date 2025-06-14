from antidote import inject
from atomic_agents.lib.base.base_io_schema import BaseIOSchema
from rich.console import Console, ConsoleOptions, RenderResult
from rich.syntax import Syntax
from rich.panel import Panel
import yaml
from ..console import get_console, get_error_console

class SchemaBase(BaseIOSchema):
  """Base schema for all schemas in the Goldentooth Agent."""

  @inject
  def print(self, console: Console = inject[get_console()]) -> None:
    """Print the schema in a pretty format using rich."""
    console.print(self)

  @inject
  def debug(self, console: Console = inject[get_error_console()]) -> None:
    """Print the schema in a debug format."""
    console.print(self)

  def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
    """Render the schema as a rich console object."""
    yaml_output = yaml.safe_dump(self.model_dump(), sort_keys=False, allow_unicode=True)
    syntax = Syntax(yaml_output, "yaml", theme="monokai", line_numbers=False)
    panel = Panel(syntax, title=self.__class__.__name__)
    yield panel

  @classmethod
  def all_subclasses(cls):
    """Get all subclasses of this class, recursively."""
    return set(cls.__subclasses__()).union(
      s for c in cls.__subclasses__() for s in c.all_subclasses()
    )
