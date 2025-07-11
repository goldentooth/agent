from __future__ import annotations

import typer

from .commands import flow_list_cli, flow_run_cli, flow_search_cli

app = typer.Typer(
    name="flow",
    help="Flow command interface for executing and managing flows",
    no_args_is_help=True,
)

# Register commands
app.command("list", help="List available flows")(flow_list_cli)
app.command("search", help="Search flows by name or metadata")(flow_search_cli)
app.command("run", help="Execute a flow with input data")(flow_run_cli)
