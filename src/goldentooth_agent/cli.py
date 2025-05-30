import asyncio
import typer
from dotenv import load_dotenv
from .chat_session import ChatSession
from .initial_context import InitialContext

load_dotenv()
app = typer.Typer()

@app.command()
def chat():
  """
  Start a chat session
  """
  initial_context = InitialContext()
  chat_session = ChatSession(initial_context)
  asyncio.run(chat_session.start())

@app.command()
def null():
  """
  Placeholder command for future use
  """

