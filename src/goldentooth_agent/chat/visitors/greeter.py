from ...schemata import AgentOutputSchema
from ...chat import ChatSession

class GreeterVisitor:
  """Visitor that greets the user in a chat session."""

  def visit(self, session: ChatSession):
    from ...greeting import Greeting
    greeting = Greeting.get(session.initial_context)
    session.console.print(greeting)
    # session.console.print(session.format_agent_text(greeting))
    output = AgentOutputSchema.model_validate({
      "chat_message": greeting,
    })
    session.memory.add_message("assistant", output)

if __name__ == "__main__":
  from ...initial_context import InitialContext
  initial_context = InitialContext()
  session = ChatSession(initial_context)
  GreeterVisitor().visit(session)
  user_input = session.console.input("\n[bold blue]You:[/bold blue] ")
