from antidote import inject
from atomic_agents.lib.base.base_io_schema import BaseIOSchema
from goldentooth_agent.core.context import Context, context_autothunk
from goldentooth_agent.core.thunk import Thunk
from typing import Annotated
from .context import INTAKE_KEY
from .tool import IntakeTool, IntakeInput, IntakeOutput

def get_intake() -> Thunk[Context, Context]:
  """Get a thunk that retrieves user input from the console."""
  @context_autothunk(name="get_intake")
  @inject
  async def _get_intake(
    intake_tool: IntakeTool = inject.me(),
  ) -> Annotated[BaseIOSchema, INTAKE_KEY]:
    input_schema = IntakeInput(prompt="You:", style="bold blue")
    intake_tool.input_schema = IntakeInput
    intake_tool.output_schema = IntakeOutput
    return intake_tool.run(input_schema) # type: ignore
  return _get_intake
