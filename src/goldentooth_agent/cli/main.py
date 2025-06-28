import typer
from dotenv import load_dotenv

from . import commands

load_dotenv()

app = typer.Typer()
app.add_typer(commands.chat.app, help="Talk to the agent.")
app.add_typer(commands.tools.app, name="tools", help="Manage tools and utilities.")
app.add_typer(commands.flow.app, name="flow", help="Execute and manage flows.")
app.add_typer(
    commands.context.app, name="context", help="Inspect and manage context state."
)
app.add_typer(commands.agents.app, name="agents", help="Manage agent instances.")
app.add_typer(
    commands.debug.app, name="debug", help="System debugging and diagnostics."
)
app.add_typer(
    commands.demo.app, name="demo", help="Interactive demonstrations and tutorials."
)
app.add_typer(
    commands.pipeline.app, name="pipeline", help="Execute and manage tool pipelines."
)
app.add_typer(
    commands.instructor.app,
    name="instructor",
    help="Structured output with Instructor.",
)
app.add_typer(
    commands.docs.app,
    name="docs", 
    help="Manage knowledge base documents and embeddings.",
)
app.add_typer(
    commands.github.app,
    name="github",
    help="Sync GitHub organizations and repositories.",
)
app.add_typer(
    commands.setup.app,
    name="setup",
    help="Initialize and configure the system.",
)
app.add_typer(
    commands.git_sync.app,
    name="git",
    help="Sync knowledge base data to Git repositories.",
)
