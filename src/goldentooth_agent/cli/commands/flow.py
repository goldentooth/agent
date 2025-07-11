"""Flow management commands for the CLI."""

import typer

from ..core import CommandContext, CommandResult, Display

# Create command group
app = typer.Typer(
    name="flow",
    help="Manage and interact with flows",
    rich_markup_mode="rich",
)


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
    # Get global options from main CLI
    try:
        from ..main import get_global_cli_options

        global_options = get_global_cli_options()
    except ImportError:
        global_options = {"no_color": False, "plain": False}

    # Create command context using global options
    context = CommandContext.from_cli(
        no_color=global_options["no_color"],
        plain=global_options["plain"],
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
