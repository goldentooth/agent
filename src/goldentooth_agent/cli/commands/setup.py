"""Setup and initialization CLI commands."""

import asyncio
from typing import Optional

import typer
from antidote import inject
from rich.console import Console

from ...core.document_store import DocumentStore
from ...core.embeddings import EmbeddingsService, VectorStore
from ...core.paths import Paths
from ...core.sample_data import install_sample_data

app = typer.Typer()
console = Console()


@app.command("init")
def initialize_system(
    sample_data: bool = typer.Option(True, "--sample-data/--no-sample-data", help="Install sample data"),
    embed: bool = typer.Option(True, "--embed/--no-embed", help="Embed sample data after installation"),
):
    """Initialize the Goldentooth Agent system with sample data."""
    
    @inject
    def handle(
        paths: Paths = inject.me(),
        document_store: DocumentStore = inject.me(),
        embeddings_service: EmbeddingsService = inject.me(),
        vector_store: VectorStore = inject.me(),
    ) -> None:
        """Handle the init command."""
        try:
            console.print("[bold green]Initializing Goldentooth Agent system...[/bold green]")
            
            # Show data directory info
            data_dir = paths.data()
            console.print(f"[cyan]Data directory: {data_dir}[/cyan]")
            
            if sample_data:
                console.print("[cyan]Installing sample data...[/cyan]")
                with console.status("[bold green]Installing sample documents..."):
                    result = install_sample_data(paths)
                
                if result["success"]:
                    console.print(f"[green]✓ Installed {result['total_installed']} sample documents[/green]")
                    for store_type, count in result["installed_counts"].items():
                        if count > 0:
                            console.print(f"  [dim]{store_type}: {count} documents[/dim]")
                else:
                    console.print(f"[red]Error installing sample data: {result.get('error', 'Unknown error')}[/red]")
                    raise typer.Exit(1)
                
                # Embed sample data if requested
                if embed and result["total_installed"] > 0:
                    console.print("[cyan]Embedding sample documents...[/cyan]")
                    
                    async def embed_all_sample_data():
                        embedded_count = 0
                        
                        # Embed GitHub organizations
                        for org_id in document_store.github_orgs.list():
                            try:
                                org_doc = document_store.github_orgs.load(org_id)
                                org_embedding = await embeddings_service.create_document_embedding(
                                    org_doc.model_dump()
                                )
                                vector_store.store_document(
                                    "github.orgs",
                                    org_id,
                                    org_embedding["text_content"],
                                    org_embedding["embedding"],
                                    org_embedding["metadata"]
                                )
                                embedded_count += 1
                            except Exception as e:
                                console.print(f"[yellow]Warning: Could not embed org {org_id}: {e}[/yellow]")
                        
                        # Embed GitHub repositories
                        for repo_id in document_store.github_repos.list():
                            try:
                                repo_doc = document_store.github_repos.load(repo_id)
                                repo_embedding = await embeddings_service.create_document_embedding(
                                    repo_doc.model_dump()
                                )
                                vector_store.store_document(
                                    "github.repos",
                                    repo_id,
                                    repo_embedding["text_content"],
                                    repo_embedding["embedding"],
                                    repo_embedding["metadata"]
                                )
                                embedded_count += 1
                            except Exception as e:
                                console.print(f"[yellow]Warning: Could not embed repo {repo_id}: {e}[/yellow]")
                        
                        # Embed notes
                        for note_id in document_store.notes.list():
                            try:
                                note_doc = document_store.notes.load(note_id)
                                note_embedding = await embeddings_service.create_document_embedding(
                                    note_doc.model_dump()
                                )
                                vector_store.store_document(
                                    "notes",
                                    note_id,
                                    note_embedding["text_content"],
                                    note_embedding["embedding"],
                                    note_embedding["metadata"]
                                )
                                embedded_count += 1
                            except Exception as e:
                                console.print(f"[yellow]Warning: Could not embed note {note_id}: {e}[/yellow]")
                        
                        return embedded_count
                    
                    try:
                        with console.status("[bold green]Creating embeddings..."):
                            embedded_count = asyncio.run(embed_all_sample_data())
                        console.print(f"[green]✓ Embedded {embedded_count} documents[/green]")
                    except Exception as e:
                        console.print(f"[yellow]Warning: Embedding failed: {e}[/yellow]")
            
            # Show final status
            console.print("\n[bold green]🎉 System initialization complete![/bold green]")
            console.print("\n[dim]Try these commands to explore:[/dim]")
            console.print("[dim]  goldentooth-agent docs stats[/dim]")
            console.print("[dim]  goldentooth-agent docs ask \"What repositories are available?\"[/dim]")
            console.print("[dim]  goldentooth-agent docs summarize[/dim]")
        
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)
    
    handle()


@app.command("status")  
def show_system_status():
    """Show overall system status and configuration."""
    
    @inject
    def handle(
        paths: Paths = inject.me(),
        document_store: DocumentStore = inject.me(),
        vector_store: VectorStore = inject.me(),
    ) -> None:
        """Handle the status command."""
        try:
            from rich.table import Table
            
            # System info
            console.print("[bold green]Goldentooth Agent System Status[/bold green]\n")
            
            # Paths table
            paths_table = Table(title="System Paths")
            paths_table.add_column("Type", style="cyan")
            paths_table.add_column("Path", style="green")
            paths_table.add_column("Exists", style="dim")
            
            data_dir = paths.data()
            config_dir = paths.config()
            cache_dir = paths.cache()
            
            paths_table.add_row("Data", str(data_dir), "✓" if data_dir.exists() else "✗")
            paths_table.add_row("Config", str(config_dir), "✓" if config_dir.exists() else "✗")
            paths_table.add_row("Cache", str(cache_dir), "✓" if cache_dir.exists() else "✗")
            
            console.print(paths_table)
            
            # Document counts
            doc_counts = document_store.get_document_count()
            total_docs = sum(doc_counts.values())
            
            docs_table = Table(title="Document Store")
            docs_table.add_column("Store Type", style="cyan")
            docs_table.add_column("Documents", style="green")
            
            for store_type, count in doc_counts.items():
                docs_table.add_row(store_type, str(count))
            docs_table.add_row("[bold]Total[/bold]", f"[bold]{total_docs}[/bold]")
            
            console.print(docs_table)
            
            # Vector store stats
            vector_stats = vector_store.get_stats()
            
            vector_table = Table(title="Vector Store")
            vector_table.add_column("Metric", style="cyan")
            vector_table.add_column("Value", style="green")
            
            vector_table.add_row("Embeddings", str(vector_stats["total_documents"]))
            vector_table.add_row("Engine", vector_stats["embedding_engine"])
            
            console.print(vector_table)
            
            # Status summary
            if total_docs == 0:
                console.print("\n[yellow]💡 No documents found. Run 'goldentooth-agent setup init' to get started.[/yellow]")
            elif vector_stats["total_documents"] == 0:
                console.print("\n[yellow]💡 Documents found but not embedded. Run 'goldentooth-agent docs embed' to enable RAG queries.[/yellow]")
            else:
                console.print(f"\n[green]✓ System ready with {total_docs} documents and {vector_stats['total_documents']} embeddings[/green]")
        
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)
    
    handle()