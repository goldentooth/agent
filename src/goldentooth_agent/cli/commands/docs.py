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
                "Total Documents", str(vector_stats["total_documents"])
            )
            vector_table.add_row("Total Chunks", str(vector_stats["total_chunks"]))
            vector_table.add_row("Embedding Engine", vector_stats["embedding_engine"])
            vector_table.add_row("Database Path", vector_stats["database_path"])
            vector_table.add_row("Sidecar Files", str(vector_stats["sidecar_files"]))

            # Add embedding counts
            if "embedding_counts" in vector_stats:
                embedding_counts = vector_stats["embedding_counts"]
                vector_table.add_row(
                    "Document Embeddings", str(embedding_counts.get("documents", 0))
                )
                vector_table.add_row(
                    "Chunk Embeddings", str(embedding_counts.get("chunks", 0))
                )

            console.print(vector_table)

            # Chunk statistics table if there are chunks
            if vector_stats["total_chunks"] > 0:
                chunk_table = Table(title="Chunk Statistics")
                chunk_table.add_column("Store Type", style="cyan")
                chunk_table.add_column("Chunks", style="green")

                for store_type, count in vector_stats.get(
                    "chunks_by_store_type", {}
                ).items():
                    chunk_table.add_row(store_type, str(count))

                console.print(chunk_table)

                # Chunk type distribution
                if vector_stats.get("chunks_by_type"):
                    chunk_type_table = Table(title="Chunk Type Distribution")
                    chunk_type_table.add_column("Chunk Type", style="cyan")
                    chunk_type_table.add_column("Count", style="green")

                    for chunk_type, count in vector_stats["chunks_by_type"].items():
                        chunk_type_table.add_row(chunk_type, str(count))

                    console.print(chunk_type_table)

        except Exception as e:
            console.print(f"[red]Error showing stats: {e}[/red]")
            raise typer.Exit(1) from None

    handle()


@app.command("chunks")
def show_document_chunks(
    store_type: str = typer.Argument(
        ..., help="Store type (e.g., github.repos, notes)"
    ),
    document_id: str = typer.Argument(..., help="Document ID"),
    show_content: bool = typer.Option(
        False, "--content", help="Show full content of each chunk"
    ),
):
    """Show chunk information for a specific document."""

    @inject
    def handle(rag_service: RAGService = inject.me()) -> None:
        """Handle the chunks command."""

        async def chunks_async() -> None:
            try:
                with console.status(
                    f"[bold green]Getting chunks for {store_type}/{document_id}..."
                ):
                    result = await rag_service.get_document_chunks_info(
                        document_id, store_type
                    )

                if result.get("error"):
                    console.print(f"[red]Error: {result['message']}[/red]")
                    raise typer.Exit(1)

                # Display chunk information
                console.print(
                    f"[bold green]Chunks for {store_type}/{document_id}:[/bold green]"
                )

                if result["total_chunks"] == 0:
                    console.print(f"[yellow]{result['message']}[/yellow]")
                    return

                # Summary information
                console.print(
                    f"[cyan]Total chunks: {result['total_chunks']} | "
                    f"Total characters: {result['total_characters']}[/cyan]"
                )

                # Chunk type distribution
                if result["chunk_types"]:
                    type_str = ", ".join(
                        f"{ctype}({count})"
                        for ctype, count in result["chunk_types"].items()
                    )
                    console.print(f"[dim]Chunk types: {type_str}[/dim]")

                console.print()

                # Display each chunk
                chunks_table = Table()
                chunks_table.add_column("Index", style="blue")
                chunks_table.add_column("Type", style="cyan")
                chunks_table.add_column("Title", style="green")
                chunks_table.add_column("Size", style="yellow")
                if show_content:
                    chunks_table.add_column("Content", style="dim", max_width=50)

                for chunk in result["chunks"]:
                    content_preview = ""
                    if show_content:
                        content = chunk["content"]
                        content_preview = (
                            content[:100] + "..." if len(content) > 100 else content
                        )

                    row_data = [
                        str(chunk["chunk_index"]),
                        chunk["chunk_type"],
                        chunk["title"] or "[dim]No title[/dim]",
                        f"{chunk['size_chars']} chars",
                    ]

                    if show_content:
                        row_data.append(content_preview)

                    chunks_table.add_row(*row_data)

                console.print(chunks_table)

            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                raise typer.Exit(1) from None

        # Run the async process
        asyncio.run(chunks_async())

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
    use_chunks: bool = typer.Option(
        True, "--chunks/--no-chunks", help="Use intelligent chunking for documents"
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
                    f"[cyan]Processing {total_docs} documents for embedding{'with chunking' if use_chunks else ''}...[/cyan]"
                )

                processed = 0
                skipped = 0
                errors = 0
                total_chunks_created = 0

                for store_name, doc_ids in docs_to_process.items():
                    for doc_id in doc_ids:
                        try:
                            # Check if already embedded (unless force)
                            vector_doc_id = f"{store_name}.{doc_id}"
                            existing = vector_store.get_document(vector_doc_id)
                            existing_chunks = vector_store.get_document_chunks(
                                store_name, doc_id
                            )

                            if (existing or existing_chunks) and not force:
                                console.print(
                                    f"  [dim]Skipping {store_name}/{doc_id} (already embedded)[/dim]"
                                )
                                skipped += 1
                                continue

                            if dry_run:
                                action = "chunk and embed" if use_chunks else "embed"
                                console.print(
                                    f"  [blue]Would {action} {store_name}/{doc_id}[/blue]"
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

                            # Decide whether to use chunking
                            should_chunk = (
                                use_chunks
                                and embeddings_service.should_use_chunking(
                                    store_name, doc_data
                                )
                            )

                            if should_chunk:
                                # Use chunking approach
                                console.print(
                                    f"  [green]Chunking and embedding {store_name}/{doc_id}...[/green]"
                                )

                                # Delete any existing chunks first
                                vector_store.delete_document_chunks(store_name, doc_id)

                                # Create chunks and embeddings
                                chunk_result = await embeddings_service.create_document_chunks_with_embeddings(
                                    store_name, doc_id, doc_data
                                )

                                # Store chunks in vector database
                                stored_chunk_ids = vector_store.store_document_chunks(
                                    store_name,
                                    doc_id,
                                    chunk_result["chunks"],
                                    chunk_result["embeddings"],
                                    chunk_result["metadata"],
                                )

                                total_chunks_created += len(stored_chunk_ids)
                                console.print(
                                    f"    [dim]Created {len(stored_chunk_ids)} chunks[/dim]"
                                )
                            else:
                                # Use traditional full-document embedding
                                console.print(
                                    f"  [green]Embedding {store_name}/{doc_id} (full document)...[/green]"
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
                if total_chunks_created > 0:
                    console.print(f"  Chunks created: {total_chunks_created}")

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
                table.add_column("Type", style="blue")
                table.add_column("Preview", style="dim")

                for result in results:
                    score = f"{result['similarity_score']:.3f}"
                    doc_ref = f"{result['store_type']}/{result['document_id']}"

                    # Add chunk information if this is a chunk
                    if result.get("is_chunk", False):
                        chunk_type = result.get("chunk_type", "unknown")
                        chunk_title = result.get("chunk_title", "")
                        doc_ref += f"#{result.get('chunk_id', 'unknown')}"
                        type_info = f"Chunk ({chunk_type})"
                        if chunk_title:
                            type_info += f": {chunk_title}"
                    else:
                        type_info = "Document"

                    preview = result["content_preview"][:100]
                    if len(result["content_preview"]) > 100:
                        preview += "..."

                    table.add_row(score, doc_ref, type_info, preview)

                console.print(table)

            except Exception as e:
                console.print(f"[red]Error during search: {e}[/red]")
                raise typer.Exit(1) from None

        # Run the async search process
        asyncio.run(search_async())

    handle()


@app.command("chunk-search")
def search_chunks_by_type(
    chunk_types: str = typer.Argument(
        ...,
        help="Chunk types to search for (comma-separated, e.g., 'repo_core,note_section')",
    ),
    question: str | None = typer.Option(
        None,
        "--question",
        "-q",
        help="Optional question for semantic similarity search",
    ),
    max_results: int = typer.Option(
        10, "--max-results", "-m", help="Maximum number of chunks to return"
    ),
    store_type: str | None = typer.Option(
        None, "--type", "-t", help="Filter by store type"
    ),
):
    """Search for chunks of specific types, optionally with semantic similarity."""

    @inject
    def handle(rag_service: RAGService = inject.me()) -> None:
        """Handle the chunk-search command."""

        async def chunk_search_async() -> None:
            try:
                # Parse chunk types
                parsed_chunk_types = [ct.strip() for ct in chunk_types.split(",")]
                console.print(
                    f"[cyan]Searching for chunk types: {', '.join(parsed_chunk_types)}[/cyan]"
                )

                if question:
                    console.print(f"[cyan]Question: {question}[/cyan]")

                with console.status("[bold green]Searching chunks..."):
                    result = await rag_service.search_chunks_by_type(
                        chunk_types=parsed_chunk_types,
                        question=question,
                        max_results=max_results,
                        store_type=store_type,
                    )

                if result.get("error"):
                    console.print(f"[red]Error: {result['error_message']}[/red]")
                    raise typer.Exit(1)

                # Display results
                chunks = result["chunks"]
                if not chunks:
                    console.print(
                        f"[yellow]No chunks found for types: {', '.join(parsed_chunk_types)}[/yellow]"
                    )
                    if result.get("message"):
                        console.print(f"[dim]{result['message']}[/dim]")
                    return

                console.print(f"[green]Found {result['total_found']} chunks[/green]")
                console.print(f"[dim]Search method: {result['search_method']}[/dim]\n")

                # Display chunks in a table
                table = Table(title=f"Chunks of Type: {', '.join(parsed_chunk_types)}")
                table.add_column("Score", style="green")
                table.add_column("Document", style="cyan")
                table.add_column("Chunk", style="blue")
                table.add_column("Title", style="yellow")
                table.add_column("Preview", style="dim")

                for chunk in chunks:
                    score = f"{chunk['similarity_score']:.3f}" if question else "N/A"
                    doc_ref = f"{chunk['store_type']}/{chunk['document_id']}"
                    chunk_ref = f"#{chunk.get('chunk_id', 'unknown')}"
                    chunk_title = chunk.get("chunk_title", "Untitled")

                    preview = chunk.get("content", "")[:100]
                    if len(chunk.get("content", "")) > 100:
                        preview += "..."

                    table.add_row(score, doc_ref, chunk_ref, chunk_title, preview)

                console.print(table)

            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                raise typer.Exit(1) from None

        # Run the async search process
        asyncio.run(chunk_search_async())

    handle()


@app.command("chunk-summary")
def show_chunk_summary(
    store_type: str = typer.Argument(
        ..., help="Store type (e.g., github.repos, notes)"
    ),
    document_id: str = typer.Argument(..., help="Document ID"),
    show_previews: bool = typer.Option(
        False, "--previews", help="Show content previews for each chunk"
    ),
):
    """Get a detailed summary of all chunks for a specific document."""

    @inject
    def handle(rag_service: RAGService = inject.me()) -> None:
        """Handle the chunk-summary command."""

        async def chunk_summary_async() -> None:
            try:
                with console.status(
                    f"[bold green]Getting chunk summary for {store_type}/{document_id}..."
                ):
                    result = await rag_service.get_document_chunk_summary(
                        store_type=store_type,
                        document_id=document_id,
                        include_content_preview=show_previews,
                    )

                if result.get("error"):
                    console.print(f"[red]Error: {result['error_message']}[/red]")
                    raise typer.Exit(1)

                # Display summary
                console.print(
                    f"[bold green]Chunk Summary for {store_type}/{document_id}:[/bold green]"
                )

                if not result["has_chunks"]:
                    console.print(
                        f"[yellow]{result.get('message', 'No chunks available')}[/yellow]"
                    )
                    return

                # Overview statistics
                console.print(f"[cyan]Total chunks: {result['total_chunks']}[/cyan]")
                console.print(
                    f"[cyan]Total characters: {result['total_characters']}[/cyan]"
                )
                console.print(
                    f"[cyan]Average chunk size: {result['avg_chunk_size']} chars[/cyan]"
                )

                # Chunk type distribution
                if result["chunk_types"]:
                    type_distribution = ", ".join(
                        f"{ctype}({count})"
                        for ctype, count in result["chunk_types"].items()
                    )
                    console.print(f"[dim]Chunk types: {type_distribution}[/dim]")

                console.print()

                # Detailed chunk list
                table = Table()
                table.add_column("Index", style="blue")
                table.add_column("Type", style="cyan")
                table.add_column("ID", style="yellow")
                table.add_column("Title", style="green")
                table.add_column("Size", style="magenta")
                if show_previews:
                    table.add_column("Preview", style="dim", max_width=40)

                for chunk in result["chunks"]:
                    row_data = [
                        str(chunk["chunk_index"]),
                        chunk["chunk_type"],
                        chunk["chunk_id"].split(".")[
                            -1
                        ],  # Show just the last part of ID
                        chunk["title"] or "[dim]No title[/dim]",
                        f"{chunk['size_chars']} chars",
                    ]

                    if show_previews and "content_preview" in chunk:
                        row_data.append(chunk["content_preview"])

                    table.add_row(*row_data)

                console.print(table)

            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                raise typer.Exit(1) from None

        # Run the async process
        asyncio.run(chunk_summary_async())

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
        0.01, "--threshold", help="Similarity threshold (0.0-1.0)"
    ),
    show_sources: bool = typer.Option(
        True, "--show-sources/--no-sources", help="Show source documents"
    ),
    chunk_types: str | None = typer.Option(
        None,
        "--chunk-types",
        help="Filter to specific chunk types (comma-separated, e.g., 'repo_core,note_section')",
    ),
    prioritize_chunks: bool = typer.Option(
        False,
        "--prioritize-chunks",
        help="Prioritize chunks over full documents in ranking",
    ),
):
    """Ask a question and get an AI-powered answer using RAG."""

    @inject
    def handle(rag_service: RAGService = inject.me()) -> None:
        """Handle the ask command."""

        async def ask_async() -> None:
            try:
                console.print(f"[cyan]Question: {question}[/cyan]\n")

                # Parse chunk types if provided
                parsed_chunk_types = None
                if chunk_types:
                    parsed_chunk_types = [ct.strip() for ct in chunk_types.split(",")]
                    console.print(
                        f"[dim]Filtering to chunk types: {', '.join(parsed_chunk_types)}[/dim]"
                    )

                if prioritize_chunks:
                    console.print("[dim]Prioritizing chunks over full documents[/dim]")

                with console.status("[bold green]Thinking..."):
                    result = await rag_service.query(
                        question=question,
                        max_results=max_results,
                        store_type=store_type,
                        include_metadata=show_sources,
                        similarity_threshold=threshold,
                        chunk_types=parsed_chunk_types,
                        prioritize_chunks=prioritize_chunks,
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

                        # Add chunk information if this is a chunk
                        if doc.get("is_chunk", False):
                            chunk_type = doc.get("chunk_type", "unknown")
                            chunk_title = doc.get("chunk_title", "")
                            doc_ref += f"#{doc.get('chunk_id', 'unknown')}"
                            chunk_info = f" ({chunk_type}"
                            if chunk_title:
                                chunk_info += f": {chunk_title}"
                            chunk_info += ")"
                            doc_ref += chunk_info

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
                    info_parts = [
                        f"Retrieved {metadata['documents_found']} documents, used {metadata['documents_used']}"
                    ]

                    if metadata.get("chunks_used", 0) > 0:
                        info_parts.append(f"chunks: {metadata['chunks_used']}")
                    if metadata.get("full_docs_used", 0) > 0:
                        info_parts.append(f"full docs: {metadata['full_docs_used']}")

                    if metadata.get("chunk_types_found"):
                        chunk_types_str = ", ".join(metadata["chunk_types_found"])
                        info_parts.append(f"chunk types: {chunk_types_str}")

                    console.print(f"\n[dim]{', '.join(info_parts)}[/dim]")

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
