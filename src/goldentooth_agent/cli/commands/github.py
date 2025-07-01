"""GitHub integration CLI commands."""

import asyncio

import typer
from antidote import inject
from rich.console import Console
from rich.table import Table

from ...core.document_store import DocumentStore
from ...core.embeddings import EmbeddingsService, VectorStore
from ...core.github import GitHubClient

app = typer.Typer()
console = Console()


@app.command("sync-org")
def sync_organization(
    org_name: str = typer.Argument(..., help="GitHub organization name"),
    repos: bool = typer.Option(True, "--repos/--no-repos", help="Include repositories"),
    embed: bool = typer.Option(
        True, "--embed/--no-embed", help="Embed documents after sync"
    ),
) -> None:
    """Sync a GitHub organization and its repositories."""

    @inject
    def handle(
        github_client: GitHubClient = inject.me(),
        embeddings_service: EmbeddingsService = inject.me(),
        vector_store: VectorStore = inject.me(),
    ) -> None:
        """Handle the sync-org command."""
        try:
            with console.status(f"[bold green]Syncing organization: {org_name}..."):
                result = github_client.sync_organization(org_name, include_repos=repos)

            if result.get("error"):
                console.print(
                    f"[red]Error syncing organization: {result['error']}[/red]"
                )
                raise typer.Exit(1)

            # Show sync results
            console.print(
                f"[green]✓ Organization '{org_name}' synced successfully[/green]"
            )
            if repos:
                console.print(
                    f"[cyan]  Synced {result['repos_synced']} repositories[/cyan]"
                )

            # Embed documents if requested
            if embed:
                console.print("[cyan]Embedding documents...[/cyan]")

                async def embed_docs() -> int:
                    # Embed organization
                    org_doc = github_client.document_store.github_orgs.load(org_name)
                    org_embedding = await embeddings_service.create_document_embedding(
                        org_doc.model_dump()
                    )
                    vector_store.store_document(
                        "github.orgs",
                        org_name,
                        org_embedding["text_content"],
                        org_embedding["embedding"],
                        org_embedding["metadata"],
                    )

                    embedded_repos = 0
                    if repos:
                        # Embed repositories
                        repo_ids = github_client.document_store.github_repos.list()
                        for repo_id in repo_ids:
                            try:
                                repo_doc = (
                                    github_client.document_store.github_repos.load(
                                        repo_id
                                    )
                                )
                                if repo_doc.full_name.startswith(f"{org_name}/"):
                                    repo_embedding = await embeddings_service.create_document_embedding(
                                        repo_doc.model_dump()
                                    )
                                    vector_store.store_document(
                                        "github.repos",
                                        repo_id,
                                        repo_embedding["text_content"],
                                        repo_embedding["embedding"],
                                        repo_embedding["metadata"],
                                    )
                                    embedded_repos += 1
                            except Exception as e:
                                console.print(
                                    f"[yellow]Warning: Could not embed {repo_id}: {e}[/yellow]"
                                )

                    return embedded_repos

                try:
                    embedded_repos = asyncio.run(embed_docs())
                    console.print(
                        f"[green]✓ Embedded organization + {embedded_repos} repositories[/green]"
                    )
                except Exception as e:
                    console.print(f"[yellow]Warning: Embedding failed: {e}[/yellow]")

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1) from None

    handle()


@app.command("sync-user")
def sync_user_repos(
    username: str | None = typer.Option(
        None, "--user", "-u", help="Username (default: authenticated user)"
    ),
    max_repos: int | None = typer.Option(
        20, "--max", "-m", help="Maximum repositories to sync"
    ),
    embed: bool = typer.Option(
        True, "--embed/--no-embed", help="Embed documents after sync"
    ),
) -> None:
    """Sync repositories for a user (or authenticated user)."""

    @inject
    def handle(
        github_client: GitHubClient = inject.me(),
        embeddings_service: EmbeddingsService = inject.me(),
        vector_store: VectorStore = inject.me(),
    ) -> None:
        """Handle the sync-user command."""
        try:
            user_display = username or "authenticated user"
            with console.status(
                f"[bold green]Syncing repositories for {user_display}..."
            ):
                result = github_client.sync_user_repos(
                    username=username, max_repos=max_repos
                )

            if result.get("error"):
                console.print(
                    f"[red]Error syncing user repositories: {result['error']}[/red]"
                )
                raise typer.Exit(1)

            # Show sync results
            console.print(
                f"[green]✓ Synced {result['repos_synced']} repositories for {user_display}[/green]"
            )

            # Embed documents if requested
            if embed and result["repos_synced"] > 0:
                console.print("[cyan]Embedding repositories...[/cyan]")

                async def embed_repos() -> int:
                    embedded_count = 0
                    repo_ids = github_client.document_store.github_repos.list()

                    for repo_id in repo_ids:
                        try:
                            repo_doc = github_client.document_store.github_repos.load(
                                repo_id
                            )
                            # Check if this repo was just synced (has recent last_synced)
                            if repo_doc.last_synced and (
                                repo_doc.last_synced.isoformat() == result["timestamp"]
                                or abs(
                                    repo_doc.last_synced.timestamp()
                                    - datetime.fromisoformat(
                                        result["timestamp"]
                                    ).timestamp()
                                )
                                < 60
                            ):
                                repo_embedding = (
                                    await embeddings_service.create_document_embedding(
                                        repo_doc.model_dump()
                                    )
                                )
                                vector_store.store_document(
                                    "github.repos",
                                    repo_id,
                                    repo_embedding["text_content"],
                                    repo_embedding["embedding"],
                                    repo_embedding["metadata"],
                                )
                                embedded_count += 1
                        except Exception as e:
                            console.print(
                                f"[yellow]Warning: Could not embed {repo_id}: {e}[/yellow]"
                            )

                    return embedded_count

                try:
                    from datetime import datetime

                    embedded_count = asyncio.run(embed_repos())
                    console.print(
                        f"[green]✓ Embedded {embedded_count} repositories[/green]"
                    )
                except Exception as e:
                    console.print(f"[yellow]Warning: Embedding failed: {e}[/yellow]")

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1) from None

    handle()


@app.command("list-orgs")
def list_user_organizations() -> None:
    """List organizations for the authenticated user."""

    @inject
    def handle(github_client: GitHubClient = inject.me()) -> None:
        """Handle the list-orgs command."""
        try:
            with console.status("[bold green]Fetching organizations..."):
                orgs = github_client.get_authenticated_user_orgs()

            if not orgs:
                console.print(
                    "[yellow]No organizations found for the authenticated user.[/yellow]"
                )
                return

            table = Table(title="Your GitHub Organizations")
            table.add_column("Name", style="cyan")
            table.add_column("Login", style="green")
            table.add_column("Public Repos", style="blue")
            table.add_column("Description", style="dim", max_width=50)

            for org in orgs:
                description = org.get("description") or "[dim]No description[/dim]"
                if len(description) > 47:
                    description = description[:47] + "..."

                table.add_row(
                    org.get("name") or org["id"],
                    org["id"],
                    str(org["public_repos"]),
                    description,
                )

            console.print(table)

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1) from None

    handle()


@app.command("rate-limit")
def show_rate_limit() -> None:
    """Show GitHub API rate limit status."""

    @inject
    def handle(github_client: GitHubClient = inject.me()) -> None:
        """Handle the rate-limit command."""
        try:
            rate_limit = github_client.get_api_rate_limit()

            if rate_limit.get("error"):
                console.print(
                    f"[red]Error getting rate limit: {rate_limit['error']}[/red]"
                )
                raise typer.Exit(1)

            table = Table(title="GitHub API Rate Limit Status")
            table.add_column("API", style="cyan")
            table.add_column("Limit", style="green")
            table.add_column("Remaining", style="blue")
            table.add_column("Reset Time", style="dim")

            from datetime import datetime

            core_reset = datetime.fromtimestamp(rate_limit["core_reset"]).strftime(
                "%H:%M:%S"
            )
            search_reset = datetime.fromtimestamp(rate_limit["search_reset"]).strftime(
                "%H:%M:%S"
            )

            table.add_row(
                "Core",
                str(rate_limit["core_limit"]),
                str(rate_limit["core_remaining"]),
                core_reset,
            )
            table.add_row(
                "Search",
                str(rate_limit["search_limit"]),
                str(rate_limit["search_remaining"]),
                search_reset,
            )

            console.print(table)

            # Warning if running low
            if rate_limit["core_remaining"] < 100:
                console.print(
                    "[yellow]⚠️  Warning: Core API rate limit is running low[/yellow]"
                )

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1) from None

    handle()


@app.command("status")
def show_github_status() -> None:
    """Show status of synced GitHub data."""

    @inject
    def handle(document_store: DocumentStore = inject.me()) -> None:
        """Handle the status command."""
        try:
            # Get counts
            org_count = len(document_store.github_orgs.list())
            repo_count = len(document_store.github_repos.list())

            table = Table(title="GitHub Data Status")
            table.add_column("Type", style="cyan")
            table.add_column("Count", style="green")
            table.add_column("Examples", style="dim", max_width=50)

            # Organizations
            org_examples = ", ".join(document_store.github_orgs.list()[:3])
            if len(document_store.github_orgs.list()) > 3:
                org_examples += (
                    f", ... (+{len(document_store.github_orgs.list()) - 3} more)"
                )

            table.add_row(
                "Organizations", str(org_count), org_examples or "[dim]none[/dim]"
            )

            # Repositories
            repo_examples = ", ".join(document_store.github_repos.list()[:3])
            if len(document_store.github_repos.list()) > 3:
                repo_examples += (
                    f", ... (+{len(document_store.github_repos.list()) - 3} more)"
                )

            table.add_row(
                "Repositories", str(repo_count), repo_examples or "[dim]none[/dim]"
            )

            console.print(table)

            if org_count == 0 and repo_count == 0:
                console.print(
                    "\n[dim]💡 Use 'goldentooth-agent github sync-org <org-name>' to sync GitHub data[/dim]"
                )

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1) from None

    handle()
