"""Rich display utilities for CLI output."""

# pyright: reportUnknownVariableType=false
# pyright: reportUnknownArgumentType=false

from __future__ import annotations

import json
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator, Optional, Union

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table
from rich.terminal_theme import DIMMED_MONOKAI
from rich.tree import Tree

from .context import CommandContext, CommandResult
from .exceptions import CLIError


class Display:
    """Rich display utilities for consistent CLI output."""

    def __init__(self, context: CommandContext) -> None:
        super().__init__()
        self.context = context
        self.console = context.console

        # Configure recording if requested
        if context.record_svg:
            self.console = Console(record=True)

    def print(self, *args: Any, **kwargs: Any) -> None:
        """Print with current console configuration."""
        self.console.print(*args, **kwargs)

    def error(self, message: str, exit_code: int = 1) -> None:
        """Display error message and exit."""
        self.console.print(f"❌ Error: {message}", style="red")
        if exit_code > 0:
            raise CLIError(message, exit_code=exit_code)

    def success(self, message: str) -> None:
        """Display success message."""
        self.console.print(f"✅ {message}", style="green")

    def warning(self, message: str) -> None:
        """Display warning message."""
        self.console.print(f"⚠️  {message}", style="yellow")

    def info(self, message: str) -> None:
        """Display info message."""
        self.console.print(f"ℹ️  {message}", style="blue")

    def panel(
        self,
        content: Any,
        title: Optional[str] = None,
        border_style: str = "blue",
    ) -> None:
        """Display content in a panel."""
        self.console.print(Panel(content, title=title, border_style=border_style))

    def table(
        self,
        data: list[dict[str, Any]],
        title: Optional[str] = None,
        headers: Optional[list[str]] = None,
    ) -> None:
        """Display data in a table format."""
        if not data:
            self.warning("No data to display")
            return

        # Determine headers
        if headers is None:
            headers = list(data[0].keys()) if data else []

        # Create table
        table = Table(title=title, show_header=True, header_style="bold blue")

        # Add columns
        for header in headers:
            table.add_column(header, style="dim")

        # Add rows
        for row in data:
            table.add_row(*[str(row.get(header, "")) for header in headers])

        self.console.print(table)

    def tree(
        self,
        data: dict[str, Any],
        title: str = "Data",
        guide_style: str = "blue",
    ) -> None:
        """Display hierarchical data as a tree."""
        tree = Tree(title, guide_style=guide_style)
        self._add_tree_nodes(tree, data)
        self.console.print(tree)

    def _add_tree_nodes(self, tree: Tree, data: Any) -> None:
        """Recursively add nodes to tree."""
        if isinstance(data, dict):
            for key, value in data.items():
                key_str = str(key)
                if isinstance(value, (dict, list)):
                    branch = tree.add(f"[bold]{key_str}[/bold]")
                    self._add_tree_nodes(branch, value)
                else:
                    tree.add(f"[bold]{key_str}[/bold]: {str(value)}")
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, (dict, list)):
                    branch = tree.add(f"[bold]{i}[/bold]")
                    self._add_tree_nodes(branch, item)
                else:
                    tree.add(f"[bold]{i}[/bold]: {str(item)}")

    @contextmanager
    def spinner(self, message: str) -> Iterator[None]:
        """Context manager for displaying a spinner during operations."""
        if self.context.plain_output:
            # Plain output: just show message
            self.console.print(f"⏳ {message}...")
            yield
        else:
            # Rich output: show spinner
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                TimeElapsedColumn(),
                console=self.console,
            ) as progress:
                task = progress.add_task(message, total=None)
                yield
                progress.update(task, completed=True)

    def progress_bar(
        self,
        iterable: Any,
        description: str = "Processing...",
        total: Optional[int] = None,
    ) -> Any:
        """Display a progress bar for iterable operations."""
        if self.context.plain_output:
            # Plain output: no progress bar
            return iterable

        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            "[progress.percentage]{task.percentage:>3.0f}%",
            console=self.console,
        ).track(iterable, description=description, total=total)

    def display_result(self, result: CommandResult) -> None:
        """Display command result based on context configuration."""
        if not result.success:
            self.error(
                result.error_message or "Command failed", exit_code=result.exit_code
            )
            return

        if self.context.output_format == "json":
            self.console.print(json.dumps(result.to_json(), indent=2))
        elif self.context.output_format == "text":
            if result.formatted_output:
                self.console.print(result.formatted_output)
            elif result.display_data:
                self._display_data(result.display_data)
            else:
                self.console.print(result.to_text())
        else:  # auto format
            self._display_data(result.data or result.display_data)

    def _display_data(self, data: Any) -> None:
        """Display data in appropriate format."""
        if isinstance(data, dict):
            if len(data) > 5:  # Large dict: use tree
                self.tree(data)
            else:  # Small dict: use panel
                content = "\n".join(
                    f"[bold]{str(k)}[/bold]: {str(v)}" for k, v in data.items()
                )
                self.panel(content)
        elif isinstance(data, list):
            if data and isinstance(data[0], dict):
                # Type assertion for list of dicts
                dict_list: list[dict[str, Any]] = [
                    item for item in data if isinstance(item, dict)
                ]
                self.table(dict_list)
            else:
                for item in data:
                    self.console.print(f"• {str(item)}")
        else:
            self.console.print(str(data))

    def save_svg(self, path: Optional[Union[str, Path]] = None) -> None:
        """Save recorded output as SVG."""
        if not self.context.record_svg:
            return

        if path is None:
            path = self.context.svg_output_path or "output.svg"

        if hasattr(self.console, "save_svg"):
            self.console.save_svg(str(path), theme=DIMMED_MONOKAI)
            self.info(f"SVG saved to {path}")
        else:
            self.warning("SVG recording not available")

    def measure_time(self, func: Any, *args: Any, **kwargs: Any) -> tuple[Any, float]:
        """Measure execution time of a function."""
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        return result, execution_time
