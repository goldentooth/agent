import typer
from dotenv import load_dotenv

load_dotenv()

app = typer.Typer(
    help="""Goldentooth Agent - AI-powered document processing and chat.
"""
)
