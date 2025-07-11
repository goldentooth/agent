"""Flow management commands for the CLI."""

from typing import Annotated

import typer

from ..core import CommandContext, CommandResult, Display

# Create command group
app = typer.Typer(
    name="flow",
    help="Manage and interact with flows",
    rich_markup_mode="rich",
)

# Global state for options
_global_context_options = {
    "no_color": False,
    "plain": False,
}


@app.callback()
def flow_callback(
    ctx: typer.Context,
    no_color: Annotated[
        bool,
        typer.Option("--no-color", help="Disable colored output"),
    ] = False,
    plain: Annotated[
        bool,
        typer.Option("--plain", help="Use plain text output without formatting"),
    ] = False,
) -> None:
    """Manage and interact with flows."""
    # For now, just use the direct options - we'll handle flexible positioning later
    _global_context_options["no_color"] = no_color
    _global_context_options["plain"] = plain


def flow_list_implementation() -> CommandResult:
    """Implementation function for flow list command.

    This function contains the actual command logic and can be easily
    unit tested without CLI framework overhead.

    Returns:
        CommandResult with the flow list output
    """
    # TODO: Implement flow listing logic
    return CommandResult(
        success=True,
        data={"flows": []},
        formatted_output="[dim]No flows available[/dim]",
    )


@app.command("list")
def flow_list_cli(ctx: typer.Context) -> None:
    """List available flows.

    Shows all registered flows with their categories, tags, and metadata.
    """
    # Get global options from main CLI
    try:
        from ..main import get_global_cli_options

        global_options = get_global_cli_options()
    except ImportError:
        global_options = {"no_color": False, "plain": False}

    # Merge options (flow-level > global)
    no_color = _global_context_options["no_color"] or global_options["no_color"]
    plain = _global_context_options["plain"] or global_options["plain"]

    # Create command context using merged options
    context = CommandContext.from_cli(
        no_color=no_color,
        plain=plain,
    )

    # Create display manager
    display = Display(context)

    try:
        # Execute command implementation
        result = flow_list_implementation()

        # Display result
        display.display_result(result)

        # Exit with appropriate code
        if not result.success:
            raise typer.Exit(result.exit_code)

    except Exception as e:
        display.error(f"Unexpected error: {str(e)}", exit_code=1)


if __name__ == "__main__":
    app()
