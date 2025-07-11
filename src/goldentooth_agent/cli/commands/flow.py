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
    # Store global options
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
def flow_list_cli() -> None:
    """List available flows.

    Shows all registered flows with their categories, tags, and metadata.
    """
    # Create command context using global options
    context = CommandContext.from_cli(
        no_color=_global_context_options["no_color"],
        plain=_global_context_options["plain"],
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
