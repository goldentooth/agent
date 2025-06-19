from __future__ import annotations
from antidote import injectable, inject
from atomic_agents.lib.base.base_io_schema import BaseIOSchema
from atomic_agents.lib.base.base_tool import BaseToolConfig, BaseTool
from goldentooth_agent.core.context import Context
from goldentooth_agent.core.tool.registry import register_tool
from pydantic import Field
import shlex
from typer import Typer, Context as TyperContext
from .inject import get_command_typer

class CommandInput(BaseIOSchema):
  """Schema for the input to the Command tool."""
  input: str = Field(..., description="The command as provided by the user.")

class CommandOutput(BaseIOSchema):
  """Schema for the output from the Command tool."""

class CommandConfig(BaseToolConfig):
  """Configuration for the Command tool."""
  pass

@register_tool()
@injectable(factory_method='create')
class CommandTool(BaseTool):
  """Command tool that executes a command provided by the user."""
  input_schema = CommandInput
  output_schema = CommandOutput

  def __init__(
    self,
    config: CommandConfig = CommandConfig(title="tools.command", description="Executes a command provided by the user."),
  ):
    """Initialize the Display tool."""
    super().__init__(config)

  @classmethod
  def create(cls) -> CommandTool:
    """Create an instance of this tool."""
    return cls()

  @inject
  def run(self, params: CommandInput, context: Context, app: Typer = inject[get_command_typer()]) -> CommandOutput: # type: ignore[override]
    """Run the Command tool and return the resulting input."""
    args = shlex.split(params.input)
    @app.callback(invoke_without_command=True)
    def callback(typer_context: TyperContext):
      """Main command callback that sets up the environment."""
      typer_context.obj = context

    app(args, standalone_mode=False)
    return CommandOutput()

  def get_info(self) -> str:
    return "\n".join([
      "Use the Command tool to execute commands provided by the user.",
    ])

if __name__ == "__main__":
  # Example usage
  from antidote import world
  command_tool = world[CommandTool]
  command_input = CommandInput(input="/hello")
  command_output = command_tool.run(command_input) # type: ignore[call-arg]
  print(f"Your command returned: {command_output}") # type: ignore[no-untyped-call]
