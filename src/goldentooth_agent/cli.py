import asyncio
import typer
from .agent import GoldentoothAgent

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

