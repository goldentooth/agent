"""
Main codebase introspection service providing high-level query interface.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from antidote import inject, injectable
from pydantic import BaseModel, Field

from goldentooth_agent.core.embeddings import VectorStore

from .collection import CodebaseCollection, CodebaseInfo
from .schema import CodebaseDocumentType


class IntrospectionQuery(BaseModel):
    """Query for codebase introspection."""

    query: str = Field(..., description="Natural language query")
    codebases: list[str] | None = Field(
        default=None, description="Specific codebases to search"
    )
    document_types: list[CodebaseDocumentType] | None = Field(
        default=None, description="Document types to include"
    )
    limit: int = Field(default=10, description="Maximum results")
    include_source: bool = Field(
        default=True, description="Include source code in results"
    )


class IntrospectionResult(BaseModel):
    """Result from codebase introspection query."""

    query: str = Field(..., description="Original query")
    results: list[dict[str, Any]] = Field(
        ..., description="Search results with metadata"
    )
    total_results: int = Field(..., description="Total number of results found")
    codebases_searched: list[str] = Field(
        ..., description="Codebases that were searched"
    )
    execution_time: float = Field(..., description="Query execution time in seconds")

    def get_code_snippets(self) -> list[str]:
        """Extract code snippets from results."""
        snippets = []
        for result in self.results:
            if result.get("metadata", {}).get("document_type") in [
                "source_code",
                "function_definition",
                "class_definition",
            ]:
                content = result.get("content", "")
                if content:
                    snippets.append(content)
        return snippets

    def get_documentation_sections(self) -> list[str]:
        """Extract documentation sections from results."""
        docs = []
        for result in self.results:
            if result.get("metadata", {}).get("document_type") in [
                "module_api",
                "module_background",
            ]:
                content = result.get("content", "")
                if content:
                    docs.append(content)
        return docs


class CodebaseComparison(BaseModel):
    """Comparison between different codebases."""

    query: str = Field(..., description="Comparison query")
    codebases: list[str] = Field(..., description="Codebases being compared")
    similarities: dict[str, list[dict[str, Any]]] = Field(
        ..., description="Similar patterns by codebase"
    )
    differences: dict[str, str] = Field(..., description="Key differences identified")
    recommendations: list[str] = Field(
        ..., description="Recommendations based on comparison"
    )


@injectable
class CodebaseIntrospectionService:
    """
    High-level service for codebase introspection and analysis.

    Mechanical query processing:
    1. Parse natural language query into search terms
    2. Route to appropriate document types based on query intent
    3. Perform vector search across indexed documents
    4. Post-process results with ranking and filtering
    5. Return structured results with metadata
    """

    def __init__(
        self,
        vector_store: VectorStore = inject.me(),
        collection_name: str = "agent_codebase",
    ) -> None:
        self.collection = CodebaseCollection(vector_store, collection_name)
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the service and add default codebase."""
        if self._initialized:
            return

        # Add the current Goldentooth Agent codebase
        current_path = Path(__file__).parent.parent.parent.parent.parent
        await self.collection.add_codebase(
            name="goldentooth_agent",
            root_path=current_path,
            display_name="Goldentooth Agent",
            description="The main Goldentooth Agent codebase with flow-based architecture",
        )

        self._initialized = True

    async def index_current_codebase(self) -> dict[str, Any]:
        """Index the current Goldentooth Agent codebase."""
        await self.initialize()
        return await self.collection.index_codebase("goldentooth_agent")

    async def add_external_codebase(
        self,
        name: str,
        path: Path,
        display_name: str | None = None,
        description: str = "",
    ) -> dict[str, Any]:
        """Add and index an external codebase for comparison."""
        await self.initialize()

        await self.collection.add_codebase(
            name=name,
            root_path=path,
            display_name=display_name,
            description=description,
        )

        return await self.collection.index_codebase(name)

    async def query(self, query: IntrospectionQuery) -> IntrospectionResult:
        """
        Execute an introspection query.

        Mechanical process:
        1. Analyze query intent to determine search strategy
        2. Route to appropriate document types
        3. Execute vector search with filters
        4. Post-process and rank results
        5. Return structured response
        """
        import time

        start_time = time.time()

        await self.initialize()

        # Determine which codebases to search
        codebases_to_search = query.codebases or ["goldentooth_agent"]

        # Determine document types based on query intent
        document_types = query.document_types or self._infer_document_types(query.query)

        # Execute search
        search_results = await self.collection.search(
            query=query.query,
            codebase_names=codebases_to_search,
            document_types=document_types,
            limit=query.limit,
        )

        # Process results
        processed_results = []
        for result in search_results:
            # Extract metadata safely
            metadata = result.get("metadata", {})
            processed_result = {
                "content": result.get("content", ""),
                "score": result.get("score", 0.0),
                "metadata": metadata,
                "source": {
                    "file_path": metadata.get("file_path", ""),
                    "module_path": metadata.get("module_path", ""),
                    "line_start": metadata.get("line_start", 0),
                    "line_end": metadata.get("line_end", 0),
                },
            }

            # Add source code if requested
            if query.include_source and metadata.get("document_type") not in [
                "source_code",
                "function_definition",
                "class_definition",
            ]:
                # Try to find related source code
                source_content = await self._find_related_source(metadata)
                if source_content:
                    processed_result["related_source"] = source_content

            processed_results.append(processed_result)

        execution_time = time.time() - start_time

        return IntrospectionResult(
            query=query.query,
            results=processed_results,
            total_results=len(search_results),
            codebases_searched=codebases_to_search,
            execution_time=execution_time,
        )

    async def compare_codebases(
        self, query: str, codebase_names: list[str]
    ) -> CodebaseComparison:
        """
        Compare implementations across different codebases.

        Mechanical comparison:
        1. Search for similar patterns in each codebase
        2. Identify common implementations and differences
        3. Analyze architectural patterns and design choices
        4. Generate comparison summary and recommendations
        """
        await self.initialize()

        similarities = {}
        differences = {}

        # Search each codebase for the query
        for codebase_name in codebase_names:
            codebase_query = IntrospectionQuery(
                query=query, codebases=[codebase_name], limit=5
            )
            result = await self.query(codebase_query)
            similarities[codebase_name] = result.results

        # Analyze differences (simplified implementation)
        for codebase_name in codebase_names:
            codebase_results = similarities[codebase_name]
            if codebase_results:
                # Extract key characteristics
                doc_types = [
                    r["metadata"].get("document_type") for r in codebase_results
                ]
                complexity_scores = [
                    r["metadata"].get("complexity_score", 0) for r in codebase_results
                ]
                avg_complexity = (
                    sum(complexity_scores) / len(complexity_scores)
                    if complexity_scores
                    else 0
                )

                differences[codebase_name] = (
                    f"Primary document types: {', '.join(set(doc_types))}. "
                    f"Average complexity: {avg_complexity:.2f}"
                )

        # Generate recommendations (simplified)
        recommendations = [
            "Compare architectural patterns between codebases",
            "Look for reusable components and design patterns",
            "Consider consolidating similar functionality",
        ]

        if len(codebase_names) > 1:
            recommendations.append(
                f"Analyze trade-offs between {' and '.join(codebase_names)} approaches"
            )

        return CodebaseComparison(
            query=query,
            codebases=codebase_names,
            similarities=similarities,
            differences=differences,
            recommendations=recommendations,
        )

    def _infer_document_types(self, query: str) -> list[CodebaseDocumentType]:
        """Infer which document types to search based on query content."""
        query_lower = query.lower()

        # Keywords that suggest specific document types
        type_keywords = {
            CodebaseDocumentType.FUNCTION_DEFINITION: [
                "function",
                "method",
                "def",
                "callable",
            ],
            CodebaseDocumentType.CLASS_DEFINITION: [
                "class",
                "object",
                "type",
                "inheritance",
            ],
            CodebaseDocumentType.MODULE_BACKGROUND: [
                "design",
                "architecture",
                "motivation",
                "theory",
                "background",
            ],
            CodebaseDocumentType.MODULE_API: [
                "api",
                "interface",
                "usage",
                "example",
                "how to",
            ],
            CodebaseDocumentType.SOURCE_CODE: [
                "implementation",
                "code",
                "source",
                "algorithm",
            ],
            CodebaseDocumentType.TEST_CODE: ["test", "testing", "spec", "verification"],
        }

        matching_types = []
        for doc_type, keywords in type_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                matching_types.append(doc_type)

        # Default to comprehensive search if no specific types inferred
        if not matching_types:
            matching_types = [
                CodebaseDocumentType.MODULE_API,
                CodebaseDocumentType.MODULE_BACKGROUND,
                CodebaseDocumentType.FUNCTION_DEFINITION,
                CodebaseDocumentType.CLASS_DEFINITION,
            ]

        return matching_types

    async def _find_related_source(self, metadata: dict[str, Any]) -> str | None:
        """Find related source code for a documentation result."""
        # This would search for source code in the same module
        module_path = metadata.get("module_path")
        if not module_path:
            return None

        # Search for source code in the same module
        source_query = IntrospectionQuery(
            query=f"module:{module_path}",
            document_types=[CodebaseDocumentType.SOURCE_CODE],
            limit=1,
        )

        try:
            result = await self.query(source_query)
            if result.results:
                content = result.results[0]["content"]
                if isinstance(content, str):
                    return content[:500] + "..."  # Truncate for display
                return str(content)[:500] + "..."
        except Exception:
            pass

        return None

    async def get_codebase_overview(self, codebase_name: str) -> dict[str, Any]:
        """Get comprehensive overview of a codebase."""
        await self.initialize()

        codebase_info = self.collection.get_codebase_info(codebase_name)
        if not codebase_info:
            raise ValueError(f"Codebase '{codebase_name}' not found")

        # Get architecture overview
        arch_query = IntrospectionQuery(
            query="architecture system design overview",
            codebases=[codebase_name],
            document_types=[
                CodebaseDocumentType.MODULE_BACKGROUND,
                CodebaseDocumentType.MODULE_API,
            ],
            limit=5,
        )
        arch_result = await self.query(arch_query)

        # Get key components
        components_query = IntrospectionQuery(
            query="main components core modules",
            codebases=[codebase_name],
            document_types=[
                CodebaseDocumentType.CLASS_DEFINITION,
                CodebaseDocumentType.MODULE_API,
            ],
            limit=10,
        )
        components_result = await self.query(components_query)

        return {
            "codebase_info": codebase_info.model_dump(),
            "architecture": arch_result.model_dump(),
            "key_components": components_result.model_dump(),
            "summary": {
                "total_documents": codebase_info.document_count,
                "total_lines": codebase_info.total_lines,
                "last_indexed": codebase_info.last_indexed,
            },
        }

    def list_available_codebases(self) -> list[CodebaseInfo]:
        """List all available codebases."""
        return self.collection.list_codebases()
