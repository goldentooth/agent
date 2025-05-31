import instructor
import anthropic
from atomic_agents.lib.components.agent_memory import AgentMemory
from atomic_agents.agents.base_agent import BaseAgent, BaseAgentConfig
from ..context_provider import ContextProviderRegistry
from ..initial_context import InitialContext
from ..schemata import AgentOutputSchema, UserInputSchema
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator

MODEL = "claude-sonnet-4-20250514"

class AgentFactory:
  """A factory class for creating a chat agent with a specific initial context."""

  @staticmethod
  def create_agent(*,
    initial_context: InitialContext,
    system_prompt_generator: SystemPromptGenerator,
  ) -> BaseAgent:
    """Create and return a chat agent with the given initial context."""

    agent = BaseAgent(
      config=BaseAgentConfig(
        client=instructor.from_anthropic(anthropic.AsyncClient()),
        memory=AgentMemory(),
        model=MODEL,
        system_prompt_generator=system_prompt_generator,
        model_api_parameters={
          "max_tokens": 2048,
        },
        input_schema=UserInputSchema,
        output_schema=AgentOutputSchema,
      )
    )

    ContextProviderRegistry.populate(agent, initial_context)

    return agent

if __name__ == "__main__":
  from datetime import datetime
  from ..system_prompt import SystemPromptFactory
  initial_context = InitialContext(current_date=datetime.now())
  system_prompt_generator = SystemPromptFactory.get(initial_context)
  agent = AgentFactory.create_agent(
    initial_context=initial_context,
    system_prompt_generator=system_prompt_generator,
  )

  print("Agent created with model:", agent.model)
  print("Initial context date:", initial_context.current_date)
  print("Input schema:", agent.input_schema)
  print("Output schema:", agent.output_schema)
  print("System prompt generator:", agent.system_prompt_generator)
  print("Context providers registered:", ContextProviderRegistry.keys())
