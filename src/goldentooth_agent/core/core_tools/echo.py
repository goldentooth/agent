from __future__ import annotations
from antidote import inject, injectable
from atomic_agents.agents.base_agent import BaseAgentInputSchema, BaseAgentOutputSchema
from atomic_agents.lib.base.base_tool import BaseToolConfig, BaseTool
from atomic_agents.lib.components.system_prompt_generator import (
    SystemPromptContextProviderBase,
)
from goldentooth_agent.core.logging import get_logger
from goldentooth_agent.core.tool import register_tool
from goldentooth_agent.core.tool_agent import register_tool_agent


class EchoConfig(BaseToolConfig):
    """Configuration for the Echo tool."""

    pass


@register_tool_agent
@register_tool
@injectable(factory_method="create")
class EchoTool(BaseTool, SystemPromptContextProviderBase):
    """Echo tool that returns the input string as output."""

    input_schema = BaseAgentInputSchema
    output_schema = BaseAgentOutputSchema

    def __init__(
        self,
        config: EchoConfig = EchoConfig(
            title="tools.echo",
            description="Echo tool that returns the input string as output.",
        ),
    ):
        super().__init__(config)

    @classmethod
    def create(cls) -> EchoTool:
        """Create an instance of this tool."""
        return cls()

    @inject
    def run(self, params: BaseAgentInputSchema, logger=inject[get_logger(__name__)]) -> BaseAgentOutputSchema:  # type: ignore[attr-defined]
        logger.debug(f"Running EchoTool with input: {params.chat_message}")
        return BaseAgentOutputSchema(chat_message=params.chat_message)

    def get_info(self) -> str:
        """Provide information about the Echo tool."""
        return "\n".join(
            [
                "Use the Echo tool to return the input string as output.",
                "This tool simply echoes back the input string without any modifications.",
            ]
        )


if __name__ == "__main__":
    # Example usage
    from antidote import world

    tool = world[EchoTool]
    input_data = BaseAgentInputSchema(chat_message="Hello, World!")
    output_data = tool.run(input_data)  # type: ignore[call-arg]
    print(output_data.model_dump_json(indent=2))
    print("EchoTool created and run successfully.")
