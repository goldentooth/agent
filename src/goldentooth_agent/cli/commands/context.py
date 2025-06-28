from __future__ import annotations

import json
import sys
from typing import Annotated, Any

import typer
from antidote import inject
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.tree import Tree

from goldentooth_agent.core.context import Context

# Type aliases to handle legitimate Any usage
ContextValue = Any  # type: ignore[explicit-any]  # Context values can be any type
ParsedValue = Any  # type: ignore[explicit-any]  # Parsed values can be any type

app = typer.Typer()


@app.command("inspect")
def inspect_context(
    key: Annotated[
        str | None, typer.Option("--key", "-k", help="Specific key to inspect")
    ] = None,
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format: rich, json, tree")
    ] = "rich",
    show_history: Annotated[
        bool, typer.Option("--history", help="Show context history")
    ] = False,
    show_computed: Annotated[
        bool, typer.Option("--computed", help="Show computed properties")
    ] = False,
) -> None:
    """Inspect context state and structure."""

    @inject
    def handle() -> None:
        """Handle context inspection."""
        console = Console()

        # Create a sample context for demonstration
        context = create_demo_context()

        if key:
            # Inspect specific key
            try:
                value = context.get(key)
                show_key_details(console, key, value, format)
            except KeyError:
                console.print(f"[red]Error: Key '{key}' not found in context[/red]")
                available_keys = list(context.keys())
                if available_keys:
                    console.print(
                        f"[dim]Available keys: {', '.join(available_keys)}[/dim]"
                    )
                raise typer.Exit(1)
        else:
            # Inspect entire context
            show_context_overview(console, context, format, show_history, show_computed)

    handle()


@app.command("set")
def set_context_value(
    key: Annotated[str, typer.Argument(help="Context key to set")],
    value: Annotated[
        str, typer.Argument(help="Value to set (JSON string or plain text)")
    ],
    type_hint: Annotated[
        str | None,
        typer.Option("--type", help="Value type: str, int, float, bool, json"),
    ] = None,
) -> None:
    """Set a value in the context."""

    @inject
    def handle() -> None:
        """Handle setting context value."""
        console = Console()

        # Parse value based on type hint
        parsed_value = parse_value(value, type_hint)

        # For demo purposes, create a context and show the operation
        context = Context()
        context.set(key, parsed_value)

        console.print(
            f"[green]✓[/green] Set context key '{key}' = {repr(parsed_value)}"
        )

        # Show the updated context
        console.print("\n[bold blue]Updated Context:[/bold blue]")
        show_context_overview(console, context, "rich", False, False)

    handle()


@app.command("export")
def export_context(
    format: Annotated[
        str, typer.Option("--format", "-f", help="Export format: json, yaml")
    ] = "json",
    output: Annotated[
        str | None, typer.Option("--output", "-o", help="Output file (default: stdout)")
    ] = None,
) -> None:
    """Export context to file or stdout."""

    @inject
    def handle() -> None:
        """Handle context export."""
        console = Console(file=sys.stderr)  # Errors to stderr

        # Create demo context
        context = create_demo_context()

        # Export context data
        if format == "json":
            export_data = export_context_as_json(context)
        elif format == "yaml":
            console.print("[yellow]YAML export not yet implemented[/yellow]")
            raise typer.Exit(1)
        else:
            console.print(f"[red]Error: Unknown format '{format}'[/red]")
            raise typer.Exit(1)

        # Output to file or stdout
        if output:
            try:
                with open(output, "w") as f:
                    f.write(export_data)
                console.print(f"[green]✓[/green] Context exported to {output}")
            except Exception as e:
                console.print(f"[red]Error writing to file: {e}[/red]")
                raise typer.Exit(1)
        else:
            print(export_data)

    handle()


def create_demo_context() -> Context:
    """Create a demo context with sample data."""
    context = Context()

    # Add some sample data
    context.set("user_name", "Alice")
    context.set("session_id", "demo_session_123")
    context.set(
        "model_config",
        {"name": "claude-3.5-sonnet", "temperature": 0.7, "max_tokens": 1000},
    )
    context.set("message_count", 5)
    context.set("last_response", "Hello! How can I help you today?")
    context.set(
        "agent_metadata",
        {
            "agent_type": "echo",
            "version": "1.0.0",
            "capabilities": ["text_processing", "math", "conversation"],
        },
    )

    return context


def show_key_details(
    console: Console, key: str, value: ContextValue, format: str
) -> None:
    """Show details for a specific context key."""
    if format == "json":
        if isinstance(value, (dict, list)):
            print(json.dumps(value, indent=2))
        else:
            print(json.dumps({"key": key, "value": value}, indent=2))
    elif format == "rich":
        console.print()
        console.print(
            Panel.fit(
                f"[bold cyan]Key:[/bold cyan] {key}\n"
                f"[bold cyan]Type:[/bold cyan] {type(value).__name__}\n"
                f"[bold cyan]Value:[/bold cyan]",
                border_style="cyan",
                title="🔍 Context Key Details",
            )
        )

        if isinstance(value, (dict, list)):
            syntax = Syntax(json.dumps(value, indent=2), "json", theme="monokai")
            console.print(syntax)
        else:
            console.print(f"  {repr(value)}")
        console.print()
    else:
        # Tree format
        tree = Tree(f"Key: {key}")
        if isinstance(value, dict):
            for k, v in value.items():
                tree.add(f"{k}: {repr(v)}")
        elif isinstance(value, list):
            for i, item in enumerate(value):
                tree.add(f"[{i}]: {repr(item)}")
        else:
            tree.add(f"Value: {repr(value)}")
        console.print(tree)


def show_context_overview(
    console: Console,
    context: Context,
    format: str,
    show_history: bool,
    show_computed: bool,
) -> None:
    """Show overview of entire context."""
    if format == "json":
        export_data = export_context_as_json(context)
        print(export_data)
    elif format == "rich":
        # Rich table display
        table = Table(
            title="Context Overview", show_header=True, header_style="bold magenta"
        )
        table.add_column("Key", style="cyan", no_wrap=True)
        table.add_column("Type", style="green")
        table.add_column("Value Preview", style="blue")

        for key in context.keys():
            value = context.get(key)
            value_type = type(value).__name__

            # Create value preview
            if isinstance(value, (dict, list)):
                preview = json.dumps(value)  # type: ignore[unreachable]  # False positive
            else:
                preview = str(value)

            if len(preview) > 50:
                preview = preview[:47] + "..."

            table.add_row(key, value_type, preview)

        console.print()
        console.print(table)
        console.print()

        # Show statistics
        key_count = len(list(context.keys()))
        console.print(
            Panel.fit(
                f"[bold blue]Total Keys:[/bold blue] {key_count}\n"
                f"[bold blue]Context Type:[/bold blue] {type(context).__name__}",
                border_style="blue",
                title="📊 Context Statistics",
            )
        )

        if show_history:
            console.print("\n[yellow]History tracking not yet implemented[/yellow]")

        if show_computed:
            console.print("\n[yellow]Computed properties not yet implemented[/yellow]")

    elif format == "tree":
        # Tree display
        tree = Tree("Context")
        for key in context.keys():
            value = context.get(key)
            key_node = tree.add(f"[cyan]{key}[/cyan] ({type(value).__name__})")

            if isinstance(value, dict):
                for k, v in value.items():  # type: ignore[unreachable]  # False positive
                    key_node.add(f"{k}: {repr(v)}")
            elif isinstance(value, list):
                for i, item in enumerate(value):  # type: ignore[unreachable]  # False positive
                    key_node.add(f"[{i}]: {repr(item)}")
            else:
                key_node.add(repr(value))

        console.print()
        console.print(tree)
        console.print()


def export_context_as_json(context: Context) -> str:
    """Export context as JSON string."""
    data: dict[str, ContextValue] = {}
    for key in context.keys():
        value = context.get(key)
        data[key] = value

    return json.dumps(data, indent=2, default=str)


def parse_value(value_str: str, type_hint: str | None) -> ParsedValue:
    """Parse a value string based on type hint."""
    if type_hint == "int":
        return int(value_str)
    elif type_hint == "float":
        return float(value_str)
    elif type_hint == "bool":
        return value_str.lower() in ("true", "yes", "1", "on")
    elif type_hint == "json":
        return json.loads(value_str)
    elif type_hint == "str" or type_hint is None:
        # Try JSON first, fall back to string
        try:
            return json.loads(value_str)
        except json.JSONDecodeError:
            return value_str
    else:
        return value_str


@app.command("keys")
def list_context_keys() -> None:
    """List all available context keys."""

    @inject
    def handle() -> None:
        """Handle listing context keys."""
        console = Console()

        # Create demo context
        context = create_demo_context()
        keys = list(context.keys())

        if not keys:
            console.print("[yellow]No keys in context[/yellow]")
            return

        console.print("\n[bold blue]Available Context Keys:[/bold blue]")
        for key in sorted(keys):
            value = context.get(key)
            value_type = type(value).__name__
            console.print(f"  • [cyan]{key}[/cyan] ({value_type})")

        console.print(f"\n[dim]Total: {len(keys)} keys[/dim]")

    handle()
