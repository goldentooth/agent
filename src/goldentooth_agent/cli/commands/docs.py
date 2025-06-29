"""Document management CLI commands."""

import asyncio
import json

import typer
from antidote import inject
from rich.console import Console
from rich.table import Table

from ...core.document_store import DocumentStore
from ...core.embeddings import EmbeddingsService, VectorStore
from ...core.rag import RAGService

app = typer.Typer()
console = Console()


@app.command("list")
def list_documents(
    store_type: str | None = typer.Option(
        None, "--type", "-t", help="Filter by store type"
    ),
    limit: int | None = typer.Option(
        None, "--limit", "-l", help="Limit number of results"
    ),
):
    """List all documents in the knowledge base."""

    @inject
    def handle(document_store: DocumentStore = inject.me()) -> None:
        """Handle the list command."""
        try:
            if store_type:
                # Validate store type
                valid_types = [
                    "github.orgs",
                    "github.repos",
                    "goldentooth.nodes",
                    "goldentooth.services",
                    "notes",
                ]
                if store_type not in valid_types:
                    console.print(
                        f"[red]Invalid store type. Valid types: {', '.join(valid_types)}[/red]"
                    )
                    raise typer.Exit(1)

                # Get documents for specific store type
                if store_type == "github.orgs":
                    docs = document_store.github_orgs.list()
                elif store_type == "github.repos":
                    docs = document_store.github_repos.list()
                elif store_type == "goldentooth.nodes":
                    docs = document_store.goldentooth_nodes.list()
                elif store_type == "goldentooth.services":
                    docs = document_store.goldentooth_services.list()
                elif store_type == "notes":
                    docs = document_store.notes.list()

                if limit:
                    docs = docs[:limit]

                console.print(f"[green]Documents in {store_type}:[/green]")
                for doc_id in docs:
                    console.print(f"  • {doc_id}")

                if not docs:
                    console.print(f"  [dim]No documents found in {store_type}[/dim]")

            else:
                # List all documents across all stores
                all_docs = document_store.list_all_documents()

                table = Table(title="Document Store Summary")
                table.add_column("Store Type", style="cyan")
                table.add_column("Count", style="green")
                table.add_column("Documents", style="dim")

                for store_name, doc_list in all_docs.items():
                    count = len(doc_list)
                    preview = ", ".join(doc_list[:3])
                    if len(doc_list) > 3:
                        preview += f", ... (+{len(doc_list) - 3} more)"
                    if not preview:
                        preview = "[dim]none[/dim]"

                    table.add_row(store_name, str(count), preview)

                console.print(table)

        except Exception as e:
            console.print(f"[red]Error listing documents: {e}[/red]")
            raise typer.Exit(1) from None

    handle()


@app.command("show")
def show_document(
    store_type: str = typer.Argument(
        ..., help="Store type (e.g., github.repos, notes)"
    ),
    document_id: str = typer.Argument(..., help="Document ID"),
    raw: bool = typer.Option(False, "--raw", help="Show raw YAML content"),
):
    """Show details of a specific document."""

    @inject
    def handle(document_store: DocumentStore = inject.me()) -> None:
        """Handle the show command."""
        try:
            # Validate store type and get document
            if store_type == "github.orgs":
                if not document_store.github_orgs.exists(document_id):
                    console.print(
                        f"[red]Document '{document_id}' not found in {store_type}[/red]"
                    )
                    raise typer.Exit(1)
                doc = document_store.github_orgs.load(document_id)

            elif store_type == "github.repos":
                if not document_store.github_repos.exists(document_id):
                    console.print(
                        f"[red]Document '{document_id}' not found in {store_type}[/red]"
                    )
                    raise typer.Exit(1)
                doc = document_store.github_repos.load(document_id)

            elif store_type == "goldentooth.nodes":
                if not document_store.goldentooth_nodes.exists(document_id):
                    console.print(
                        f"[red]Document '{document_id}' not found in {store_type}[/red]"
                    )
                    raise typer.Exit(1)
                doc = document_store.goldentooth_nodes.load(document_id)

            elif store_type == "goldentooth.services":
                if not document_store.goldentooth_services.exists(document_id):
                    console.print(
                        f"[red]Document '{document_id}' not found in {store_type}[/red]"
                    )
                    raise typer.Exit(1)
                doc = document_store.goldentooth_services.load(document_id)

            elif store_type == "notes":
                if not document_store.notes.exists(document_id):
                    console.print(
                        f"[red]Document '{document_id}' not found in {store_type}[/red]"
                    )
                    raise typer.Exit(1)
                doc = document_store.notes.load(document_id)

            else:
                console.print(f"[red]Invalid store type: {store_type}[/red]")
                raise typer.Exit(1)

            if raw:
                # Show raw YAML file content
                file_path = document_store.get_document_path(store_type, document_id)
                if file_path.exists():
                    content = file_path.read_text()
                    console.print(
                        f"[cyan]Raw YAML content for {store_type}/{document_id}:[/cyan]"
                    )
                    console.print(content)
                else:
                    console.print(f"[red]File not found: {file_path}[/red]")
            else:
                # Show formatted document details
                console.print(f"[cyan]Document: {store_type}/{document_id}[/cyan]")
                console.print(json.dumps(doc.model_dump(), indent=2, default=str))

        except Exception as e:
            console.print(f"[red]Error showing document: {e}[/red]")
            raise typer.Exit(1) from None

    handle()


@app.command("paths")
def show_paths() -> None:
    """Show file system paths for document stores."""

    @inject
    def handle(document_store: DocumentStore = inject.me()) -> None:
        """Handle the paths command."""
        try:
            paths = document_store.get_store_paths()

            table = Table(title="Document Store Paths")
            table.add_column("Store Type", style="cyan")
            table.add_column("Path", style="green")
            table.add_column("Exists", style="dim")

            for store_name, path in paths.items():
                exists = "✓" if path.exists() else "✗"
                table.add_row(store_name, str(path), exists)

            console.print(table)

        except Exception as e:
            console.print(f"[red]Error showing paths: {e}[/red]")
            raise typer.Exit(1) from None

    handle()


@app.command("stats")
def show_stats() -> None:
    """Show statistics about the document store and vector database."""

    @inject
    def handle(
        document_store: DocumentStore = inject.me(),
        vector_store: VectorStore = inject.me(),
    ) -> None:
        """Handle the stats command."""
        try:
            # Get document store stats
            doc_counts = document_store.get_document_count()

            # Get vector store stats
            vector_stats = vector_store.get_stats()

            # Document store table
            doc_table = Table(title="Document Store Statistics")
            doc_table.add_column("Store Type", style="cyan")
            doc_table.add_column("Document Count", style="green")

            total_docs = 0
            for store_type, count in doc_counts.items():
                doc_table.add_row(store_type, str(count))
                total_docs += count

            doc_table.add_row("[bold]Total[/bold]", f"[bold]{total_docs}[/bold]")
            console.print(doc_table)

            # Vector store table
            vector_table = Table(title="Vector Store Statistics")
            vector_table.add_column("Metric", style="cyan")
            vector_table.add_column("Value", style="green")

            vector_table.add_row(
                "Total Embeddings", str(vector_stats["total_documents"])
            )
            vector_table.add_row("Embedding Engine", vector_stats["embedding_engine"])
            vector_table.add_row("Database Path", vector_stats["database_path"])

            # Add per-store-type embedding counts
            for store_type, count in vector_stats["by_store_type"].items():
                vector_table.add_row(f"  {store_type}", str(count))

            console.print(vector_table)

        except Exception as e:
            console.print(f"[red]Error showing stats: {e}[/red]")
            raise typer.Exit(1) from None

    handle()


@app.command("sidecar")
def manage_sidecar_files(
    action: str = typer.Argument(..., help="Action: sync, status, or clean"),
    show_paths: bool = typer.Option(False, "--paths", help="Show file paths"),
):
    """Manage .emb.gz sidecar embedding files."""

    @inject
    def handle(vector_store: VectorStore = inject.me()) -> None:
        """Handle the sidecar command."""
        try:
            if action == "sync":
                with console.status(
                    "[bold green]Syncing embeddings to sidecar files..."
                ):
                    result = vector_store.sync_sidecar_files()

                console.print(
                    f"[green]✓ Synced {result['created_files']} embedding files[/green]"
                )

                if result["errors"]:
                    console.print(
                        f"[yellow]⚠️  {len(result['errors'])} errors occurred:[/yellow]"
                    )
                    for error in result["errors"]:
                        console.print(f"[dim]  {error}[/dim]")

                if show_paths:
                    console.print("\n[cyan]Created files:[/cyan]")
                    for path in result["sidecar_paths"]:
                        console.print(f"[dim]  {path}[/dim]")

            elif action == "status":
                stats = vector_store.get_stats()
                metadata = vector_store.get_sidecar_metadata()
                sidecar_paths = vector_store.get_all_sidecar_paths()

                # Sidecar files table
                table = Table(title="Sidecar Embedding Files Status")
                table.add_column("Metric", style="cyan")
                table.add_column("Value", style="green")

                table.add_row("Total .emb.gz files", str(stats["sidecar_files"]))
                table.add_row("Metadata path", str(stats["metadata_path"]))
                table.add_row(
                    "Tracked in metadata", str(len(metadata.get("embeddings", {})))
                )

                if metadata.get("model"):
                    table.add_row("Embedding model", metadata["model"])
                if metadata.get("dimensions"):
                    table.add_row("Vector dimensions", str(metadata["dimensions"]))
                if metadata.get("compression"):
                    table.add_row("Compression", metadata["compression"])

                console.print(table)

                if show_paths:
                    console.print("\n[cyan]Sidecar file paths:[/cyan]")
                    for path in sidecar_paths:
                        size_kb = path.stat().st_size / 1024
                        console.print(f"[dim]  {path} ({size_kb:.1f} KB)[/dim]")

            elif action == "clean":
                # This would implement cleanup of orphaned sidecar files
                console.print("[yellow]Clean action not yet implemented[/yellow]")
                console.print(
                    "[dim]This would remove .emb.gz files that don't have corresponding YAML files[/dim]"
                )

            else:
                console.print(f"[red]Unknown action: {action}[/red]")
                console.print("[dim]Available actions: sync, status, clean[/dim]")
                raise typer.Exit(1)

        except Exception as e:
            console.print(f"[red]Error managing sidecar files: {e}[/red]")
            raise typer.Exit(1) from None

    handle()


@app.command("embed")
def embed_documents(
    store_type: str | None = typer.Option(
        None, "--type", "-t", help="Embed only specific store type"
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Re-embed existing documents"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be embedded without doing it"
    ),
):
    """Embed documents into the vector store for RAG."""

    @inject
    def handle(
        document_store: DocumentStore = inject.me(),
        embeddings_service: EmbeddingsService = inject.me(),
        vector_store: VectorStore = inject.me(),
    ) -> None:
        """Handle the embed command."""

        async def embed_async() -> None:
            try:
                all_docs = document_store.list_all_documents()

                # Filter by store type if specified
                if store_type:
                    if store_type not in all_docs:
                        console.print(f"[red]Invalid store type: {store_type}[/red]")
                        raise typer.Exit(1)
                    docs_to_process = {store_type: all_docs[store_type]}
                else:
                    docs_to_process = all_docs

                total_docs = sum(len(docs) for docs in docs_to_process.values())

                if total_docs == 0:
                    console.print("[yellow]No documents found to embed.[/yellow]")
                    return

                console.print(
                    f"[cyan]Processing {total_docs} documents for embedding...[/cyan]"
                )

                processed = 0
                skipped = 0
                errors = 0

                for store_name, doc_ids in docs_to_process.items():
                    for doc_id in doc_ids:
                        try:
                            # Check if already embedded (unless force)
                            vector_doc_id = f"{store_name}.{doc_id}"
                            existing = vector_store.get_document(vector_doc_id)

                            if existing and not force:
                                console.print(
                                    f"  [dim]Skipping {store_name}/{doc_id} (already embedded)[/dim]"
                                )
                                skipped += 1
                                continue

                            if dry_run:
                                console.print(
                                    f"  [blue]Would embed {store_name}/{doc_id}[/blue]"
                                )
                                processed += 1
                                continue

                            # Load document data
                            if store_name == "github.orgs":
                                doc = document_store.github_orgs.load(doc_id)
                                doc_data = doc.model_dump()
                            elif store_name == "github.repos":
                                doc = document_store.github_repos.load(doc_id)
                                doc_data = doc.model_dump()
                            elif store_name == "goldentooth.nodes":
                                doc = document_store.goldentooth_nodes.load(doc_id)
                                doc_data = doc.model_dump()
                            elif store_name == "goldentooth.services":
                                doc = document_store.goldentooth_services.load(doc_id)
                                doc_data = doc.model_dump()
                            elif store_name == "notes":
                                doc = document_store.notes.load(doc_id)
                                doc_data = doc.model_dump()
                            else:
                                console.print(
                                    f"  [red]Unknown store type: {store_name}[/red]"
                                )
                                errors += 1
                                continue

                            # Create embedding
                            console.print(
                                f"  [green]Embedding {store_name}/{doc_id}...[/green]"
                            )
                            embedding_result = (
                                await embeddings_service.create_document_embedding(
                                    doc_data
                                )
                            )

                            # Store in vector database
                            vector_store.store_document(
                                store_name,
                                doc_id,
                                embedding_result["text_content"],
                                embedding_result["embedding"],
                                embedding_result["metadata"],
                            )

                            processed += 1

                        except Exception as e:
                            console.print(
                                f"  [red]Error embedding {store_name}/{doc_id}: {e}[/red]"
                            )
                            errors += 1

                # Summary
                console.print("\n[cyan]Embedding complete:[/cyan]")
                console.print(f"  Processed: {processed}")
                console.print(f"  Skipped: {skipped}")
                console.print(f"  Errors: {errors}")

                if dry_run:
                    console.print(
                        "\n[blue]This was a dry run. Use --force to actually embed documents.[/blue]"
                    )

            except Exception as e:
                console.print(f"[red]Error during embedding: {e}[/red]")
                raise typer.Exit(1) from None

        # Run the async embedding process
        asyncio.run(embed_async())

    handle()


@app.command("search")
def search_documents(
    query: str = typer.Argument(..., help="Search query"),
    limit: int = typer.Option(5, "--limit", "-l", help="Maximum number of results"),
    store_type: str | None = typer.Option(
        None, "--type", "-t", help="Filter by store type"
    ),
):
    """Search documents using semantic similarity."""

    @inject
    def handle(
        embeddings_service: EmbeddingsService = inject.me(),
        vector_store: VectorStore = inject.me(),
    ) -> None:
        """Handle the search command."""

        async def search_async() -> None:
            try:
                console.print(f"[cyan]Searching for: '{query}'[/cyan]")

                # Create embedding for query
                query_embedding = await embeddings_service.create_embedding(query)

                # Search for similar documents
                results = vector_store.search_similar(
                    query_embedding, limit=limit, store_type=store_type
                )

                if not results:
                    console.print("[yellow]No similar documents found.[/yellow]")
                    return

                # Display results
                table = Table(title=f"Search Results for '{query}'")
                table.add_column("Score", style="green")
                table.add_column("Document", style="cyan")
                table.add_column("Preview", style="dim")

                for result in results:
                    score = f"{result['similarity_score']:.3f}"
                    doc_ref = f"{result['store_type']}/{result['document_id']}"
                    preview = result["content_preview"][:100]
                    if len(result["content_preview"]) > 100:
                        preview += "..."

                    table.add_row(score, doc_ref, preview)

                console.print(table)

            except Exception as e:
                console.print(f"[red]Error during search: {e}[/red]")
                raise typer.Exit(1) from None

        # Run the async search process
        asyncio.run(search_async())

    handle()


@app.command("ask")
def ask_question(
    question: str = typer.Argument(
        ..., help="Question to ask about the knowledge base"
    ),
    max_results: int = typer.Option(
        5, "--max-results", "-m", help="Maximum documents to retrieve"
    ),
    store_type: str | None = typer.Option(
        None, "--type", "-t", help="Filter by store type"
    ),
    threshold: float = typer.Option(
        0.1, "--threshold", help="Similarity threshold (0.0-1.0)"
    ),
    show_sources: bool = typer.Option(
        True, "--show-sources/--no-sources", help="Show source documents"
    ),
):
    """Ask a question and get an AI-powered answer using RAG."""

    @inject
    def handle(rag_service: RAGService = inject.me()) -> None:
        """Handle the ask command."""

        async def ask_async() -> None:
            try:
                console.print(f"[cyan]Question: {question}[/cyan]\n")

                with console.status("[bold green]Thinking..."):
                    result = await rag_service.query(
                        question=question,
                        max_results=max_results,
                        store_type=store_type,
                        include_metadata=show_sources,
                        similarity_threshold=threshold,
                    )

                # Display the answer
                console.print("[bold green]Answer:[/bold green]")
                console.print(result["answer"])

                # Display sources if requested
                if show_sources and result["retrieved_documents"]:
                    console.print(
                        f"\n[cyan]Sources ({len(result['retrieved_documents'])} documents):[/cyan]"
                    )

                    for i, doc in enumerate(result["retrieved_documents"], 1):
                        score = doc["similarity_score"]
                        doc_ref = f"{doc['store_type']}/{doc['document_id']}"
                        preview = doc["content_preview"][:100]
                        if len(doc["content_preview"]) > 100:
                            preview += "..."

                        console.print(
                            f"  {i}. [dim]{doc_ref}[/dim] (score: {score:.3f})"
                        )
                        console.print(f"     {preview}")

                # Display metadata
                metadata = result["metadata"]
                if not metadata.get("error"):
                    console.print(
                        f"\n[dim]Retrieved {metadata['documents_found']} documents, used {metadata['documents_used']}[/dim]"
                    )

            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                raise typer.Exit(1) from None

        # Run the async ask process
        asyncio.run(ask_async())

    handle()


@app.command("summarize")
def summarize_knowledge_base(
    store_type: str | None = typer.Option(
        None, "--type", "-t", help="Summarize specific store type"
    ),
    max_docs: int = typer.Option(20, "--max-docs", help="Maximum documents to analyze"),
):
    """Generate an AI summary of the knowledge base contents."""

    @inject
    def handle(rag_service: RAGService = inject.me()) -> None:
        """Handle the summarize command."""

        async def summarize_async() -> None:
            try:
                with console.status("[bold green]Analyzing knowledge base..."):
                    result = await rag_service.summarize_documents(
                        store_type=store_type,
                        max_documents=max_docs,
                    )

                if result["metadata"].get("error"):
                    console.print(f"[red]Error: {result['summary']}[/red]")
                    raise typer.Exit(1)

                # Display the summary
                console.print("[bold green]Knowledge Base Summary:[/bold green]")
                console.print(result["summary"])

                # Display metadata
                metadata = result["metadata"]
                console.print(
                    f"\n[dim]Analyzed {metadata['documents_analyzed']} documents[/dim]"
                )
                if store_type:
                    console.print(f"[dim]Store type: {store_type}[/dim]")

            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                raise typer.Exit(1) from None

        # Run the async summarize process
        asyncio.run(summarize_async())

    handle()


@app.command("insights")
def get_document_insights(
    store_type: str = typer.Argument(
        ..., help="Store type (e.g., github.repos, notes)"
    ),
    document_id: str = typer.Argument(..., help="Document ID"),
):
    """Get AI-generated insights about a specific document."""

    @inject
    def handle(rag_service: RAGService = inject.me()) -> None:
        """Handle the insights command."""

        async def insights_async() -> None:
            try:
                with console.status(
                    f"[bold green]Analyzing {store_type}/{document_id}..."
                ):
                    result = await rag_service.get_document_insights(
                        document_id, store_type
                    )

                if result["metadata"].get("error"):
                    console.print(f"[red]Error: {result['insights']}[/red]")
                    raise typer.Exit(1)

                # Display the insights
                console.print(
                    f"[bold green]Insights for {store_type}/{document_id}:[/bold green]"
                )
                console.print(result["insights"])

                # Display metadata
                metadata = result["metadata"]
                if "content_length" in metadata:
                    console.print(
                        f"\n[dim]Document size: {metadata['content_length']} characters[/dim]"
                    )

            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                raise typer.Exit(1) from None

        # Run the async insights process
        asyncio.run(insights_async())

    handle()
