from typing import Union, Optional
from pydantic import Field, create_model
from atomic_agents.agents.base_agent import BaseIOSchema
from atomic_agents.lib.base.base_tool import BaseToolConfig
from goldentooth_agent.tool.registry import ToolRegistry

tool_input_schemata = tuple(tool.input_schema for tool in ToolRegistry.all())
tool_output_schemata = tuple(tool.output_schema for tool in ToolRegistry.all())
tool_input_schemata_union = Union[*tool_input_schemata] if tool_input_schemata else BaseIOSchema
tool_output_schemata_union = Union[*tool_output_schemata] if tool_output_schemata else

ChatSessionIOSchema = create_model(
  "ChatSessionIOSchema",
  __doc__="Schema for input/output in a chat session.",
  chat_message=(str, Field(..., description="The response message to return to the next member of the conversation.")),
  tool_name=(Optional[str], Field(..., description=f"The name of the tool to use (one of: {', '.join(ToolRegistry.keys())}), or None if no tool is used.")),
  tool_input=(Optional[tool_input_schemata_union], Field(..., description="Input parameters for the selected tool; only required if a tool is used.")),
  tool_output=(Optional[tool_output_schemata_union], Field(..., description="Output results from the tool; only provided if a tool is used.")),
  ttl=(Optional[int], Field(3, description="Time to live (in rounds) for the chat session. Always decremented by 1 after each round.")),
  __base__=BaseIOSchema,
)

config_fields = {
  tool.metadata_class.get_name(): (tool.config_class, ...)
  for tool in ToolRegistry.all()
}

ChatSessionToolConfig = create_model( # type: ignore[no-redef]
  "ChatSessionToolConfig",
  __doc__="Configuration for the chat session tool.",
  __base__=BaseToolConfig,
  **{
    **config_fields, # type: ignore[assignment]
  },
)

if __name__ == "__main__":
    # Example usage
    print(ChatSessionIOSchema.schema_json(indent=2))
    print(ChatSessionToolConfig.schema_json(indent=2))
    print("Registered tools:", ToolRegistry.keys())
    print("Tool input schema union:", tool_input_schemata_union)
    print("Tool output schema union:", tool_output_schemata_union)
