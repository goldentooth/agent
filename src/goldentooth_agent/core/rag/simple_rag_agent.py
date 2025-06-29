"""
Simplified RAG agent using the working core components.
"""

from typing import Any

from antidote import inject

from ..flow_agent import FlowAgent, AgentInput, AgentOutput
from .simple_rag_service import SimpleRAGService


class SimpleRAGAgent:
    """Simplified RAG agent for document-based conversations."""

    def __init__(
        self,
        rag_service: SimpleRAGService = inject.me(),
        name: str = "SimpleRAGAgent",
    ) -> None:
        """Initialize the simple RAG agent."""
        self.rag_service = rag_service
        self.name = name

    async def process_question(
        self,
        question: str,
        conversation_history: list[dict[str, str]] | None = None,
        max_results: int = 5,
        store_type: str | None = None,
    ) -> dict[str, Any]:
        """Process a question using the RAG service.

        Args:
            question: User's question
            conversation_history: Previous conversation context (optional)
            max_results: Maximum number of documents to retrieve
            store_type: Optional filter by document store type

        Returns:
            RAG response with answer, sources, and metadata
        """
        # For now, we'll focus on the current question
        # Conversation history integration can be added later
        
        result = await self.rag_service.query(
            question=question,
            max_results=max_results,
            store_type=store_type,
        )
        
        # Convert to expected format (compatible with existing CLI)
        response_obj = type('RAGResponse', (), {
            'response': result["answer"],
            'sources': result["retrieved_documents"],
            'confidence': self._calculate_confidence(result),
            'suggestions': self._generate_suggestions(result),
            'metadata': result["metadata"],
        })()
        
        return response_obj

    def _calculate_confidence(self, result: dict[str, Any]) -> float:
        """Calculate confidence score based on retrieval results."""
        docs = result.get("retrieved_documents", [])
        
        if not docs:
            return 0.3  # Low confidence with no sources
        
        # Base confidence on similarity scores
        similarities = [doc.get("similarity_score", 0.0) for doc in docs]
        avg_similarity = sum(similarities) / len(similarities)
        
        # Adjust based on number of sources
        source_bonus = min(0.2, len(docs) * 0.05)  # Up to 0.2 bonus for multiple sources
        
        confidence = min(1.0, avg_similarity + source_bonus)
        return round(confidence, 2)

    def _generate_suggestions(self, result: dict[str, Any]) -> list[str]:
        """Generate helpful suggestions based on the result."""
        suggestions = []
        
        docs = result.get("retrieved_documents", [])
        
        if not docs:
            suggestions.extend([
                "Try using different keywords or more specific terms",
                "Consider broadening your search with related concepts",
            ])
        elif len(docs) < 3:
            suggestions.append("Try asking more specific questions for better results")
        
        # Add suggestions based on document types found
        doc_types = set()
        for doc in docs:
            if doc.get("is_chunk"):
                chunk_type = doc.get("chunk_type", "content")
                doc_types.add(f"chunk:{chunk_type}")
            else:
                store_type = doc.get("store_type", "unknown")
                doc_types.add(f"doc:{store_type}")
        
        if "doc:github.repos" in doc_types:
            suggestions.append("Found repository information - try asking about specific projects")
        
        return suggestions[:3]  # Limit to 3 suggestions


def create_simple_rag_agent() -> SimpleRAGAgent:
    """Factory function to create a simple RAG agent with dependencies."""
    from ..paths import Paths
    from ..document_store import DocumentStore
    from ..embeddings import OpenAIEmbeddingsService, VectorStore
    from ..llm.claude_client import ClaudeFlowClient
    
    # Initialize all dependencies
    paths = Paths()
    document_store = DocumentStore(paths=paths)
    embeddings_service = OpenAIEmbeddingsService(paths=paths)
    vector_store = VectorStore(paths=paths)
    claude_client = ClaudeFlowClient()
    
    # Create RAG service
    rag_service = SimpleRAGService(
        document_store=document_store,
        embeddings_service=embeddings_service,
        vector_store=vector_store,
        claude_client=claude_client,
    )
    
    # Create and return agent
    return SimpleRAGAgent(rag_service=rag_service)