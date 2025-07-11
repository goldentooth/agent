"""Template for CLI command modules.

This file serves as a template for creating new CLI command modules.
Copy this file and modify it to create new command groups.
"""

from typing import Annotated, Optional

import typer
from rich.console import Console

from ..core import CommandContext, CommandResult, Display
from ..core.exceptions import CLIError

# Create command group
app = typer.Typer(
    name="template",
    help="Template command group for demonstration",
    rich_markup_mode="rich",
)

# Console for direct output
console = Console()


def template_command_implementation(
    input_data: str,
    option_flag: bool = False,
    format_option: str = "text",
) -> CommandResult:
    """Implementation function for template command.

    This function contains the actual command logic and can be easily
    unit tested without CLI framework overhead.

    Args:
        input_data: The input data to process
        option_flag: Boolean option flag
        format_option: Format option (text, json, etc.)

    Returns:
        CommandResult with the command output
    """
    try:
        # Command implementation logic here
        processed_data = f"Processed: {input_data}"

        if option_flag:
            processed_data += " (with option)"

        return CommandResult(
            data={"processed": processed_data},
            success=True,
            formatted_output=processed_data,
        )

    except Exception as e:
        return CommandResult(
            success=False,
            error_message=str(e),
            exit_code=1,
        )


@app.command("example")
def template_command_cli(
    input_data: Annotated[str, typer.Argument(help="Input data to process")],
    option_flag: Annotated[
        bool, typer.Option("--flag", "-f", help="Enable option flag")
    ] = False,
    format_option: Annotated[
        str, typer.Option("--format", help="Output format")
    ] = "text",
    plain: Annotated[
        bool, typer.Option("--plain", help="Plain output without formatting")
    ] = False,
    no_color: Annotated[
        bool, typer.Option("--no-color", help="Disable colored output")
    ] = False,
    record: Annotated[
        bool, typer.Option("--record", help="Record output as SVG")
    ] = False,
    record_path: Annotated[
        Optional[str], typer.Option("--record-path", help="SVG output path")
    ] = None,
) -> None:
    """Template command with modern Typer patterns.

    This command demonstrates the recommended patterns for CLI commands:
    - Uses Annotated[] syntax for parameters
    - Delegates to separate implementation function
    - Supports rich output with plain fallback
    - Includes SVG recording capability
    """
    # Create command context
    context = CommandContext.from_cli(
        input_data=input_data,
        output_format=format_option,
        plain=plain,
        no_color=no_color,
        record=record,
        record_path=record_path,
    )

    # Create display manager
    display = Display(context)

    try:
        # Execute command implementation
        with display.spinner("Processing..."):
            result = template_command_implementation(
                input_data=input_data,
                option_flag=option_flag,
                format_option=format_option,
            )

        # Display result
        display.display_result(result)

        # Save SVG if requested
        display.save_svg()

        # Exit with appropriate code
        if not result.success:
            raise typer.Exit(result.exit_code)

    except CLIError as e:
        display.error(str(e), exit_code=e.exit_code)
    except Exception as e:
        display.error(f"Unexpected error: {str(e)}", exit_code=1)


@app.command("list")
def template_list_command(
    format_option: Annotated[
        str, typer.Option("--format", help="Output format")
    ] = "table",
    plain: Annotated[bool, typer.Option("--plain", help="Plain output")] = False,
) -> None:
    """List template items with rich table output."""
    context = CommandContext.from_cli(
        output_format=format_option,
        plain=plain,
    )

    display = Display(context)

    # Example data
    data = [
        {"name": "item1", "type": "type1", "status": "active"},
        {"name": "item2", "type": "type2", "status": "inactive"},
        {"name": "item3", "type": "type1", "status": "active"},
    ]

    if format_option == "json":
        console.print_json(data=data)
    else:
        display.table(data, title="Template Items")


if __name__ == "__main__":
    app()
