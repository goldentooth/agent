"""Git integration CLI commands."""

from pathlib import Path

import typer
from antidote import inject
from rich.console import Console
from rich.table import Table

from ...core.git_integration import GitDataSync

app = typer.Typer()
console = Console()


@app.command("setup")
def setup_git_repository(
    repo_path: str = typer.Argument(
        ..., help="Path where Git repository should be created"
    ),
    remote_url: str | None = typer.Option(
        None, "--remote", "-r", help="Remote repository URL"
    ),
) -> None:
    """Set up a Git repository for knowledge base data."""

    @inject
    def handle(git_sync: GitDataSync = inject.me()) -> None:
        """Handle the setup command."""
        try:
            repo_path_obj = Path(repo_path).expanduser().resolve()

            with console.status(
                f"[bold green]Setting up Git repository at {repo_path_obj}..."
            ):
                result = git_sync.setup_git_repository(repo_path_obj, remote_url)

            if result["success"]:
                console.print(f"[green]✓ {result['message']}[/green]")
                console.print(f"[cyan]Repository path: {result['repo_path']}[/cyan]")
                if remote_url:
                    console.print(f"[cyan]Remote URL: {remote_url}[/cyan]")

                console.print("\n[dim]Next steps:[/dim]")
                console.print(f"[dim]  goldentooth-agent git sync {repo_path}[/dim]")
            else:
                console.print(f"[red]Error: {result['error']}[/red]")
                raise typer.Exit(1)

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1) from None

    handle()


@app.command("sync")
def sync_to_git(
    repo_path: str = typer.Argument(..., help="Path to Git repository"),
    message: str | None = typer.Option(None, "--message", "-m", help="Commit message"),
    push: bool = typer.Option(False, "--push", help="Push to remote repository"),
) -> None:
    """Sync knowledge base data to Git repository."""

    @inject
    def handle(git_sync: GitDataSync = inject.me()) -> None:
        """Handle the sync command."""
        try:
            repo_path_obj = Path(repo_path).expanduser().resolve()

            with console.status(f"[bold green]Syncing data to {repo_path_obj}..."):
                result = git_sync.sync_to_git(repo_path_obj, message, push)

            if result["success"]:
                console.print("[green]✓ Sync completed[/green]")
                console.print(f"[cyan]Files copied: {result['files_copied']}[/cyan]")

                if "files_changed" in result and result["files_changed"]:
                    console.print(
                        f"[cyan]Files committed: {len(result['files_changed'])}[/cyan]"
                    )
                    console.print(
                        f"[dim]Commit message: {result['commit_message']}[/dim]"
                    )

                    if push:
                        if result.get("pushed"):
                            console.print("[green]✓ Pushed to remote[/green]")
                        else:
                            console.print(
                                "[yellow]⚠️  Could not push to remote[/yellow]"
                            )
                            if result.get("push_error"):
                                console.print(
                                    f"[dim]Error: {result['push_error']}[/dim]"
                                )
                else:
                    console.print("[dim]No changes to commit[/dim]")
            else:
                console.print(f"[red]Error: {result['error']}[/red]")
                raise typer.Exit(1)

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1) from None

    handle()


@app.command("status")
def show_git_status(
    repo_path: str = typer.Argument(..., help="Path to Git repository"),
) -> None:
    """Show Git repository status."""

    @inject
    def handle(git_sync: GitDataSync = inject.me()) -> None:
        """Handle the status command."""
        try:
            repo_path_obj = Path(repo_path).expanduser().resolve()
            status = git_sync.get_git_status(repo_path_obj)

            if not status["exists"]:
                console.print(f"[red]Git repository not found at {repo_path_obj}[/red]")
                console.print(
                    "[dim]Run 'goldentooth-agent git setup <path>' to create one[/dim]"
                )
                raise typer.Exit(1)

            # Repository info table
            table = Table(title=f"Git Repository Status: {repo_path_obj}")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")

            table.add_row(
                "Current Branch", status["current_branch"] or "[dim]detached[/dim]"
            )
            table.add_row("Modified Files", str(status["modified_files"]))
            table.add_row("New Files", str(status["new_files"]))
            table.add_row("Total Changes", str(status["total_changes"]))

            if status["remote_url"]:
                table.add_row("Remote URL", status["remote_url"])
            else:
                table.add_row("Remote URL", "[dim]none[/dim]")

            if status["last_commit_hash"]:
                table.add_row("Last Commit", status["last_commit_hash"][:8])
                table.add_row(
                    "Commit Message", status["last_commit_message"] or "[dim]none[/dim]"
                )
                table.add_row(
                    "Commit Date", status["last_commit_date"] or "[dim]none[/dim]"
                )
            else:
                table.add_row("Last Commit", "[dim]no commits[/dim]")

            console.print(table)

            if status["total_changes"] > 0:
                console.print(
                    f"\n[yellow]💡 {status['total_changes']} files have changes. Run sync to commit them.[/yellow]"
                )

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1) from None

    handle()


@app.command("auto-sync")
def auto_sync_after_github_sync(
    repo_path: str = typer.Argument(..., help="Path to Git repository"),
    org_name: str | None = typer.Option(
        None, "--org", help="GitHub organization to sync first"
    ),
    push: bool = typer.Option(False, "--push", help="Push to remote after sync"),
) -> None:
    """Sync GitHub data and automatically commit to Git repository."""

    @inject
    def handle(git_sync: GitDataSync = inject.me()) -> None:
        """Handle the auto-sync command."""
        try:
            repo_path_obj = Path(repo_path).expanduser().resolve()

            # First, sync GitHub data if org specified
            if org_name:
                console.print(
                    f"[cyan]Step 1: Syncing GitHub organization '{org_name}'...[/cyan]"
                )
                # Import here to avoid circular imports
                from antidote import world

                from ...core.github import GitHubClient

                github_client = world.get(GitHubClient)
                if github_client is None:
                    console.print("[red]Error: GitHubClient not available[/red]")
                    return
                    
                github_result = github_client.sync_organization(
                    org_name, include_repos=True
                )

                if github_result.get("error"):
                    console.print(
                        f"[red]GitHub sync failed: {github_result['error']}[/red]"
                    )
                    raise typer.Exit(1)

                console.print(
                    f"[green]✓ Synced {github_result['repos_synced']} repositories[/green]"
                )

            # Then sync to Git
            console.print("[cyan]Step 2: Syncing to Git repository...[/cyan]")

            commit_message = "Auto-sync: GitHub data update"
            if org_name:
                commit_message += f" for {org_name}"
            commit_message += f" - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

            git_result = git_sync.sync_to_git(repo_path_obj, commit_message, push)

            if git_result["success"]:
                console.print("[green]✓ Git sync completed[/green]")
                console.print(
                    f"[cyan]Files copied: {git_result['files_copied']}[/cyan]"
                )

                if git_result.get("files_changed"):
                    console.print(
                        f"[cyan]Files committed: {len(git_result['files_changed'])}[/cyan]"
                    )

                    if push and git_result.get("pushed"):
                        console.print("[green]✓ Pushed to remote repository[/green]")

                console.print("\n[green]🎉 Complete workflow finished![/green]")
                console.print(
                    f"[dim]GitHub → Local Storage → Git Repository{' → Remote' if push else ''}[/dim]"
                )
            else:
                console.print(f"[red]Git sync failed: {git_result['error']}[/red]")
                raise typer.Exit(1)

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1) from None

    handle()


if __name__ == "__main__":
    from datetime import datetime
