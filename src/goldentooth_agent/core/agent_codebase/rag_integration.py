"""
Integration between codebase introspection and existing RAG infrastructure.
"""

from __future__ import annotations

from typing import Any

from antidote import inject, injectable
from pydantic import BaseModel, Field

from goldentooth_agent.core.rag.rag_service import RAGService

from .introspection import CodebaseIntrospectionService, IntrospectionQuery, IntrospectionResult
from .source import DocumentSource


class CodebaseRAGQuery(BaseModel):
    """Query that combines codebase introspection with RAG capabilities."""
    
    query: str = Field(..., description="Natural language query")
    include_codebase: bool = Field(default=True, description="Include codebase introspection")
    include_documents: bool = Field(default=True, description="Include document store search")
    codebase_weight: float = Field(default=0.6, description="Weight for codebase results (0-1)")
    max_results: int = Field(default=10, description="Maximum total results")


class CodebaseRAGResult(BaseModel):
    """Combined result from codebase introspection and document RAG."""
    
    query: str = Field(..., description="Original query")
    codebase_results: list[dict[str, Any]] = Field(default_factory=list, description="Codebase introspection results")
    document_results: list[dict[str, Any]] = Field(default_factory=list, description="Document store results")
    combined_answer: str = Field(default="", description="Synthesized answer")
    sources: list[str] = Field(default_factory=list, description="Source references")
    execution_time: float = Field(default=0.0, description="Total execution time")


@injectable
class CodebaseRAGIntegration:
    """
    Integration service that combines codebase introspection with document RAG.
    
    Mechanical integration process:
    1. Route queries to appropriate services based on content
    2. Execute parallel searches in codebase and document store
    3. Combine and rank results based on relevance
    4. Synthesize comprehensive answers using LLM
    5. Return unified response with source attribution
    """
    
    def __init__(
        self,
        rag_service: RAGService = inject.me(),
        introspection_service: CodebaseIntrospectionService = inject.me()
    ) -> None:
        self.rag_service = rag_service
        self.introspection_service = introspection_service
    
    async def query(self, query: CodebaseRAGQuery) -> CodebaseRAGResult:
        """
        Execute a combined codebase and document query.
        
        Mechanical process:
        1. Analyze query to determine search strategy
        2. Execute parallel searches in codebase and documents
        3. Combine results with weighted scoring
        4. Generate synthesized answer using LLM
        5. Return comprehensive result
        """
        import asyncio
        import time
        
        start_time = time.time()
        
        # Prepare search tasks
        tasks = []
        
        # Codebase introspection
        if query.include_codebase:
            codebase_query = IntrospectionQuery(
                query=query.query,
                limit=int(query.max_results * query.codebase_weight)
            )
            tasks.append(self._search_codebase(codebase_query))
        else:
            tasks.append(self._empty_codebase_result())
        
        # Document store search
        if query.include_documents:
            doc_limit = int(query.max_results * (1 - query.codebase_weight))
            tasks.append(self._search_documents(query.query, doc_limit))
        else:
            tasks.append(self._empty_document_result())
        
        # Execute searches in parallel
        codebase_result, document_result = await asyncio.gather(*tasks)
        
        # Combine results
        combined_results = self._combine_results(
            codebase_result, 
            document_result, 
            query.codebase_weight
        )
        
        # Generate synthesized answer
        answer = await self._synthesize_answer(query.query, combined_results)
        
        # Extract sources
        sources = self._extract_sources(codebase_result, document_result)
        
        execution_time = time.time() - start_time
        
        return CodebaseRAGResult(
            query=query.query,
            codebase_results=codebase_result.get("results", []),
            document_results=document_result.get("results", []),
            combined_answer=answer,
            sources=sources,
            execution_time=execution_time
        )
    
    async def _search_codebase(self, query: IntrospectionQuery) -> dict[str, Any]:
        """Search codebase using introspection service."""
        try:
            result = await self.introspection_service.query(query)
            return {
                "results": result.results,
                "total": result.total_results,
                "source_type": "codebase"
            }
        except Exception as e:
            return {"results": [], "total": 0, "error": str(e), "source_type": "codebase"}
    
    async def _search_documents(self, query: str, limit: int) -> dict[str, Any]:
        """Search document store using RAG service."""
        try:
            # Use RAG service's search capability
            result = await self.rag_service.search(query, limit=limit)
            
            # Format results to match codebase format
            formatted_results = []
            for doc in result.get("documents", []):
                formatted_results.append({
                    "content": doc.get("content", ""),
                    "score": doc.get("score", 0.0),
                    "metadata": doc.get("metadata", {}),
                    "source": {
                        "file_path": doc.get("metadata", {}).get("file_path", ""),
                        "source_name": doc.get("metadata", {}).get("source_name", "")
                    }
                })
            
            return {
                "results": formatted_results,
                "total": len(formatted_results),
                "source_type": "documents"
            }
        except Exception as e:
            return {"results": [], "total": 0, "error": str(e), "source_type": "documents"}
    
    async def _empty_codebase_result(self) -> dict[str, Any]:
        """Return empty codebase result."""
        return {"results": [], "total": 0, "source_type": "codebase"}
    
    async def _empty_document_result(self) -> dict[str, Any]:
        """Return empty document result."""
        return {"results": [], "total": 0, "source_type": "documents"}
    
    def _combine_results(
        self,
        codebase_result: dict[str, Any],
        document_result: dict[str, Any],
        codebase_weight: float
    ) -> list[dict[str, Any]]:
        """
        Combine and rank results from both sources.
        
        Mechanical combination:
        1. Apply source-specific weights to scores
        2. Merge result lists
        3. Sort by weighted relevance score
        4. Remove duplicates based on content similarity
        """
        combined = []
        
        # Add codebase results with weight
        for result in codebase_result.get("results", []):
            weighted_result = result.copy()
            weighted_result["weighted_score"] = result.get("score", 0.0) * codebase_weight
            weighted_result["source_type"] = "codebase"
            combined.append(weighted_result)
        
        # Add document results with weight
        document_weight = 1.0 - codebase_weight
        for result in document_result.get("results", []):
            weighted_result = result.copy()
            weighted_result["weighted_score"] = result.get("score", 0.0) * document_weight
            weighted_result["source_type"] = "documents"
            combined.append(weighted_result)
        
        # Sort by weighted score (descending)
        combined.sort(key=lambda x: x.get("weighted_score", 0.0), reverse=True)
        
        # TODO: Add deduplication based on content similarity
        
        return combined
    
    async def _synthesize_answer(self, query: str, results: list[dict[str, Any]]) -> str:
        """
        Synthesize a comprehensive answer from combined results.
        
        Mechanical synthesis:
        1. Extract key information from top results
        2. Identify code examples and documentation
        3. Generate coherent answer using LLM
        4. Include both conceptual explanation and practical examples
        """
        if not results:
            return "No relevant information found in the codebase or documents."
        
        # Extract content from top results
        content_pieces = []
        code_examples = []
        documentation = []
        
        for result in results[:5]:  # Use top 5 results
            content = result.get("content", "")
            source_type = result.get("source_type", "")
            
            if source_type == "codebase":
                # Categorize codebase content
                doc_type = result.get("metadata", {}).get("document_type", "")
                if doc_type in ["function_definition", "class_definition", "source_code"]:
                    code_examples.append(content[:500])  # Truncate for synthesis
                else:
                    documentation.append(content[:500])
            else:
                # Document store content
                documentation.append(content[:500])
        
        # Build synthesis prompt
        synthesis_prompt = f"""Based on the following information, provide a comprehensive answer to the query: "{query}"

Documentation and explanations:
{chr(10).join(documentation[:3])}

Code examples:
{chr(10).join(code_examples[:3])}

Please provide a clear, practical answer that combines conceptual understanding with concrete examples where relevant."""
        
        try:
            # Use RAG service's LLM to synthesize answer
            response = await self.rag_service.claude_client.generate_response(
                messages=[{"role": "user", "content": synthesis_prompt}],
                max_tokens=1000
            )
            return response.get("content", "Unable to generate synthesis.")
        except Exception as e:
            # Fallback to simple concatenation
            return f"Based on the available information:\n\n" + "\n\n".join(content_pieces[:3])
    
    def _extract_sources(
        self,
        codebase_result: dict[str, Any],
        document_result: dict[str, Any]
    ) -> list[str]:
        """Extract source references from results."""
        sources = []
        
        # Codebase sources
        for result in codebase_result.get("results", [])[:3]:
            source_info = result.get("source", {})
            file_path = source_info.get("file_path", "")
            module_path = result.get("metadata", {}).get("module_path", "")
            
            if file_path and module_path:
                sources.append(f"Code: {module_path} ({file_path})")
            elif file_path:
                sources.append(f"Code: {file_path}")
        
        # Document sources
        for result in document_result.get("results", [])[:3]:
            source_info = result.get("source", {})
            source_name = source_info.get("source_name", "")
            file_path = source_info.get("file_path", "")
            
            if source_name and file_path:
                sources.append(f"Docs: {source_name} ({file_path})")
            elif source_name:
                sources.append(f"Docs: {source_name}")
        
        return sources
    
    async def get_codebase_overview(self) -> dict[str, Any]:
        """Get comprehensive overview of the codebase for RAG context."""
        return await self.introspection_service.get_codebase_overview("goldentooth_agent")
    
    async def index_codebase_for_rag(self) -> dict[str, Any]:
        """Index the codebase for RAG queries."""
        return await self.introspection_service.index_current_codebase()