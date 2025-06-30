"""
CLI commands for codebase introspection and analysis.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

import typer
from antidote import world
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from goldentooth_agent.core.agent_codebase import (
    CodebaseDocumentType,
    CodebaseIntrospectionService,
    IntrospectionQuery,
)
from goldentooth_agent.core.agent_codebase.rag_integration import (
    CodebaseRAGIntegration,
    CodebaseRAGQuery,
)

app = typer.Typer(name="codebase", help="Codebase introspection and analysis commands")
console = Console()


@app.command("index")
def index_codebase(
    codebase_name: str | None = typer.Argument(
        None, help="Codebase name (default: goldentooth_agent)"
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Force full re-indexing (ignores change detection)"
    ),
) -> None:
    """
    Index a codebase for introspection queries.

    Mechanically, this:
    1. Extracts documents from Python files using AST parsing
    2. Processes README.md and README.bg.md files
    3. Chunks content based on document types
    4. Generates embeddings and stores in vector database
    5. Updates indexing statistics
    """

    async def _index() -> None:
        introspection_service = world.get(CodebaseIntrospectionService)

        if codebase_name:
            # Index specific codebase (assumes it's already added)
            result = await introspection_service.collection.index_codebase(
                codebase_name, force_full_reindex=force
            )
        else:
            # Index current codebase
            if force:
                result = await introspection_service.collection.index_codebase(
                    "goldentooth_agent", force_full_reindex=True
                )
            else:
                result = await introspection_service.index_current_codebase()

        # Enhanced stats display with change detection info
        stats_text = (
            f"✅ Indexing completed!\n\n"
            f"📊 **Statistics:**\n"
            f"• Documents total: {result.get('documents_total', result.get('documents_processed', 0))}\n"
            f"• Documents processed: {result.get('documents_processed', 0)}\n"
            f"• Documents skipped: {result.get('documents_skipped', 0)}\n"
            f"• Chunks created: {result['chunks_created']}\n"
            f"• Total lines: {result['total_lines']}\n"
            f"• Codebase: {result['codebase_name']}"
        )

        # Add change detection stats if available
        if "change_detection_stats" in result:
            cd_stats = result["change_detection_stats"]
            stats_text += (
                f"\n\n💡 **Change Detection:**\n"
                f"• Total fingerprints: {cd_stats.get('total_documents', 0)}\n"
                f"• Stale docs removed: {result.get('stale_documents_removed', 0)}"
            )

        # Add token usage stats if available
        if "token_usage" in result:
            token_stats = result["token_usage"]
            budget_status = result.get("budget_status", {})

            stats_text += (
                f"\n\n💰 **Token Usage:**\n"
                f"• Tokens used: {token_stats.get('tokens_used', 0):,}\n"
                f"• Estimated cost: ${token_stats.get('estimated_cost_usd', 0):.4f}\n"
                f"• Tokens saved: {token_stats.get('tokens_saved', 0):,}\n"
                f"• Cost saved: ${token_stats.get('cost_saved_usd', 0):.4f}\n"
                f"• Cache hit rate: {token_stats.get('cache_hit_rate', 0):.1%}"
            )

            # Add budget warnings
            warnings = budget_status.get("warnings", [])
            if warnings:
                stats_text += "\n\n⚠️ **Budget Warnings:**\n" + "\n".join(
                    f"• {w}" for w in warnings
                )

        console.print(Panel.fit(stats_text, title="🔍 Codebase Indexing"))

    asyncio.run(_index())


@app.command("query")
def query_codebase(
    query: str = typer.Argument(..., help="Query to search for in the codebase"),
    limit: int = typer.Option(5, "--limit", "-l", help="Maximum number of results"),
    doc_type: str | None = typer.Option(
        None, "--type", "-t", help="Document type filter"
    ),
    include_source: bool = typer.Option(
        True, "--source/--no-source", help="Include source code"
    ),
    format_output: str = typer.Option(
        "rich", "--format", "-f", help="Output format (rich, json)"
    ),
) -> None:
    """
    Query the codebase using natural language.

    Mechanical query process:
    1. Parse query intent to determine search strategy
    2. Route to appropriate document types
    3. Perform vector similarity search
    4. Rank results by relevance
    5. Display formatted results
    """

    async def _query() -> None:
        introspection_service = world.get(CodebaseIntrospectionService)

        # Build query
        document_types = None
        if doc_type:
            try:
                document_types = [CodebaseDocumentType(doc_type)]
            except ValueError:
                console.print(f"❌ Invalid document type: {doc_type}")
                console.print(
                    f"Valid types: {', '.join([t.value for t in CodebaseDocumentType])}"
                )
                return

        introspection_query = IntrospectionQuery(
            query=query,
            limit=limit,
            document_types=document_types,
            include_source=include_source,
        )

        # Execute query
        with console.status("🔍 Searching codebase..."):
            result = await introspection_service.query(introspection_query)

        # Display results
        if format_output == "json":
            console.print(json.dumps(result.model_dump(), indent=2))
        else:
            _display_query_results(result)

    asyncio.run(_query())


@app.command("rag")
def rag_query(
    query: str = typer.Argument(..., help="Query combining codebase and documents"),
    codebase_weight: float = typer.Option(
        0.6, "--codebase-weight", "-w", help="Weight for codebase results (0-1)"
    ),
    max_results: int = typer.Option(
        10, "--max-results", "-m", help="Maximum total results"
    ),
    include_codebase: bool = typer.Option(
        True, "--codebase/--no-codebase", help="Include codebase search"
    ),
    include_documents: bool = typer.Option(
        True, "--docs/--no-docs", help="Include document search"
    ),
) -> None:
    """
    Query using combined codebase introspection and document RAG.

    Mechanical RAG process:
    1. Execute parallel searches in codebase and document store
    2. Combine results with weighted scoring
    3. Synthesize comprehensive answer using LLM
    4. Display unified response with source attribution
    """

    async def _rag_query() -> None:
        rag_integration = world.get(CodebaseRAGIntegration)

        rag_query_obj = CodebaseRAGQuery(
            query=query,
            include_codebase=include_codebase,
            include_documents=include_documents,
            codebase_weight=codebase_weight,
            max_results=max_results,
        )

        # Execute combined query
        with console.status("🧠 Processing RAG query..."):
            result = await rag_integration.query(rag_query_obj)

        # Display comprehensive result
        _display_rag_results(result)

    asyncio.run(_rag_query())


@app.command("overview")
def codebase_overview(
    codebase_name: str = typer.Option(
        "goldentooth_agent", "--codebase", "-c", help="Codebase name"
    )
) -> None:
    """Get comprehensive overview of a codebase."""

    async def _overview() -> None:
        introspection_service = world.get(CodebaseIntrospectionService)

        with console.status("📊 Generating codebase overview..."):
            overview = await introspection_service.get_codebase_overview(codebase_name)

        _display_codebase_overview(overview)

    asyncio.run(_overview())


@app.command("compare")
def compare_codebases(
    query: str = typer.Argument(..., help="What to compare across codebases"),
    codebases: str = typer.Option(
        "goldentooth_agent", "--codebases", "-c", help="Comma-separated codebase names"
    ),
) -> None:
    """Compare implementations across different codebases."""

    async def _compare() -> None:
        introspection_service = world.get(CodebaseIntrospectionService)

        codebase_list = [name.strip() for name in codebases.split(",")]

        with console.status("🔍 Comparing codebases..."):
            comparison = await introspection_service.compare_codebases(
                query, codebase_list
            )

        _display_comparison_results(comparison)

    asyncio.run(_compare())


@app.command("add")
def add_codebase(
    name: str = typer.Argument(..., help="Codebase identifier"),
    path: str = typer.Argument(..., help="Path to codebase root"),
    display_name: str | None = typer.Option(
        None, "--display-name", "-d", help="Human-readable name"
    ),
    description: str = typer.Option("", "--description", help="Codebase description"),
    index_now: bool = typer.Option(
        True, "--index/--no-index", help="Index immediately after adding"
    ),
) -> None:
    """Add an external codebase for comparison and analysis."""

    async def _add() -> None:
        introspection_service = world.get(CodebaseIntrospectionService)

        codebase_path = Path(path)
        if not codebase_path.exists():
            console.print(f"❌ Path does not exist: {path}")
            return

        with console.status("➕ Adding codebase..."):
            result = await introspection_service.add_external_codebase(
                name=name,
                path=codebase_path,
                display_name=display_name,
                description=description,
            )

        if index_now:
            console.print(f"✅ Added and indexed codebase '{name}'")
            console.print(
                f"📊 Documents: {result['documents_processed']}, Chunks: {result['chunks_created']}"
            )
        else:
            console.print(f"✅ Added codebase '{name}' (not indexed)")
            console.print(
                "💡 Run 'goldentooth-agent codebase index {name}' to index it"
            )

    asyncio.run(_add())


@app.command("list")
def list_codebases() -> None:
    """List all available codebases."""

    async def _list() -> None:
        introspection_service = world.get(CodebaseIntrospectionService)
        await introspection_service.initialize()

        codebases = introspection_service.list_available_codebases()

        if not codebases:
            console.print(
                "No codebases available. Add one with 'goldentooth-agent codebase add'"
            )
            return

        table = Table(title="📚 Available Codebases")
        table.add_column("Name", style="cyan")
        table.add_column("Display Name", style="green")
        table.add_column("Documents", justify="right")
        table.add_column("Lines", justify="right")
        table.add_column("Last Indexed", style="dim")

        for codebase in codebases:
            table.add_row(
                codebase.name,
                codebase.display_name,
                str(codebase.document_count),
                str(codebase.total_lines),
                codebase.last_indexed or "Never",
            )

        console.print(table)

    asyncio.run(_list())


@app.command("tokens")
def token_analysis(
    days: int = typer.Option(30, "--days", "-d", help="Analysis period in days"),
    show_breakdown: bool = typer.Option(
        False, "--breakdown", "-b", help="Show detailed cost breakdown"
    ),
    export_path: str | None = typer.Option(
        None, "--export", "-e", help="Export data to file"
    ),
) -> None:
    """Analyze token usage and costs for embedding operations."""

    async def _analyze() -> None:
        introspection_service = world.get(CodebaseIntrospectionService)
        await introspection_service.initialize()

        token_tracker = introspection_service.collection.token_tracker

        # Get comprehensive statistics
        stats = token_tracker.get_usage_statistics(days=days)
        budget_status = token_tracker.check_budget_status()

        # Display main statistics
        console.print(
            Panel.fit(
                f"📊 **Token Usage Analysis** ({days} days)\n\n"
                f"💰 **Cost Summary:**\n"
                f"• Total operations: {stats['total_operations']:,}\n"
                f"• Total tokens: {stats['total_tokens']:,}\n"
                f"• Total cost: ${stats['total_cost_usd']:.4f}\n"
                f"• Cache hit rate: {stats['cache_hit_rate']:.1%}\n\n"
                f"💡 **Change Detection Savings:**\n"
                f"• Operations skipped: {stats['change_detection_savings']['operations_skipped']:,}\n"
                f"• Tokens saved: {stats['change_detection_savings']['estimated_tokens_saved']:,}\n"
                f"• Cost saved: ${stats['change_detection_savings']['estimated_cost_saved_usd']:.4f}\n\n"
                f"📈 **Budget Status:**\n"
                f"• Daily usage: {budget_status['daily_used']:,} / {budget_status['daily_limit']:,} ({budget_status['daily_usage_pct']:.1%})\n"
                f"• Monthly usage: {budget_status['monthly_used']:,} / {budget_status['monthly_limit']:,} ({budget_status['monthly_usage_pct']:.1%})",
                title="🪙 Token Analysis",
            )
        )

        # Show warnings if any
        if budget_status["warnings"]:
            console.print(
                Panel(
                    "\n".join(f"⚠️ {warning}" for warning in budget_status["warnings"]),
                    title="Budget Warnings",
                    border_style="yellow",
                )
            )

        # Show detailed breakdown if requested
        if show_breakdown:
            console.print("\n📋 **Detailed Breakdown:**")

            # By operation type
            if stats["by_operation_type"]:
                table = Table(title="By Operation Type")
                table.add_column("Operation", style="cyan")
                table.add_column("Count", justify="right")
                table.add_column("Tokens", justify="right")
                table.add_column("Cost", justify="right")

                for op_type, data in stats["by_operation_type"].items():
                    table.add_row(
                        op_type, f"{data[0]:,}", f"{data[1]:,}", f"${data[2]:.4f}"
                    )
                console.print(table)

            # By document type
            if stats["by_document_type"]:
                table = Table(title="By Document Type")
                table.add_column("Document Type", style="green")
                table.add_column("Count", justify="right")
                table.add_column("Tokens", justify="right")

                for doc_type, data in stats["by_document_type"].items():
                    table.add_row(doc_type, f"{data[0]:,}", f"{data[1]:,}")
                console.print(table)

        # Export data if requested
        if export_path:
            from pathlib import Path

            export_file = Path(export_path)
            token_tracker.export_usage_data(export_file)
            console.print(f"✅ Data exported to {export_path}")

    asyncio.run(_analyze())


@app.command("budget")
def budget_management(
    daily_limit: int | None = typer.Option(
        None, "--daily-limit", help="Set daily token limit"
    ),
    monthly_limit: int | None = typer.Option(
        None, "--monthly-limit", help="Set monthly token limit"
    ),
    warning_threshold: float | None = typer.Option(
        None, "--warning-threshold", help="Warning threshold (0.0-1.0)"
    ),
    reset_usage: bool = typer.Option(False, "--reset", help="Reset usage counters"),
) -> None:
    """Manage token budget and limits."""

    async def _budget() -> None:
        introspection_service = world.get(CodebaseIntrospectionService)
        await introspection_service.initialize()

        token_tracker = introspection_service.collection.token_tracker

        # Update budget settings if provided
        if daily_limit is not None:
            token_tracker.budget.daily_limit = daily_limit
            token_tracker._save_budget()
            console.print(f"✅ Daily limit set to {daily_limit:,} tokens")

        if monthly_limit is not None:
            token_tracker.budget.monthly_limit = monthly_limit
            token_tracker._save_budget()
            console.print(f"✅ Monthly limit set to {monthly_limit:,} tokens")

        if warning_threshold is not None:
            if not 0.0 <= warning_threshold <= 1.0:
                console.print("❌ Warning threshold must be between 0.0 and 1.0")
                return
            token_tracker.budget.warning_threshold = warning_threshold
            token_tracker._save_budget()
            console.print(f"✅ Warning threshold set to {warning_threshold:.1%}")

        if reset_usage:
            token_tracker.budget.daily_used = 0
            token_tracker.budget.monthly_used = 0
            token_tracker._save_budget()
            console.print("✅ Usage counters reset")

        # Display current budget status
        budget_status = token_tracker.check_budget_status()

        console.print(
            Panel.fit(
                f"💰 **Budget Configuration:**\n"
                f"• Daily limit: {budget_status['daily_limit']:,} tokens\n"
                f"• Monthly limit: {budget_status['monthly_limit']:,} tokens\n"
                f"• Warning threshold: {token_tracker.budget.warning_threshold:.1%}\n\n"
                f"📊 **Current Usage:**\n"
                f"• Daily used: {budget_status['daily_used']:,} ({budget_status['daily_usage_pct']:.1%})\n"
                f"• Monthly used: {budget_status['monthly_used']:,} ({budget_status['monthly_usage_pct']:.1%})\n"
                f"• Within budget: {'✅ Yes' if budget_status['within_budget'] else '❌ No'}",
                title="🏦 Token Budget",
            )
        )

    asyncio.run(_budget())


def _display_query_results(result: Any) -> None:
    """Display introspection query results."""
    console.print(
        Panel.fit(
            f"🔍 **Query:** {result.query}\n"
            f"📊 **Results:** {result.total_results} found in {result.execution_time:.2f}s\n"
            f"🗂️ **Codebases:** {', '.join(result.codebases_searched)}",
            title="Query Results",
        )
    )

    for i, res in enumerate(result.results, 1):
        metadata = res.get("metadata", {})
        source = res.get("source", {})

        # Create title
        doc_type = metadata.get("document_type", "unknown")
        module_path = metadata.get("module_path", "")
        title = f"[{i}] {doc_type}: {module_path}"

        # Create content preview
        content = res.get("content", "")
        preview = content[:300] + "..." if len(content) > 300 else content

        # Add source info
        file_path = source.get("file_path", "")
        line_info = ""
        if source.get("line_start") and source.get("line_end"):
            line_info = f" (lines {source['line_start']}-{source['line_end']})"

        console.print(
            Panel(
                f"**Score:** {res.get('score', 0):.3f}\n"
                f"**File:** {file_path}{line_info}\n\n"
                f"{preview}",
                title=title,
            )
        )


def _display_rag_results(result: Any) -> None:
    """Display RAG query results."""
    console.print(
        Panel.fit(
            f"🧠 **Query:** {result.query}\n"
            f"⏱️ **Time:** {result.execution_time:.2f}s\n"
            f"📊 **Results:** {len(result.codebase_results)} codebase + {len(result.document_results)} docs",
            title="RAG Query Results",
        )
    )

    # Display synthesized answer
    if result.combined_answer:
        console.print(
            Panel(
                result.combined_answer,
                title="🎯 Synthesized Answer",
                border_style="green",
            )
        )

    # Display sources
    if result.sources:
        console.print(
            Panel(
                "\n".join(f"• {source}" for source in result.sources),
                title="📚 Sources",
                border_style="blue",
            )
        )


def _display_codebase_overview(overview: dict[str, Any]) -> None:
    """Display codebase overview."""
    codebase_info = overview["codebase_info"]
    summary = overview["summary"]

    console.print(
        Panel.fit(
            f"📚 **{codebase_info['display_name']}**\n"
            f"📁 Path: {codebase_info['root_path']}\n"
            f"📊 Documents: {summary['total_documents']}\n"
            f"📝 Lines: {summary['total_lines']}\n"
            f"🕐 Last Indexed: {summary['last_indexed']}\n\n"
            f"📖 {codebase_info['description']}",
            title="Codebase Overview",
        )
    )


def _display_comparison_results(comparison: Any) -> None:
    """Display codebase comparison results."""
    console.print(
        Panel.fit(
            f"🔍 **Query:** {comparison.query}\n"
            f"📚 **Codebases:** {', '.join(comparison.codebases)}",
            title="Codebase Comparison",
        )
    )

    # Display recommendations
    if comparison.recommendations:
        console.print(
            Panel(
                "\n".join(f"• {rec}" for rec in comparison.recommendations),
                title="💡 Recommendations",
                border_style="yellow",
            )
        )
