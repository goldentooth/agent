from antidote import inject
from atomic_agents.agents.base_agent import BaseAgent, BaseAgentConfig, AgentMemory
from atomic_agents.lib.base.base_io_schema import BaseIOSchema
from goldentooth_agent.core.agent import register_agent
from goldentooth_agent.core.logging import get_logger
from goldentooth_agent.core.util import NoOpInstructor
from pydantic import BaseModel
from rich.console import Console
from typing import Optional, AsyncGenerator
from .tool import IntakeInput, IntakeOutput


class IntakeAgent(BaseAgent):
    """Agent that wraps a tool and provides a simple interface for interaction."""

    @inject
    def __init__(self, logger=inject[get_logger(__name__)]):
        """Initialize the IntakeAgent."""
        agent_config = BaseAgentConfig(
            client=NoOpInstructor(),
            model="Intake",
            memory=AgentMemory(),
            system_prompt_generator=None,
            system_role="user",
            input_schema=IntakeInput,
            output_schema=IntakeOutput,
            temperature=None,
            max_tokens=None,
            model_api_parameters=None,
        )
        super().__init__(agent_config)

    from goldentooth_agent.core.console import get_console

    @inject
    def get_response(
        self,
        response_model=None,
        console: Console = inject[get_console()],
        logger=inject[get_logger(__name__)],
    ) -> type[BaseModel]:
        """Get the response from the tool agent."""
        params: IntakeInput = self.current_intake_input  # type: ignore[assignment]
        string = console.input(
            f"\n[{params.style}]{params.prompt}[/{params.style}] "
            if params.style
            else f"\n{params.prompt} "
        )
        return IntakeOutput(string=string)  # type: ignore[return-value]

    @inject
    def run(self, intake_input: Optional[BaseIOSchema] = None) -> BaseIOSchema:  # type: ignore[override]
        """Run the tool agent with the provided user input."""
        if intake_input:
            self.memory.initialize_turn()
            self.current_intake_input = intake_input
        if not isinstance(intake_input, self.input_schema):
            raise TypeError(
                f"Expected input of type {self.input_schema}, got {type(intake_input)}"
            )
        return self.get_response()  # type: ignore[call-arg]

    @inject
    async def run_async(self, intake_input: Optional[BaseIOSchema] = None) -> AsyncGenerator[BaseIOSchema, None]:  # type: ignore[override]
        """Run the tool agent asynchronously with the provided user input."""
        if intake_input:
            self.memory.initialize_turn()
            self.current_intake_input = intake_input
        response = self.get_response()  # type: ignore[call-arg]
        yield response  # type: ignore[return-value]
        self.memory.add_message("assistant", response)  # type: ignore[call-arg]


register_agent(IntakeAgent, obj=IntakeAgent(), id="intake")

if __name__ == "__main__":
    from rich.console import Console

    agent = IntakeAgent()
    response = agent.run(
        IntakeInput(prompt="Please enter your name:", style="bold blue")
    )
    Console().print(response)
