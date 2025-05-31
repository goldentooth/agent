import asyncio
import typer
from dotenv import load_dotenv
from .chat import ChatSession
from .initial_context import InitialContext
from .system_prompt import SystemPromptFactory

load_dotenv()
app = typer.Typer()

@app.command()
def chat():
  """
  Start a chat session
  """
  initial_context = InitialContext()
  system_prompt_generator = SystemPromptFactory.get()
  chat_session = ChatSession(
    initial_context=initial_context,
    system_prompt_generator=system_prompt_generator,
  )
  asyncio.run(chat_session.start())

@app.command()
def null():
  """
  Placeholder command for future use
  """

