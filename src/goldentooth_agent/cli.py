import asyncio
import typer
from dotenv import load_dotenv
from .agent import GoldentoothAgent

load_dotenv()
app = typer.Typer()

@app.command()
def chat():
  """
  Start a chat session
  """
  agent = GoldentoothAgent()
  asyncio.run(agent.chat())

@app.command()
def null():
  """
  Placeholder command for future use
  """

