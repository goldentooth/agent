from ...schemata import AgentOutputSchema
from ...chat import ChatSession
from ...greeting.greeting import Greeting

class GreeterVisitor:
  """Visitor that greets the user in a chat session."""

  def visit(self, session: ChatSession):
    """Visit the chat session and greet the user."""
    greeting = Greeting.get(session.initial_context)
    session.console.print(greeting)
    # session.console.print(session.format_agent_text(greeting))
    output = AgentOutputSchema.model_validate({
      "chat_message": greeting,
    })
    session.memory.add_message("assistant", output)

if __name__ == "__main__":
  from ...initial_context import InitialContext
  from ...system_prompt import SystemPromptFactory
  initial_context = InitialContext()
  system_prompt_generator = SystemPromptFactory.get(initial_context)
  session = ChatSession(
    initial_context=initial_context,
    system_prompt_generator=system_prompt_generator,
  )
  GreeterVisitor().visit(session)
  user_input = session.console.input("\n[bold blue]You:[/bold blue] ")
